"""Main API controller"""  
from datetime import datetime, timezone
from fastapi import FastAPI, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from neumai.Pipelines import Pipeline, PipelineRun, PipelineRunModel, TriggerSyncTypeEnum, PipelineRunStatus

app = FastAPI(name=__name__)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/v2/pipelines', summary="Create and run a pipeline")
def create_and_run_pipeline(pipeline_request: dict, response: Response):
    pipeline_id = str(uuid4())
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    created_timestamp: float = utc_time.timestamp()
    pipeline: Pipeline = Pipeline.as_pipeline(pipeline_request)
    pipeline.set_id(pipeline_id)

    # Validate Pipeline config
    try:
        pipeline.validate()
    except Exception as e:
        return Response(f"Validation failed. Issue: {e}", status_code=400)
    
    # Run Pipeline
    vectors_stored = pipeline.runPipeline()

    # Optionally store the pipeline config...
    pipeline_run =  PipelineRunModel(content=PipelineRun(
        id=uuid4(), 
        created=created_timestamp,
        pipeline_id=pipeline_id,
        trigger_type="async",
        sync_type=TriggerSyncTypeEnum.full,
        detailed_status=PipelineRunStatus(
            status="completed"
        ),
        vectors_written=vectors_stored,
    ), status_code=200)

    return pipeline_run