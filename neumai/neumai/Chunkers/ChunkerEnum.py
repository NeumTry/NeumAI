from enum import Enum

class ChunkerEnum(str, Enum):
    characterchunker = "characterchunker"
    customchunker = "customchunker"
    recursivechunker = "recursivechunker"

    def as_chunker_enum(chunker_name: str):
        if chunker_name == None or chunker_name == "":
            return None
        try:
            enum_to_return = ChunkerEnum[chunker_name.lower()]
            return enum_to_return
        except KeyError as e:
            return None