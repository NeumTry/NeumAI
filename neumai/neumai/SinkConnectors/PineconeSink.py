from typing import List, Optional
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.SinkConnectors.SinkConnector import SinkConnector
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.Exceptions import (
    PineconeConnectionException,
    PineconeInsertionException,
    PineconeIndexInfoException,
    PineconeQueryException,
)
from neumai.SinkConnectors.filter_utils import FilterCondition, FilterOperator
from pydantic import Field
import pinecone

class  PineconeSink(SinkConnector):
    """
    Pinecone Sink

    A sink connector specifically designed for Pinecone, facilitating the output of processed data into a Pinecone environment.

    Attributes:
    -----------
    api_key : str
        API key for accessing the Pinecone service.

    environment : str
        The specific Pinecone environment to connect to.

    index : str
        The index in Pinecone where the data will be stored.

    namespace : str
        Namespace within the Pinecone environment. Used for organizing data.
    """

    api_key: str = Field(..., description="API key for Pinecone.")

    environment: str = Field(..., description="Pinecone environment.")

    index: str = Field(..., description="Index for Pinecone.")

    namespace: str = Field(..., description="Data namespace.")

    @property
    def sink_name(self) -> str:
        return 'PineconeSink'
    
    @property
    def required_properties(self) -> List[str]:
        return ['api_key', 'environment', 'index', 'namespace']

    @property
    def optional_properties(self) -> List[str]:
        return []

    def validation(self) -> bool:
        """config_validation connector setup"""
        import pinecone
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)    
            index = pinecone.Index(index_name=self.index)
            index.describe_index_stats()
        except Exception as e:
            raise PineconeConnectionException(f"Pinecone connection couldn't be initialized. See exception: {e}")
        return True 

    def delete_vectors_with_file_id(self, file_id: str) -> bool:
        api_key =  self.api_key
        environment = self.environment
        index = self.index
        namespace = self.namespace
        if environment == "gcp-starter":
            raise Exception("Pinecone does not support deleting vectors by metadata in the gcp starter environment")
        pinecone.init(      
            api_key=api_key,      
            environment=environment)    
        index = pinecone.Index(index)
        index.delete(filter={"_file_entry_id": {"$eq": file_id}}, namespace=namespace)
        return True

    def store(self, vectors_to_store:List[NeumVector]) -> int:
        api_key =  self.api_key
        environment = self.environment
        index = self.index
        namespace = self.namespace
        if environment == "gcp-starter": namespace = None # short-term fix given gcp-starter limitation

        try:
            pinecone.init(api_key=api_key, environment=environment)    
            index = pinecone.Index(index_name=index)
            batch_size = 32 # how does changing this affect ?
            vectors_stored = 0
            for i in range(0, len(vectors_to_store), batch_size):
                # set end position of batch
                i_end = min(i + batch_size, len(vectors_to_store))
                # get batch of texts and ids
                vector_batch = vectors_to_store[i:i_end]
                to_upsert = [(vector.id, vector.vector, vector.metadata) for vector in vector_batch]
                result = index.upsert(vectors=to_upsert, namespace=namespace)
                vectors_stored += result['upserted_count'] 
        except Exception as e:
            raise PineconeInsertionException(f"Failed to store in Pinecone. Exception - {e}")
        return int(vectors_stored)
    
    def translate_to_pinecone(filter_conditions:List[FilterCondition]):
        query_parts = []

        for condition in filter_conditions:
            mongo_operator = {
                FilterOperator.EQUAL: '$eq',
                FilterOperator.NOT_EQUAL: '$ne',
                FilterOperator.GREATER_THAN: '$gt',
                FilterOperator.GREATER_THAN_OR_EQUAL: '$gte',
                FilterOperator.LESS_THAN: '$lt',
                FilterOperator.LESS_THAN_OR_EQUAL: '$lte',
                FilterOperator.IN: '$in',
            }.get(condition.operator, None)

            if mongo_operator:
                query_parts.append({condition.field: {mongo_operator: condition.value}})
            else:
                # TODO Handle complex cases like IN, NOT IN, etc.
                pass

        return {"$and": query_parts}  # Combine using $and

    def search(self, vector: List[float], number_of_results:int, filters:List[FilterCondition] = []) -> List[NeumSearchResult]:
        import pinecone
        api_key =  self.api_key
        environment = self.environment
        index = self.index
        namespace = self.namespace
        if environment == "gcp-starter": namespace = None # short-term fix given gcp-starter limitation
        
        filters_pinecone =  self.translate_to_pinecone(filters)

        try:
            pinecone.init(      
                api_key=api_key,      
                environment=environment)    
            index = pinecone.Index(index)
            results = index.query(
                vector=vector, 
                filter=filters_pinecone,
                top_k=number_of_results, 
                namespace=namespace, 
                include_values=False, 
                include_metadata=True)["matches"]
        except Exception as e:
            raise PineconeQueryException(f"Failed to query pinecone. Exception - {e}")
        
        matches = []
        for result in results:
            matches.append(NeumSearchResult(id= result["id"], metadata=result["metadata"], score=result["score"]))
        return matches
    
    def info(self) -> NeumSinkInfo:
        import pinecone
        api_key =  self.api_key
        environment = self.environment
        index = self.index
        namespace = self.namespace
        if environment == "gcp-starter": namespace = None # short-term fix given gcp-starter limitation
        
        try:
            pinecone.init(      
                api_key=api_key,      
                environment=environment)    
            index = pinecone.Index(index)
            namespaces = index.describe_index_stats()["namespace"]
            if namespace in namespaces:
                return NeumSinkInfo(number_vectors_stored=namespaces[namespace]["vector_count"])
        except Exception as e:
            raise PineconeIndexInfoException(f"Failed to get info for pinecone. Exception - {e}")