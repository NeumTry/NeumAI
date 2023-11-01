from typing import List, Tuple
from .SinkConnector import SinkConnector
from NeumVector import NeumVector

class PineconeSink(SinkConnector):
    @property
    def sink_name(self) -> str:
        return 'PineconeSink'
    
    @property
    def requiredProperties(self) -> List[str]:
        return ['api_key', 'environment', 'index']

    @property
    def optionalProperties(self) -> List[str]:
        return ['namespace']

    def validation(self) -> bool:
        """Validate connector setup"""
        import pinecone
        try:
            api_key = self.sink_information['api_key']
            environment = self.sink_information['environment']
            index = self.sink_information['index']
        except:
            raise ValueError("Required properties not set")
        try:
            pinecone.init(api_key=api_key, environment=environment)    
            index = pinecone.Index(index_name=index)
        except Exception as e:
            raise ValueError(f"Pinecone connection couldn't be initialized. See exception: {e}")
        return True 

    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> int:
        import pinecone
        api_key =  self.sink_information['api_key']
        environment = self.sink_information['environment']
        index = self.sink_information['index']
        namespace = self.sink_information.get("namespace", f"pipeline_{pipeline_id}")
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
        return int(vectors_stored)
    
    def search(self, vector: List[float], number_of_results:int, pipeline_id:str) -> List:
        import pinecone
        api_key = self.sink_information["api_key"]
        environment = self.sink_information['environment']
        index = self.sink_information['index']
        namespace = self.sink_information.get("namespace", f"pipeline_{pipeline_id}")
        pinecone.init(      
            api_key=api_key,      
            environment=environment)    
        index = pinecone.Index(index)
        results = index.query(vector=vector, top_k=number_of_results, namespace=namespace, include_values=False, include_metadata=True)["matches"]
        matches = []
        for result in results:
            matches.append(str(result["metadata"]))
        return matches