from abc import abstractmethod, ABC
from langchain.docstore.document import Document
from typing import List, Generator

class Chunker(ABC):
    def __init__(self, chunker_information:dict) -> None:
        self.chunker_information = chunker_information
    
    @property
    @abstractmethod
    def chunker_name(self) -> str:
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
    def chunk(self, documents:List[Document]) -> Generator[List[Document], None, None]:
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
        return {
            "requiredProperties":self.requiredProperties,
            "optionalProperties":self.optionalProperties,
        }