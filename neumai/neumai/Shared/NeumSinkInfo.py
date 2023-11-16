from abc import ABC
from neumai.Shared.Exceptions import NeumSinkInfoEmptyException

class NeumSinkInfo(ABC):
    def __init__(self, number_vectors_stored:int) -> None:
        self.number_vectors_stored:str = number_vectors_stored

    def as_sink_info(dct:dict):
        if dct == None:
            raise NeumSinkInfoEmptyException("Received empty dict when converting to as_sink_info")
        return NeumSinkInfo(
            number_vectors_stored=dct.get("number_vectors_stored", None),
        )
    
    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['number_vectors_stored'] = self.number_vectors_stored
        return json_to_return