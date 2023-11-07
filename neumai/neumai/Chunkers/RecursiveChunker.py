from neumai.Chunkers.Chunker import Chunker
from neumai.Shared.NeumDocument import NeumDocument
from typing import List, Generator
from langchain.text_splitter import (RecursiveCharacterTextSplitter)

class RecursiveChunker(Chunker):
    """Recursive Chunker \n
    chunker_information optional: \n
    [chunk_size, chunk_overlap, batch_size]"""
    
    @property
    def chunker_name(self) -> str:
        return "RecursiveChunker"
    
    @property
    def requiredProperties(self) -> List[str]:
        return []

    @property
    def optionalProperties(self) -> List[str]:
        return ["chunk_size" , "chunk_overlap" , "batch_size", "separators"]

    def chunk(self, documents:List[NeumDocument]) -> Generator[List[NeumDocument], None, None]:
        
        batch_size = self.chunker_information.get('batch_size', 1000)

        text_splitter = RecursiveCharacterTextSplitter(
            separators = self.chunker_information.get('separators', ["\n\n", "\n", " ", ""]),
            chunk_size = self.chunker_information.get('chunk_size', 500),
            chunk_overlap  = self.chunker_information.get('chunk_overlap', 0),
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
    
    def validate(self) -> bool:
        return True   