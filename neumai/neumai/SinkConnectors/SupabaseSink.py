from typing import List, Optional
from neumai.SinkConnectors.SinkConnector import SinkConnector
from neumai.Shared.NeumSinkInfo import NeumSinkInfo
from neumai.Shared.NeumVector  import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from neumai.Shared.Exceptions import(
    SupabaseConnectionException,
    SupabaseInsertionException,
    SupabaseIndexInfoException,
    SupabaseQueryException
)
from neumai.SinkConnectors.filter_utils import FilterCondition, FilterOperator
from pydantic import Field
import vecs

class SupabaseSink(SinkConnector):
    """
    Supabase Sink

    A connector designed for exporting data to Supabase, a cloud-based database platform. It manages connections and data transfers to specific Supabase databases.

    Attributes:
    -----------
    database_connection : str
        Connection string or details required to connect to the Supabase database.

    collection_name : str
        Optional name of the collection within Supabase where the data will be stored.
    """

    database_connection: str = Field(..., description="Database connection for Supabase.")

    collection_name: str = Field(..., description="Collection name.")

    @property
    def sink_name(self) -> str:
        return 'SupabaseSink'
    
    @property
    def required_properties(self) -> List[str]:
        return ['database_connection', 'collection_name']

    @property
    def optional_properties(self) -> List[str]:
        return []

    def validation(self) -> bool:
        """config_validation connector setup"""
        import vecs
        try:
            vx = vecs.create_client(self.database_connection)
        except Exception as e:
            raise SupabaseConnectionException(f"Supabase connection couldn't be initialized. See exception: {e}")
        return True 

    def delete_vectors_with_file_id(self, file_id: str) -> bool:
        database_connection = self.database_connection
        vx = vecs.create_client(database_connection)
        try:
            collection_name = self.collection_name
            db = vx.get_collection(name=collection_name)
            db.delete(filters={"_file_entry_id": {"$eq": file_id}})
        except Exception as e:
            raise Exception(f"Supabase deletion failed. Exception {e}")
        finally:
            vx.disconnect()
        return True
    
    def store(self, vectors_to_store:List[NeumVector]) -> int:
        database_connection = self.database_connection
        vx = vecs.create_client(database_connection)
        try:
            collection_name = self.collection_name
            dimensions = len(vectors_to_store[0].vector)
            db = vx.get_or_create_collection(name=collection_name, dimension=dimensions)
            to_upsert = []
            for i in range(0, len(vectors_to_store)):
                to_upsert.append((vectors_to_store[i].id, vectors_to_store[i].vector, vectors_to_store[i].metadata))

            db.upsert(records=to_upsert)
        except Exception as e:
            raise SupabaseInsertionException(f"Supabase storing failed. Exception {e}")
        finally:
            vx.disconnect()
        return len(vectors_to_store)
    
    def translate_to_supabase(filter_conditions:List[FilterCondition]):
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
                # Handle complex cases like IN, NOT IN, etc.
                pass

        return {"$and": query_parts}  # Combine using $and, can be changed to $or if needed

    def search(self, vector: List[float], number_of_results:int, filters:List[FilterCondition]=[]) -> List:
        database_connection = self.database_connection
        vx = vecs.create_client(database_connection)
        collection_name = self.collection_name
        filters_supabase = self.translate_to_supabase(filters)

        try:
            db = vx.get_collection(name=collection_name)
        except:
            raise SupabaseQueryException(f"Collection {collection_name} does not exist")
        finally:
            vx.disconnect()
        try:
            results = db.query(
                data=vector,
                include_metadata=True,
                include_value=True,
                limit=number_of_results,
                filters=filters_supabase
            )
        except Exception as e:
            raise SupabaseQueryException(f"Error querying vectors from Supabase. Exception: {e}")
        finally:
            vx.disconnect()
        matches = []
        for result in results:
            matches.append(NeumSearchResult(
                id= str(result[0]),
                metadata=result[2],
                score=result[1]
            ))
        
        return matches
    
    def info(self) -> NeumSinkInfo:
        database_connection = self.database_connection
        vx = vecs.create_client(database_connection)
        collection_name = self.collection_name
        try:
            db = vx.get_collection(name=collection_name)
        except:
            raise SupabaseIndexInfoException(f"Collection {collection_name} does not exist")
        finally:
            vx.disconnect()
        
        number_of_vectors = db.table.select('count(*)')[0].count

        return NeumSinkInfo(number_vectors_stored=number_of_vectors)