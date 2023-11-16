from enum import Enum

class EmbedConnectorEnum(str, Enum):
    openaiembed = "openaiembed"
    azureopenaiembed = "azureopenaiembed"
    replicateembed = "replicateembed"

    def as_embed_connector_enum(embed_connector_name: str):
        if embed_connector_name == None or embed_connector_name == "":
            return None
        try:
            enum_to_return = EmbedConnectorEnum[embed_connector_name.lower()]
            return enum_to_return
        except KeyError as e:
            return None