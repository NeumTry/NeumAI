from abc import abstractmethod, ABC
from typing import List, Generator
from neumai_tools import NeumDocument
from Sources import LocalFile
from Loaders.Loader import Loader
from neumai_tools import CSVLoader

class NeumCSVLoader(Loader):
    """" Neum Website Connector """

    @property
    def loader_name(self) -> str:
        return "NeumCSVLoader"
    
    @property
    def requiredProperties(self) -> List[str]:
        return []

    @property
    def optionalProperties(self) -> List[str]:
        return ["id_key" , "source_column" , "encoding"]
    
    @property
    def availableMetadata(self) -> List[str]:
        return ["custom"]

    @property
    def availableContent(self) -> List[str]:
        return ["custom"]

    def load(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        """Load data into Document objects."""
        source_column = self.loader_information.get('source_coulmn', None)
        encoding = self.loader_information.get('encoding', "utf-8") # modify to use encoding
        id_key = self.loader_information.get('id_key', 'id') # default to id
        selector = self.selector
        embed_keys = selector.to_embed
        metadata_keys = selector.to_metadata
        try:
            loader = CSVLoader(file_path=file.file_path, id_key=id_key, source_column=source_column, embed_keys=embed_keys, metadata_keys=metadata_keys, encoding=encoding)
            documents = loader.load()
        except UnicodeDecodeError as e:
            loader = CSVLoader(file_path=file.file_path, id_key=id_key, source_column=source_column, embed_keys=embed_keys, metadata_keys=metadata_keys, encoding="cp1252-8")
            documents = loader.load()
        for doc in documents:
            doc.metadata.update(file.metadata)
            yield doc

    def validate(self) -> bool:
        return True   