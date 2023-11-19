from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    QdrantInsertionException,
    QdrantIndexInfoException,
    QdrantQueryException
)
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List, Optional
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import UpdateStatus
from qdrant_client import QdrantClient
from pydantic import Field

class QdrantSink(SinkConnector):
    """
    Qdrant Sink

    A sink connector for Qdrant, designed to facilitate data output into a Qdrant storage system.

    Attributes:
    -----------
    url : str
        URL for accessing the Qdrant service.

    api_key : str
        API key required for authenticating with the Qdrant service.

    collection_name : Optional[str]
        Optional name of the collection in Qdrant where the data will be stored.
    """

    url: str = Field(..., description="URL for Qdrant.")

    api_key: str = Field(..., description="API key for Qdrant.")

    collection_name: Optional[str] = Field(None, description="Optional collection name.")

    @property
    def sink_name(self) -> str:
        return 'QdrantSink'
    
    @property
    def required_properties(self) -> List[str]:
        return ['url', 'api_key']

    @property
    def optional_properties(self) -> List[str]:
        return ['collection_name']

    def validation(self) -> bool:
        """config_validation connector setup"""
        from qdrant_client import QdrantClient
        qdrant_client = QdrantClient(
            url=self.url, 
            api_key=self.api_key,
        )
        return True 

    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> int:
        url = self.url
        api_key = self.api_key
        collection_name = self.collection_name
        if collection_name == None: f"pipeline_{pipeline_id}"

        qdrant_client = QdrantClient(
            url=url, 
            api_key=api_key,
        )
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=len(vectors_to_store[0].vector), distance=Distance.DOT)
        )
        points = [PointStruct(id=vector.id, vector=vector.vector, payload=vector.metadata) for vector in vectors_to_store]
        operation_info = qdrant_client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )
        if(operation_info.status == UpdateStatus.COMPLETED):
            return  len(points)
        raise QdrantInsertionException("Qdrant storing failed. Try again later.")
    
    def search(self, vector: List[float], number_of_results: int, pipeline_id: str) -> List:
        url = self.url
        api_key = self.api_key
        collection_name = self.collection_name
        if collection_name == None: f"pipeline_{pipeline_id}"

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
            raise QdrantQueryException(f"Failed to query Qdrant. Exception - {e}")
        
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
        url = self.url
        api_key = self.api_key
        collection_name = self.collection_name
        if collection_name == None: f"pipeline_{pipeline_id}"

        try:
            qdrant_client = QdrantClient(
                url=url, 
                api_key=api_key,
            )
            collection_info = qdrant_client.get_collection(collection_name=collection_name)
            return(NeumSinkInfo(number_vectors_stored=collection_info.indexed_vectors_count))
        except Exception as e:
            raise QdrantIndexInfoException(f"Failed to get information from Qdrant. Exception - {e}")