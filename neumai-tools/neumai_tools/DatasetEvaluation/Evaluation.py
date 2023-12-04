from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from neumai.Pipelines.Pipeline import Pipeline
from .DatasetUtils import DatasetResult, DatasetEntry
from neumai.Shared.NeumSearch import NeumSearchResult
import numpy as np

class Evaluation(BaseModel, ABC):
    pipeline: Pipeline = Field(...,description="")
    dataset_entry: DatasetEntry = Field(...,description="Dataset entry for evaluation")
    result_output: NeumSearchResult = Field(..., description="Actual result for retrieval")

    @abstractmethod
    def evaluate(self) -> DatasetResult:
        """Method that runs evaluation and generates results"""

class CosineEvaluation(Evaluation):

    def evaluate(self) -> DatasetResult:
        # Calculate score -> cosine similarity between expected output and result

        # Calculate vectors for both outputs
        expected_output_vector = self.pipeline.embed.embed_query(query=self.dataset_entry.expected_output)
        result_vector = self.pipeline.embed.embed_query(query=self.result_output.metadata['text'])

        # Normalize the vectors to unit vectors
        expected_output_vector_norm = expected_output_vector / np.linalg.norm(expected_output_vector)
        result_vector_norm = result_vector / np.linalg.norm(result_vector)

        # Calculate the dot product and return
        similarity = np.dot(expected_output_vector_norm, result_vector_norm)

        dataset_result = DatasetResult(
            dataset_entry=self.dataset_entry, 
            raw_result=self.result_output,
            score=similarity
        )

        return dataset_result