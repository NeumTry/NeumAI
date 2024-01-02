from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    SinglestoreConnectionException,
    SinglestoreInsertionException,
    SinglestoreIndexInfoException,
    SinglestoreQueryException
)
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List, Optional
from neumai.SinkConnectors.filter_utils import FilterCondition, FilterOperator
from pydantic import Field
import singlestoredb as s2

class SingleStoreSink(SinkConnector):
    """
    SingleStore Sink

    This sink connector is used for integrating with SingleStore databases, enabling the output of data to a specified SingleStore table.

    Attributes:
    -----------
    url : str
        URL for connecting to the SingleStore database.

    api_key : str
        API key for authentication with the SingleStore service.

    table : str
        The name of the table within SingleStore where data needs to be stored. This table needs to be pre-created.

    batch_size : Optional[str]
        Optional size of row batches to be extracted and stored in SingleStore. Default is 1000.
    """

    url: str = Field(..., description="URL for SingleStore.")

    api_key: str = Field(..., description="API key for SingleStore.")

    table: str = Field(..., description="Table name. Needs to be pre-created")

    batch_size: Optional[str] = Field(1000, description="Optional size of row batches extracted")

    @property
    def sink_name(self) -> str:
        return 'SingleStoreSink'

    @property
    def required_properties(self) -> List[str]:
        return ['url', 'api_key', 'table']

    @property
    def optional_properties(self) -> List[str]:
        return ['batch_size']

    def validation(self) -> bool:
        """config_validation connector setup"""
        import singlestoredb as s2
        try: 
            s2.connect(self.url)
        except Exception as e:
            raise SinglestoreConnectionException(f"There was a problem connecting to Singlestore. See Exception: {e}")
        return True 

    def delete_vectors_with_file_id(self, file_id: str) -> bool:
        with s2.connect(self.url) as conn:
            with conn.cursor() as cur:
                delete_query = f"""DELETE FROM {self.table} WHERE _file_entry_id='{file_id}';"""
                cur.execute(delete_query)
        return True
    
    def store(self, vectors_to_store:List[NeumVector]) -> int:
        batch_size = self.batch_size
        url = self.url
        table = self.table

        # Get metadata list
        # metadata_fields = ""
        if vectors_to_store[0].metadata is not None:
            metadata_keys = vectors_to_store[0].metadata.keys()
            if(len(metadata_keys) > 0):
                metadata_fields = ', ' + ', '.join(metadata_keys)
            else: metadata_fields = ""

        # Determine the number of batches
        num_batches = (len(vectors_to_store) + batch_size-1) // batch_size
        try:
            with s2.connect(url) as conn:
                with conn.cursor() as cur:
                    for batch_num in range(num_batches):
                        # Get the start and end indices for this batch
                        start_idx = batch_num * 1000
                        end_idx = start_idx + 1000
                        # Generate the values string for this batch
                        # Assumes a string based id. Needs to ensure the table is created as such
                        if metadata_fields != "":
                            value_strings = [
                                "(\'{}\', \'{}\', json_array_pack(\'{}\'), {})".format(
                                    vectors_to_store[i].id, vectors_to_store[i].vector, ', '.join(["'" + str(value) + "'" for value in vectors_to_store[i].metadata.values()])
                                )
                                for i in range(start_idx, min(end_idx, len(vectors_to_store)))
                            ]
                        else:
                            value_strings = [
                                "(\'{}\', \'{}\', json_array_pack(\'{}\'))".format(
                                    vectors_to_store[i].id, vectors_to_store[i].vector
                                )
                                for i in range(start_idx, min(end_idx, len(vectors_to_store)))
                            ]
                        values_sql = ',\n'.join(value_strings)
                        insert_query = f"""INSERT INTO {table} (id, vector{metadata_fields})\nVALUES\n{values_sql};"""
                        cur.execute(insert_query)
        except Exception as e:
            raise SinglestoreInsertionException("SingleStore storing failed. Try again later.")
        
        return len(vectors_to_store), None
    
    def translate_to_sql(filter_conditions:List[FilterCondition]):
        query_parts = []
        for condition in filter_conditions:
            sql_operator = condition.operator.value
            # Handle special formatting for IN, NOT IN, BETWEEN, etc.
            if condition.operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
                values = '(' + ', '.join(map(str, condition.value.split(','))) + ')'
            else:
                values = condition.value

            query_parts.append(f"{condition.field} {sql_operator} {values}")

        conditions_str = " AND ".join(query_parts)
        return conditions_str

    def search(self, vector: List[float], number_of_results: int, filters:List[FilterCondition]=[]) -> List[NeumSearchResult]:
        url = self.url
        table = self.table

        if len(filters)>0:
            list_of_fields = ",".join([f.field for f in filters])
            query = f"""SELECT id, text, dot_product(vector, json_array_pack('{vector}')) AS score, {list_of_fields}
            FROM {table}
            WHERE {self.translate_to_sql(filters)}
            ORDER BY score DESC
            LIMIT {number_of_results}"""
        
        else:
            query = f"""SELECT id, text, dot_product(vector, json_array_pack('{vector}')) AS score
            FROM {table}
            ORDER BY score DESC
            LIMIT {number_of_results}"""

        try:
            with s2.connect(url, results_type="dict") as conn:
                with conn.cursor() as cur:
                    matches:List[NeumSearchResult] = []
                    cur.execute(query)
                    for row in cur.fetchall():
                        matches.append(NeumSearchResult(id = str(dict(row)['id']), metadata={"text": str(dict(row)['text'])}, score=dict(row)['score']))
                    return matches
        except Exception as e:
            raise SinglestoreQueryException(f"Failed to query single store. Exception - {e}")

    def info(self) -> NeumSinkInfo:
        url = self.url
        table = self.table

        query = f"""SELECT Count(*) as count
        FROM {table}"""
        
        try:
            with s2.connect(url, results_type="dict") as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return NeumSinkInfo(number_vectors_stored=dict(rows[0])["count"])
        except Exception as e:
            raise SinglestoreIndexInfoException(f"Failed to get info for singlestore. Exception - {e}") 