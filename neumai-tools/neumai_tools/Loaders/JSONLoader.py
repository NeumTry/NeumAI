import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from langchain.docstore.document import Document  # Assume this is part of your existing code
from langchain.document_loaders.base import BaseLoader  # Assume this is part of your existing code

class JSONLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
        embed_keys: Optional[List[str]] = None,
        metadata_keys: Optional[List[str]] = None
    ):
        self.file_path = file_path
        self.embed_keys = embed_keys
        self.metadata_keys = metadata_keys

    def create_documents(self, processed_data_list):
        documents = []
        for processed_data in processed_data_list:
            content = ''.join(processed_data['data'])
            metadata = processed_data['metadata']
            document = Document(page_content=content, metadata=metadata)
            documents.append(document)
        return documents

    def extract_metadata(self, item: Dict) -> Dict:
        metadata = {}
        if self.metadata_keys:
            for key in self.metadata_keys:
                if key in item:
                    metadata[key] = item[key]
        return metadata

    def process_item(self, item, prefix="", metadata={}):
        if isinstance(item, dict):
            new_metadata = self.extract_metadata(item)
            new_metadata.update(metadata)  # Merge existing metadata with new metadata
            result = []
            for key, value in item.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if self.embed_keys is None or new_prefix in self.embed_keys or not self.embed_keys:
                    result.extend(self.process_item(value, new_prefix, new_metadata))
            return result
        elif isinstance(item, list):
            result = []
            for value in item:
                result.extend(self.process_item(value, prefix, metadata))
            return result
        else:
            return [{'data': [f"{prefix}: {item}"], 'metadata': metadata}]

    def process_json(self, data):
        return self.process_item(data)

    def load(self) -> List[Document]:
        docs = []
        with open(self.file_path, 'r') as json_file:
            try:
                data = json.load(json_file)
                processed_json = self.process_json(data)
                docs = self.create_documents(processed_json)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the file.")
        return docs



    