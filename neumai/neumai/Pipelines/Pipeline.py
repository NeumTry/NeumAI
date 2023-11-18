from .PipelineRun import PipelineRun
from .TriggerSchedule import TriggerSchedule
from neumai.SinkConnectors.SinkConnector import SinkConnector
from neumai.EmbedConnectors.EmbedConnector import EmbedConnector
from neumai.Sources.SourceConnector import SourceConnector
from neumai.Shared.NeumVector import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

class Pipeline(BaseModel):
    """Pipeline managing the flow of data from sources through embedding to the sink, including configurations and state."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the pipeline")

    name: Optional[str] = Field(None, description="Name of the pipeline")

    created: Optional[float] = Field(None, description="Timestamp of when the pipeline was created")

    updated: Optional[float] = Field(None, description="Timestamp of when the pipeline was last updated")

    sources: List[SourceConnector] = Field(..., description="List of source connectors involved in the pipeline")

    embed: EmbedConnector = Field(..., description="Embedding connector for data processing")

    sink: SinkConnector = Field(..., description="Sink connector for final data output")

    trigger_schedule: Optional[TriggerSchedule] = Field(None, description="Scheduling details for triggering the pipeline")

    latest_run: Optional[PipelineRun] = Field(None, description="Information about the latest run of the pipeline")

    owner: Optional[str] = Field(None, description="Owner of the pipeline")
    
    is_deleted: bool = Field(False, description="Flag to indicate if the pipeline is marked as deleted")

    def set_id(self, id: str):
        self.id = id
    
    def set_created(self, created: float):
        self.created = created

    def set_updated(self, updated: float):
        self.updated = updated

    def set_latest_run(self, pipeline_run: PipelineRun):
        self.latest_run = pipeline_run

    def set_owner(self, owner: str):
        self.owner = owner
    
    def available_metadata(self) -> List[str]:
        available_metadata = []
        for source in self.sources:
            available_metadata += source.custom_metadata.keys()
        # Check if data_connector exists and has a selector
        if hasattr(source.data_connector, 'selector') and source.data_connector.selector:
            available_metadata += source.data_connector.selector.to_metadata

        # Check if loader exists and has a selector
        if hasattr(source.loader, 'selector') and source.loader.selector:
            available_metadata += source.loader.selector.to_metadata
        return available_metadata

    def config_validation(self) -> bool:
        """Running validation for each connector"""
        try:
            for source in self.sources:
                source.validation()
            self.embed.validation()
            self.sink.validation()
            return True
        except Exception as e:
            raise e
        
    def run(self) -> int:
        # This method is meant for local development only. Not to be used in production.
        # The Neum AI framework provides parallelization constructs through yielding
        # These should be used to run pipelines at scale.
        try:
            self.config_validation()
        except Exception as e:
            raise e
        
        try:
            total_vectors_stored = 0
            for source in self.sources:
                for cloudFile in source.list_files_full():
                    for localFile in source.download_files(cloudFile=cloudFile):
                        for document in source.load_data(file=localFile):
                            for chunks in source.chunk_data(document=document):
                                embeddings, embeddings_info = self.embed.embed(documents=chunks)
                                vectors_to_store = [NeumVector(id=str(uuid4()), vector=embeddings[i], metadata=chunks[i].metadata) for i in range(0,len(embeddings))]
                                total_vectors_stored += self.sink.store(vectors_to_store=vectors_to_store, pipeline_id=self.id)
            return total_vectors_stored
        except Exception as e:
            raise e
    
    def search(self, query:str, number_of_results:int) -> List[NeumSearchResult]:
        vector_for_query = self.embed.embed_query(query=query)
        matches =  self.sink.search(vector=vector_for_query, number_of_results=number_of_results, pipeline_id=self.id)
        return matches

    def as_pipeline_model(self):
        content_to_return = {}
        content_to_return['id'] = self.id
        content_to_return['name'] = self.name
        content = []
        for source in self.sources:
            content.append(source.as_json())
        content_to_return['sources'] = content
        content_to_return['embed'] = self.embed.as_json()
        content_to_return['sink'] = self.sink.as_json()
        content_to_return['created'] = self.created
        content_to_return['updated'] = self.updated
        if self.trigger_schedule == None:
            content_to_return['trigger_schedule'] = None
        else:
            content_to_return['trigger_schedule'] = self.trigger_schedule.json()

        content_to_return['latest_run'] = self.latest_run.json()
        content_to_return['available_metadata'] = self.available_metadata()

        return content_to_return

    def as_json(self):
        json_body = {}
        json_source = []
        for source in self.sources:
            json_source.append(source.as_json())
        json_body['sources'] = json_source
        json_body['embed'] = self.embed.as_json()
        json_body['sink'] = self.sink.as_json()
        return json_body