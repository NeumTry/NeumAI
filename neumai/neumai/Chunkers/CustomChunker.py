from typing import List, Generator, Optional
from neumai.Chunkers.Chunker import Chunker
from neumai.Shared.NeumDocument import NeumDocument
from pydantic import Field
from neumai.Shared.Exceptions import CustomChunkerException

class CustomChunker(Chunker):
    """
    Custom Chunker for specialized text data chunking.

    This chunker is designed to handle specific chunking operations based on custom logic defined in the 'code' attribute. It allows for flexible and customized text processing, suitable for unique chunking requirements.

    Attributes:
    -----------
    code : str
        The custom code or logic required for the chunking operation. This should be a valid string representation of the chunking logic or algorithm.
    
    batch_size : Optional[int]
        The optional batch size for chunking operations. Defines the number of items to process in one batch. Default is 1000.
    """

    code: str = Field(..., description="Code required for the chunker.")

    batch_size: Optional[int] = Field(1000, description="Optional batch size for chunking.")

    @property
    def chunker_name(self) -> str:
        return "CustomChunker"

    @property
    def required_properties(self) -> List[str]:
        return ["code"]

    @property
    def optional_properties(self) -> List[str]:
        return ["batch_size"]

    def chunk(self, documents:List[NeumDocument]) -> Generator[List[NeumDocument], None, None]:
        try:
            from neumai_tools.SemanticHelpers import semantic_chunking
        except ImportError:
            raise ImportError("You must run " "`pip install neumai-tools")
        
        chunking_code_exec=self.code
        batch_size = self.batch_size
        
        # Probably add some code to check the code I am about to run.
        # Code format must follow:
        # def split_text_into_chunks(text) -> List[NeumDocument]:

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

    def config_validation(self) -> bool:
        try:
            from neumai_tools.SemanticHelpers import semantic_chunking
        except ImportError:
            raise ImportError("You must run " "`pip install neumai-tools")
        try:
            chunks = semantic_chunking(documents=[NeumDocument(id="test", content="test", metadata={})], chunking_code_exec=self.code)
        except Exception as e:
            raise CustomChunkerException(f"Connection to Sharepoint failed, check credentials. See Exception: {e}")   
        return True   