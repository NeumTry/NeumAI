from abc import abstractmethod, ABC
from typing import List, Generator
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from Loaders.Loader import Loader
from langchain.document_loaders import PyPDFLoader

class PDFLoader(Loader):
    """" PDF Loader """
    """" loader_information contains: """
    """ [] """

    @property
    def loader_name(self) -> str:
        return "PDFLoader"
    
    @property
    def requiredProperties(self) -> List[str]:
        return []

    @property
    def optionalProperties(self) -> List[str]:
        return []

    @property
    def availableMetadata(self) -> List[str]:
        return []

    @property
    def availableContent(self) -> List[str]:
        return []

    #Probably worth re-writing directly on top of pypdf to get access
    #to more metadata including images, tables, etc.
    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""
        loader = PyPDFLoader(file_path=file.file_path)
        documents = loader.load()
        # join the file and document metadata objects
        for doc in documents:
            doc.metadata.update(file.metadata)
            yield NeumDocument(id=file.id, content=doc.page_content, metadata=doc.metadata)
    
    def validate(self) -> bool:
        return True   