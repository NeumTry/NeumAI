from typing import List
from pydantic import BaseModel, Field

class Selector(BaseModel):
    """Selector class for specifying items to embed and metadata."""

    to_embed: List[str] = Field(default_factory=list, description="List of items to embed.")
    
    to_metadata: List[str] = Field(default_factory=list, description="List of metadata items.")