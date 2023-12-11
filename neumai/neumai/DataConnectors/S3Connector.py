from datetime import datetime
from typing import List, Generator, Optional
import boto3
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import S3ConnectionException
from neumai.DataConnectors.DataConnector import DataConnector
from pydantic import Field
import tempfile
import os

class S3Connector(DataConnector):
    """
    S3 Connector

    Extracts files from an S3 Bucket
    
    Attributes:
    -----------

    aws_key_id : str
        Access key ID to the S3 bucket
    aws_access_key : str
        Access key to the S3 bucket
    bucket_name : str
        Name of S3 bucket
    prefix : Optional[str]
        File prefix filter
    selector : Optional[Selector]
        Optional selector object to define what data data should be used to generate embeddings or stored as metadata with the vector.
    
    """
    
    aws_key_id: str = Field(..., description="AWS Key ID for S3 access.")

    aws_access_key: str = Field(..., description="AWS Access Key for S3 access.")

    bucket_name: str = Field(..., description="S3 bucket name.")

    prefix: Optional[str] = Field("", description="Optional prefix for S3 files.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

    @property
    def connector_name(self) -> str:
        return "S3Connector"
    
    @property
    def required_properties(self) -> List[str]:
        return ["aws_key_id", "aws_access_key", "bucket_name"]

    @property
    def optional_properties(self) -> List[str]:
        return ["prefix"]
    
    @property
    def available_metadata(self) -> str:
        return ["key" , "last_modified", "metadata" ]
    
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
        aws_key_id= self.aws_key_id
        aws_access_key= self.aws_access_key
        bucket_name= self.bucket_name
        prefix = self.prefix
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
            yield CloudFile(file_identifier=obj.key, metadata=selected_metadata, id=obj.key)

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # Connect to S3
        aws_key_id= self.aws_key_id
        aws_access_key= self.aws_access_key
        bucket_name= self.bucket_name
        prefix = self.prefix
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
                    "key" : obj.key,
                    "last_modified" : obj.last_modified
                }
                selected_metadata  = {k: metadata[k] for k in self.selector.to_metadata if k in metadata}
                # If metadata passed, then I will add all the user generated values that are associated to the file
                if "metadata" in self.selector.to_metadata:
                    # Make an additional call to get the full context
                    additional_metdata:dict = s3_client.head_object(Bucket=bucket_name, Key=obj.key)
                    selected_metadata.update(additional_metdata['Metadata'])
                yield CloudFile(file_identifier=obj.key, metadata=selected_metadata, id=obj.key)

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        # Connect to S3
        aws_key_id= self.aws_key_id
        aws_access_key= self.aws_access_key
        bucket_name= self.bucket_name
        session = boto3.Session(
            aws_access_key_id=aws_key_id,
            aws_secret_access_key=aws_access_key,
        )
        s3_client = session.client("s3")
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = f"{temp_dir}/{cloudFile.file_identifier}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            s3_client.download_file(bucket_name, cloudFile.file_identifier, file_path)
            yield LocalFile(file_path=file_path, metadata=cloudFile.metadata, id=cloudFile.id)

    def config_validation(self) -> bool:      
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_key_id,
                aws_secret_access_key=self.aws_access_key,
            )
            client = session.client("s3")
            client.head_bucket(Bucket=self.bucket_name)
        except Exception as e:
            raise S3ConnectionException(f"Connection to S3 failed, check key and key ID. See Exception: {e}")
        return True 

