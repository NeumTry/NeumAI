from pydantic import BaseModel, Field
from neumai.Pipelines.Pipeline import Pipeline
from neumai_tools.PipelineCollection.PipelineCollection import PipelineCollection
from .Evaluation import Evaluation, CosineEvaluation
from .DatasetUtils import DatasetEntry, DatasetResult, DatasetResults
from uuid import uuid4
from typing import List, Type
import numpy as np

class Dataset(BaseModel):

    name : str = Field(... , description="")
    dataset_entries : List[DatasetEntry] = Field(... , description="")
    evaluation_type: Type[Evaluation] = Field(...,description="Evaluation type for results.")

    def run_with_pipeline(self, pipeline: Pipeline) -> DatasetResults:

        dataset_results = DatasetResults()

        for dataset_entry in self.dataset_entries:
            # Generate results
            result_output = pipeline.search(query=dataset_entry.query, number_of_results=1)[0]

            dataset_result = self.evaluation_type(pipeline=pipeline, dataset_entry=dataset_entry, result_output=result_output).evaluate()

            dataset_results.dataset_results.append(dataset_result)
        
        return dataset_results

    
    def run_with_pipeline_collection_unified(self, pipeline_collection: PipelineCollection):
        dataset_results = DatasetResults()

        for dataset_entry in self.dataset_entries:
            # Generate results
            result_output = pipeline_collection.search_unified(query=dataset_entry.query, number_of_results=1)[0]

            dataset_result = self.evaluation_type(pipeline=pipeline_collection.pipelines[0], dataset_entry=dataset_entry, result_output=result_output).evaluate()

            dataset_results.dataset_results.append(dataset_result)
        
        return dataset_results
    
    def run_with_pipeline_collection_separate(self, pipeline_collection: PipelineCollection):
        dataset_results_separate: dict[str,DatasetResults] = {}
        for pipeline in pipeline_collection.pipelines:
            dataset_results = DatasetResults()

            for dataset_entry in self.dataset_entries:
                # Generate results
                result_output = pipeline.search(query=dataset_entry.query, number_of_results=1)[0]
                
                dataset_result = self.evaluation_type(pipeline=pipeline, dataset_entry=dataset_entry, result_output=result_output).evaluate()

                dataset_results.dataset_results.append(dataset_result)

            dataset_results_separate[pipeline.id] = dataset_results
            
        return dataset_results_separate