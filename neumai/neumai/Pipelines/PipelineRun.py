from typing import Any, Optional
from .TriggerSyncTypeEnum import TriggerSyncTypeEnum
from pydantic import BaseModel

class PipelineRunTaskDetails(BaseModel):

    completed_embedding_tasks: int
    completed_storing_tasks: int
    failed_embedding_tasks: int
    failed_storing_tasks: int

    def toJson(self):
        json_to_return = {}
        json_to_return['completed_embedding_tasks'] = self.completed_embedding_tasks
        json_to_return['completed_storing_tasks'] = self.completed_storing_tasks
        json_to_return['failed_embedding_tasks'] = self.failed_embedding_tasks
        json_to_return['failed_storing_tasks'] = self.failed_storing_tasks

        return json_to_return
    
    def as_pipeline_run_task_details(task_details: dict):
        if task_details == None:
            return None
        return PipelineRunStatus(
            completed_embedding_tasks=task_details.get("completed_embedding_tasks", None),
            completed_storing_tasks=task_details.get("completed_storing_tasks", None),
            failed_embedding_tasks=task_details.get("failed_embedding_tasks", None),
            failed_storing_tasks=task_details.get("failed_storing_tasks", None),
        )
    
class PipelineRunStatus(BaseModel):
    status: str
    message: Optional[str] = None
    exception_detail: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.status = self.status.lower()
    
    def as_pipeline_run_status(detailed_status: dict):
        if detailed_status == None:
            return PipelineRunStatus(status="Unknown",message="Something went wrong in our end, please email kevin@tryneum.com and we will get you unblocked")
        return PipelineRunStatus(
            status=detailed_status.get("status", None),
            message=detailed_status.get("message", None),
            exception_detail=detailed_status.get("exception_detail", None),
        )
    
class PipelineRun(BaseModel):
    id: str
    created: float
    pipeline_id: str
    trigger_type: str
    sync_type: TriggerSyncTypeEnum
    detailed_status: Optional[PipelineRunStatus] = None
    vectors_written: int = 0
    task_details: Optional[PipelineRunTaskDetails] = None
    last_updated: Optional[float] = None
    number_of_documents: Optional[int] = None
    finished_distributing: bool = False
    processing_time: Optional[float] = None
                                                 
    def set_id(self, id: str):
        self.id = id

    def set_number_of_documents(self, number_of_documents):
        self.number_of_documents = number_of_documents
    
    def set_finished_distributing(self, finished_distributing):
        self.finished_distributing = finished_distributing

    def set_detailed_status(self, detailed_status: PipelineRunStatus):
        self.detailed_status = detailed_status
    
    def set_pipeline_id(self, pipeline_id: str):
        self.pipeline_id = pipeline_id

    def set_created(self, created: float):
        self.created = created

    def set_processing_time(self, processing_time: float):
        self.processing_time = processing_time
    
    def as_pipeline_run(dct:dict):
        if dct == None:
            return PipelineRun(id=None, created=None, pipeline_id = None, trigger_type=None, sync_type=None, detailed_status=None, vectors_written=None, number_of_documents=None, finished_distributing=None)
        return PipelineRun(
            id=dct.get("id", None),
            pipeline_id=dct.get("pipeline_id"),
            created=dct.get("created", None),
            trigger_type=dct.get("trigger_type", None),
            sync_type=TriggerSyncTypeEnum.as_trigger_sync_type(trigger_sync_type=dct.get("sync_type", None)),
            detailed_status=PipelineRunStatus.as_pipeline_run_status(detailed_status=dct.get("detailed_status", None)),
            vectors_written=dct.get("vectors_written", None),
            task_details=PipelineRunTaskDetails.as_pipeline_run_task_details(dct.get("task_details", None)),
            last_updated=dct.get("last_updated", None),
            number_of_documents=dct.get("number_of_documents",None),
            finished_distributing=dct.get("finished_distributing",None),# we could do something like in distributed tasks where we store the state of the DAG in the pipeline run object.. for now just doing finished_distributing
            processing_time=dct.get("processing_time", None)
        )