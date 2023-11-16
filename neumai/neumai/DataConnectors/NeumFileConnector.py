from datetime import datetime
from typing import List, Generator
import tempfile
from neumai.DataConnectors.DataConnector import DataConnector
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile

class NeumFileConnector(DataConnector):
    """ Neum Simple File Connector \n
    connector_information required:[ url ] \n
    available metadata: [ url ]"""

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
        availableMetadata = {'url':self.connector_information['url']}
        selected_metadata  = {k: availableMetadata[k] for k in self.selector.to_metadata if k in availableMetadata}
        yield CloudFile(file_identifier=self.connector_information['url'], metadata=selected_metadata, id=self.connector_information['url'])

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

    def validate(self) -> bool:
        # Check for required properties
        try:
            self.connector_information['url']
        except:
            raise ValueError(f"Required properties not set. Required properties: {self.requiredProperties}")
        
        # Check for metadata
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided") 
        return True 
