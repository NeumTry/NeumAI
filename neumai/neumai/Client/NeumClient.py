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

    def search_pipeline(self, pipeline_id:str, query:str, num_of_results:int = 3, track:bool = False, filter:dict = {}, requested_by:str = None):
        url = f"{self.endpoint}/pipelines/{pipeline_id}/search"

        payload = {
            "number_of_results": num_of_results,
            "query": query,
            "collect_retrieval":track,
            "requested_by":requested_by,
            "filter":filter
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
    
    def search_file(self, pipeline_id:str, file_id:str, query:str, num_of_results:int = 3, track:bool = False, requested_by:str = None):
        url = f"{self.endpoint}/pipelines/{pipeline_id}/files/search?file_id={file_id}"

        payload = {
            "number_of_results": num_of_results,
            "query": query,
            "collect_retrieval":track,
            "requested_by":requested_by,
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

    def get_files(self, pipeline_id:str):
        url = f"{self.endpoint}/pipelines/{pipeline_id}/files"

        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            print(f"Pipeline trigger failed. Exception - {e}")
    
    def get_file(self, pipeline_id:str, file_id:str):
        url = f"{self.endpoint}/pipelines/{pipeline_id}/files?file_id={file_id}"

        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            print(f"Pipeline trigger failed. Exception - {e}")
    
    def get_retrievals_by_file_id(self, pipeline_id:str, file_id:str):
        url = f"{self.endpoint}/retrievals/{pipeline_id}/files?file_id={file_id}"

        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            print(f"Pipeline trigger failed. Exception - {e}")

    def get_retrievals_by_pipeline_id(self, pipeline_id:str):
        url = f"{self.endpoint}/retrievals/{pipeline_id}"

        headers = {
            "accept": "application/json",
            "neum-api-key": self.api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            return json.loads(response.text)
        except Exception as e:
            print(f"Pipeline trigger failed. Exception - {e}")
    
    def provide_retrieval_feedback(self, pipeline_id:str, retrieval_id:str, status:str):
        url = f"{self.endpoint}/retrievals/{pipeline_id}/{retrieval_id}"

        payload = {
            "status":status
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