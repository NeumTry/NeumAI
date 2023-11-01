from datetime import datetime
from Connectors.Connector import Connector
from typing import List, Generator
from abc import abstractmethod, ABC, abstractproperty
from supabase import create_client, Client
from Shared.LocalFile import LocalFile
from Shared.CloudFile import CloudFile
from Shared.Selector import Selector
from Loaders import Loader, AutoLoader, HTMLLoader, MarkdownLoader, NeumCSVLoader, NeumJSONLoader, PDFLoader
import tempfile
import os


class NeumSimpleFileConnector(Connector):
    """ Neum Simple File Connector \n Requires a `url` as part of the `connector_information`."""

    def __init__(self, connector_information:dict, selector:Selector) -> None:
        self.connector_information = connector_information
        self.selector = selector

    @property
    def connector_name(self) -> str:
        return "NeumSimpleFileConnector"
    
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
        return []
    
    @property
    def schedule_avaialable(self) -> bool:
        return True

    @property
    def auto_sync_available(self) -> bool:
        return False
    
    @property
    def compatible_loaders(self) -> List[Loader]:
        return ["AutoLoader", "HTMLLoader", "MarkdownLoader", "NeumCSVLoader", "NeumJSONLoader", "PDFLoader"]
    
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        # Connect to supabase
        available_metadata = {'url':self.connector_information['url']}
        selected_metadata  = {k: available_metadata[k] for k in self.selector.to_metadata if k in available_metadata}
        yield CloudFile(file_identifier=self.connector_information['url'], metadata=selected_metadata, id=self.connector_information['url'])

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # Connect to supabase
        yield self.connect_and_list_full()

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        # Connect to random file location
        import requests
        response = requests.get(cloudFile.file_identifier)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.content)
            yield LocalFile(file_path=temp_file.name, metadata=cloudFile.metadata, id=cloudFile.id)

    def validate(self) -> bool:
        try:
            url = self.connector_information['url']
        except:
            raise ValueError("Required properties not set")
        
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided") 
        return True 
