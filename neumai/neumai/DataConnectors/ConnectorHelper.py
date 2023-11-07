from neumai.DataConnectors.DataConnector import DataConnector
from neumai.DataConnectors import (
    S3Connector,
    NeumWebsiteConnector,
    AzureBlobConnector,
    SupabaseConnector,
    PostgresConnector,
    NeumSimpleFileConnector
)
from neumai.Shared.Selector import Selector
from starlette.exceptions import HTTPException

# Helper function to map connector configuration to object type

def as_connector(dct:dict):
    if dct == None:
        raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
    connector_name = dct.get("connector_name", None)
    connector_information = dct.get("connector_information", None)
    selector = Selector.as_selector(dct.get("selector", None))
    if connector_name == "AzureBlobConnector":
        return AzureBlobConnector(connector_information=connector_information, selector=selector)
    elif connector_name == "NeumWebsiteConnector":
        return NeumWebsiteConnector(connector_information=connector_information, selector=selector)
    elif connector_name == "S3Connector":
        return S3Connector(connector_information=connector_information, selector=selector)
    elif connector_name == "SupabaseConnector":
        return SupabaseConnector(connector_information=connector_information, selector=selector)
    elif connector_name == "PostgresConnector":
        return PostgresConnector(connector_information=connector_information, selector=selector)
    elif connector_name == "NeumSimpleFileConnector":
        return NeumSimpleFileConnector(connector_information=connector_information, selector=selector)
    return None