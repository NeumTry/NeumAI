from abc import abstractmethod, ABC
from typing import List, Generator
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from datetime import datetime

class DataConnector(ABC):
    def __init__(self, connector_information:dict = {}, selector:Selector = Selector(to_embed=[], to_metadata=[])) -> None:
        self.connector_information = connector_information
        self.selector = selector

    @property
    @abstractmethod
    def connector_name(self) -> str:
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
    def schedule_avaialable(self) -> bool:
        pass

    @property
    @abstractmethod
    def auto_sync_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def compatible_loaders(self) -> List[str]:
        pass

    @abstractmethod
    def connect_and_list_full(self) -> Generator[CloudFile, None, None]:
        """Connect to source and download file into local storage"""
    
    @abstractmethod
    def connect_and_list_delta(self, last_run:datetime) -> Generator[LocalFile, None, None]:
        """Check for changes in the source"""
        """Code to be pushed to a worker and run on a schedule"""
    
    @abstractmethod
    def connect_and_download(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        """Connect to source and download file into local storage"""

    @abstractmethod
    def validate(self) -> bool:
        """Validate if the connector is correctly configured"""

    # To do auto_sync logic.

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['connector_name'] = self.connector_name
        json_to_return['connector_information'] = self.connector_information
        json_to_return['selector'] = self.selector.toJson()
        return json_to_return
    
    def to_model(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..
        This is different than toJson, here we use it to create a model, we don't want to return the api key in the body back. Eventualyl this should be its own class...
        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['connector_name'] = self.connector_name
        json_to_return['connector_information'] = self.connector_information
        json_to_return['selector'] = self.selector.to_model()
        return json_to_return

    def config(self):
        json_to_return = {}
        json_to_return['required_properties'] = self.required_properties
        json_to_return['optional_properties'] = self.optional_properties
        json_to_return['available_metadata'] = self.available_metadata
        json_to_return['compatible_loaders'] = self.compatible_loaders
        json_to_return['schedule_avaialable'] = self.schedule_avaialable
        json_to_return['auto_sync_available'] = self.auto_sync_available
        return json_to_return