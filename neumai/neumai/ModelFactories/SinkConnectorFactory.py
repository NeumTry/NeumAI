from neumai.SinkConnectors import (
    PineconeSink,
    QdrantSink,
    SinkConnector,
    SingleStoreSink,
    SupabaseSink,
    WeaviateSink,
)
from neumai.SinkConnectors.SinkConnectorEnum import SinkConnectorEnum
from neumai.Shared.Exceptions import InvalidSinkConnectorException

available_sink_connectors = [enum.value for enum in list(SinkConnectorEnum)]

class SinkConnectorFactory:
    """Class that leverages the Factory pattern to get the appropriate sink connector
    """
    def get_sink(sink_name: str, sink_information: dict) -> SinkConnector:
        sink_connector_name = sink_name.replace(" ","").lower()
        sink_connector_enum = SinkConnectorEnum.as_data_connector_enum(sink_connector_name=sink_connector_name)
        if sink_connector_enum == SinkConnectorEnum.pineconesink:
            return PineconeSink(**sink_information)
        elif sink_connector_enum == SinkConnectorEnum.qdrantsink:
            return QdrantSink(**sink_information)
        elif sink_connector_enum == SinkConnectorEnum.singlestoresink:
            return SingleStoreSink(**sink_information)
        elif sink_connector_enum == SinkConnectorEnum.supabasesink:
            return SupabaseSink(**sink_information)
        elif sink_connector_enum == SinkConnectorEnum.weaviatesink:
            return WeaviateSink(**sink_information)
        else:
            raise InvalidSinkConnectorException(f"{sink_connector_name} is an invalid sink connector. Available connectors: {available_sink_connectors}]")
