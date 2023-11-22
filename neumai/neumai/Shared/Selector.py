from typing import List
from pydantic import BaseModel, Field

class Selector(BaseModel):
    """
    Selector class for specifying items to embed and metadata.

    This class is used to define specific criteria for data processing, particularly for selecting what items should be embedded and what should be stored as metadata.

    Attributes:
    -----------
    to_embed : List[str]
        List of items to embed, specified by their identifiers or names.

    to_metadata : List[str]
        List of metadata items to include, specified by their identifiers or names.
    """

    to_embed: List[str] = Field(default_factory=list, description="List of items to embed.")
    
    to_metadata: List[str] = Field(default_factory=list, description="List of metadata items.")