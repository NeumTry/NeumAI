from typing import List
from .SinkConnector import SinkConnector
from Shared.NeumSinkInfo import NeumSinkInfo
from Shared.NeumVector  import NeumVector
from Shared.NeumSearch import NeumSearchResult

class SupabaseSink(SinkConnector):
    @property
    def sink_name(self) -> str:
        return 'SupabaseSink'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ['database_connection']

    @property
    def optionalProperties(self) -> List[str]:
        return ['collection_name']

    def validation(self) -> bool:
        """Validate connector setup"""
        import vecs
        try:
            database_connection = self.sink_information['database_connection']
        except:
            raise ValueError("Required properties not set")
        try:
            vx = vecs.create_client(database_connection)
        except Exception as e:
            raise ValueError(f"Supabase connection couldn't be initialized. See exception: {e}")
        return True 

    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> int:
        import vecs
        from vecs import Collection
        database_connection = self.sink_information['database_connection']
        vx = vecs.create_client(database_connection)
        collection_name = self.sink_information.get("collection_name", f"pipeline_{pipeline_id}")

        dimensions = len(vectors_to_store[0].vector)
        db = vx.get_or_create_collection(name=collection_name, dimension=dimensions)

        # supabase is doing some chunking here to automatically partition and batch the data, we should understand this further.
        # Also, this won't scale if there are too many items in the array
        toUpsert = []
        for i in range(0, len(vectors_to_store)):
            toUpsert.append((vectors_to_store[i].id, vectors_to_store[i].vector, vectors_to_store[i].metadata))

        db.upsert(records=toUpsert)

        # do we need to re index every time? this might be super costly. Can we check if there's an index and if not index otherwise don't?
        # db.create_index()
        # need to figure out how to do this only once. 
        vx.disconnect()
        return len(vectors_to_store)
    
    def search(self, vector: List[float], number_of_results:int, pipeline_id:str) -> List:
        import vecs
        DB_CONNECTION = self.sink_information['database_connection']
        vx = vecs.create_client(DB_CONNECTION)
        collection_name = self.sink_information.get("collection_name", f"pipeline_{pipeline_id}")
        try:
            db = vx.get_collection(name=collection_name)
        except:
            raise Exception(f"Collection {collection_name} does not exist")
        
        try:
            results = db.query(
                data=vector,           # required
                include_metadata=True,
                include_value=True,
                limit=number_of_results,  # number of records to return
            )
        except Exception as e:
            raise Exception(f"Error querying vectors from Supabase. Exception: {e}")
        
        matches = []
        for result in results:
            matches.append(NeumSearchResult(
                id= str(result[0]),
                metadata=result[2],
                score=result[1]
            ))
        
        vx.disconnect()
        return matches
    
    def info(self, pipeline_id: str) -> NeumSinkInfo:
        import vecs
        DB_CONNECTION = self.sink_information['database_connection']
        vx = vecs.create_client(DB_CONNECTION)
        collection_name = self.sink_information.get("collection_name", f"pipeline_{pipeline_id}")
        try:
            db = vx.get_collection(name=collection_name)
        except:
            raise Exception(f"Collection {collection_name} does not exist")
        
        number_of_vectors = db.table.select('count(*)')[0].count

        vx.disconnect()
        return NeumSinkInfo(number_vectors_stored=number_of_vectors)