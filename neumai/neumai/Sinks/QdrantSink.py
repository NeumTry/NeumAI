from typing import List, Tuple
from .SinkConnector import SinkConnector
from NeumVector import NeumVector
from starlette.exceptions import HTTPException

class QdrantSink(SinkConnector):
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
        # metadata: url, api_key, cluster namme, collection name
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
        raise HTTPException(status_code=500, detail="Qdrant storing failed. Try again later.")
    
    def search(self, vector: List[float], number_of_results: int, pipeline_id: str) -> List:
        from qdrant_client import QdrantClient
        api_key = self.sink_information["api_key"]
        url = self.sink_information['url']
        collection_name = self.sink_information['collection_name']
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
        matches = []
        for result in search_result:
            matches.append(str(result.payload))
        return matches