from datetime import datetime
from Connectors.Connector import Connector
from typing import List, Generator
from abc import abstractmethod
from Shared.LocalFile import LocalFile
from Shared.CloudFile import CloudFile
from Shared.Selector import Selector
from Loaders.Loader import Loader
from Loaders import HTMLLoader
from bs4 import BeautifulSoup
import tempfile
import os
import requests


class NeumWebsiteConnector(Connector):
    """" Neum Website Connector """
    """" connector_information contains: """
    """ [url] """

    def __init__(self, connector_information:dict, selector:Selector) -> None:
        self.connector_information = connector_information
        self.selector = selector
  
    @property
    def connector_name(self) -> str:
        return "NeumWebsiteConnector"
    
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
        return ["HTMLLoader"]
    
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        # Send an HTTP GET request to the website
        url:str = str(self.connector_information['url'])
        clean_url = url.replace(" ", "")
        list_urls = clean_url.split(" , ")
        for u in list_urls:
            available_metadata = {'url':u}
            selected_metadata  = {k: available_metadata[k] for k in self.selector.to_metadata if k in available_metadata}
            yield CloudFile(file_identifier=u, metadata=selected_metadata, id=u)

    def connect_and_list_delta(self) -> Generator[CloudFile, None, None]:
        yield from self.connect_and_list_full()
    
    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
            response = requests.get(cloudFile.file_identifier)
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the <body> element and extract its HTML content
            body = soup.find('body')
            body_html = str(body)  # Convert the body tag to a string to get its HTML content
            # Create a temporary file and write the extracted HTML to it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding="utf-8") as temp:
                temp.write(body_html)
                yield LocalFile(file_path=temp.name, metadata=cloudFile.metadata, id=cloudFile.id)
        
    def validate(self) -> bool:
        try:
            url:str = str(self.connector_information['url'])
        except:
            raise ValueError("Required properties not set")
        
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            response = requests.get(url)
        except Exception as e:
            raise Exception(f"Connection to website failed, check url. See Exception: {e}")      
        return True 