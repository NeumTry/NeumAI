from .PipelineRun import PipelineRun
from .TriggerSchedule import TriggerSchedule
from neumai.Sinks.SinkConnector import SinkConnector
from neumai.Embeds.EmbedConnector import EmbedConnector
from neumai.Sources.SourceConnector import SourceConnector
from neumai.Embeds.EmbedHelper import as_embed
from neumai.Sinks.SinkHelper import as_sink
from neumai.Shared.NeumVector import NeumVector
from neumai.Shared.NeumSearch import NeumSearchResult
from typing import List
import uuid

accepted_trigger_sync_types: List = []
class Pipeline(object):
    def __init__(self, 
                source:  List[SourceConnector], # Change to only support a list of Sources for V2
                embed: EmbedConnector, 
                sink: SinkConnector, 
                name:str = None,
                id: str = None, 
                created: float = None, 
                updated: float = None,
                trigger_schedule: TriggerSchedule = None, 
                latest_run: PipelineRun = None, 
                owner: str = None, 
                is_deleted: bool = False):
        self.id = id
        self.name = name
        self.created = created
        self.updated = updated
        self.source = source
        self.embed = embed
        self.sink = sink
        self.trigger_schedule = trigger_schedule
        self.latest_run = latest_run 
        self.owner = owner
        self.is_deleted = is_deleted

    def validate(self) -> bool:
        """Running validation for each connector"""
        try:
            for source in self.source:
                source.validation()
            self.embed.validation()
            self.sink.validation()
        except Exception as e:
            raise e
        
    def runPipeline(self) -> int:
        # This method is meant for local development only. Not to be used in production.
        # The Neum AI framework provides parallelization constructs through yielding
        # These should be used to run pipelines at scale.

        total_vectors_stored = 0
        for source in self.source:
            for cloudFile in source.list_files_full():
                for localFile in source.download_files(cloudFile=cloudFile):
                    for document in source.load_data(file=localFile):
                        for chunks in source.chunk_data(document=document):
                            embeddings, embeddings_info = self.embed.embed(documents=chunks)
                            vectors_to_store = [NeumVector(id=str(uuid.uuid4()), vector=vector, metadata=document.metadata) for vector in embeddings]
                            total_vectors_stored += self.sink.store(vectors_to_store=vectors_to_store, pipeline_id=pipeline.id)

        return total_vectors_stored
    
    def searchPipeline(self, query:str, number_of_results:int) -> List[NeumSearchResult]:
        vector_for_query = self.embed.embed_query(query=query)
        matches =  self.sink.search(vector=vector_for_query, number_of_results=number_of_results, pipeline_id=self.id)
        return matches

    def toPipelineModel(self):
        content_to_return = {}
        content_to_return['id'] = self.id
        content_to_return['name'] = self.name
        content = []
        for source in self.source:
            content.append(source.to_model())
        content_to_return['source'] = content
        content_to_return['embed'] = self.embed.to_model()
        content_to_return['sink'] = self.sink.to_model()
        content_to_return['created'] = self.created
        content_to_return['updated'] = self.updated
        if self.trigger_schedule == None:
            content_to_return['trigger_schedule'] = None
        else:
            content_to_return['trigger_schedule'] = self.trigger_schedule.to_model()

        content_to_return['latest_run'] = self.latest_run.toJson()
        content_to_return['available_metadata'] = self.available_metadata()

        return content_to_return
    
    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['id'] = self.id
        json_to_return['name'] = self.name
        json_source = []
        for source in self.source:
            json_source.append(source.toJson())
        json_to_return['source'] = json_source
        json_to_return['embed'] = self.embed.toJson()
        json_to_return['sink'] = self.sink.toJson()
        json_to_return['owner'] = self.owner
        json_to_return['created'] = self.created
        json_to_return['updated'] = self.updated
        json_to_return['is_deleted'] = self.is_deleted

        if self.trigger_schedule == None:
            json_to_return['trigger_schedule'] = None
        else:
            json_to_return['trigger_schedule'] = self.trigger_schedule.toJson()

        json_to_return['latest_run'] = self.latest_run.toJson()
        json_to_return['available_metadata'] = self.available_metadata()
        return json_to_return

    def as_request(self):
        json_body = {}
        json_source = []
        for source in self.source:
            json_source.append(source.toJson())
        json_body['source'] = json_source
        json_body['embed'] = self.embed.toJson()
        json_body['sink'] = self.sink.toJson()
        return json_body

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
        for source in self.source:
            available_metadata += source.customMetadata.keys()
            available_metadata += source.connector.selector.to_metadata
            available_metadata += source.loader.selector.to_metadata
        return available_metadata

    def as_pipeline(dct:dict):
        if dct == None:
            return None
        
        source = dct.get("source")
        source_value = []
        for s in source:
            source_value.append(SourceConnector.as_source_connector(s))
        return Pipeline(
            name=dct.get("name", None),
            id=dct.get("id", None),
            source=source_value,
            embed = as_embed(dct.get("embed")),
            sink = as_sink(dct.get("sink")),
            trigger_schedule=TriggerSchedule.as_trigger_schedule(dct.get("trigger_schedule", None)),
            latest_run=PipelineRun.as_pipeline_run(dct.get("latest_run", None)),
            created=dct.get("created", None),
            updated=dct.get("updated", None),
            owner=dct.get("owner", None),
            is_deleted=dct.get("is_deleted", False)
        )