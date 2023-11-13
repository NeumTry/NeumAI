from datetime import datetime
from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator
from supabase import create_client, Client
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
import tempfile
import os


class SupabaseStorageConnector(DataConnector):
    """" Supabase File Connector \n
    connector_information requires:\n
    [ bucket, folder, url, key ]"""

    @property
    def connector_name(self) -> str:
        return "SupabaseStorageConnector"
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["bucket","folder", "url", "key"]

    @property
    def optionalProperties(self) -> List[str]:
        return []
    
    @property
    def availableMetadata(self) -> str:
        return ['name', 'updated_at', 'created_at', 'last_accessed_at']

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
        # Connect to supabase
        bucket = self.connector_information["bucket"]
        folder = self.connector_information['folder']
        url = self.connector_information['url']
        key = self.connector_information['key']
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
        bucket = self.connector_information["bucket"]
        folder = self.connector_information['folder']
        url = self.connector_information['url']
        key = self.connector_information['key']
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
        url = self.connector_information['url']
        key = self.connector_information['key']
        folder= self.connector_information['folder']
        bucket = self.connector_information["bucket"]

        supabase: Client = create_client(url, key)
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{folder}/{cloudFile.file_identifier}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(f"{file_path}", "wb") as file:
                supabase_file = supabase.storage.from_(bucket).download(folder + "/" + cloudFile.file_identifier)
                file.write(supabase_file)
            yield LocalFile(file_path=file_path, metadata=cloudFile.metadata, id=cloudFile.id)

    def validate(self) -> bool:
        try:
            folder= self.connector_information['folder']
            url = self.connector_information['url']
            key = self.connector_information['key']
        except:
            raise ValueError("Required properties not set")
        
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            supabase: Client = create_client(url, key)
        except Exception as e:
            raise Exception(f"Connection to Supabase failed, check credentials. See Exception: {e}")
        return True 
