from enum import Enum
class SyncType(Enum):
    Full = "full"
    Delta = "delta"

def triggerPipeline(pipeline:str, api_key:str, sync_type:SyncType):
    import requests
    import json

    url = f"https://api.neum.ai/v1/pipelines/{pipeline}/trigger"

    # Headers
    headers = {
        "neum-api-key":api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json={ "sync_type": sync_type.value })
    return json.loads(response.text)

def searchPipeline(pipeline:str, api_key:str, query:str, num_of_results:int = 3):
    import requests
    import json

    url = f"https://api.neum.ai/pipelines/{pipeline}/search"

    payload = {
        "number_of_results": num_of_results,
        "query": query
    }
    headers = {
        "accept": "application/json",
        "neum-api-key": api_key,
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return json.loads(response.text)