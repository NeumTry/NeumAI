from neumai.Shared.NeumSearch import NeumSearchResult
from pydantic import BaseModel, Field
from neumai.Pipelines.Pipeline import Pipeline
from neumai_tools.PipelineCollection.PipelineCollection import PipelineCollection
from uuid import uuid4
from typing import List
import numpy as np

class DatasetEntry(BaseModel):

    id : str =  Field(uuid4() , description="")
    query : str = Field(... , description="")
    expected_output : str = Field(... , description="")

class DatasetResult(BaseModel):

    dataset_entry : DatasetEntry = Field(... , description="")
    raw_result : NeumSearchResult = Field(... , description="")
    score : float = Field(..., description="")

class DatasetResults(BaseModel):
    dataset_results_id : str = Field(uuid4(), description="")
    dataset_results : List[DatasetResult] = Field([], description="")

class Dataset(BaseModel):

    name : str = Field(... , description="")
    dataset_entries : List[DatasetEntry] = Field(... , description="")

    def run_with_pipeline(self, pipeline: Pipeline) -> DatasetResults:

        dataset_results = DatasetResults()

        for dataset_entry in self.dataset_entries:
            # Generate results
            result = pipeline.search(query=dataset_entry.query, number_of_results=1)[0]

            # Calculate score -> cosine similarity between expected output and result
            expected_output_vector = pipeline.embed.embed_query(query=dataset_entry.expected_output)
            # Need to add vector to search result. For not will just re-calculate
            result_vector = pipeline.embed.embed_query(query=result.metadata['text'])
            # Normalize the vectors to unit vectors
            expected_output_vector = expected_output_vector / np.linalg.norm(expected_output_vector)
            expected_output_vector = result_vector / np.linalg.norm(result_vector)
            # Calculate the dot product and return
            similarity = np.dot(expected_output_vector, expected_output_vector)

            dataset_result = DatasetResult(
                dataset_entry=dataset_entry, 
                raw_result=result,
                score=similarity
            )

            dataset_results.dataset_results.append(dataset_result)
        
        return dataset_results

    
    def run_with_pipeline_collection_unified(self, pipeline_collection: PipelineCollection):
        dataset_results = DatasetResults()

        for dataset_entry in self.dataset_entries:
            # Generate results
            result = pipeline_collection.search_unified(query=dataset_entry.query, number_of_results=1)[0]

            # Calculate score -> cosine similarity between expected output and result
            expected_output_vector = pipeline_collection.pipelines[0].embed.embed_query(query=dataset_entry.expected_output)
            # Need to add vector to search result. For not will just re-calculate
            result_vector = pipeline_collection.pipelines[0].embed.embed_query(query=result.metadata['text'])
            # Normalize the vectors to unit vectors
            expected_output_vector = expected_output_vector / np.linalg.norm(expected_output_vector)
            expected_output_vector = result_vector / np.linalg.norm(result_vector)
            # Calculate the dot product and return
            similarity = np.dot(expected_output_vector, expected_output_vector)

            dataset_result = DatasetResult(
                dataset_entry=dataset_entry, 
                raw_result=result,
                score=similarity
            )

            dataset_results.dataset_results.append(dataset_result)
        
        return dataset_results
    
    def run_with_pipeline_collection_separate(self, pipeline_collection: PipelineCollection):
        """"""