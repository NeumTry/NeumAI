from abc import ABC
from neumai.Shared.Exceptions import CloudFileEmptyException

class CloudFile(ABC):
    def __init__(self, metadata:dict, file_identifier:str = None, id:str = None, data:str = None, type:str = None) -> None:
        self.file_identifier:str = file_identifier
        self.data:str = data
        self.metadata:dict = metadata
        self.type:str = type
        self.id:str = id

    def as_file(dct:dict):
        if dct == None:
            raise CloudFileEmptyException("Received empty dict when converting to as_file")
        return CloudFile(
            file_identifier=dct.get("file_identifier", None),
            data=dct.get("data", None),
            metadata=dct.get("metadata", None),
            type=dct.get("type", None),
            id=dct.get("id", None)
        )
    
    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['file_identifier'] = self.file_identifier
        json_to_return['data'] = self.data
        json_to_return['metadata'] = self.metadata
        json_to_return['type'] = self.type
        json_to_return['id'] = self.id
        return json_to_return
    