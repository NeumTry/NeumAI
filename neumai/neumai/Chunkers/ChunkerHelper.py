from neumai.Chunkers import (
    CharacterChunker,
    CustomChunker,
    RecursiveChunker
)    
from starlette.exceptions import HTTPException

def as_chunker(dct:dict):
    if dct == None:
        raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
    chunker_name = dct.get("chunker_name", None)
    chunker_information = dct.get("chunker_information", None)
    if chunker_name == "CharacterChunker":
        return CharacterChunker(chunker_information=chunker_information)
    elif chunker_name == "CustomChunker":
        return CustomChunker(chunker_information=chunker_information)
    elif chunker_name == "RecursiveChunker":
        return RecursiveChunker(chunker_information=chunker_information)
    return None