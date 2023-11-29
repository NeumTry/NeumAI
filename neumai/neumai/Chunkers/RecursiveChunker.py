from typing import List, Generator, Optional
from neumai.Chunkers.Chunker import Chunker
from neumai.Shared.NeumDocument import NeumDocument
from langchain.text_splitter import (RecursiveCharacterTextSplitter)
from pydantic import Field

class RecursiveChunker(Chunker):

    """
    Recursive Chunker for multi-level text data chunking.

    This chunker is designed to perform text chunking recursively using a variety of specified separators. It's useful for complex chunking tasks where multiple layers of chunking are necessary.

    Attributes:
    -----------
    chunk_size : Optional[int]
        The optional chunk size, defining the maximum size of each chunk. Default is 500 characters.
    
    chunk_overlap : Optional[int]
        The optional chunk overlap size, specifying how much overlap there should be between consecutive chunks. Default is 0 (no overlap).

    batch_size : Optional[int]
        The optional batch size for processing chunks. Defines the number of chunks to process in one batch. Default is 1000.

    separators : Optional[List[str]]
        A list of optional separators to be used for recursive chunking. Each separator defines a new level of chunking. Default separators include newline and space characters.
    """

    chunk_size: Optional[int] = Field(default=500, description="Optional chunk size.")

    chunk_overlap: Optional[int] = Field(default=0, description="Optional chunk overlap.")

    batch_size: Optional[int] = Field(default=1000, description="Optional batch size for processing.")

    separators: Optional[List[str]] = Field(["\n\n", "\n", " ", ""], description="Optional list of separators for chunking.")

    @property
    def chunker_name(self) -> str:
        return "RecursiveChunker"

    @property
    def required_properties(self) -> List[str]:
        return []

    @property
    def optional_properties(self) -> List[str]:
        return ["chunk_size", "chunk_overlap", "batch_size", "separators"]


    def chunk(self, documents:List[NeumDocument]) -> Generator[List[NeumDocument], None, None]:
        
        batch_size = self.batch_size

        text_splitter = RecursiveCharacterTextSplitter(
            separators = self.separators,
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