from typing import List, Optional, Tuple
from neumai.SinkConnectors.SinkConnector import SinkConnector
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    WeaviateConnectionException,
    WeaviateInsertionException,
    WeaviateIndexInfoException,
    WeaviateQueryException
)
import weaviate
from weaviate.util import generate_uuid5, _capitalize_first_letter

class WeaviateSink(SinkConnector):
    """ Weaviate Sink\n
    sink_information requires : [ url , api_key ]"""

    @property
    def sink_name(self) -> str:
        return 'WeaviateSink'
    
    @property
    def required_properties(self) -> List[str]:
        return ['url', 'api_key']

    @property
    def optional_properties(self) -> List[str]:
        return ['class_name', 'num_workers', 'shard_count', 'batch_size', 'is_dynamic_batch', 'batch_connection_error_retries']

    def validation(self) -> bool:
        """Validate connector setup"""
        try:
            url = self.sink_information["url"]
            if 'https' not in url:
                api_key = self.sink_information["api_key"]
        except:
            raise ValueError(f"Required properties not set. Required properties: {self.required_properties}")
        try:
            if 'https' not in url:
                client = weaviate.Client(
                    url=url
                )
            else:
                api_key = self.sink_information["api_key"]
                client = weaviate.Client(
                    url=url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
                )
        except Exception as e:
            raise WeaviateConnectionException(f"Weaviate couldn't be initialized. See exception: {e}")
        return True 

    def _check_batch_result(self, results: Optional[List[dict[str, any]]], task_id: str, partial_failure: dict):
        if results is not None:
            for result in results:
                if "result" in result and "errors" in result["result"]:
                    if "error" in result["result"]["errors"]:
                        print(f"[ERROR] Task Id {task_id} encountered an error when batching to weaviate {result['result']}")
                        partial_failure['did_fail'] = True
                        partial_failure['latest_failure'] = result["result"]["errors"]["error"]
                        partial_failure['number_of_failures'] += 1

    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> Tuple[List, dict]:
        url = self.sink_information["url"]
        num_workers = self.sink_information.get('num_workers', 1)
        shard_count = self.sink_information.get('shard_count', 1)
        batch_size = self.sink_information.get('batch_size', 100)
        is_dynamic_batch = self.sink_information.get('is_dynamic_batch', False)
        batch_connection_error_retries = self.sink_information.get('batch_connection_error_retries', 3)
        class_name = self.sink_information.get('class_name', f"pipeline_{pipeline_id.replace('-','_')}")
        partial_failure = {'did_fail': False, 'latest_failure': None, 'number_of_failures': 0}

        if 'https' not in url:
            client = weaviate.Client(
                url=url
            )
        else:
            api_key = self.sink_information["api_key"]
            client = weaviate.Client(
                url=url,
                auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
            )
        try:
            client.schema.create_class({
                "class": class_name,
                "shardingConfig":{"desiredCount":shard_count},
            })
        except weaviate.UnexpectedStatusCodeException as e:
            if 'already exists' not in e.message:
                raise WeaviateInsertionException(f"Error when creating class in weaviate. Error: {e}")
            
        with client.batch.configure(
            batch_size=batch_size,
            callback=lambda results: self._check_batch_result(results, task_id, partial_failure),
            num_workers=num_workers,
            dynamic=is_dynamic_batch,
            connection_error_retries=batch_connection_error_retries
        ) as batch:
            for i in range(0, len(vectors_to_store)):
                try:
                    batch.add_data_object(
                        data_object=vectors_to_store[i].metadata,
                        class_name=class_name,
                        vector=vectors_to_store[i].vector,
                        uuid=generate_uuid5(vectors_to_store[i].id)
                    )
                except Exception as e:
                    print(f"[ERROR] Got exception from Weaviate when adding data object to batch for task {task_id} and batch # {i}. Exception: {str(e)}")
                    raise WeaviateInsertionException(f"Error when adding data object to Weaviate. Error: {e}")

        return len(vectors_to_store)

    def search(self, vector: List[float], number_of_results: int, pipeline_id: str) -> List[NeumSearchResult]:
        api_key = self.sink_information["api_key"]
        url = self.sink_information['url']
        # Weaviate requires first letter to be capitalized
        class_name = _capitalize_first_letter(self.sink_information.get('class_name', f"Pipeline_{pipeline_id.replace('-', '_')}"))
        client = weaviate.Client(
            url=url,
            auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
        )
        
        try:
            class_schema = client.schema.get(class_name)
        except Exception as e:
            raise WeaviateQueryException(f"There was an error retrieving the class schema from weaviate")

        full_class_schema_properties = [property['name'] for property in class_schema['properties']]
        matches = []
        try:
            search_result = (
                client.query
                .get(class_name=class_name, properties=full_class_schema_properties)
                .with_near_vector(content = {
                    'vector' : vector
                })
                .with_limit(number_of_results)
                .with_additional(['id','certainty'])
                .do()
            )

            for result in search_result["data"]["Get"][class_name]:
                # unify our api with the metadata.. or just return whatever metadata we have. (?)
                matches.append(NeumSearchResult(id=result['_additional']['id'], score=result['_additional']['certainty'], metadata= {k: v for k, v in result.items() if k != "_additional"}))
        except Exception as e:
            raise WeaviateQueryException(f"There was an error querying weaviate. Error {e}")
        return matches

    def info(self, pipeline_id:str) -> NeumSinkInfo:
        api_key = self.sink_information["api_key"]
        url = self.sink_information['url']
        
        class_name = _capitalize_first_letter(self.sink_information.get('class_name', f"Pipeline_{pipeline_id.replace('-', '_')}"))
        client = weaviate.Client(
            url=url,
            auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
        )
        try:
            response = (
                client.query
                .aggregate(class_name=class_name)
                .with_meta_count()
                .do()
            )
            vectors_stored_in_class = response["data"]["Aggregate"][class_name]["meta"]["count"]
            return NeumSinkInfo(number_vectors_stored=vectors_stored_in_class)
        except Exception as e:
            raise WeaviateIndexInfoException(f"There was an error getting class info from weaviate {e}")