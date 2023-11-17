from abc import ABC
from neumai.Pipelines.Pipeline import Pipeline
from neumai.Pipelines.TriggerSyncTypeEnum import TriggerSyncTypeEnum
import requests
import json

class NeumClient(ABC):
    def __init__(self, api_key:str) -> None:
        self.api_key = api_key

    def createPipeline(self, pipeline:Pipeline):
        import requests
        
        url = f"https://api.neum.ai/v2/pipelines"

        # Headers
        headers = {
            "neum-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=pipeline.as_request())
        return response.json()['id']

    def getPipeline(self, pipeline_id:str):
        import requests
        import json

        url = f"https://api.neum.ai/v2/pipelines/{pipeline_id}"

        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key
        }

        response = requests.get(url, headers=headers)
        return(json.loads(response.text))
    
    def triggerPipeline(self, pipeline_id:str, sync_type:TriggerSyncTypeEnum):
        url = f"https://api.neum.ai/v2/pipelines/{pipeline_id}/trigger"

        # Headers
        headers = {
            "neum-api-key":self.api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json={ "sync_type": sync_type.value })
        return json.loads(response.text)

    def search(self, pipeline_id:str, query:str, num_of_results:int = 3, track:bool = False):
        url = f"https://api.neum.ai/v2/pipelines/{pipeline_id}/search"

        payload = {
            "number_of_results": num_of_results,
            "query": query,
            "collect_retrieval":track
        }
        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key,
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        return json.loads(response.text)