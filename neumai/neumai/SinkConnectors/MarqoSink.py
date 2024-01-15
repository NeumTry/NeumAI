from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    MarqoInsertionException,
    MarqoIndexInfoException,
    MarqoQueryException
)
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List, Union, Any
from pydantic import Field
import marqo
from neumai.SinkConnectors.filter_utils import (
    FilterCondition, 
    FilterOperator, 
    dict_to_filter_condition,
)


class MarqoSink(SinkConnector):
    """
    Marqo Sink

    A sink connector for Marqo, designed to facilitate data output into a Marqo storage system.

    Attributes:
    -----------
    url : str
        URL for accessing the Marqo service.

    api_key : str
        API key required for authenticating with the Marqo service.

    index_name : str
        Name of the index in Marqo where the data will be stored.
    """

    url: str = Field(..., description="URL for Marqo.")

    api_key: str = Field(default=None, description="API key for Marqo.")

    index_name: str = Field(..., description="Index name.")

    @property
    def sink_name(self) -> str:
        return 'MarqoSink'
    
    @property
    def required_properties(self) -> List[str]:
        return ['url', 'api_key', 'index_name']

    @property
    def optional_properties(self) -> List[str]:
        return []

    def validation(self) -> bool:
        """config_validation connector setup"""
        marqo_client = marqo.Client(url=self.url, api_key=self.api_key)
        return True 
    
    def _create_index(
        self,
        index_name: str,
        marqo_client,
        embedding_dim,
        similarity: str = 'cosinesimil',
        recreate_index: bool = True,
        ):
        '''
        Create a new index
        :similarity: similarity function, it should be one of l1, l2, linf and cosinesimil
        '''
        if recreate_index:
            if index_name in [i.index_name for i in marqo_client.get_indexes()['results']]:
                marqo_client.delete_index(index_name)

        if not index_name:
            raise Exception('Index name must not be none')

        if similarity not in ['cosinesimil', 'l1', 'l2', 'linf']:
            raise Exception('Similarity function must be one of l1, l2, linf and cosinesimil')

        if index_name in [i.index_name for i in marqo_client.get_indexes()['results']] and recreate_index==False:
            raise Exception(f'Index {index_name} already exists, please use another name')

        # Not using any model, providing own vectors
        # https://docs.marqo.ai/1.4.0/API-Reference/Indexes/create_index/#no-model
        marqo_client.create_index(
        index_name=index_name,
        settings_dict={
                    'index_defaults': {
                        'model': 'no_model',
                        'model_properties': {
                            'dimensions': embedding_dim
                        },
                        'ann_parameters':{
                            'space_type': similarity
                        }
                    }
                }
        )


    def store(self, vectors_to_store:List[NeumVector]) -> int:
        url = self.url
        api_key = self.api_key
        index_name = self.index_name

        marqo_client = marqo.Client(
            url=url, 
            api_key=api_key,
        )
        self._create_index(index_name=index_name,
                          marqo_client=marqo_client,
                          similarity="cosinesimil",
                          embedding_dim=len(vectors_to_store[0].vector))
        mod_vecs = []
        for vec in vectors_to_store:
            _id = vec.id
            _vec = vec.vector
            dic = {
                    '_id': _id,
                    'neum': {
                        'vector': _vec
                    }
                }
            # Using the two lines below, we can unroll the elements in metadata
            # and add them separately
            for k,v in vec.metadata.items():
                dic[k] = v
            # dic['metadata'] = vec.metadata
            mod_vecs.append(
                dic
            )
        operation_info = marqo_client.index(index_name).add_documents(
            documents=mod_vecs,
            mappings={
                'neum': 
                    {
                    'type': 'custom_vector'
                    }
            },
            tensor_fields=['neum'],
            auto_refresh=True
            )
        
        if(operation_info['errors'] == False):
            return  len(operation_info['items'])
        raise MarqoInsertionException("Marqo storing failed. Try again later.")
    

    def _get_marqo_filter(self, column: str, value: Any, operator: FilterOperator) -> str:
        """A function to convert filters/conditions marqo DSL filter.

        Args:
            column (str): The field name to filter on(in terms of marqo)
            value (Any): The value of the field name to process on
            operator (FilterOperator): The filter operator to apply so as to filter

        Raises:
            Exception: Exception for operator not supported

        Returns:
            str: The marqo DSL filter string
        """
        if operator==FilterOperator.EQUAL.value:
            return f"{column}:{value} AND "
        elif operator==FilterOperator.LESS_THAN.value:
            return f"{column}:[* TO {value-1}] AND "
        elif operator==FilterOperator.LESS_THAN_OR_EQUAL.value:
            return f"{column}:[* TO {value}] AND "
        elif operator==FilterOperator.GREATER_THAN.value:
            return f"{column}:[{value+1} TO *] AND "
        elif operator==FilterOperator.GREATER_THAN_OR_EQUAL.value:
            return f"{column}:[{value} TO *] AND "
        else:
            raise Exception(f"Operator {operator} is currently not supported")
    

    def _get_filter_string_from_filter_condition(self, filter_conditions:List[FilterCondition]):

        _filter_string = ""
        for condition in filter_conditions:
            field = condition.field
            operator = condition.operator

            _filter_string+=self._get_marqo_filter(
                column=field, value=condition.value, operator=operator.value)
                
        if _filter_string.endswith(" AND "):
            _filter_string = _filter_string.rstrip(" AND ")
        return _filter_string
    

    def search(self, vector: List[float], number_of_results: int, filters: List[FilterCondition] = []) -> List:
        url = self.url
        api_key = self.api_key
        index_name = self.index_name
        filter_string = self._get_filter_string_from_filter_condition(filter_conditions=filters)
        
        try:
            marqo_client = marqo.Client(
                url=url, 
                api_key=api_key,
            )
            search_result = marqo_client.index(index_name).search(
                context={
                    'tensor':[{'vector': vector, 'weight' : 1}]
                },
                limit=number_of_results,
                filter_string=filter_string if filter_string else None
            )
        except Exception as e:
            raise MarqoQueryException(f"Failed to query Marqo. Exception - {e}")
        
        matches = []
        for result in search_result['hits']:
            matches.append(
                NeumSearchResult(
                    id=result['_id'],
                    metadata={k:result[k] for k in list(result.keys()) if k not in ['_id', '_score']},
                    score=result['_score']
                )
            )
        return matches

    
    def _get_embeddings_from_ids(self, ids):
        marqo_client = marqo.Client(
            url=self.url, 
            api_key=self.api_key,
        )
        embeddings = []
        for i in ids:
            doc = marqo_client.index(self.index_name).get_document(
                document_id=i,
                expose_facets=True)
            tensor = doc['_tensor_facets'][0]['_embedding']
            embeddings.append(tensor)
        return embeddings
    
    def get_representative_vector(self) -> list:
        """
        This methods calculates the representative vector for a 
        particular index (collection of vectors). Currently, this 
        is simply using the mean of all the vectors in the index.

        Returns:
            list: Returns the representative vector as a list of floats
        """
        import numpy as np

        marqo_client = marqo.Client(
            url=self.url, 
            api_key=self.api_key,
        )

        # In Neum, we have one vector per document for marqo, so max number of vectors
        # would be same as number of documents
        max_results = marqo_client.index(self.index_name).get_stats()['numberOfDocuments']

        vector_dimension = marqo_client.index(
            self.index_name
            ).get_settings()['index_defaults']['model_properties']['dimensions']
        
        dummy_vector = [1.0 for _ in range(vector_dimension)]
        ids = [i.id for i in self.search(
            vector=dummy_vector, number_of_results=max_results)]
        embeddings = self._get_embeddings_from_ids(ids)

        return list(np.mean(embeddings, 0))

    
    def info(self) -> NeumSinkInfo:
        url = self.url
        api_key = self.api_key
        index_name = self.index_name

        try:
            marqo_client = marqo.Client(
                url=url, 
                api_key=api_key,
            )
            index_stats = marqo_client.index(index_name).get_stats()
            return(NeumSinkInfo(number_vectors_stored=index_stats['numberOfVectors']))
        except Exception as e:
            raise MarqoIndexInfoException(f"Failed to get information from Marqo. Exception - {e}")
    
    def delete_vectors_with_file_id(self, file_id: str) -> bool:
        marqo_client = marqo.Client(url=self.url, api_key=self.api_key)
        deletion_info = marqo_client.index(self.index_name).delete_documents(ids=[file_id])
        if not deletion_info:
            raise Exception("Marqo doesn't have support to delete vectors by metadata")
        return True