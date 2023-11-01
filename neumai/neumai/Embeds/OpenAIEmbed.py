from typing import List, Tuple
from langchain.embeddings.openai import OpenAIEmbeddings
from .EmbedConnector import EmbedConnector
from neumai_tools import NeumDocument

class OpenAIEmbed(EmbedConnector):
    @property
    def embed_name(self) -> str:
        return 'OpenAIEmbed'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["api_key"]

    @property
    def optionalProperties(self) -> List[str]:
        return ['organization', 'max_retries', 'chunk_size']

    def validation(self) -> bool:
        """Validate connector setup"""
        try:
            api_key = self.embed_information['api_key']
        except:
            raise ValueError("Required properties not set")
        try:
            organization = self.embed_information.get('organization', None)
            OpenAIEmbeddings(max_retries=20, openai_api_key=api_key, openai_organization=organization, chunk_size=1000)
        except Exception as e:
            raise ValueError(f"OpenAI couldn't be initialized. See exception: {e}")
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with OpenAI"""
        cost_per_token = 0.000000001 # ADA-002 as of Sept 2023
        max_retries = self.embed_information.get('max_retries', 20)
        chunk_size = self.embed_information.get('chunk_size', 1000)
        organization = self.embed_information.get('organization', None)

        embedding = OpenAIEmbeddings(max_retries=max_retries, openai_api_key=self.embed_information['api_key'], openai_organization=organization, chunk_size=chunk_size)
        embeddings = []
        texts = [x.content for x in documents]
        # do we want to persist some embeddings if they were able to be wrriten but not another "batch" of them? or should we treat all texts as an atomic operation
        embeddings, embedding_info = embedding.embed_documents(texts=texts)
        info = {
            "estimated_cost":str(embedding_info['tokens_used'] * cost_per_token),
            "total_tokens":str(embedding_info['tokens_used']),
            "attempts_used":str(embedding_info['attempts_per_chunk'])
        }
        return embeddings,info

    def embed_query(self, query: str) -> List[float]:
        import openai
        openai.api_key = self.embed_information["api_key"]
        openai.organization = self.embed_information.get("organization", "")
        result = openai.Embedding.create(input=query, model="text-embedding-ada-002")
        return result['data'][0]['embedding']
