from abc import abstractmethod, ABC
from typing import List, Generator
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.Selector import Selector
from pydantic import BaseModel
import json

class Loader(ABC, BaseModel):    
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
    def available_content(self) -> List[str]:
        pass

    @abstractmethod
    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""

    @abstractmethod
    def config_validation(self) -> bool:
        """config_validation if the loader is correctly configured"""

    def as_json(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['loader_name'] = self.loader_name
        json_to_return['loader_information'] = json.loads(self.json())
        return json_to_return

    def config(self):
        json_to_return = {}
        json_to_return['required_properties'] = self.required_properties
        json_to_return['optional_properties'] = self.optional_properties
        json_to_return['available_metadata'] = self.available_metadata
        json_to_return['available_content'] = self.available_content
        return json_to_return