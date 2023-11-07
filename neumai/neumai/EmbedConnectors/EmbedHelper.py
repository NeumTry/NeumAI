from neumai.EmbedConnectors import (
    OpenAIEmbed,
    ReplicateEmbed,
    AzureOpenAIEmbed
)
from starlette.exceptions import HTTPException

def as_embed(dct:dict):
    if dct == None:
        raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
    embed_name = dct.get("embed_name", None)
    embed_information = dct.get("embed_information", None)
    if embed_name == "OpenAIEmbed":
        return OpenAIEmbed(embed_information=embed_information)
    elif embed_name == "ReplicateEmbed":
        return ReplicateEmbed(embed_information=embed_information)
    elif embed_name == "AzureOpenAIEmbed":
        return AzureOpenAIEmbed(embed_information=embed_information)
    return None