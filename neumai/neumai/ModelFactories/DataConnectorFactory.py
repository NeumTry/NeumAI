from neumai.DataConnectors import (
    AzureBlobConnector,
    DataConnector,
    FileConnector,
    WebsiteConnector,
    S3Connector,
    SharepointConnector,
    SingleStoreConnector,
    SupabaseStorageConnector,
    PostgresConnector,
)
from neumai.DataConnectors.DataConnectorEnum import DataConnectorEnum
from neumai.Shared.Exceptions import InvalidDataConnectorException

available_connectors = [enum.value for enum in list(DataConnectorEnum)]
class DataConnectorFactory:
    """Class that leverages the Factory pattern to get the appropriate data connector
    """
    def get_data_connector(data_connector_name: str, connector_information: dict) -> DataConnector:
        connector_name = data_connector_name.replace(" ","").lower()
        connector_name_enum = DataConnectorEnum.as_data_connector_enum(data_connector_name=connector_name)
        if connector_name_enum == DataConnectorEnum.azureblobconnector:
            return AzureBlobConnector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.websiteconnector:
            return WebsiteConnector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.fileconnector:
            return FileConnector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.postgresconnector:
            return PostgresConnector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.s3connector:
            return S3Connector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.sharepointconnector:
            return SharepointConnector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.singlestoreconnector:
            return SingleStoreConnector(**connector_information)
        elif connector_name_enum == DataConnectorEnum.supabasestorageconnector:
            return SupabaseStorageConnector(**connector_information)
        else:
            raise InvalidDataConnectorException(f"{connector_name} is an invalid Data Connector. Available connectors: {available_connectors}] ")
