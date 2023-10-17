import csv
from typing import Dict, List, Optional
from abc import ABC
from .NeumDocument import NeumDocument

class CSVLoader(ABC):
    def __init__(
        self,
        file_path: str,
        id_key: str,  # Add id_key parameter here
        source_column: Optional[str] = None,
        csv_args: Optional[Dict] = None,
        encoding: Optional[str] = 'utf-8-sig',
        embed_keys: Optional[List[str]] = None,
        metadata_keys: Optional[List[str]] = None
    ):
        self.file_path = file_path
        self.id_key = id_key  # Store id_key
        self.source_column = source_column
        self.encoding = encoding
        self.csv_args = csv_args or {}
        self.embed_keys = embed_keys
        self.metadata_keys = metadata_keys

    # ... rest of your code ...

    def load(self) -> List[NeumDocument]:
        docs = []
        with open(self.file_path, newline="", encoding=self.encoding) as csvfile:
            csv_reader = csv.DictReader(csvfile, **self.csv_args)  # type: ignore
            for i, row in enumerate(csv_reader):
                document_id = row.get(self.id_key, "")  # Extract id value using id_key
                metadata = self.extract_metadata(row)
                
                if self.embed_keys is not None:
                    row = {k: row[k] for k in self.embed_keys if k in row}
                elif self.embed_keys is None:
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

                doc = NeumDocument(page_content=content, metadata=metadata, id=document_id)  # Pass the id value to Document
                docs.append(doc)

        return docs
