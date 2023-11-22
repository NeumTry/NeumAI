from datetime import datetime
from typing import List, Generator, Optional
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import SharepointConnectionException
from neumai.DataConnectors.DataConnector import DataConnector
from pydantic import Field
import tempfile
import requests

class SharepointConnector(DataConnector):
    """
    Sharepoint Connector

    Extracts all files from an Sharepoint site. 
    
    Attributes:
    -----------

    tenant_id : str
        Sharepoint Tenant ID
    site_id : str
        Site ID for Sharepoint
    client_id : str
        App Registration Client ID
    client_secret : str
        App Registration Client secret
    selector : Optional[Selector]
        Optional selector object to define what data data should be used to generate embeddings or stored as metadata with the vector.
    
    """
    
    tenant_id: str = Field(..., description="Tenant ID for Sharepoint.")

    site_id: str = Field(..., description="Site ID for Sharepoint.")

    client_id: str = Field(..., description="Client ID for Sharepoint.")

    client_secret: str = Field(..., description="Client Secret for Sharepoint.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

    @property
    def connector_name(self) -> str:
        return "SharepointConnector"
    
    @property
    def required_properties(self) -> List[str]:
        return ["tenant_id", "client_id", "client_secret", "site_id"]

    @property
    def optional_properties(self) -> List[str]:
        return []

    @property
    def available_metadata(self) -> str:
        return ["createdDateTime", "lastModifiedDateTime", "name", "createdBy.user.email", "createdBy.user.id", "createdBy.user.displayName", "lastModifiedBy.user.email", "lastModifiedBy.user.id", "lastModifiedBy.user.displayName"]
    
    @property
    def schedule_avaialable(self) -> bool:
        return True

    @property
    def auto_sync_available(self) -> bool:
        return False
    
    @property
    def compatible_loaders(self) -> List[str]:
        return ["AutoLoader", "HTMLLoader", "MarkdownLoader", "CSVLoader", "JSONLoader", "PDFLoader"]
    
    def process_folder(self, site_id:str, drive_id:str, folder_id:str, headers:dict) -> Generator[CloudFile, None, None]:
        import requests
        folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{folder_id}/children"
        folder_response = requests.get(folder_url, headers=headers)
        folder_info = folder_response.json()
        folder_items =  folder_info.get('value', [])
        for item in folder_items:
            if 'file' in item.keys():
                # It's a file, download it
                file_url = item['@microsoft.graph.downloadUrl']
                file_name = item['name']
                file_type = item['file']['mimeType']
                available_metadata = {
                    "createdDateTime":item['createdDateTime'],
                    "lastModifiedDateTime":item['lastModifiedDateTime'],
                    "name":item['name'],
                    "createdBy.user.email":item['createdBy']['user']['email'],
                    "createdBy.user.id":item['createdBy']['user']['id'],
                    "createdBy.user.displayName":item['createdBy']['user']['displayName'],
                    "lastModifiedBy.user.email":item['createdBy']['user']['email'],
                    "lastModifiedBy.user.id":item['createdBy']['user']['id'],
                    "lastModifiedBy.user.displayName":item['createdBy']['user']['displayName'],
                }
                selected_metadata  = {k: available_metadata[k] for k in self.selector.to_metadata if k in available_metadata}
                yield CloudFile(file_identifier=file_url, id=file_name, type=file_type, metadata=selected_metadata)
            
            elif 'folder' in item.keys():
                # It's a folder, process it recursively
                yield from self.process_folder(site_id=site_id, drive_id=drive_id, folder_id=item['id'], headers=headers)
    
    def process_folder_delta(self, site_id:str, drive_id:str, folder_id:str, headers:dict, metadata_keys:List[str], last_run:datetime) -> Generator[CloudFile, None, None]:
        import requests
        folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{folder_id}/children"
        folder_response = requests.get(folder_url, headers=headers)
        folder_info = folder_response.json()
        folder_items =  folder_info.get('value', [])
        for item in folder_items:
            if 'file' in item.keys():
                # It's a file, download it
                file_url = item['@microsoft.graph.downloadUrl']
                file_name = item['name']
                file_type = item['file']['mimeType']
                available_metadata = {
                    "createdDateTime":item['createdDateTime'],
                    "lastModifiedDateTime":item['lastModifiedDateTime'],
                    "name":item['name'],
                    "createdBy.user.email":item['createdBy']['user']['email'],
                    "createdBy.user.id":item['createdBy']['user']['id'],
                    "createdBy.user.displayName":item['createdBy']['user']['displayName'],
                    "lastModifiedBy.user.email":item['createdBy']['user']['email'],
                    "lastModifiedBy.user.id":item['createdBy']['user']['id'],
                    "lastModifiedBy.user.displayName":item['createdBy']['user']['displayName'],
                }
                if last_run < item['lastModifiedDateTime']:
                    selected_metadata  = {k: available_metadata[k] for k in metadata_keys if k in available_metadata}
                    yield CloudFile(file_identifier=file_url, id=file_name, type=file_type, metadata=selected_metadata)
            
            elif 'folder' in item.keys():
                # It's a folder, process it recursively
                yield from self.process_folder(site_id=site_id, drive_id=drive_id, folder_id=item['id'], headers=headers)

    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        """Connect to source and download file into local storage"""
        import requests

        #Required
        tenant_id = self.tenant_id
        client_id = self.client_id
        client_secret = self.client_secret
        site_id = self.site_id

        #Auth
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        token_r = requests.post(token_url, headers={"Content-Type":"application/x-www-form-urlencoded"}, data=token_data)
        token = token_r.json().get('access_token')

        # Get all document libraries in the site
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        doc_libraries_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        doc_libraries_response = requests.get(doc_libraries_url, headers=headers)
        doc_libraries_info = doc_libraries_response.json()

        # Iterate through all document libraries
        for doc_library in doc_libraries_info.get('value', []):
            doc_library_id = doc_library['id']
            yield from self.process_folder(site_id=site_id, drive_id=doc_library_id, folder_id='root', headers=headers)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[LocalFile, None, None]:
        """Check for changes in the source"""
        """Code to be pushed to a worker and run on a schedule"""
        import requests

        #Required
        tenant_id = self.tenant_id
        client_id = self.client_id
        client_secret = self.client_secret
        site_id = self.site_id

        #Auth
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        token_r = requests.post(token_url, headers={"Content-Type":"application/x-www-form-urlencoded"}, data=token_data)
        token = token_r.json().get('access_token')

        # Get all document libraries in the site
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        doc_libraries_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        doc_libraries_response = requests.get(doc_libraries_url, headers=headers)
        doc_libraries_info = doc_libraries_response.json()

        # Iterate through all document libraries
        for doc_library in doc_libraries_info.get('value', []):
            doc_library_id = doc_library['id']
            yield from self.process_folder_delta(site_id=site_id, drive_id=doc_library_id, folder_id='root', headers=headers, last_run=last_run)
        
    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        """Connect to source and download file into local storage"""
        #Download file
        id = cloudFile.id
        file_identifier = cloudFile.file_identifier
        type = cloudFile.type
        metadata = cloudFile.metadata
        import requests
        file_r = requests.get(file_identifier)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{id}") as temp_file:
            temp_file.write(file_r.content)
        yield LocalFile(file_path=temp_file.name, metadata=metadata, id=id, type=type)
    
    def config_validation(self) -> bool:
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://graph.microsoft.com/.default'
            }
            token_r = requests.post(token_url, headers={"Content-Type":"application/x-www-form-urlencoded"}, data=token_data)
            token = token_r.json().get('access_token')

            # Get all document libraries in the site
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            doc_libraries_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives"
            requests.get(doc_libraries_url, headers=headers)
        except Exception as e:
            raise SharepointConnectionException(f"Connection to Sharepoint failed, check credentials. See Exception: {e}")       
        return True 