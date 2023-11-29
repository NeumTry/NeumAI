from typing import List, Generator, Optional
from neumai.Chunkers.Chunker import Chunker
from neumai.Shared.NeumDocument import NeumDocument
from langchain.text_splitter import (CharacterTextSplitter)
from pydantic import Field

class CharacterChunker(Chunker):
    """
    Character Chunker

    Chunk text data based on the number of characters. This chunker is designed to break down text into manageable pieces based on character count, making it suitable for processing large texts or for use in systems that require fixed-size input.

    Attributes:
    -----------

    chunk_size : Optional[int]
        The size of each chunk in terms of the number of characters. Default is 500 characters.

    chunk_overlap : Optional[int]
        The number of characters that will overlap between consecutive chunks. Default is 0, meaning no overlap.

    batch_size : Optional[int]
        The size of the batch for processing chunks. Specifies how many chunks are processed together. Default is 1000.

    separator : Optional[str]
        The separator to be used between chunks. Default is a double newline ("\n\n").
    """
    

    chunk_size: Optional[int] = Field(default=500, description="Optional chunk size.")

    chunk_overlap: Optional[int] = Field(default=0, description="Optional chunk overlap.")

    batch_size: Optional[int] = Field(default=1000, description="Optional batch size for processing.")

    separator: Optional[str] = Field(default="\n\n", description="Optional separator for chunking.")

    @property
    def chunker_name(self) -> str:
        return "CharacterChunker"

    @property
    def required_properties(self) -> List[str]:
        return []

    @property
    def optional_properties(self) -> List[str]:
        return ["chunk_size", "chunk_overlap", "batch_size", "separator"]

    def chunk(self, documents:List[NeumDocument]) -> Generator[List[NeumDocument], None, None]:

        batch_size = self.batch_size

        text_splitter = CharacterTextSplitter(
            separator = self.separator,
            chunk_size = self.chunk_size,
            chunk_overlap  = self.chunk_overlap,
            length_function = len,
        )
        
        # Iterate through documents to chunk them and them merge them back up
        documents_to_embed:List[NeumDocument] = []
        for doc in documents:
            chunks = text_splitter.split_text(doc.content)
            for i in range(len(chunks)):
                documents_to_embed.append(NeumDocument(id=doc.id + "_" + str(i), content=chunks[i], metadata=doc.metadata))
                if(len(documents_to_embed) == batch_size):
                    yield documents_to_embed
                    documents_to_embed = []

        # Pass last remaining
        if(len(documents_to_embed) > 0):
            yield documents_to_embed

    def config_validation(self) -> bool:
        return True   