from typing import List, Generator, Optional, Dict
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Loaders.Loader import Loader
from pydantic import Field
from neumai.Shared.Selector import Selector
import csv

class CSVLoader(Loader):
    """
    CSV Loader

    A utility class for loading and processing CSV files. This loader is designed to handle various CSV formats and configurations, making it flexible for different data loading requirements.

    Attributes:
    -----------
    id_key : Optional[str]
        An optional ID key that can be used to identify unique records within the CSV file. If provided, it specifies the column name that contains unique identifiers.

    source_column : Optional[str]
        An optional source column name from which to load data. If specified, only this column will be used for further processing.

    encoding : Optional[str]
        An optional encoding type for reading the CSV file. This should be a valid encoding type understood by Python's CSV parser.

    csv_args : Optional[Dict]
        Optional additional arguments that can be passed to the CSV reader. This can include settings like delimiter, quotechar, etc.

    selector : Optional[Selector]
        An optional Selector object to define criteria for selecting, embedding, or modifying metadata in the data. Default is a Selector with empty 'to_embed' and 'to_metadata' lists.
    """

    id_key: Optional[str] = Field("id", description="Optional ID key.")

    source_column: Optional[str] = Field(None, description="Optional source column.")

    encoding: Optional[str] = Field("utf-8-sig", description="Optional encoding type.")

    csv_args: Optional[Dict] = Field(None, description="Optional additional CSV arguments.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for loader metadata")

    @property
    def loader_name(self) -> str:
        return "CSVLoader"

    @property
    def required_properties(self) -> List[str]:
        return []

    @property
    def optional_properties(self) -> List[str]:
        return ["id_key", "source_column", "encoding", "csv_args"]
    
    @property
    def available_metadata(self) -> List[str]:
        return ["custom"]

    @property
    def available_content(self) -> List[str]:
        return ["custom"]
    
    def config_validation(self) -> bool:
        return True   

    def load(self, file: LocalFile) -> Generator[NeumDocument, None, None]:
        source_column = self.source_column
        encoding = self.encoding# modify to use encoding
        csv_args = self.csv_args # default to id
        id_key = self.id_key # default to id
        selector = self.selector

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
