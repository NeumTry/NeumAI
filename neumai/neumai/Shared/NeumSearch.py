from pydantic import BaseModel, Field
from typing import List, Optional
from neumai.Shared.Exceptions import NeumSearchResultEmptyException

class NeumSearchResult(BaseModel):

    id:str = Field(..., description="Search result vector ID")
    metadata:dict = Field(...,description="Search result vector metadata")
    score:float =  Field(..., description="Search result similarity score")
    vector: Optional[List[float]] = Field(..., description="Search result vector")

    def __init__(self, id:str, metadata:dict, score:float, vector:List[float]) -> None:
        self.id =  id
        self.vector = vector
        self.metadata = metadata
        self.score = score