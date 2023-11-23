from psycopg2.extras import DictCursor
from datetime import datetime
from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator, Optional
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import PostgresConnectionException
from decimal import Decimal
from pydantic import Field
import psycopg2
import json

class PostgresConnector(DataConnector):
    """
    Postgres Connector

    Extracts data from any Postgres database using a given query.
    
    Attributes:
    -----------

    connection_string : str
        Connection string for the Postgres database.
    query : str
        Query to be executed to pull data from the database. (i.e. Select * From TableName)
    selector : Optional[Selector]
        Optional selector object to define what data data should be used to generate embeddings or stored as metadata with the vector.
    
    """

    connection_string: str = Field(..., description="Connection string for the Postgres database.")

    query: str = Field(..., description="Query to execute on the Postgres database.")

    batch_size: Optional[int] = Field(1000, description="Batch size for processing data.")
    
    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

    @property
    def connector_name(self) -> str:
        return "PostgresConnector"

    @property
    def required_properties(self) -> List[str]:
        return ["connection_string", "query"]

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
        return ["JSONLoader"]
    
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)  # Convert Decimal to a string representation
            elif isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO format string
            return super().default(obj)
    
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        connection_string = self.connection_string
        query = self.query
        
        # Optional
        batch_size = self.batch_size

        with psycopg2.connect(connection_string) as connection:
            with connection.cursor(cursor_factory=DictCursor, name='neumai') as cursor:
                cursor.itersize = 1000  # fetch 1000 rows at a time
                cursor.execute(query)
                batch_rows = []
                for row in cursor:
                    serialized_string = json.dumps(dict(row),cls=self.CustomEncoder)
                    serialized_dict = json.loads(serialized_string)
                    batch_rows.append(serialized_dict)
                    if(len(batch_rows) == batch_size):
                        yield CloudFile(data=json.dumps(batch_rows), metadata={}, id="Postgres")
                        batch_rows = []
                if len(batch_rows) > 0:
                    yield CloudFile(data=json.dumps(batch_rows), metadata={}, id="Postgres")

    def connect_and_list_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        # No metadatadata to determine what rows are new. Needs to be done through websocket
        yield from self.connect_and_list_full()

    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        data = json.loads(cloudFile.data)
        for row in data:
            yield LocalFile(in_mem_data=json.dumps(row), metadata=cloudFile.metadata)

    def config_validation(self) -> bool:
        if not all(x in self.available_metadata for x in self.selector.to_metadata):
            raise ValueError("Invalid metadata values provided")
        try:
            psycopg2.connect(self.connection_string)
        except Exception as e:
            raise PostgresConnectionException(f"Connection to Postgres failed, check credentials. See Exception: {e}")      
        return True   