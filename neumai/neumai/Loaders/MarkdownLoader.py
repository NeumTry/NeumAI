from typing import List, Generator
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Loaders.Loader import Loader
from langchain.document_loaders import UnstructuredMarkdownLoader

class MarkdownLoader(Loader):
    """ 
    Markdown Loader

    Loads Markdown files leveraging Unstructure Markdown Loader.

    Attributes:
    -----------

    None

    """

    @property
    def loader_name(self) -> str:
        return "MarkdownLoader"
    
    @property
    def required_properties(self) -> List[str]:
        return []

    @property
    def optional_properties(self) -> List[str]:
        return []
    
    @property
    def available_metadata(self) -> List[str]:
        return []

    @property
    def available_content(self) -> List[str]:
        return []

    #Probably worth re-writing directly on top of pypdf to get access
    #to more metadata including images, tables, etc.
    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""
        loader = UnstructuredMarkdownLoader(file_path=file.file_path)
        documents = loader.load()
        for doc in documents:
            yield NeumDocument(id=file.id, content=doc.page_content, metadata=file.metadata)

    def config_validation(self) -> bool:
        return True   