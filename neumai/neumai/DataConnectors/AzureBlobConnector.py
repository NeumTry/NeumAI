from datetime import datetime
from neumai.DataConnectors import DataConnector
from typing import List, Generator
from azure.storage.blob import BlobClient, ContainerClient
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Exceptions import AzureBlobConnectionException
import tempfile
import os
from neumai.Shared.Selector import Selector
from pydantic import BaseModel

class AzureBlobConnector(BaseModel , DataConnector):
    """" Azure Blob connector """

    connection_string: str
    """Connection string to connect to azure blob [required]"""

    container_name: str
    """Container name to connect to [required]"""

    @property
    def connector_name(self) -> str:
        return "AzureBlobConnector"
    
    @property
    def required_properties(self) -> List[str]:
        return ["connection_string", "container_name"]

    @property
    def optional_properties(self) -> List[str]:
        return []
    
    @property
    def available_metadata(self) -> str:
        return ['name', 'last_modified', 'creation_time', 'last_access_on']

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
        container = ContainerClient.from_connection_string(
            conn_str=self.connection_string, container_name=self.container_name
        )

        #Process files
        file_list = container.list_blobs()
        for file in file_list:
            name = file.name
            metadata = {
                "creation_time": file.creation_time.isoformat(),
                "last_modified": file.last_modified.isoformat(),
                "last_access_on": file.last_accessed_on.isoformat() if file.last_accessed_on is not None else None
            }
            selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
            yield CloudFile(file_identifier=name, metadata=selected_metadata, id = name)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        container = ContainerClient.from_connection_string(
            conn_str=self.connection_string, container_name=self.container_name
        )

        #Process files
        file_list = container.list_blobs()
        for file in file_list:
            last_update_date = file.last_modified
            if(last_run < last_update_date):
                name = file.name
                metadata = {
                    "creation_time": file.creation_time.isoformat(),
                    "last_modified": file.last_modified.isoformat(),
                    "last_access_on": file.last_accessed_on.isoformat() if file.last_accessed_on is not None else None
                }
                selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
                yield CloudFile(file_identifier=name, metadata=selected_metadata, id=name)

    def connect_and_download(self,  cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        client = BlobClient.from_connection_string(conn_str=self.connection_string, container_name=self.container_name, blob_name=cloudFile.file_identifier)
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{self.container_name}/{cloudFile.file_identifier}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(f"{file_path}", "wb") as file:
                blob_data = client.download_blob()
                blob_data.readinto(file)
            yield LocalFile(file_path=file_path, metadata=cloudFile.metadata, id=cloudFile.id)
        
    def validate(self) -> bool:
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")

        try:
            ContainerClient.from_connection_string(
                conn_str=self.connection_string, container_name=self.container_name
            )
        except Exception as e:
            raise AzureBlobConnectionException(f"Connection to Azure Blob Storage failed, check credentials. See Exception: {e}")
        return True     


    
 