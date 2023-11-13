from psycopg2.extras import DictCursor
from datetime import datetime
from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from decimal import Decimal
import psycopg2
import json


class PostgresConnector(DataConnector):
    """Postgres Connector \n
    connector_information requires:\n
    [ connection_string, query, batch_size]"""
    
    @property
    def connector_name(self) -> str:
        return "PostgresConnector"
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["connection_string", "query"]

    @property
    def optionalProperties(self) -> List[str]:
        return ["batch_size"]
    
    @property
    def availableMetadata(self) -> str:
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
        connection_string = self.connector_information['connection_string']
        query = self.connector_information['query']
        
        # Optional
        batch_size = self.connector_information.get('batch_size', 1000)

        with psycopg2.connect(connection_string) as connection:
            with connection.cursor(cursor_factory=DictCursor, name='pipeline_id') as cursor:
                cursor.itersize = 1000  # fetch 1000 rows at a time
                cursor.execute(query)
                batch_rows = []
                for row in cursor:
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
            connection_string = self.connector_information['connection_string']
            query = self.connector_information['query']
        except:
            raise ValueError("Required properties not set")
        
        if not all(x in self.availableMetadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        
        try:
            connection = psycopg2.connect(connection_string)
        except Exception as e:
            raise Exception(f"Connection to Postgres failed, check credentials. See Exception: {e}")      
        return True   