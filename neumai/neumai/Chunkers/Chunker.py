from abc import abstractmethod, ABC
from neumai.Shared.NeumDocument import NeumDocument
from typing import List, Generator
from pydantic import BaseModel
import json
class Chunker(ABC, BaseModel):
    
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
    def config_validation(self) -> bool:
        """config_validation if the chunker is correctly configured"""

    def as_json(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['chunker_name'] = self.chunker_name
        json_to_return['chunker_information'] = json.loads(self.json())
        return json_to_return

    def config(self):
        json_to_return = {}
        json_to_return['required_properties'] = self.required_properties
        json_to_return['optional_properties'] = self.optional_properties
        return json_to_return