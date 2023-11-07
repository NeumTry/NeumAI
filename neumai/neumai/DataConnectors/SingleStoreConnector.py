from psycopg2.extras import DictCursor
from datetime import datetime
from DataConnector import DataConnector
from typing import List, Generator
from neumai.SharedLocalFile import LocalFile
from neumai.SharedCloudFile import CloudFile
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
    def requiredProperties(self) -> List[str]:
        return ["url", "query"]

    @property
    def optionalProperties(self) -> List[str]:
        return ["batch_size"]
    
    @property
    def availableMetadata(self) -> str:
        return []

    @property
    def availableContent(self) -> str:
        return ['row']
    
    @property
    def schedule_avaialable(self) -> bool:
        return True

    @property
    def auto_sync_available(self) -> bool:
        return False
    
    @property
    def compatible_loaders(self) -> List[str]:
        return ["NeumJSONLoader"]
    
    def datetime_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

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
                        batch_rows.append(row)
                        if(len(batch_rows) == batch_size):
                            json_object = json.dumps(batch_rows, default=self.datetime_serializer)
                            yield CloudFile(data=json_object, metadata={})
                            batch_rows = []

                if len(batch_rows) > 0:
                        json_object = json.dumps(batch_rows, default=self.datetime_serializer)
                        yield CloudFile(data=json_object, metadata={})

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # No metadatadata to determine what rows are new. Needs to be done through websocket
        yield from self.connect_and_list_full()

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
         data = json.loads(cloudFile.data)
         for row in data:
            yield LocalFile(in_mem_data=dict(row), metadata=cloudFile.metadata)
    
    def validate(self) -> bool:
        try:
            url = self.connector_information['url']
            query = self.connector_information['query']
        except:
            raise ValueError("Required properties not set")
        
        try: 
            s2.connect(url, results_type="dict")
        except:
            raise Exception("Connection URL is incorrect")
        return True 
                