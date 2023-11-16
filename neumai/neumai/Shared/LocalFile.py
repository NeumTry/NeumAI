from abc import ABC
from neumai.Shared.Exceptions import LocalFileEmptyException

class LocalFile(ABC):
    def __init__(self, metadata:dict, file_path:str = None, in_mem_data:dict = None, type:str = "Any", id:str = None) -> None:
        self.file_path:str = file_path
        self.metadata:dict = metadata
        self.in_mem_data:dict = in_mem_data
        self.type:str = type
        self.id:str = id

    def as_file(dct:dict):
        if dct == None:
            raise LocalFileEmptyException("Received empty dict when converting to as_file")
        return LocalFile(
            file_path=dct.get("file_path", None),
            metadata=dct.get("metadata", None),
            in_mem_data=dct.get("in_mem_data", None),
            type=dct.get("type", None),
            id=dct.get("id", None)
        )
    
    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['file_path'] = self.file_path
        json_to_return['metadata'] = self.metadata
        json_to_return['in_mem_data'] = self.in_mem_data
        json_to_return['type'] = self.type
        json_to_return['id'] = self.id
        return json_to_return
    