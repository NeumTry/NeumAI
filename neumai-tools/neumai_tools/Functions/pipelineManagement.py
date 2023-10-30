def createPipeline(pipeline_config:dict, api_key:str):
    import requests
    
    url = f"https://api.neum.ai/v1/pipelines"

    # Headers
    headers = {
        "neum-api-key":api_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=pipeline_config)
    return response.json()['id']

def getPipeline(pipeline:str, api_key:str):
    import requests
    import json

    url = f"https://api.neum.ai/v1/pipelines/{pipeline}"

    headers = {
        "accept": "application/json",
        "neum-api-key": api_key
    }

    response = requests.get(url, headers=headers)
    return(json.loads(response.text))