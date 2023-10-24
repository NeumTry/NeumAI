import csv
from typing import Dict, List, Optional
from abc import ABC
from .NeumDocument import NeumDocument
from .Selector import Selector

class CSVLoader(ABC):
    def __init__(
        self,
        file_path: str,
        id_key: str,  # Add id_key parameter here
        source_column: Optional[str] = None,
        csv_args: Optional[Dict] = None,
        encoding: Optional[str] = 'utf-8-sig',
        selector: Selector = Selector(to_embed=[], to_metadata=[])
    ):
        self.file_path = file_path
        self.id_key = id_key 
        self.source_column = source_column
        self.encoding = encoding
        self.csv_args = csv_args or {}
        self.selector = selector

    def extract_metadata(self, row: Dict) -> Dict:
        metadata = {}
        if self.selector.to_metadata:
            for key in self.selector.to_metadata:
                if key in row:
                    metadata[key] = row[key]
        return metadata

    def load(self) -> List[NeumDocument]:
        docs = []
        with open(self.file_path, newline="", encoding=self.encoding) as csvfile:
            csv_reader = csv.DictReader(csvfile, **self.csv_args)  # type: ignore
            for i, row in enumerate(csv_reader):
                document_id = f"{row.get(self.id_key, '')}.{self.id_key}"  # Create a unique id with a prefix
                metadata = self.extract_metadata(row)
                
                if self.selector.to_embed is not None:
                    row = {k: row[k] for k in self.selector.to_embed if k in row}
                elif self.selector.to_embed is None:
                    row = {k: row[k] for k in row}
                
                content = "\n".join(f"{k.strip()}: {v.strip()}" for k, v in row.items())
                
                try:
                    source = (
                        row[self.source_column]
                        if self.source_column is not None
                        else self.file_path
                    )
                except KeyError:
                    raise ValueError(
                        f"Source column '{self.source_column}' not found in CSV file."
                    )
                
                metadata["source"] = source
                metadata["row"] = i

                doc = NeumDocument(content=content, metadata=metadata, id=document_id)  # Pass the id value to Document
                docs.append(doc)

        return docs
