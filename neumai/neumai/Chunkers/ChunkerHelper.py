from neumai.Chunkers import (
    CharacterChunker,
    CustomChunker,
    RecursiveChunker
)    
from starlette.exceptions import HTTPException

def as_chunker(dct:dict):
    chunker_name = dct.get("chunker_name", None)
    chunker_information = dct.get("chunker_information", None)
    if chunker_name == "CharacterChunker":
        return CharacterChunker(chunker_information=chunker_information)
    elif chunker_name == "CustomChunker":
        return CustomChunker(chunker_information=chunker_information)
    elif chunker_name == "RecursiveChunker":
        return RecursiveChunker(chunker_information=chunker_information)
    else:
        return RecursiveChunker(chunker_information=chunker_information)