import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union
from abc import ABC
from .NeumDocument import NeumDocument
from .Selector import Selector

class JSONLoader(ABC):
    def __init__(
        self,
        id_key: str,
        file_data: dict = None,
        file_path: Union[str, Path] = None,
        selector: Selector = Selector(to_embed=[], to_metadata=[]),
    ):
        self.file_data = file_data
        self.file_path = file_path
        self.id_key = id_key
        self.selector = selector

    def create_documents(self, processed_data_list):
        documents = []
        for processed_data in processed_data_list:
            content = ''.join(processed_data['data'])
            metadata = processed_data['metadata']
            document_id = processed_data['id']  # Get the id value from processed_data
            document = NeumDocument(content=content, metadata=metadata, id=document_id)  # Pass the id to NeumDocument
            documents.append(document)
        return documents

    def extract_metadata(self, item: Dict) -> Dict:
        metadata = {}
        if self.selector.to_metadata:
            for key in self.selector.to_metadata:
                if key in item:
                    metadata[key] = item[key]
        return metadata

    def process_item(self, item, prefix="", metadata={}, document_id=None):
        if isinstance(item, dict):
            new_metadata = self.extract_metadata(item)
            new_metadata.update(metadata)  # Merge existing metadata with new metadata
            result = []
            for key, value in item.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                new_document_id = f"{item.get(self.id_key, '')}.{new_prefix}"  # Create a unique id with a prefix
                if self.selector.to_embed is None or new_prefix in self.selector.to_embed or not self.selector.to_embed:
                    result.extend(self.process_item(value, new_prefix, new_metadata, new_document_id))
            return result
        elif isinstance(item, list):
            result = []
            for value in item:
                result.extend(self.process_item(value, prefix, metadata))
            return result
        else:
            return [{'data': [f"{item}"], 'metadata': metadata, 'id': document_id}]


    def process_json(self, data):
        return self.process_item(data)

    def load(self) -> List[NeumDocument]:
        docs = []
        if self.file_path is not None:
            with open(self.file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    processed_json = self.process_json(data)
                    docs = self.create_documents(processed_json)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format in the file.")
            return docs
        
        elif self.file_data is not None:
            try:
                data = json.loads(self.file_data)
                processed_json = self.process_json(data)
                docs = self.create_documents(processed_json)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")
            return docs
    