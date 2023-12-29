from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    LanceDBInsertionException,
    LanceDBIndexInfoException,
    LanceDBQueryException
)
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List, Optional
from pydantic import Field

import lancedb
from lancedb import DBConnection


class LanceDBSink(SinkConnector):

    """
    LanceDB sink

    A sink connector for LanceDB, designed to facilitate data output into a 
    LanceDB storage system. For details about LanceDB, refer to 
    https://github.com/lancedb/lancedb.


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
        a vector index will be created for searching instead of a brute-force
        knn search.


    Example usage:
        ldb = LanceDBSink(uri="data/test_ldb_sink", table_name="demo_ldb_table")
        ldb.store(neum_vectors)
        ldb.search(query)
    """

    uri: str = Field(..., description="URI for LanceDB database")
    api_key: Optional[str] = Field(default=None, description="API key for LanceDB cloud")
    region: Optional[str] = Field(default=None, description="Region for use of LanceDB cloud")
    table_name: str = Field(..., description="Name of LanceDB table to use")
    create_index: bool = Field(
        default=False, 
        description="Boolean to decide whether to create an index or perform a flat search")

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
    

    def search(self, vector: List[float], 
               number_of_results: int, filter: dict = {}) -> List[NeumSearchResult]:

        db = self._get_db_connection()
        tbl = db.open_table(self.table_name)

        if self.create_index:
            # Some config options are there, need to figure 
            # out how to input them
            # For more details, refer to docs
            # - https://lancedb.github.io/lancedb/python/python/#lancedb.table.Table.create_index
            tbl.create_index(metric="cosine", replace=True)

        try:
            search_results = tbl.search(query=vector)
            for k,v in filter.items():
                search_results = search_results.where(f"{k} = {v}")
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