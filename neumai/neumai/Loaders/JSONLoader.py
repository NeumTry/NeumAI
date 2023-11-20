from typing import List, Generator, Optional
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Loaders.Loader import Loader
from pydantic import Field
from neumai.Shared.Selector import Selector
import json

class JSONLoader(Loader):
    """
    JSON Loader

    A class for loading and processing JSON data. This loader is tailored for handling JSON files, offering flexibility in how JSON data is ingested and used in various applications.

    Attributes:
    -----------
    id_key : Optional[str]
        An optional ID key for identifying unique records in the JSON data. If specified, it is used to denote a unique identifier within the JSON structure.

    selector : Optional[Selector]
        An optional Selector object used to define criteria for selecting, embedding, or modifying metadata in the JSON data. Default is a Selector with empty 'to_embed' and 'to_metadata' lists.
    """

    id_key: Optional[str] = Field('id', description="Optional ID key.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for loader metadata")

    @property
    def loader_name(self) -> str:
        return "JSONLoader"

    @property
    def required_properties(self) -> List[str]:
        return []

    @property
    def optional_properties(self) -> List[str]:
        return ["id_key"]

    @property
    def loader_name(self) -> str:
        return "JSONLoader"
    
    @property
    def available_metadata(self) -> List[str]:
        return ["custom"]

    @property
    def available_content(self) -> List[str]:
        return ["custom"]
    
    def config_validation(self) -> bool:
        return True   

    def load(self, file: LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""
        id_key = self.id_key

        json_data = None
        if file.file_path:
            with open(file.file_path, 'r') as json_file:
                json_data = json.load(json_file)
        elif file.in_mem_data:
            json_data = json.loads(file.in_mem_data)

        if json_data is not None:
            processed_json = self.process_item(item=json_data, id_key=id_key)

            for item in processed_json:
                content = ''.join(item['data'])
                metadata: dict = item['metadata']
                document_id = item['id']
                metadata.update(file.metadata)
                yield NeumDocument(content=content, metadata=metadata, id=document_id)

    def process_item(self, item, prefix="", metadata=None, document_id=None, id_key="id"):
        if metadata is None:
            metadata = {}

        if isinstance(item, dict):
            new_metadata = self.extract_metadata(item, self.selector.to_metadata)
            new_metadata.update(metadata)
            result = []
            for key, value in item.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                new_document_id = f"{item.get(id_key, '')}.{new_prefix}" if id_key in item else new_prefix
                if self.selector.to_embed is None or new_prefix in self.selector.to_embed or not self.selector.to_embed:
                    result.extend(self.process_item(item=value, prefix=new_prefix, metadata=new_metadata, document_id=new_document_id, id_key=id_key))
            return result
        elif isinstance(item, list):
            result = []
            for value in item:
                result.extend(self.process_item(item=value, prefix=prefix, metadata=metadata, document_id=document_id, id_key=id_key))
            return result
        else:
            return [{'data': [f"{item}"], 'metadata': metadata, 'id': document_id or prefix}]

    def extract_metadata(self, item: dict, metadata_keys: List[str]) -> dict:
        return {key: item[key] for key in metadata_keys if key in item}