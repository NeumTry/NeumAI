from DataConnectors import AzureBlobConnector
from Pipelines import Pipeline
# a = AzureBlobConnector(connection_string="A",container_name="A")

# p = Pipeline(a,None, None)

# print(p.sources)

from pydantic import BaseModel

from typing import Optional
class User(BaseModel):
    username: Optional[str]
    email: str

dicttest = {}
# Example usage:
user2 = User(username=None, email="a")

dicttest['connector_information'] = user2.dict()

print(dicttest)