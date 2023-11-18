from typing import List, Tuple
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument
from pydantic import Field
import replicate

class ReplicateEmbed(EmbedConnector):
    """Replicate Embed Connector."""

    api_key: str = Field(..., description="API key for the Replicate service.")

    replicate_model: str = Field(..., description="Model identifier for Replicate.")

    @property
    def embed_name(self) -> str:
        return 'ReplicateEmbed'

    @property
    def required_properties(self) -> List[str]:
        return ['api_key', 'replicate_model']

    @property
    def optional_properties(self) -> List[str]:
        return []

    def validation(self) -> bool:
        """config_validation connector setup"""
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with Azure OpenAI"""
        api_key = self.api_key
        model = self.replicate_model
        client = replicate.Client(api_token=api_key)
        batch_size = 32
        batched_embeddings = []
        for i in range(0, len(documents), batch_size):
            # set end position of batch
            i_end = min(i + batch_size, len(documents))
            # get batch of texts and ids
            lines_batch = [doc.content for doc in documents[i:i_end]]
            output = client.run(
                model,
                input={"text_batch": lines_batch}
            )
            batched_embeddings  += [record for record in output['data']]
        
        info = {
            "estimated_cost":str("Not implemented"),
            "total_tokens":str("Not implemented"),
            "attempts_used":str("Not implemented")
        }

        return batched_embeddings, info

    def embed_query(self, query: str) -> List[float]:
        api_key = self.api_key
        model = self.replicate_model
        client = replicate.Client(api_token=api_key)
        output = client.run(
            model,
            input={"text": query}
        )

        return output['data']