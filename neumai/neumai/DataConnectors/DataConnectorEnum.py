from enum import Enum

class DataConnectorEnum(str, Enum):
    azureblobconnector = "azureblobconnector"
    neumfileconnector = "neumfileconnector"
    neumwebsiteconnector = "neumwebsiteconnector"
    postgresconnector = "postgresconnector"
    s3connector = "s3connector"
    sharepointconnector = "sharepointconnector"
    singlestoreconnector = "singlestoreconnector"
    supabasestorageconnector = "supabasestorageconnector"

    def as_data_connector_enum(data_connector_name: str):
        if data_connector_name == None or data_connector_name == "":
            return None
        try:
            enum_to_return = DataConnectorEnum[data_connector_name.lower()]
            return enum_to_return
        except KeyError as e:
            return None