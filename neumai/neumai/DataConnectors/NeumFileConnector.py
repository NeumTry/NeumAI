from datetime import datetime
from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
import tempfile


class NeumFileConnector(DataConnector):
    """ Neum Simple File Connector \n
    connector_information required:[ url ] \n
    available metadata: [ url ]\n
    available content: [ file ]"""

    @property
    def connector_name(self) -> str:
        return "NeumFileConnector"
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["url"]

    @property
    def optionalProperties(self) -> List[str]:
        return []

    @property
    def availableMetadata(self) -> str:
        return ['url']

    @property
    def availableContent(self) -> str:
        return ['file']
    
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
        available_metadata = {'url':self.connector_information['url']}
        selected_metadata  = {k: available_metadata[k] for k in self.selector.to_metadata if k in available_metadata}
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
            url = self.connector_information['url']
        except:
            raise ValueError("Required properties not set")
        
        # Check for metadata
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided") 
        return True 
