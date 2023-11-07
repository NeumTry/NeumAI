from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List

class QdrantSink(SinkConnector):
    """ Qdrant Sink\n
    sink_information requires : [ 'url', 'api_key' ]"""

    @property
    def sink_name(self) -> str:
        return 'QdrantSink'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ['url', 'api_key']

    @property
    def optionalProperties(self) -> List[str]:
        return ['collection_name']

    def validation(self) -> bool:
        """Validate connector setup"""
        from qdrant_client import QdrantClient
        try:
            url = self.sink_information["url"]
            api_key = self.sink_information["api_key"]
        except:
            raise ValueError("Required properties not set")
        try:
            qdrant_client = QdrantClient(
                url=url, 
                api_key=api_key,
            )
        except Exception as e:
            raise ValueError(f"Qdrant connection couldn't be initialized. See exception: {e}")
        return True 

    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> int:
        from qdrant_client.http.models import Distance, VectorParams
        from qdrant_client.http.models import PointStruct
        from qdrant_client.http.models import UpdateStatus
        from qdrant_client import QdrantClient

        url = self.sink_information["url"]
        api_key = self.sink_information["api_key"]
        collection_name = self.sink_information.get("collection_name", f"pipeline_{pipeline_id}")
        qdrant_client = QdrantClient(
            url=url, 
            api_key=api_key,
        )
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.DOT)
        )
        points = [PointStruct(id=vector.id, vector=vector.vector, payload=vector.metadata) for vector in vectors_to_store]
        operation_info = qdrant_client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )
        if(operation_info.status == UpdateStatus.COMPLETED):
            return  len(points)
        raise Exception("Qdrant storing failed. Try again later.")
    
    def search(self, vector: List[float], number_of_results: int, pipeline_id: str) -> List:
        from qdrant_client import QdrantClient
        api_key = self.sink_information["api_key"]
        url = self.sink_information['url']
        collection_name = self.sink_information['collection_name']
        try:
            qdrant_client = QdrantClient(
                url=url, 
                api_key=api_key,
            )
            search_result = qdrant_client.search(
                collection_name=collection_name,
                query_vector=vector, 
                with_payload= True,
                limit=number_of_results
            )
        except Exception as e:
            raise(f"Failed to query Qdrant. Exception - {e}")
        
        matches = []
        for result in search_result:
            matches.append(
                NeumSearchResult(
                    id=result.id,
                    metadata=result.payload,
                    score=result.score
                )
            )
        return matches
    
    def info(self, pipeline_id: str) -> NeumSinkInfo:
        from qdrant_client import QdrantClient
        api_key = self.sink_information["api_key"]
        url = self.sink_information['url']
        collection_name = self.sink_information['collection_name']
        try:
            qdrant_client = QdrantClient(
                url=url, 
                api_key=api_key,
            )
            collection_info = qdrant_client.get_collection(collection_name=collection_name)
            return(NeumSinkInfo(number_vectors_stored=collection_info.indexed_vectors_count))
        except Exception as e:
            raise(f"Failed to get information from Qdrant. Exception - {e}")