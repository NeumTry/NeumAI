from abc import abstractmethod, ABC
from typing import List, Generator
from Shared.NeumDocument import NeumDocument
from Shared.LocalFile import LocalFile
from Shared.Selector import Selector

class Loader(ABC):
    def __init__(self, loader_information:dict = {}, selector:Selector = Selector(to_embed=[], to_metadata=[])) -> None:
        self.loader_information = loader_information
        self.selector = selector
    
    @property
    @abstractmethod
    def loader_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def required_properties(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def optional_properties(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def available_metadata(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def availableContent(self) -> List[str]:
        pass

    @abstractmethod
    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the loader is correctly configured"""

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['loader_name'] = self.loader_name
        json_to_return['loader_information'] = self.loader_information
        json_to_return['selector'] = self.selector.toJson()
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different than toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['loader_name'] = self.loader_name
        json_to_return['loader_information'] = self.loader_information
        json_to_return['selector'] = self.selector.to_model()
        return json_to_return

    def config(self):
        json_to_return = {}
        json_to_return['required_properties'] = self.required_properties
        json_to_return['optional_properties'] = self.optional_properties
        json_to_return['available_metadata'] = self.available_metadata
        json_to_return['availableContent'] = self.availableContent
        return json_to_return