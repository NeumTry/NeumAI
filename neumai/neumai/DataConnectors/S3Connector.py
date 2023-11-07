from datetime import datetime
from typing import List, Generator
import boto3
from Shared.LocalFile import LocalFile
from Shared.CloudFile import CloudFile
from DataConnector import DataConnector
import tempfile
import os


class S3Connector(DataConnector):
    """" Neum File Connector \n
    connector_information contains: \n
    [ aws_key_id, aws_access_key, bucket_name ]"""

    @property
    def connector_name(self) -> str:
        return "S3Connector"
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["aws_key_id", "aws_access_key", "bucket_name"]

    @property
    def optionalProperties(self) -> List[str]:
        return ["prefix"]
    
    @property
    def availableMetadata(self) -> str:
        return ["last_modified", "metadata" ] # TODO need to flatten

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
        #Connect to S3
        aws_key_id= self.connector_information['aws_key_id']
        aws_access_key= self.connector_information['aws_access_key']
        bucket_name= self.connector_information['bucket_name']
        prefix = self.connector_information.get("prefix", "")
        session = boto3.Session(
            aws_access_key_id=aws_key_id,
            aws_secret_access_key=aws_access_key,
        )
        s3_resource = session.resource('s3')
        s3_client = session.client("s3")
        bucket = s3_resource.Bucket(bucket_name)

        # List out the files to be passed on
        for obj in bucket.objects.filter(Prefix=prefix):
            # Hard coded metadata available on the object
            metadata = {
                "last_modified" : obj.last_modified
            }
            selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
            # If metadata passed, then I will add all the user generated values that are associated to the file
            if "metadata" in self.selector.to_metadata:
                # Make an additional call to get the full context
                additional_metdata:dict = s3_client.head_object(Bucket=bucket_name, Key=obj.key)
                selected_metadata.update(additional_metdata['Metadata'])
            yield CloudFile(file_identifier=obj.key, metadata=selected_metadata)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # Connect to S3
        aws_key_id= self.connector_information['aws_key_id']
        aws_access_key= self.connector_information['aws_access_key']
        bucket_name= self.connector_information['bucket_name']
        prefix = self.connector_information.get("prefix", "")   
        session = boto3.Session(
            aws_access_key_id=aws_key_id,
            aws_secret_access_key=aws_access_key,
        )
        s3_resource = session.resource('s3')
        s3_client = session.client("s3")
        bucket = s3_resource.Bucket(bucket_name)

        # List out the files that have changed
        for obj in bucket.objects.filter(Prefix=prefix):    
            # Check if file has changed
            if(last_run < obj.last_modified):
                # If file changed, then download
                metadata = {
                    "last_modified" : obj.last_modified
                }
                selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
                # If metadata passed, then I will add all the user generated values that are associated to the file
                if "metadata" in self.selector.to_metadata:
                    # Make an additional call to get the full context
                    additional_metdata:dict = s3_client.head_object(Bucket=bucket_name, Key=obj.key)
                    selected_metadata.update(additional_metdata['Metadata'])
                yield CloudFile(file_identifier=obj.key, metadata=selected_metadata)


    
    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        # Connect to S3
        aws_key_id= self.connector_information['aws_key_id']
        aws_access_key= self.connector_information['aws_access_key']
        bucket_name= self.connector_information['bucket_name']
        session = boto3.Session(
            aws_access_key_id=aws_key_id,
            aws_secret_access_key=aws_access_key,
        )
        s3_client = session.client("s3")
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{cloudFile.file_identifier}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            s3_client.download_file(bucket_name, cloudFile.file_identifier, file_path)
            yield LocalFile(file_path=file_path, metadata=cloudFile.metadata, id=cloudFile.file_identifier)

    def validate(self) -> bool:
        try:
            aws_key_id= self.connector_information['aws_key_id']
            aws_access_key= self.connector_information['aws_access_key']
            bucket_name= self.connector_information['bucket_name']
        except:
            raise ValueError("Required properties not set")
        
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            session = boto3.Session(
                aws_access_key_id=aws_key_id,
                aws_secret_access_key=aws_access_key,
            )
            s3_resource = session.resource('s3')
            s3_client = session.client("s3")
            bucket = s3_resource.Bucket(bucket_name)
        except Exception as e:
            raise Exception(f"Connection to S3 failed, check key and key ID. See Exception: {e}")
        return True 

