from abc import abstractmethod, ABC
from typing import List, Generator
from Shared.NeumDocument import NeumDocument
from Shared.LocalFile import LocalFile
from Loaders.Loader import Loader
from neumai_tools import JSONLoader

class NeumJSONLoader(Loader):
    """" Neum Website Connector """

    @property
    def requiredProperties(self) -> List[str]:
        return []

    @property
    def optionalProperties(self) -> List[str]:
        return ["id_key"]

    @property
    def loader_name(self) -> str:
        return "NeumJSONLoader"
    
    @property
    def availableMetadata(self) -> List[str]:
        return ["custom"]

    @property
    def availableContent(self) -> List[str]:
        return ["custom"]

    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""
        id_key = self.loader_information.get('id_key', "id")
        if file.file_path != None:
            loader = JSONLoader(file_path=file.file_path, id_key=id_key, selector=self.selector)
        elif file.in_mem_data != None:
            loader = JSONLoader(file_data=file.in_mem_data, id_key=id_key, selector=self.selector)
        
        documents = loader.load()
        # join the file and document metadata objects
        for doc in documents:
            doc.metadata.update(file.metadata)
            yield doc

    def validate(self) -> bool:
        return True   