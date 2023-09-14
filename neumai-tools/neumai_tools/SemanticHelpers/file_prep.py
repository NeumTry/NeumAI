import pandas as pd
import json

def read_file_and_prepare_input(file_path, loader_choice):
    text_input = ""
    example_rows = None
    columns = None
    
    if loader_choice == "CSVLoader":
        try:
            df = pd.read_csv(file_path)
            example_rows = df.head(2).to_dict(orient='records')
            columns = df.columns.tolist()
        except pd.errors.ParserError:
            print("Error: Invalid CSV format in the file.")
            return None

    elif loader_choice == "JSONLoader":
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                if isinstance(data, list):
                    example_rows = data[:2]
                    columns = list(data[0].keys()) if data else []
                elif isinstance(data, dict):
                    example_rows = list(data.values())[:2]
                    columns = list(data.keys())
                else:
                    print("Error: JSON file should contain a list or dictionary.")
                    return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in the file.")
            return None

    if columns:
        text_input += "Columns (Properties): " + ', '.join(columns) + "\n"
    if example_rows:
        text_input += "Example Rows:\n"
        for i, row in enumerate(example_rows):
            row_text = ', '.join([f"{k}: {v}" for k, v in row.items()])
            text_input += f"Row {i + 1}: {row_text}\n"
            
    return text_input