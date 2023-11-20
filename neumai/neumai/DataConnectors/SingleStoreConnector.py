from datetime import datetime
from neumai.DataConnectors.DataConnector import DataConnector
from typing import List, Generator, Optional
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import SinglestoreConnectionException
from decimal import Decimal
from pydantic import Field
import singlestoredb as s2
import json


class SingleStoreConnector(DataConnector):
    """
    SingleStore Connector

    Extracts rows from Single Store database
    
    Attributes:
    -----------

    connection_string : str
        Connection string to Single Store database (i.e. \<user\>:\<password\>@\<host\>:\<port\>/\<database_name\>)
    query : str
        Query to extract data from database (i.e. Select * From TableName)
    batch_size : Optional[int]
        Number of rows to process per batch
    selector : Optional[Selector]
        Optional selector object to define what data data should be used to generate embeddings or stored as metadata with the vector.
    
    """
    
    connection_string: str = Field(..., description="Connection string to Single Store database.")

    query: str = Field(..., description="Query to be executed.")

    batch_size: Optional[int] = Field(1000, description="Number of rows to process per batch.")

    selector: Optional[Selector] = Field(Selector(to_embed=[], to_metadata=[]), description="Selector for data connector metadata")

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
        batch_size = self.batch_size
        
        with s2.connect(connection_string, results_type="dict") as conn:
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
    
    def config_validation(self) -> bool:
        try: 
            s2.connect(self.connection_string, results_type="dict")
        except Exception as e:
            raise SinglestoreConnectionException(f"There was a problem connecting to Singlestore. See Exception: {e}")
        return True 
                