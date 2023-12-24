from pydantic import BaseModel, Field
from typing import List, Optional
from neumai.Shared.Exceptions import NeumSearchResultEmptyException

class NeumSearchResult(BaseModel):

    id:str = Field(..., description="Search result vector ID")
    metadata:dict = Field(...,description="Search result vector metadata")
    score: Optional[float] =  Field(None, description="Search result similarity score")
    vector: Optional[List[float]] = Field(None, description="Search result vector")