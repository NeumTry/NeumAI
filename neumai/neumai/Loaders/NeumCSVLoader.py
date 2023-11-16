from typing import List, Generator
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Loaders.Loader import Loader
import csv

class NeumCSVLoader(Loader):
    """" Neum CSV Loader """

    @property
    def loader_name(self) -> str:
        return "NeumCSVLoader"
    
    @property
    def required_properties(self) -> List[str]:
        return []

    @property
    def optional_properties(self) -> List[str]:
        return ["id_key" , "source_column" , "encoding", "csv_args"]
    
    @property
    def available_metadata(self) -> List[str]:
        return ["custom"]

    @property
    def availableContent(self) -> List[str]:
        return ["custom"]
    
    def validate(self) -> bool:
        return True   

    def load(self, file: LocalFile) -> Generator[NeumDocument, None, None]:
        source_column = self.loader_information.get('source_coulmn', None)
        encoding = self.loader_information.get('encoding', "utf-8-sig") # modify to use encoding
        csv_args = self.loader_information.get('csv_args', None) # default to id
        id_key = self.loader_information.get('id_key', 'id') # default to id
        selector = self.selector
        embed_keys = selector.to_embed
        metadata_keys = selector.to_metadata

        with open(file.file_path, newline="", encoding=encoding) as csvfile:
            csv_reader = csv.DictReader(csvfile, **csv_args)  # Use csv_args if provided
            for i, row in enumerate(csv_reader):
                document_id = f"{row.get(id_key, '')}.{id_key}"
                metadata = self.extract_metadata(row)
                content = self.extract_content(row)
                source = row[source_column] if source_column else file.file_path
                metadata["source"] = source
                metadata["row"] = i
                doc = NeumDocument(content=content, metadata=metadata, id=document_id)
                yield doc

    def extract_metadata(self, row: dict) -> dict:
        # Adapted from CSVLoader.extract_metadata()
        return {key: row[key] for key in self.selector.to_metadata if key in row}
    
    def extract_content(self, row: dict) -> str:
        # Content extraction logic goes here
        if self.selector.to_embed:
            row = {k: row[k] for k in self.selector.to_embed if k in row}
        return "\n".join(f"{k.strip()}: {v.strip()}" for k, v in row.items())
