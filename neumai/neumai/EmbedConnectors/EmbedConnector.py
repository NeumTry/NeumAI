from abc import ABC, abstractmethod
from typing import List, Tuple
from neumai.Shared.NeumDocument import NeumDocument
from pydantic import BaseModel
import json

class EmbedConnector(ABC, BaseModel):

    @property
    @abstractmethod
    def embed_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def required_properties(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def optional_properties(self) -> List[str]:
        pass

    @abstractmethod
    def validation(self) -> bool:
        """config_validation connector setup"""

    @abstractmethod
    def embed(self, documents:List[NeumDocument]) -> Tuple[List, dict]:
        """Generate embeddings with a given service"""
    
    @abstractmethod
    def embed_query(self, query:str) -> List[float]:
        """Generate embeddings with a given service"""

    def as_json(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['embed_name'] = self.embed_name
        json_to_return['embed_information'] = json.loads(self.json())
        return json_to_return
    
    def config(self):
        json_to_return = {}
        json_to_return['required_properties'] = self.required_properties
        json_to_return['optional_properties'] = self.optional_properties
        return json_to_return