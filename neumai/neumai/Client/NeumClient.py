from abc import ABC
from neumai.Pipelines.Pipeline import Pipeline
from neumai.Pipelines.TriggerSyncTypeEnum import TriggerSyncTypeEnum
import requests
import json

class NeumClient(ABC):
    def __init__(self, api_key:str, endpoint:str = 'https://api.neum.ai/v2') -> None:
        self.api_key = api_key
        self.endpoint = endpoint

    def create_pipeline(self, pipeline:Pipeline):
        import requests

        url = f"{self.endpoint}/pipelines"

        # Headers
        headers = {
            "neum-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        try: 
            response = requests.post(url, headers=headers, json=pipeline.as_json())
            return response.json()['id']
        except Exception as e:
            print(f"Pipeline creation failed. Exception - {e}")
            
    def get_pipeline(self, pipeline_id:str):
        import requests
        import json

        url = f"{self.endpoint}/pipelines/{pipeline_id}"

        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key
        }
        try:
            response = requests.get(url, headers=headers)
            return(json.loads(response.text))
        except Exception as e:
            print(f"Pipeline fetching failed. Exception - {e}")
    
    def trigger_pipeline(self, pipeline_id:str, sync_type:TriggerSyncTypeEnum):
        url = f"{self.endpoint}/pipelines/{pipeline_id}/trigger"

        # Headers
        headers = {
            "neum-api-key":self.api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, json={ "sync_type": sync_type.value })
            return json.loads(response.text)
        except Exception as e:
            print(f"Pipeline trigger failed. Exception - {e}")

    def search_pipeline(self, pipeline_id:str, query:str, num_of_results:int = 3, track:bool = False):
        url = f"{self.endpoint}/pipelines/{pipeline_id}/search"

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
        try:
            response = requests.post(url, json=payload, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            print(f"Pipeline trigger failed. Exception - {e}")