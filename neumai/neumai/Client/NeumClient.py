
from abc import abstractmethod, ABC
from typing import List, Generator
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile
from neumai.Shared.Selector import Selector
from datetime import datetime

class NeumClient(ABC):
    def __init__(self, api_key:str) -> None:
        self.api_key = api_key
