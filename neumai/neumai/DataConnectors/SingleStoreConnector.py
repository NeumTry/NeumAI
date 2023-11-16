from datetime import datetime
from DataConnectors.DataConnector import DataConnector
from typing import List, Generator
from Shared.LocalFile import LocalFile
from Shared.CloudFile import CloudFile
from Shared.Exceptions import SinglestoreConnectionException
from decimal import Decimal
import singlestoredb as s2
import json


class SingleStoreConnector(DataConnector):
    """SingleStore Connector \n
    connector_information requires:\n
    [ url, query ]"""
    
    @property
    def connector_name(self) -> str:
        return "SingleStoreConnector"
    
    @property
    def required_properties(self) -> List[str]:
        return ["url", "query"]

    @property
    def optional_properties(self) -> List[str]:
        return ["batch_size"]
    
    @property
    def available_metadata(self) -> str:
        return []
    
    @property
    def schedule_avaialable(self) -> bool:
        return True

    @property
    def auto_sync_available(self) -> bool:
        return False
    
    @property
    def compatible_loaders(self) -> List[str]:
        return ["NeumJSONLoader"]
    
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)  # Convert Decimal to a string representation
            elif isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO format string
            return super().default(obj)

    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        url = self.connector_information['url']
        query = self.connector_information['query']
        batch_size = 1000
        if 'batch_size' in self.connector_information.keys():
            batch_size = self.connector_information['batch_size']
        
        with s2.connect(url, results_type="dict") as conn:
            with conn.cursor() as cur:
                batch_rows = []
                cur.execute(query)
                while True:
                    rows = cur.fetchmany(batch_size)
                    if not rows:
                        break
                    for row in rows:
                        serialized_string = json.dumps(dict(row),cls=self.CustomEncoder)
                        serialized_dict = json.loads(serialized_string)
                        batch_rows.append(serialized_dict)
                        if(len(batch_rows) == batch_size):
                            yield CloudFile(data=json.dumps(batch_rows), metadata={})
                            batch_rows = []

                if len(batch_rows) > 0:
                    yield CloudFile(data=json.dumps(batch_rows), metadata={})

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # No metadatadata to determine what rows are new. Needs to be done through websocket
        yield from self.connect_and_list_full()

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
         data = json.loads(cloudFile.data)
         for row in data:
            yield LocalFile(in_mem_data=json.dumps(row), metadata=cloudFile.metadata)
    
    def validate(self) -> bool:
        try:
            url = self.connector_information['url']
            query = self.connector_information['query']
        except:
            raise ValueError(f"Required properties not set. Required properties: {self.required_properties}")
        try: 
            s2.connect(url, results_type="dict")
        except Exception as e:
            raise SinglestoreConnectionException(f"There was a problem connecting to Singlestore. See Exception: {e}")
        return True 
                