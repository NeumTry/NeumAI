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
from neumai.SinkConnectors.filter_utils import FilterCondition
from pydantic import Field
from weaviate.util import generate_uuid5, _capitalize_first_letter
import weaviate

class WeaviateSink(SinkConnector):
    """
    Weaviate Sink

    A sink connector specifically designed for integrating with Weaviate, an open-source, ML-powered search engine. This connector enables efficient data output to a Weaviate instance, supporting various configuration options to optimize the data transfer process.

    Attributes:
    -----------
    url : str
        The URL for accessing the Weaviate instance. This should be the endpoint where Weaviate is hosted.

    api_key : str
        The API key for authenticating with the Weaviate service. This key is necessary for secure communication with the Weaviate instance.

    class_name : str
        An optional class name within Weaviate to which the data will be associated. Specifies the schema or type of data being stored.

    num_workers : Optional[int]
        The optional number of worker threads to use for data processing and uploading. Default is 1.

    shard_count : Optional[int]
        The optional number of shards to use for distributing data within Weaviate. Default is 1.

    batch_size : Optional[int]
        The optional size of batches for data processing and upload. Defines how many data items are processed together. Default is 100.

    is_dynamic_batch : Optional[bool]
        An optional flag to enable dynamic batching. If set to True, batch sizes may be adjusted dynamically based on network conditions and load. Default is False.

    batch_connection_error_retries : Optional[int]
        The optional number of retries in case of a batch connection error. Specifies how many times the connector should attempt to resend a batch in case of a connection error. Default is 3 retries.
    """

    url: str = Field(..., description="URL for Weaviate.")

    api_key: str = Field(..., description="API key for Weaviate.")

    class_name: str = Field(..., description="Class name.")

    num_workers: Optional[int] = Field(1, description="Optional number of workers.")

    shard_count: Optional[int] = Field(1, description="Optional shard count.")

    batch_size: Optional[int] = Field(100, description="Optional batch size.")

    is_dynamic_batch: Optional[bool] = Field(False, description="Optional dynamic batch flag.")

    batch_connection_error_retries: Optional[int] = Field(3, description="Optional batch connection error retries.")

    @property
    def sink_name(self) -> str:
        return 'WeaviateSink'
    
    @property
    def required_properties(self) -> List[str]:
        return ['url', 'api_key', 'class_name']

    @property
    def optional_properties(self) -> List[str]:
        return ['num_workers', 'shard_count', 'batch_size', 'is_dynamic_batch', 'batch_connection_error_retries']

    def validation(self) -> bool:
        """config_validation connector setup"""
        try:
            if 'https' not in self.url:
                client = weaviate.Client(
                    url=self.url
                )
            else:
                api_key = self.api_key
                client = weaviate.Client(
                    url=self.url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
                )
        except Exception as e:
            raise WeaviateConnectionException(f"Weaviate couldn't be initialized. See exception: {e}")
        return True 

    def _check_batch_result(self, results: Optional[List[dict[str, any]]], partial_failure: dict):
        if results is not None:
            for result in results:
                if "result" in result and "errors" in result["result"]:
                    if "error" in result["result"]["errors"]:
                        print(f"[ERROR] Error when batching to weaviate {result['result']}")
                        partial_failure['did_fail'] = True
                        partial_failure['latest_failure'] = result["result"]["errors"]["error"]
                        partial_failure['number_of_failures'] += 1

    def delete_vectors_with_file_id(self, file_id: str) -> bool:
        api_key = self.api_key
        url = self.url
        # Weaviate requires first letter to be capitalized
        class_name = self.class_name.replace("-","_")
        class_name = _capitalize_first_letter(class_name)
        client = weaviate.Client(
            url=url,
            auth_client_secret=weaviate.AuthApiKey(api_key=api_key),
        )
        client.batch.delete_objects(
            class_name=class_name,
            where={
                "path": ["_file_entry_id"],
                "operator": "Equal",
                "valueText": file_id
            },
        )
        return True
    
    def store(self, vectors_to_store:List[NeumVector]) -> Tuple[List, dict]:
        url = self.url
        num_workers = self.num_workers
        shard_count = self.shard_count
        batch_size = self.batch_size
        is_dynamic_batch = self.is_dynamic_batch
        batch_connection_error_retries = self.batch_connection_error_retries
        class_name = self.class_name.replace("-","_")
        class_name = _capitalize_first_letter(class_name)
        partial_failure = {'did_fail': False, 'latest_failure': None, 'number_of_failures': 0}

        if 'https' not in url:
            client = weaviate.Client(
                url=url
            )
        else:
            api_key = self.api_key
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
            callback=lambda results: self._check_batch_result(results, partial_failure),
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
                    raise WeaviateInsertionException(f"Error when adding data object to Weaviate. Error: {str(e)}")

        return len(vectors_to_store)

    def filter_conditions_to_weaviate_filter(filters: List[FilterCondition]) -> dict:
        if len(filters) > 1:
            weaviate_filter = {
                "operator":"And",
                "operands" : []
            }
            for filter in filters:
                weaviate_filter = {
                    "path":[filter.field],
                    "operator": filter.operator,
                    "valueText": filter.value
                }
                weaviate_filter["operands"].append(weaviate_filter)
        else:
            neum_filter =  filters[0]
            weaviate_filter = {
                "path":[neum_filter.field],
                "operator": neum_filter.operator,
                "valueText": neum_filter.value
            } 
        return weaviate_filter

    def search(self, vector: List[float], number_of_results: int, filters:List[FilterCondition]=[]) -> List[NeumSearchResult]:
        api_key = self.api_key
        url = self.url
        # Weaviate requires first letter to be capitalized
        class_name = self.class_name.replace("-","_")
        class_name = _capitalize_first_letter(class_name)
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
            client_query = (
                client.query
                .get(class_name=class_name, properties=full_class_schema_properties)
                .with_near_vector(content={'vector': vector})
                .with_limit(number_of_results)
                .with_additional(['id', 'certainty', 'vector'])
            )

            # Add .with_where(filter) only if filter is not empty
            if filters:
                weaviate_filter = self.filter_conditions_to_weaviate_filter(filters)
                client_query = client_query.with_where(weaviate_filter)

            # Final execution of the query
            search_result = client_query.do()

            for result in search_result["data"]["Get"][class_name]:
                # unify our api with the metadata.. or just return whatever metadata we have. (?)
                matches.append(NeumSearchResult(id=result['_additional']['id'], score=result['_additional']['certainty'], metadata= {k: v for k, v in result.items() if k != "_additional"}, vector=result['_additional']['vector']))
        except Exception as e:
            raise WeaviateQueryException(f"There was an error querying weaviate. Error {e}")
        return matches

    def info(self) -> NeumSinkInfo:
        api_key = self.api_key
        url = self.url
        
        class_name = self.class_name.replace("-","_")
        class_name = _capitalize_first_letter(class_name)
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
