from abc import ABC
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

class NeumSinkInfo(ABC):
    def __init__(self, number_vectors_stored:int) -> None:
        self.number_vectors_stored:str = number_vectors_stored

    def as_sink_info(dct:dict):
        if dct == None:
            raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
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

class NeumSinkInfoModel(JSONResponse):
    def __init__(
        self,
        content: NeumSinkInfo,
        status_code: int = 200,
    ) -> None:
        super().__init__(content, status_code, headers=None, media_type="application/json", background=None)