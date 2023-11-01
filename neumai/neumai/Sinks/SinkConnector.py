from starlette.exceptions import HTTPException
from typing import List, Union, Tuple
from Shared.NeumVector import NeumVector
from abc import ABC, abstractmethod

# Eventually this is an abstract class where specific implementations of it implement from it.
# Like, PineconeConnector which extends/implements from SinkConnector
class SinkConnector(ABC):
    def __init__(self, sink_information: dict):
        self.sink_information = sink_information
    
    @property
    @abstractmethod
    def sink_name(self) -> str:
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
        """Validate sink setup"""

    @abstractmethod
    def store(self, pipeline_id: str, vectors_to_store:List[NeumVector], task_id:str = "") -> int:
        """Store vectors with a given service"""

    @abstractmethod
    def search(self, vector:List[float], number_of_results:int, pipeline_id:str) -> List:
        """Search vectors for a given service"""

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['sink_name'] = self.sink_name
        json_to_return['sink_information'] = self.sink_information
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different han toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['sink_name'] = self.sink_name
        json_to_return['sink_information'] = self.sink_information
        return json_to_return

    def config(self):
        return {
            "requiredProperties":self.requiredProperties,
            "optionalProperties":self.optionalProperties,
        }