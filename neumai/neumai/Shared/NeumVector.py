from abc import ABC
from typing import List

class NeumVector(ABC):
    def __init__(self, id:str, vector:List[float], metadata:dict) -> None:
        self.id:str = id
        self.vector:List[float] = vector
        self.metadata:dict = metadata