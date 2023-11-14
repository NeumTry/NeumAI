from abc import abstractmethod, ABC
from typing import List, Generator
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Loaders.Loader import Loader
from neumai.Loaders.NeumCSVLoader import NeumCSVLoader
from neumai.Loaders.NeumJSONLoader import NeumJSONLoader
from neumai.Loaders.HTMLLoader import HTMLLoader
from neumai.Loaders.MarkdownLoader import MarkdownLoader
from neumai.Loaders.PDFLoader import PDFLoader
from langchain.document_loaders import UnstructuredFileLoader

class AutoLoader(Loader):
    """ Auto Loader\n loader_information contains: [] """

    @property
    def loader_name(self) -> str:
        return "AutoLoader"
    
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

    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""
        if "csv" in file.type:
            loader = NeumCSVLoader()
        elif "string" in file.type:
            yield NeumDocument(content=file.in_mem_data, metadata=file.metadata, id=file.id)
            return
        elif "application/octet-stream" in file.type:
            loader = MarkdownLoader()
        elif "html" in file.type:
            loader = HTMLLoader()
        elif "pdf" in file.type:
            loader = PDFLoader()
        elif "json" in file.type:
            loader = NeumJSONLoader()
        else:
            loader = UnstructuredFileLoader(file_path=file.file_path)
            documents = loader.load()
            for doc in documents:
                yield NeumDocument(id=file.id, content=doc.page_content, metadata=file.metadata)
            return 
        
        yield from loader.load(file=LocalFile)
    
    def validate(self) -> bool:
        return True   