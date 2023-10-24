from abc import ABC
from typing import List

class Selector(ABC):
    def __init__(self, to_embed:List[str] = [], to_metadata:List[str] = []):
        self.to_embed = to_embed
        self.to_metadata = to_metadata
    
    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['to_embed'] = self.to_embed
        json_to_return['to_metadata'] = self.to_metadata
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different han toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['to_embed'] = self.to_embed
        json_to_return['to_metadata'] = self.to_metadata
        return json_to_return

    def as_selector(dct:dict):
        if dct == None:
            return Selector(to_embed=[], to_metadata=[])
        return Selector(
            to_embed=dct.get("to_embed", []),
            to_metadata=dct.get("to_metadata", []),
        )