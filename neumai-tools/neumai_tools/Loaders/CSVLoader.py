
import csv
from typing import Dict, List, Optional

from langchain.docstore.document import Document  # Assume this is part of your existing code
from langchain.document_loaders.base import BaseLoader  # Assume this is part of your existing code

class CSVLoader(BaseLoader):
    def __init__(
        self,
        file_path: str,
        source_column: Optional[str] = None,
        csv_args: Optional[Dict] = None,
        encoding: Optional[str] = 'utf-8-sig',
        embed_keys: Optional[List[str]] = None,
        metadata_keys: Optional[List[str]] = None
    ):
        self.file_path = file_path
        self.source_column = source_column
        self.encoding = encoding
        self.csv_args = csv_args or {}
        self.embed_keys = embed_keys
        self.metadata_keys = metadata_keys

    def extract_metadata(self, row: Dict) -> Dict:
        metadata = {}
        if self.metadata_keys:
            for key in self.metadata_keys:
                if key in row:
                    metadata[key] = row[key]
        return metadata

    def load(self) -> List[Document]:
        docs = []
        with open(self.file_path, newline="", encoding=self.encoding) as csvfile:
            csv_reader = csv.DictReader(csvfile, **self.csv_args)  # type: ignore
            for i, row in enumerate(csv_reader):
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

                doc = Document(page_content=content, metadata=metadata)
                docs.append(doc)

        return docs