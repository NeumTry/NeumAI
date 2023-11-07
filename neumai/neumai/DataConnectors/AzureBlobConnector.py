from datetime import datetime
from Connectors.Connector import Connector
from typing import List, Generator
from azure.storage.blob import BlobClient, ContainerClient
from Shared.LocalFile import LocalFile
from Shared.CloudFile import CloudFile
from Shared.Selector import Selector
from Loaders.Loader import Loader
from Loaders import (
    AutoLoader, 
    HTMLLoader, 
    MarkdownLoader, 
    NeumCSVLoader, 
    NeumJSONLoader, 
    PDFLoader
)
import tempfile
import os


class AzureBlobConnector(Connector):
    """" Neum File Connector """

    @property
    def connector_name(self) -> str:
        return "AzureBlobConnector"
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["connection_string", "container_name"]

    @property
    def optionalProperties(self) -> List[str]:
        return []
    
    @property
    def availableMetadata(self) -> str:
        return ['name', 'last_modified', 'creation_time', 'last_access_on']

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
        # Connect to Azure Blob Storage
        connection_string = self.connector_information['connection_string']
        container_name = self.connector_information['container_name']
        container = ContainerClient.from_connection_string(
            conn_str=connection_string, container_name=container_name
        )

        #Process files
        file_list = container.list_blobs()
        for file in file_list:
            name = file.name
            metadata = {
                "creation_time": file.creation_time,
                "last_modified": file.last_modified,
                "last_access_on": file.last_accessed_on,
            }
            selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
            yield CloudFile(file_identifier=name, metadata=selected_metadata)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # Connect to Azure Blob Storage
        connection_string = self.connector_information['connection_string']
        container_name = self.connector_information['container_name']
        container = ContainerClient.from_connection_string(
            conn_str=connection_string, container_name=container_name
        )

        #Process files
        file_list = container.list_blobs()
        for file in file_list:
            last_update_date = file.last_modified
            if(last_run < last_update_date):
                name = file.name
                metadata = {
                    "creation_time": file.creation_time,
                    "last_modified": file.last_modified,
                    "last_access_on": file.last_accessed_on,
                }
                selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
                yield CloudFile(file_identifier=name, metadata=selected_metadata)

    
    def connect_and_download(self,  cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        # Connect to Azure Blob Storage
        connection_string = self.connector_information['connection_string']
        container_name = self.connector_information['container_name']
        
        client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=cloudFile.file_identifier)
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{container_name}/{cloudFile.file_identifier}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(f"{file_path}", "wb") as file:
                blob_data = client.download_blob()
                blob_data.readinto(file)
            yield LocalFile(file_path=file_path, metadata=cloudFile.metadata)
        
    def validate(self) -> bool:
        try:
            connection_string = self.connector_information['connection_string']
            container_name = self.connector_information['container_name']
        except:
            raise ValueError("Required properties not set")
        
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            container = ContainerClient.from_connection_string(
                conn_str=connection_string, container_name=container_name
            )
        except Exception as e:
            raise Exception(f"Connection to Azure Blob Storage failed, check credentials. See Exception: {e}")   
        return True     


    
 