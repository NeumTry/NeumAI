from neumai.Chunkers import (
    Chunker,
    CharacterChunker,
    CustomChunker,
    RecursiveChunker
)    
from neumai.Chunkers.ChunkerEnum import ChunkerEnum

class ChunkerFactory:
    """Class that leverages the Factory pattern to get the appropriate chunker
    """
    def get_chunker(chunker_name: str, chunker_information: dict) -> Chunker:
        if chunker_information == None:
            return RecursiveChunker()
        chunker_name_enum:ChunkerEnum = ChunkerEnum.as_chunker_enum(chunker_name)
        if chunker_name_enum == ChunkerEnum.characterchunker:
            return CharacterChunker(**chunker_information)
        elif chunker_name_enum == ChunkerEnum.customchunker:
            return CustomChunker(**chunker_information)
        elif chunker_name_enum == ChunkerEnum.recursivechunker:
            return RecursiveChunker(**chunker_information)
        else:
            return RecursiveChunker(**chunker_information)