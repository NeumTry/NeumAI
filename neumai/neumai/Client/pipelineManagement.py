from neumai.Pipelines.Pipeline import Pipeline
from neumai.Client.NeumClient import NeumClient

def createPipeline(pipeline:Pipeline, neumClient:NeumClient):
    import requests
    
    url = f"https://api.neum.ai/v1/pipelines"

    # Headers
    headers = {
        "neum-api-key": neumClient.api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=pipeline.as_request())
    return response.json()['id']

def getPipeline(pipeline:Pipeline, neumClient:NeumClient):
    import requests
    import json

    url = f"https://api.neum.ai/v1/pipelines/{pipeline}"

    headers = {
        "accept": "application/json",
        "neum-api-key": api_key
    }

    response = requests.get(url, headers=headers)
    return(json.loads(response.text))