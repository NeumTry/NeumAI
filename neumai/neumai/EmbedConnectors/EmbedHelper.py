from neumai.EmbedConnectors import (
    OpenAIEmbed,
    ReplicateEmbed,
    AzureOpenAIEmbed
)

from neumai.EmbedConnectors.EmbedConnectorEnum import EmbedConnectorEnum
from neumai.Shared.Exceptions import InvalidEmbedConnectorException

available_embed_connectors = [enum.value for enum in list(EmbedConnectorEnum)]

def as_embed(dct:dict):
    if dct == None:
        raise InvalidEmbedConnectorException("Must supply an embed connector configuration")
    if not isinstance(dct, dict):
        raise InvalidEmbedConnectorException("Embed connector configuration needs to be a dictionary")
    
    embed_connector_name = dct.get("embed_name", None)
    embed_connector_enum = EmbedConnectorEnum.as_embed_connector_enum(embed_connector_name=embed_connector_name)
    embed_information = dct.get("embed_information", None)
    if embed_connector_enum == EmbedConnectorEnum.azureopenaiembed:
        return AzureOpenAIEmbed(embed_information=embed_information)
    elif embed_connector_enum == EmbedConnectorEnum.openaiembed:
        return OpenAIEmbed(embed_information=embed_information)
    elif embed_connector_enum == EmbedConnectorEnum.replicateembed:
        return ReplicateEmbed(embed_information=embed_information)
    else:
        raise InvalidEmbedConnectorException(f"{embed_connector_name} is an invalid embed connector. Available connectors: {available_embed_connectors}] ")