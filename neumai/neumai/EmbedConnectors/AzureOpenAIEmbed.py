from typing import List, Tuple
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument

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
            raise ValueError("Required properties are not set.")
        return True 

    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with Azure OpenAI"""
        import openai
        cost_per_token = 0.000000001 # ADA-002 as of Sept 2023
        batch_size = 32 # how does changing this affect ?
        # Should we generate batched embeddings, store, then batch embeddings, store. or should we gneralte all embeddings then store? what's perf diff?
        batched_embeddings = []
        deployment_name = self.embed_information["deployment_name"]
        openai.api_key = self.embed_information["api_key"]
        openai.api_base = self.embed_information["endpoint"]
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"
        for i in range(0, len(documents), batch_size):
            # set end position of batch
            i_end = min(i + batch_size, len(documents))
            # get batch of texts and ids
            lines_batch = [doc.content for doc in documents[i:i_end]]
            result = openai.Embedding.create(input=lines_batch, engine=deployment_name)
            batched_embeddings  += [record['embedding'] for record in result['data']]
        
        info = {
            "estimated_cost":str("Not implemented"),
            "total_tokens":str("Not implemented"),
            "attempts_used":str("Not implemented")
        }

        return batched_embeddings, info
    
    def embed_query(self, query: str) -> List[float]:
        import openai
        openai.api_type = "azure"
        openai.api_key = self.embed_information["api_key"]
        openai.api_base = self.embed_information["endpoint"]
        openai.api_version = "2023-05-15"
        deployment_name = self.embed_information["deployment_name"]
        result = openai.Embedding.create(input=query, engine=deployment_name)
        return result['data'][0]['embedding']
