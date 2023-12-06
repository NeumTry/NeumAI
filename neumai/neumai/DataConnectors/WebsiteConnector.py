from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator, Optional
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import WebsiteConnectionException
from bs4 import BeautifulSoup
from pydantic import Field
import tempfile
import requests

class WebsiteConnector(DataConnector):
    """
    Website Connector

    Extracts data from a given website.
    
    Attributes:
    -----------

    url : str
        Website URL
    selector : Optional[Selector]
        Optional selector object to define what data data should be used to generate embeddings or stored as metadata with the vector.
    
    """


    url: str = Field(..., description="URL of the website to connect to.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

    @property
    def connector_name(self) -> str:
        return "WebsiteConnector"

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
        return ["HTMLLoader"]
    
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        # Send an HTTP GET request to the website
        url:str = str(self.url)
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
            # Some sites don't have a body, so instead just get all the text off it.
            if body == None:
                body = soup.get_text()
            body_html = str(body)  # Convert the body tag to a string to get its HTML content
            # Create a temporary file and write the extracted HTML to it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding="utf-8") as temp:
                temp.write(body_html)
                yield LocalFile(file_path=temp.name, metadata=cloudFile.metadata, id=cloudFile.id)
        
    def config_validation(self) -> bool:
        # Check for metadata values
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        # Check to see that site exists
        try:
            requests.get(self.url)
        except Exception as e:
            raise WebsiteConnectionException(f"Connection to website failed, check url. See Exception: {e}")      
        return True 