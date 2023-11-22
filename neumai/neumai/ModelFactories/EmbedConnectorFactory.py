from neumai.EmbedConnectors import (
    EmbedConnector,
    OpenAIEmbed,
    ReplicateEmbed,
    AzureOpenAIEmbed
)

from neumai.EmbedConnectors.EmbedConnectorEnum import EmbedConnectorEnum
from neumai.Shared.Exceptions import InvalidEmbedConnectorException


available_embed_connectors = [enum.value for enum in list(EmbedConnectorEnum)]

class EmbedConnectorFactory:
    """Class that leverages the Factory pattern to get the appropriate embed connector
    """
    def get_embed(embed_name: str, embed_information: dict) ->EmbedConnector:
        embed_connector_name = embed_name.replace(" ","").lower()
        embed_connector_enum = EmbedConnectorEnum.as_embed_connector_enum(embed_connector_name=embed_connector_name)
        if embed_connector_enum == EmbedConnectorEnum.azureopenaiembed:
            return AzureOpenAIEmbed(**embed_information)
        elif embed_connector_enum == EmbedConnectorEnum.openaiembed:
            return OpenAIEmbed(**embed_information)
        elif embed_connector_enum == EmbedConnectorEnum.replicateembed:
            return ReplicateEmbed(**embed_information)
        else:
            raise InvalidEmbedConnectorException(f"{embed_connector_name} is an invalid embed connector. Available connectors: {available_embed_connectors}] ")