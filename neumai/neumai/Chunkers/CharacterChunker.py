from typing import List, Generator, Optional
from neumai.Chunkers.Chunker import Chunker
from neumai.Shared.NeumDocument import NeumDocument
from langchain.text_splitter import (CharacterTextSplitter)
from pydantic import Field

class CharacterChunker(Chunker):
    """Character Chunker."""

    chunk_size: Optional[int] = Field(500, description="Optional chunk size.")

    chunk_overlap: Optional[int] = Field(0, description="Optional chunk overlap.")

    batch_size: Optional[int] = Field(1000, description="Optional batch size for processing.")

    separator: Optional[str] = Field("\n\n", description="Optional separator for chunking.")

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
            separators = self.separator,
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