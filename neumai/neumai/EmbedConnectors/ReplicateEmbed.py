from typing import List, Tuple
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument
import replicate

class ReplicateEmbed(EmbedConnector):
    @property
    def embed_name(self) -> str:
        return 'ReplicateEmbed'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ['api_key', 'replicate_model']

    @property
    def optionalProperties(self) -> List[str]:
        return []

    def validation(self) -> bool:
        """Validate connector setup"""
        try:
            api_key = self.embed_information["api_key"]
            model = self.embed_information["replicate_model"]
        except:
            raise ValueError(f"Required properties not set. Required properties: {self.requiredProperties}")
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with Azure OpenAI"""
        api_key = self.embed_information["api_key"]
        model = self.embed_information["replicate_model"]
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
        api_key = self.embed_information["api_key"]
        model = self.embed_information["replicate_model"]
        client = replicate.Client(api_token=api_key)
        output = client.run(
            model,
            input={"text": query}
        )

        return output['data']