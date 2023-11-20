from typing import List, Tuple, Optional
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from langchain.embeddings.openai import OpenAIEmbeddings
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.Exceptions import OpenAIConnectionException
from pydantic import BaseModel, Field

class OpenAIEmbed(EmbedConnector):
    """
    OpenAI Embed Connector

    Facilitates embedding and processing data using OpenAI's services. This connector is designed to interact directly with OpenAI's APIs, requiring an API key for authentication and operation.

    Attributes:
    -----------
    api_key : str
        The API key for accessing OpenAI services. Essential for authenticating and using OpenAI's API for data processing.

    max_retries : Optional[int]
        The maximum number of retries for connection attempts with OpenAI's services. Default is 20 retries.

    chunk_size : Optional[int]
        The size of chunks for processing data, defined by the number of items. Default is 1000, suitable for large data sets.
    """

    api_key: str = Field(..., description="API key for OpenAI services.")
    
    max_retries: Optional[int] = Field(20, description="Maximum number of retries for the connection.")

    chunk_size: Optional[int] = Field(1000, description="Size of chunks for processing data.")

    @property
    def embed_name(self) -> str:
        return 'OpenAIEmbed'
    
    @property
    def required_properties(self) -> List[str]:
        return ["api_key"]

    @property
    def optional_properties(self) -> List[str]:
        return ['max_retries', 'chunk_size']

    def validation(self) -> bool:
        """config_validation connector setup"""
        try:
            OpenAIEmbeddings(max_retries=20, api_key=self.api_key, chunk_size=1000)
        except Exception as e:
            raise OpenAIConnectionException(f"OpenAI couldn't be initialized. See exception: {e}")
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with OpenAI"""

        embedding = OpenAIEmbeddings(
            max_retries=self.max_retries,
            chunk_size=self.chunk_size,
            api_key=self.api_key, 
        )
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
        embedding = OpenAIEmbeddings(api_key=self.api_key)
        return embedding.embed_query(query)
