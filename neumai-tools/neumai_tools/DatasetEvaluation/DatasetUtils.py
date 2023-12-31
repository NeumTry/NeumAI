from pydantic import BaseModel, Field
from uuid import uuid4
from neumai.Shared.NeumSearch import NeumSearchResult
from typing import List, Optional

class DatasetEntry(BaseModel):

    id : str =  Field(uuid4() , description="")
    query : str = Field(... , description="")
    expected_output : str = Field(... , description="")

class DatasetResult(BaseModel):

    dataset_entry : DatasetEntry = Field(... , description="")
    raw_result : NeumSearchResult = Field(... , description="")
    score : Optional[float] = Field(None, description="")
    evaluation: Optional[dict] =  Field(None, description="")

class DatasetResults(BaseModel):
    dataset_results_id : str = Field(uuid4(), description="")
    dataset_results : List[DatasetResult] = Field([], description="")