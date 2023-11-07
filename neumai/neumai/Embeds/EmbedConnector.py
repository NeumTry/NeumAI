from starlette.exceptions import HTTPException
from abc import ABC, abstractmethod
from typing import List, Tuple
from Shared.NeumDocument import NeumDocument

class EmbedConnector(ABC):
    def __init__(self, embed_information: dict = {}):
        self.embed_information = embed_information

    @property
    @abstractmethod
    def embed_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def requiredProperties(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def optionalProperties(self) -> List[str]:
        pass

    @abstractmethod
    def validation(self) -> bool:
        """Validate connector setup"""

    @abstractmethod
    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with a given service"""
    
    @abstractmethod
    def embed_query(self, query:str) -> List[float]:
        """Generate embeddings with a given service"""

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['embed_name'] = self.embed_name
        json_to_return['embed_information'] = self.embed_information
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different han toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['embed_name'] = self.embed_name
        json_to_return['embed_information'] = self.embed_information
        return json_to_return
    
    def config(self):
        json_to_return = {}
        json_to_return['requiredProperties'] = self.requiredProperties
        json_to_return['optionalProperties'] = self.optionalProperties
        return json_to_return