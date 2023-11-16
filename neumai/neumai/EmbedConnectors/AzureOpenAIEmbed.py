from typing import List, Tuple
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument
from langchain.embeddings import azure_openai

class AzureOpenAIEmbed(EmbedConnector):
    @property
    def embed_name(self) -> str:
        return 'AzureOpenAIEmbed'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ['deployment_name', 'api_key', 'endpoint']

    @property
    def optionalProperties(self) -> List[str]:
        return []

    def validation(self) -> bool:
        """Validate connector setup"""
        try:
            deployment_name = self.embed_information["deployment_name"]
            api_key = self.embed_information["api_key"]
            api_base = self.embed_information["endpoint"]
        except Exception as e:
            raise ValueError(f"Required properties not set. Required properties: {self.requiredProperties}")
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with Azure OpenAI"""
        max_retries = self.embed_information.get('max_retries', 20)
        chunk_size = max(self.embed_information.get('chunk_size', 16), 16)

        embedding = azure_openai.AzureOpenAIEmbeddings(
            max_retries=max_retries,
            chunk_size=chunk_size,
            azure_deployment=self.embed_information["deployment_name"],
            api_key=self.embed_information['api_key'],
            azure_endpoint=self.embed_information['endpoint'],
        )
        embeddings = []
        texts = [x.content for x in documents]
        embeddings  = embedding.embed_documents(texts=texts)
        info = {
            "estimated_cost":str("Not implemented"),
            "total_tokens":str("Not implemented"),
            "attempts_used":str("Not implemented")
        }
        return embeddings,info
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embeddings for a single query using Azure OpenAI"""

        embedding = azure_openai.AzureOpenAIEmbeddings(
            azure_deployment=self.embed_information["deployment_name"],
            api_key=self.embed_information['api_key'],
            azure_endpoint=self.embed_information['endpoint'],
        )
        return embedding.embed_query(query)