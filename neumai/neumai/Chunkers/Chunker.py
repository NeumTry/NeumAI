from abc import abstractmethod, ABC
from neumai.Shared.NeumDocument import NeumDocument
from typing import List, Generator

class Chunker(ABC):
    def __init__(self, chunker_information:dict = {}) -> None:
        self.chunker_information = chunker_information
    
    @property
    @abstractmethod
    def chunker_name(self) -> str:
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
    def chunk(self, documents:List[NeumDocument]) -> Generator[List[NeumDocument], None, None]:
        """Chunk documents into more documents"""

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the chunker is correctly configured"""

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['chunker_name'] = self.chunker_name
        json_to_return['chunker_information'] = self.chunker_information
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different han toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['chunker_name'] = self.chunker_name
        json_to_return['chunker_information'] = self.chunker_information
        return json_to_return

    def config(self):
        json_to_return = {}
        json_to_return['required_properties'] = self.required_properties
        json_to_return['optional_properties'] = self.optional_properties
        return json_to_return