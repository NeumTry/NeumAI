from neumai.DataConnectors import (
    AzureBlobConnector,
    NeumFileConnector,
    NeumWebsiteConnector,
    S3Connector,
    SharepointConnector,
    SingleStoreConnector,
    SupabaseStorageConnector,
    PostgresConnector,
)
from neumai.DataConnectors.DataConnectorEnum import DataConnectorEnum
from neumai.Shared.Selector import Selector
from neumai.Shared.Exceptions import InvalidDataConnectorException

available_connectors = [enum.value for enum in list(DataConnectorEnum)]

def as_connector(dct:dict):
    if dct == None:
        raise InvalidDataConnectorException("Must supply a data connector configuration")
    if not isinstance(dct, dict):
        raise InvalidDataConnectorException("Data connector configuration needs to be a dictionary")
    
    connector_name = str(dct.get("connector_name", "")).replace(" ","").lower()
    connector_name_enum = DataConnectorEnum.as_data_connector_enum(data_connector_name=connector_name)
    connector_information = dct.get("connector_information", None)
    selector = Selector.as_selector(dct.get("selector", None))

    if connector_name_enum == DataConnectorEnum.azureblobconnector:
        return AzureBlobConnector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.neumwebsiteconnector:
        return NeumWebsiteConnector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.neumfileconnector:
        return NeumFileConnector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.postgresconnector:
        return PostgresConnector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.s3connector:
        return S3Connector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.sharepointconnector:
        return SharepointConnector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.singlestoreconnector:
        return SingleStoreConnector(connector_information=connector_information, selector=selector)
    elif connector_name_enum == DataConnectorEnum.supabasestorageconnector:
        return SupabaseStorageConnector(connector_information=connector_information, selector=selector)
    else:
        raise InvalidDataConnectorException(f"{connector_name} is an invalid Data Connector. Available connectors: {available_connectors}] ")
