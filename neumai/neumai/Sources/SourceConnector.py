from typing import List, Generator, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from neumai.DataConnectors.DataConnector import DataConnector
from neumai.Chunkers.Chunker import Chunker
from neumai.Chunkers.RecursiveChunker import RecursiveChunker
from neumai.Loaders.Loader import Loader
from neumai.Loaders.AutoLoader import AutoLoader
from neumai.ModelFactories import ChunkerFactory, DataConnectorFactory, LoaderFactory
from neumai.Shared.NeumDocument import NeumDocument
from neumai.Shared.LocalFile import LocalFile
from neumai.Shared.CloudFile import CloudFile

# Assuming DataConnector, Chunker, RecursiveChunker, Loader, and AutoLoader are defined elsewhere
class SourceConnector(BaseModel):
    """
    Source Connector

    This class acts as a constructor for source connectors, encompassing various components like data connectors, chunkers, and loaders. It facilitates the initial stages of data processing by managing the connection to data sources, breaking down content, and loading data for further processing.

    Attributes:
    -----------
    data_connector : DataConnector
        A connector to the data source. This component is responsible for establishing and managing the connection to the source of the data.

    chunker : Chunker
        The chunker to be used for breaking down the content. It determines how the data is segmented for processing. Default is set to RecursiveChunker, which recursively breaks down the content based on specified rules.

    loader : Loader
        The loader responsible for loading data from files or specific data types. It handles the retrieval and initial processing of data from its source. Default is set to AutoLoader, which automatically determines the appropriate method for loading data.

    custom_metadata : Dict
        A dictionary for custom metadata that can be added to the vector. This allows for the inclusion of additional, user-defined information in the data processing pipeline.
    """

    data_connector: DataConnector = Field(..., description="Connector to data source")

    chunker: Chunker = Field(default=RecursiveChunker(), description="Chunker to be used to break down content")

    loader: Loader = Field(default=AutoLoader(), description="Loader to load data from file / data type")

    custom_metadata: Optional[Dict] = Field(default_factory=dict, description="Custom metadata to be added to the vector")

    def list_files_full(self) -> Generator[CloudFile, None, None]:
        yield from self.data_connector.connect_and_list_full()

    def list_files_delta(self, last_run:datetime) -> Generator[CloudFile, None, None]:
        yield from self.data_connector.connect_and_list_delta(last_run=last_run)

    def download_files(self, cloudFile:CloudFile) -> Generator[LocalFile, None, None]:
        yield from self.data_connector.connect_and_download(cloudFile=cloudFile)

    def load_data(self, file:LocalFile) -> Generator[NeumDocument, None, None]:
        yield from self.loader.load(file=file)

    def chunk_data(self, document:NeumDocument) -> Generator[List[NeumDocument], None, None]:
        for chunk_set in self.chunker.chunk(documents=[document]):
            chunk_set_with_custom_metadata = [NeumDocument(id=chunk.id, content=chunk.content, metadata={**chunk.metadata, **self.custom_metadata, **{"text":chunk.content}}) for chunk in chunk_set]
            yield chunk_set_with_custom_metadata
    
    def validation(self) -> bool:
        core_validation = self.data_connector.config_validation() and self.loader.config_validation() and self.chunker.config_validation()
        loader_validation = self.loader.loader_name in self.data_connector.compatible_loaders
        return core_validation and loader_validation

    @validator("data_connector", pre=True, always=True)
    def deserialize_data_connector(cls, value):
        if isinstance(value, dict):
            return DataConnectorFactory.get_data_connector(value.get("connector_name"), value.get("connector_information"))
        return value
    
    @validator("chunker", pre=True, always=True)
    def deserialize_chunker(cls, value):
        if isinstance(value, dict):
            return ChunkerFactory.get_chunker(value.get("chunker_name"), value.get("chunker_information"))
        return value
        
    @validator("loader", pre=True, always=True)
    def deserialize_loader(cls, value):
        if isinstance(value, dict):
            return LoaderFactory.get_loader(value.get("loader_name"), value.get("loader_information"))
        return value
    
    def as_json(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API..

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['custom_metadata'] = self.custom_metadata
        json_to_return['data_connector'] = self.data_connector.as_json()
        json_to_return['chunker'] = self.chunker.as_json()
        json_to_return['loader'] = self.loader.as_json()
        return json_to_return
