from neumai.Chunkers import (
    CharacterChunker,
    CustomChunker,
    RecursiveChunker
)    
from neumai.Chunkers.ChunkerEnum import ChunkerEnum

def as_chunker(dct:dict):
    if dct == None:
        return RecursiveChunker()
    chunker_name = str(dct.get("chunker_name", "")).replace(" ","").lower()
    chunker_information = dct.get("chunker_information", None)
    if chunker_name == ChunkerEnum.characterchunker:
        return CharacterChunker(chunker_information=chunker_information)
    elif chunker_name == ChunkerEnum.customchunker:
        return CustomChunker(chunker_information=chunker_information)
    elif chunker_name == ChunkerEnum.recursivechunker:
        return RecursiveChunker(chunker_information=chunker_information)
    else:
        return RecursiveChunker(chunker_information=chunker_information)