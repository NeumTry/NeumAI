from abc import ABC
from starlette.exceptions import HTTPException

class NeumDocument(ABC):
    def __init__(self, id:str, content:str, metadata:dict) -> None:
        self.id:str = id
        self.content:str = content
        self.metadata:dict = metadata

    def as_file(dct:dict):
        if dct == None:
            raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
        return NeumDocument(
            content=dct.get("content", None),
            metadata=dct.get("metadata", None),
            id=dct.get("id", None),
        )
    
    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['content'] = self.content
        json_to_return['metadata'] = self.metadata
        json_to_return['id'] = self.id
        return json_to_return
    