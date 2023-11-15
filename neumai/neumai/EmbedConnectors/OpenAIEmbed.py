from typing import List, Tuple
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from langchain.embeddings.openai import OpenAIEmbeddings
from neumai.Shared.NeumDocument import NeumDocument
class OpenAIEmbed(EmbedConnector):
    """" OpenAI Embed Connector \n
    embed_information required: [ api_key ]"""

    @property
    def embed_name(self) -> str:
        return 'OpenAIEmbed'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["api_key"]

    @property
    def optionalProperties(self) -> List[str]:
        return ['max_retries', 'chunk_size']

    def validation(self) -> bool:
        """Validate connector setup"""
        try:
            api_key = self.embed_information['api_key']
        except:
            raise ValueError("Required properties not set")
        try:
            OpenAIEmbeddings(max_retries=20, api_key=api_key, chunk_size=1000)
        except Exception as e:
            raise ValueError(f"OpenAI couldn't be initialized. See exception: {e}")
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with OpenAI"""
        max_retries = self.embed_information.get('max_retries', 20)
        chunk_size = self.embed_information.get('chunk_size', 1000)

        embedding = OpenAIEmbeddings(max_retries=max_retries, api_key=self.embed_information['api_key'], chunk_size=chunk_size)
        embeddings = []
        texts = [x.content for x in documents]
        # do we want to persist some embeddings if they were able to be wrriten but not another "batch" of them? or should we treat all texts as an atomic operation
        embeddings  = embedding.embed_documents(texts=texts)
        #cost_per_token = 0.000000001 # ADA-002 as of Sept 2023
        info = {
            "estimated_cost":str("Not implemented"),
            "total_tokens":str("Not implemented"),
            "attempts_used":str("Not implemented")
        }
        return embeddings,info

    def embed_query(self, query: str) -> List[float]:
        """Generate embeddings for a single query using OpenAI"""
        embedding = OpenAIEmbeddings(api_key=self.embed_information['api_key'])
        return embedding.embed_query(query)