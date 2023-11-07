from abc import abstractmethod, ABC, abstractproperty
from neumai.Chunkers.Chunker import Chunker
from starlette.exceptions import HTTPException
from neumai.Shared.NeumDocument import NeumDocument
from typing import List, Generator
from neumai_tools import semantic_chunking

class CustomChunker(Chunker):
    """" Custom Chunker \n
    chunker_information requires: \n
    [ code ] \n
    chunker_information optional: \n
    [ batch_size ]"""
    
    @property
    def chunker_name(self) -> str:
        return "CustomChunker"
    
    @property
    def requiredProperties(self) -> List[str]:
        return ["code"]

    @property
    def optionalProperties(self) -> List[str]:
        return ["batch_size"]

    def chunk(self, documents:List[NeumDocument]) -> Generator[List[NeumDocument], None, None]:
        
        chunking_code_exec=self.chunker_information['code']
        batch_size = self.chunker_information.get('batch_size', 1000)
        
        # Probably add some code to check the code I am about to run.
        # Code format must follow:
        # def split_text_into_chunks(text) -> List[Document]:

        # Iterate through documents to chunk them and them merge them back up
        documents_to_embed:List[NeumDocument] = []
        for doc in documents:
            chunks = semantic_chunking(documents=[doc], chunking_code_exec=chunking_code_exec)
            for i in range(len(chunks)):
                documents_to_embed.append(NeumDocument(id=doc.id + "_" + str(i), content=chunks[i].page_content, metadata=doc.metadata))
                if(len(documents_to_embed) == batch_size):
                    yield documents_to_embed
                    documents_to_embed = []
        
        # Pass last remaining
        if(len(documents_to_embed) > 0):
            yield documents_to_embed

    def validate(self) -> bool:
        return True   