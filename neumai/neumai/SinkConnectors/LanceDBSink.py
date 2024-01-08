from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    LanceDBInsertionException,
    LanceDBIndexInfoException,
    LanceDBIndexCreationException,
    LanceDBQueryException
)
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List, Optional
from neumai.SinkConnectors.filter_utils import FilterCondition
from pydantic import Field

import lancedb
from lancedb import DBConnection


class LanceDBSink(SinkConnector):

    """
    LanceDB sink

    A sink connector for LanceDB, designed to facilitate data output into a 
    LanceDB storage system. For details about LanceDB, refer to 
    https://github.com/lancedb/lancedb.

    LanceDB supports flat search as well as ANN search.
    For indexing, read here - https://lancedb.github.io/lancedb/ann_indexes/#creating-an-ivf_pq-index

    Attributes:
    -----------
    uri: str
        URI for LanceDB database.
    api_key: str
        If presented, connect to LanceDB cloud. 
        Otherwise, connect to a database on file system or cloud storage.
    region: str
        Region for use of LanceDB cloud.
    table_name: str
        Name of LanceDB table to use
    create_index: bool
        LanceDB offers flat search as well as ANN search. If set to True,
        a vector index would be created for searching instead of a 
        brute-force knn search.
    metric: str
        The distance metric to use. By default it uses euclidean distance 'L2'. 
        It also supports 'cosine' and 'dot' distance as well. Needs to be set if create_index is True.
    num_partitions: int
        The number of partitions of the index. 
        Needs to be set if create_index is True. And needs to be altered as per data size.
    num_sub_vectors: int
        The number of sub-vectors (M) that will be created during 
        Product Quantization (PQ). For D dimensional vector, it will be divided into 
        M of D/M sub-vectors, each of which is presented by a single PQ code.
    accelerator: str
        The accelerator to use for the index creation process. Supports GPU and MPS.


    Example usage:
        ldb = LanceDBSink(uri="data/test_ldb_sink", table_name="demo_ldb_table")
        ldb.store(neum_vectors)
        ldb.search(query)
    """

    uri: str = Field(..., description="URI for LanceDB database")
    api_key: Optional[str] = Field(default=None, description="API key for LanceDB cloud")
    region: Optional[str] = Field(default=None, description="Region for use of LanceDB cloud")
    table_name: str = Field(..., description="Name of LanceDB table to use")
    create_index: bool = Field(default=False, description="Boolean to create index or use flat search")
    metric: str = Field(default="cosine", description="The distance metric to use in the index")
    num_partitions: int = Field(default=256, description="The number of partitions of the index")
    num_sub_vectors: int = Field(default=96, description="The number of sub-vectors (M) that will be created during Product Quantization (PQ)")
    accelerator: str = Field(default=None, description="Specify to cuda or mps (on Apple Silicon) to enable GPU training.")

    # Check API reference for more details
    # - https://lancedb.github.io/lancedb/python/python/#lancedb.connect
    # db: DBConnection = lancedb.connect(uri=uri, api_key=api_key, region=region)

    @property
    def sink_name(self) -> str:
        return "LanceDBSink"
    
    @property
    def required_properties(self) -> List[str]:
        return ['uri', 'api_key', 'table_name']
    
    @property
    def optional_properties(self) -> List[str]:
        return []
    
    def validation(self) -> bool:
        """config_validation connector setup"""
        db = lancedb.connect(uri=self.uri, api_key=self.api_key, region=self.region)
        return True 
    
    def _get_db_connection(self) -> DBConnection:
        return lancedb.connect(uri=self.uri, api_key=self.api_key, region=self.region)

    def store(self, vectors_to_store: List[NeumVector]) -> int:
        db = self._get_db_connection()
        table_name = self.table_name

        data = []
        for vec in vectors_to_store:
            dic = {
                'id': vec.id,
                'vector': vec.vector,
            }
            for k,v in vec.metadata.items():
                dic[k] = v
            data.append(dic)

        tbl = db.create_table(table_name, data=data, mode="overwrite")
        if tbl:
            return len(tbl.to_pandas())
        raise LanceDBInsertionException("LanceDB storing failed. Try later")
    

    def search(self, vector: List[float], number_of_results: int, filters: List[FilterCondition] = []) -> List[NeumSearchResult]:

        db = self._get_db_connection()
        tbl = db.open_table(self.table_name)

        if self.create_index:
            # For more details, refer to docs
            # - https://lancedb.github.io/lancedb/python/python/#lancedb.table.Table.create_index
            try:
                tbl.create_index(
                    metric=self.metric, 
                    num_partitions=self.num_partitions,
                    num_sub_vectors=self.num_sub_vectors,
                    accelerator=self.accelerator,
                    replace=True)
            except Exception as e:
                raise LanceDBIndexCreationException(f"LanceDB index creation failed. \nException - {e}")

        try:
            search_results = tbl.search(query=vector)
            for filter in filters:
                search_results = search_results.where(f"{filter.field} {filter.operator.value} {filter.value}")
            search_results = search_results.limit(number_of_results).to_pandas()

        except Exception as e:
            raise LanceDBQueryException(f"Failed to query LanceDB. Exception - {e}")

        matches = []
        cols = search_results.columns

        for i in range(len(search_results)):
            _id = search_results.iloc[i]['id']
            _vec = list(search_results.iloc[i]['vector'])
            matches.append(
                NeumSearchResult(
                    id=_id,
                    vector=_vec,
                    metadata={k:search_results.iloc[i][k] for k in cols if k not in ['id', 'vector', '_distance']},
                    score=1-search_results.iloc[i]['_distance']
                )
            )
        return matches
    

    def get_representative_vector(self) -> list:
        db = self._get_db_connection()
        tbl = db.open_table(self.table_name)
        return list(tbl.to_pandas()['vector'].mean())
    
    
    def info(self) -> NeumSinkInfo:
        try:
            db = self._get_db_connection()
            tbl = db.open_table(self.table_name)
            return(NeumSinkInfo(number_vectors_stored=len(tbl)))
        except Exception as e:
            raise LanceDBIndexInfoException(f"Failed to get information from LanceDB. Exception - {e}")
        

    def delete_vectors_with_file_id(self, file_id: str) -> bool:
        db = self._get_db_connection()
        table_name = self.table_name

        tbl = db.open_table(table_name)
        try:
            tbl.delete(where=f"id = '{file_id}'")
        except:
            raise Exception("LanceDB deletion by file id failed.")
        return True