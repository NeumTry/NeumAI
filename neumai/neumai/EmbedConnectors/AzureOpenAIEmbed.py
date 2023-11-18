from typing import List, Tuple, Optional
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument
from langchain.embeddings import azure_openai
from pydantic import Field

class AzureOpenAIEmbed(EmbedConnector):
    """Azure OpenAI Embed Connector."""

    deployment_name: str = Field(..., description="Deployment name for Azure OpenAI.")

    api_key: str = Field(..., description="API key for Azure OpenAI.")

    endpoint: str = Field(..., description="Endpoint for Azure OpenAI.")

    max_retries: Optional[int] = Field(20, description="Maximum number of retries for the connection.")

    chunk_size: Optional[int] = Field(16, description="Size of chunks for processing data.")

    @property
    def embed_name(self) -> str:
        return 'AzureOpenAIEmbed'

    @property
    def required_properties(self) -> List[str]:
        return ['deployment_name', 'api_key', 'endpoint']

    @property
    def optional_properties(self) -> List[str]:
        return ['max_retries', 'chunk_size']
    
    def validation(self) -> bool:
        """config_validation connector setup"""
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with Azure OpenAI"""
        embedding = azure_openai.AzureOpenAIEmbeddings(
            max_retries=self.max_retries,
            chunk_size=max(self.chunk_size, 16),
            azure_deployment=self.deployment_name,
            api_key=self.api_key,
            azure_endpoint=self.endpoint
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
            azure_deployment=self.deployment_name,
            api_key=self.api_key,
            azure_endpoint=self.endpoint
        )
        return embedding.embed_query(query)