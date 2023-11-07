from abc import ABC
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from typing import List

class NeumSearchResult(ABC):
    def __init__(self, id:str, metadata:dict, score:float) -> None:
        self.id =  id
        self.metadata = metadata
        self.score = score

    def as_search_result(dct:dict):
        if dct == None:
            raise HTTPException(status_code=500, detail="Value dct must be a dictionary")
        
        return NeumSearchResult(
            id=dct.get("id", None),
            metadata=dct.get("metadata", None),
            score=dct.get("score", None),
        )
    
    def toJson(self) -> dict:
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['id'] = self.id
        json_to_return['metadata'] = self.metadata
        json_to_return['score'] = self.score
        return json_to_return

class NeumSearchResultModel(JSONResponse):
    def __init__(
        self,
        content: List[NeumSearchResult],
        status_code: int = 200,
    ) -> None:
        super().__init__(content, status_code, headers=None, media_type="application/json", background=None)