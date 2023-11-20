from datetime import datetime
from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator, Optional
from supabase import create_client, Client
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import SupabaseConnectionException
from pydantic import Field
import tempfile
import os


class SupabaseStorageConnector(DataConnector):
    """
    Supabase Storage Connector

    Extracts files from Supabase bucket / folder
    
    Attributes:
    -----------

    url : str
        URL to Supabase project
    key : str
        Anon Access key to the project
    bucket : str
        Name of the storage bucket
    folder : str
        Folder name within the bucket. (Pass empty string if no bucket.)
    selector : Optional[Selector]
        Optional selector object to define what data data should be used to generate embeddings or stored as metadata with the vector.
    
    """

    url: str = Field(..., description="URL for Supabase access.")

    key: str = Field(..., description="Access key for Supabase.")
    
    bucket: str = Field(..., description="Bucket name in Supabase.")

    folder: str = Field(..., description="Folder name in the bucket.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

    @property
    def connector_name(self) -> str:
        return "SupabaseStorageConnector"
    
    @property
    def required_properties(self) -> List[str]:
        return ["bucket","folder", "url", "key"]

    @property
    def optional_properties(self) -> List[str]:
        return []
    
    @property
    def available_metadata(self) -> str:
        return ['name', 'updated_at', 'created_at', 'last_accessed_at']
    
    @property
    def schedule_avaialable(self) -> bool:
        return True

    @property
    def auto_sync_available(self) -> bool:
        return False
    
    @property
    def compatible_loaders(self) -> List[str]:
        return ["AutoLoader", "HTMLLoader", "MarkdownLoader", "CSVLoader", "JSONLoader", "PDFLoader"]
    
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        # Connect to supabase
        bucket = self.bucket
        folder = self.folder
        url = self.url
        key = self.key

        supabase: Client = create_client(url, key)
        #Process files
        file_list = supabase.storage.from_(bucket).list(folder)
        for file in file_list:
            # Download each file
            name = file['name']
            selected_metadata  = {k: file[k] for k in self.selector.to_metadata if k in file}
            yield CloudFile(file_identifier=name, metadata=selected_metadata, id=name)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # Connect to supabase
        bucket = self.bucket
        folder = self.folder
        url = self.url
        key = self.key

        supabase: Client = create_client(url, key)
        #Process files
        file_list = supabase.storage.from_(bucket).list(folder)
        for file in file_list:
            # Check if file has changed
            last_update_date = datetime.strptime(file['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if(last_run < last_update_date):
                #If file changed, then download
                name = file['name']
                selected_metadata  = {k: file[k] for k in self.selector.to_metadata if k in file}
                yield CloudFile(file_identifier=name, metadata=selected_metadata, id=name)

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        # Connect to supabase
        bucket = self.bucket
        folder = self.folder
        url = self.url
        key = self.key

        supabase: Client = create_client(url, key)
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{folder}/{cloudFile.file_identifier}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(f"{file_path}", "wb") as file:
                supabase_file = supabase.storage.from_(bucket).download(folder + "/" + cloudFile.file_identifier)
                file.write(supabase_file)
            yield LocalFile(file_path=file_path, metadata=cloudFile.metadata, id=cloudFile.id)

    def config_validation(self) -> bool:    
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            create_client(self.url, self.key)
        except Exception as e:
            raise SupabaseConnectionException(f"Connection to Supabase failed, check credentials. See Exception: {e}")
        return True 
