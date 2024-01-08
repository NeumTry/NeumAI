from typing import List, Tuple
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.Exceptions import HuggingFaceConnectonException
from huggingface_hub import InferenceClient
from pydantic import Field

class HuggingFaceEmbed(EmbedConnector):
    """
    Hugging Face Embed Connector
    """
    model:str = Field(..., description="HuggingFace model ID or a URL to a deployed Inference Endpoint")
    token: str = Field(..., description="HuggingFace token")

    @property
    def embed_name(self) -> str:
        return 'HuggingFaceEmbed'
    
    @property
    def required_properties(self) -> List[str]:
        return ["model","token"]

    @property
    def optional_properties(self) -> List[str]:
        return []
    
    def validation(self) -> bool:
        """config_validation connector setup"""
        try:
            InferenceClient(model=self.model, token=self.token)
        except Exception as e:
            raise HuggingFaceConnectonException(f"HuggingFace couldn't be initialized. See exception: {e}")
        return True 
    
    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        client = InferenceClient(model=self.model, token=self.token)
        batch_size = 32
        all_embeddings = []
        for i in range(0, len(documents), batch_size):
            # set end position of batch
            i_end = min(i + batch_size, len(documents))
            # get batch of texts and ids
            batch = [doc.content for doc in documents[i:i_end]]
            embeddings = client.feature_extraction(text=batch)
            all_embeddings.extend(embeddings.tolist())
        info = {
            "estimated_cost":str("Not implemented"),
            "total_tokens":str("Not implemented"),
            "attempts_used":str("Not implemented")
        }
        return all_embeddings, info
    
    def embed_query(self, query: str) -> List[float]:
        client = InferenceClient(model=self.model, token=self.token)
        return client.feature_extraction(text=query)

