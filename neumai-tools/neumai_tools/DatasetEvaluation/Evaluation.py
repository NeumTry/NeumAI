from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from neumai.Pipelines.Pipeline import Pipeline
from .DatasetUtils import DatasetResult, DatasetEntry
from neumai.Shared.NeumSearch import NeumSearchResult
import numpy as np
import json
import re

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

class LLMEvaluation(Evaluation):

    def evaluate(self) -> DatasetResult:
        system_prompt = """
        Evaluate the following questions and pieces of context. 

        Question: Was ketchup originally a type of medicine?
        Expected output: Yes, in the 1830's ketchup was sold as a medicine.
        Actual output: Ketchup was sold in the 1830s as medicine. In 1834, it was sold as a cure for an upset stomach by an Ohio physician named John Cook. It wasn't popularized as a condiment until the late 19th century!
        Evaluation: {
            "relevant_context": true,
            "all_context_present": true
        }

        Question: Where did the shortest war in history happen?
        Expected output: The war took place in Zanzibar.
        Actual output: The shortest war in history lasted 38 minutes! It was between Britain and Zanzibar and is known as the Anglo-Zanzibar War. This war occurred on August 27, 1896. It was over the ascension of the next Sultan in Zanzibar and resulted in a British victory.
        Evaluation: {
            "relevant_context": true,
            "all_context_present": false
        }

        Question: What animals did Roman's have as pets?
        Expected output: Ferrets, dogs and monkeys were the most popular pets in the Roman Empire.
        Actual output: Roman's didn't have cats as pets.
        Evaluation: {
            "relevant_context": false,
            "all_context_present": false
        }
        """


        user_prompt = """Question: {question}
        Expected output: {expected_output}
        Actual output: {actual_output}
        Evaluation:
        """

        generated_user_prompt = user_prompt.format(
            question=self.dataset_entry.query,
            expected_output = self.dataset_entry.expected_output,
            actual_output = self.result_output.metadata['text']
        )
        
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role":"user",
                    "content":generated_user_prompt
                }
            ],
            temperature=1,
        )
        
        match = re.search(r'\{.*?\}', response.choices[0].message.content, re.DOTALL)

        if match:
            json_object = match.group()
            # Now, json_object contains the JSON string.
            # To convert it to a Python dictionary, use json.loads if it's a valid JSON
            try:
                evaluation = json.loads(json_object)
                # data is now a Python dictionary representing your JSON object
            except json.JSONDecodeError:
                print("The extracted string is not a valid JSON.")
                evaluation = None
        else:
            print("No JSON object found in the string.")
            evaluation = None

        return DatasetResult(
            dataset_entry=self.dataset_entry,
            raw_result=self.result_output,
            evaluation=evaluation
        )