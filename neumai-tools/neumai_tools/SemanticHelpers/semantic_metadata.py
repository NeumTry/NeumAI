import openai
import json
import pandas as pd
from .file_prep import read_file_and_prepare_input

def fields_for_metadata(file_path:str, loader_choice:str):
    if loader_choice == "JSONLoader":
        with open(file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
                if isinstance(data, dict):
                    return list(data.keys())
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")
    elif loader_choice == "CSVLoader":
        # Read the CSV
        df = pd.read_csv(file_path)
        # Columns are the properties
        columns = df.columns.tolist()
        return columns

def fields_to_embed(file_path, loader_choice):
    text = read_file_and_prepare_input(file_path, loader_choice)
    
    if text is None:
        return "Failed to prepare input text"
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Based on the given properties and examples from a CSV file, please identify and return an array of the properties that hold semantic meaning and should turned into vector embeddings. These are properties that carry nuanced, contextual information that would be useful for semantic search. Do not include any columns that should be used as filters instead.\n [<column>,<column>,<column>...]"},
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