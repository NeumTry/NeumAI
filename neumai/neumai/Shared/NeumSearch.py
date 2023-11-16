from abc import ABC
from .Exceptions import NeumSearchResultEmptyException

class NeumSearchResult(ABC):
    def __init__(self, id:str, metadata:dict, score:float) -> None:
        self.id =  id
        self.metadata = metadata
        self.score = score

    def as_search_result(dct:dict):
        if dct == None:
            raise NeumSearchResultEmptyException("Received empty dict when converting to as_search_result")
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