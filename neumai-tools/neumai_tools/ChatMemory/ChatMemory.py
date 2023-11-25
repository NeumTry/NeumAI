from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.NeumVector import NeumVector
from pydantic import BaseModel, Field
from neumai.SinkConnectors.SinkConnector import SinkConnector
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

class Message(BaseModel):
    id : str = Field(default_factory=uuid4(), description="Identifier for message")
    role : str = Field(..., description="Role of user sending the message")
    content : str = Field(..., description="Content of message")
    timestamp : Optional[datetime] = Field(datetime.now(), description="Content of message")

class ChatMemory(BaseModel):

    embed : EmbedConnector = Field(..., description="Embedding model to generate vector embeddings")
    sink : SinkConnector = Field(..., description="Vector store for chat messages")

    def store_messages(self, messages:List[Message]) -> int:
        documents = [NeumDocument(id=message.id, content=message.content, metadata={"content":message.content, "role":message.role, "timestamps": message.timestamp.isoformat()}) for message in messages]
        embeddings, embeddings_info = self.embed.embed(documents=documents)
        vectors_to_store = [NeumVector(id=documents[i].id, vector=embeddings[i], metadata=documents[i].metadata) for i in range(0,len(embeddings))]
        total_vectors_stored = self.sink.store(vectors_to_store=vectors_to_store, pipeline_id=self.id)
    
    def search_messages(self, query:str, number_of_messages:int = 3) -> List[Message]:
    # We have some gaps in metadata support to accomplish this
    # Fast fix is to simply create a new class / collection / namespace for each session
        query_embedding =  self.embed.embed_query(query=query)
        search_results = self.sink.search(vector=query_embedding, number_of_results=number_of_messages, pipeline_id="")
        return [Message(id=result.id, role=result.metadata['role'], content=result.metadata['content'], timestamp=datetime.fromisoformat(result.metadata['timestamp'])) for result in search_results]
