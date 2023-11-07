from typing import List
from Shared.NeumSinkInfo import NeumSinkInfo
from .SinkConnector import SinkConnector
from Shared.NeumVector  import NeumVector
from Shared.NeumSearch import NeumSearchResult

class SingleStoreSink(SinkConnector):
    @property
    def sink_name(self) -> str:
        return 'SingleStoreSink'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ['url', 'api_key']

    @property
    def optionalProperties(self) -> List[str]:
        return ['collection_name']

    def validation(self) -> bool:
        """Validate connector setup"""
        import singlestoredb as s2
        try:
            url = self.sink_information['url']
            table = self.sink_information['table']
        except:
            raise ValueError("Required properties not set")
        try:
            s2.connect(url)
        except Exception as e:
            raise ValueError(f"SingleStore connection couldn't be initialized. See exception: {e}")
        return True 

    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> int:
        import singlestoredb as s2
        batch_size = 1000
        url = self.sink_information['url']
        table = self.sink_information['table']

        # Get metadata list
        # metadata_fields = ""
        if vectors_to_store[0].metadata is not None:
            metadata_keys = vectors_to_store[0].metadata.keys()
            if(len(metadata_keys) > 0):
                metadata_fields = ', ' + ', '.join(metadata_keys)
            else: metadata_fields = ""

        # Determine the number of batches
        num_batches = (len(vectors_to_store) + batch_size-1) // batch_size
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
        
        return len(vectors_to_store), None
    
    def search(self, vector: List[float], number_of_results: int, pipeline_id: str) -> List[NeumSearchResult]:
        import singlestoredb as s2
        url = self.sink_information['url']
        table = self.sink_information['table']

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
            raise Exception(f"Failed to query single store. Exception - {e}")

    def info(self, pipeline_id: str) -> NeumSinkInfo:
        import singlestoredb as s2
        url = self.sink_information['url']
        table = self.sink_information['table']

        query = f"""SELECT Count(*) as count
        FROM {table}"""
        
        try:
            with s2.connect(url, results_type="dict") as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return NeumSinkInfo(number_vectors_stored=dict(rows[0])["count"])
        except Exception as e:
            raise Exception(f"Failed to get info for singlestore. Exception - {e}") 