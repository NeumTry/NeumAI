from typing import (
    List,
)
import openai
import json
from .file_prep import read_file_and_prepare_input

def metadata_attributes_for_retrieval(file_path:str, loader_choice:str):
    text = read_file_and_prepare_input(file_path, loader_choice)
    if text is None:
        return "Failed to prepare input text"
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Based on the given set of columns and example data for each column, generate an output for each column using this format: \n AttributeInfo(\n    name=\"<Column>\",\n    description=\"<Description of column + short example value>\",\n    type=\"string\",\n"},
        {"role": "user", "content": text}
    ]
    
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        temperature=0.9
        
    )
    response_message = response.choices[0].message
    
    # Optionally, you might want to parse this into a Python array
    try:
        embedded_properties = json.loads(response_message)
    except json.JSONDecodeError:
        print("Couldn't decode the response into JSON. Returning the raw string instead.")
        embedded_properties = response_message
    
    return embedded_properties