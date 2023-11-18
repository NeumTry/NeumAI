from datetime import datetime
from typing import List, Generator, Optional
from neumai.DataConnectors.DataConnector import DataConnector
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from pydantic import Field
from neumai.Shared.Exceptions import NeumFileException
import tempfile

class NeumFileConnector(DataConnector):
    """Neum Simple File Connector."""

    url: str = Field(..., description="URL required for the connector.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

    @property
    def connector_name(self) -> str:
        return "NeumFileConnector"

    @property
    def required_properties(self) -> List[str]:
        return ["url"]

    @property
    def optional_properties(self) -> List[str]:
        return []

    @property
    def available_metadata(self) -> str:
        return ['url']
    
    @property
    def schedule_avaialable(self) -> bool:
        return True

    @property
    def auto_sync_available(self) -> bool:
        return False
    
    @property
    def compatible_loaders(self) -> List[str]:
        return ["AutoLoader", "HTMLLoader", "MarkdownLoader", "NeumCSVLoader", "NeumJSONLoader", "PDFLoader"]
    
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        availableMetadata = {'url':self.url}
        selected_metadata  = {k: availableMetadata[k] for k in self.selector.to_metadata if k in availableMetadata}
        yield CloudFile(file_identifier=self.url, metadata=selected_metadata, id=self.url)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # Delta is not different, we are just getting one file. 
        yield self.connect_and_list_full()

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        # Connect to random file location
        import requests
        response = requests.get(cloudFile.file_identifier)

        # Download file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            yield LocalFile(file_path=temp_file.name, metadata=cloudFile.metadata, id=cloudFile.id)

    def config_validation(self) -> bool:
        import requests
        try:
            response = requests.get(self.url)
        except Exception as e:
            raise NeumFileException(f"Connection to file failed, check url. See Exception: {e}")     
        # Check for metadata
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided") 
        return True 
