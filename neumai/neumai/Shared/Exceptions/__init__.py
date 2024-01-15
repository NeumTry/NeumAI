class AzureBlobConnectionException(Exception):
    """Raised if establishing a connection to Azure Blob fails"""
    pass

class CloudFileEmptyException(Exception):
    """Raised when the cloud file dictionary is empty"""
    pass

class LocalFileEmptyException(Exception):
    """Raised when the local file dictionary is empty"""
    pass

class InvalidDataConnectorException(Exception):
    """Raised when an invalid data connector is detected"""
    pass

class InvalidEmbedConnectorException(Exception):
    """Raised when an invalid embed connector is detected"""
    pass

class InvalidSinkConnectorException(Exception):
    """Raised when an invalid sink connector is detected"""
    pass

class NeumDocumentEmptyException(Exception):
    """Raised when the Neum document dictionary is empty"""
    pass

class NeumSearchResultEmptyException(Exception):
    """Raised when the Neum search result dictionary is empty"""
    pass

class NeumSinkInfoEmptyException(Exception):
    """Raised when the Neum search result dictionary is empty"""
    pass

class OpenAIConnectionException(Exception):
    """Raised if establishing a connection to OpenAI fails"""
    pass

class HuggingFaceConnectonException(Exception):
    """Raised if establishing a connection to HuggingFace fails"""
    pass

class PineconeConnectionException(Exception):
    """Raised if establishing a connection to Pinecone fails"""
    pass

class PineconeInsertionException(Exception):
    """Raised if inserting into Pinecone fails"""
    pass

class PineconeIndexInfoException(Exception):
    """Raised if getting index info from Pinecone fails"""
    pass

class PineconeQueryException(Exception):
    """Raised if querying Pinecone fails"""
    pass

class QdrantInsertionException(Exception):
    """Raised if inserting into Qdrant fails"""
    pass

class QdrantIndexInfoException(Exception):
    """Raised if getting index info from Qdrant fails"""
    pass

class QdrantQueryException(Exception):
    """Raised if querying Qdrant fails"""
    pass

class MarqoInsertionException(Exception):
    """Raised if inserting into Marqo fails"""
    pass

class MarqoIndexInfoException(Exception):
    """Raised if getting index info from Marqo fails"""
    pass

class MarqoQueryException(Exception):
    """Raised if querying Marqo fails"""
    pass

class LanceDBInsertionException(Exception):
    """Raised if inserting into LanceDB fails"""
    pass

class LanceDBIndexInfoException(Exception):
    """Raised if getting index info from LanceDB fails"""
    pass

class LanceDBQueryException(Exception):
    """Raised if querying LanceDB fails"""
    pass

class LanceDBIndexCreationException(Exception):
    """Raised when index creation fails in lanceDB"""
    pass

class PostgresConnectionException(Exception):
    """Raised if establishing a connection to a Postgres db fails"""
    pass

class S3ConnectionException(Exception):
    """Raised if establishing a connection to AWS S3 fails"""
    pass

class SharepointConnectionException(Exception):
    """Raised if establishing a connection to Sharepoint fails"""
    pass

class SinglestoreConnectionException(Exception):
    """Raised if establishing a connection to Singlestore fails"""
    pass

class SinglestoreInsertionException(Exception):
    """Raised if inserting into Singlestore fails"""
    pass

class SinglestoreIndexInfoException(Exception):
    """Raised if getting index info from Singlestore fails"""
    pass

class SinglestoreQueryException(Exception):
    """Raised if querying Singlestore fails"""
    pass

class SourceConnectorEmptyException(Exception):
    """Raised when the SourceConnector dictionary is empty"""
    pass

class SupabaseConnectionException(Exception):
    """Raised if establishing a connection to Supabase fails"""
    pass

class SupabaseInsertionException(Exception):
    """Raised if inserting into Supabase fails"""
    pass

class SupabaseIndexInfoException(Exception):
    """Raised if getting index info from Supabase fails"""
    pass

class SupabaseQueryException(Exception):
    """Raised if querying Supabase fails"""
    pass

class WeaviateConnectionException(Exception):
    """Raised if establishing a connection to Weaviate fails"""
    pass

class WeaviateInsertionException(Exception):
    """Raised if inserting into Weaviate fails"""
    pass

class WeaviateIndexInfoException(Exception):
    """Raised if getting index info from Weaviate fails"""
    pass

class WeaviateQueryException(Exception):
    """Raised if querying Weaviate fails"""
    pass

class WebsiteConnectionException(Exception):
    """Raised if establishing a connection to a website fails"""
    pass

class NeumFileException(Exception):
    """Rasied if file couldn't be opened"""
    pass

class CustomChunkerException(Exception):
    """Raised if provided code doesn't work with established format"""
    pass