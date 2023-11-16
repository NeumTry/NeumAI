from neumai.SinkConnectors import (
    PineconeSink,
    WeaviateSink,
    QdrantSink,
    SingleStoreSink,
    SupabaseSink
)

from neumai.SinkConnectors.SinkConnectorEnum import SinkConnectorEnum
from neumai.Shared.Exceptions import InvalidSinkConnectorException
available_sink_connectors = [enum.value for enum in list(SinkConnectorEnum)]

def as_sink(dct:dict):
    if dct == None:
        raise InvalidSinkConnectorException("Must supply a data connector configuration")
    if not isinstance(dct, dict):
        raise InvalidSinkConnectorException("Data connector configuration needs to be a dictionary")
    sink_name = dct.get("sink_name", None)
    sink_information = dct.get("sink_information", None)
    if sink_name == SinkConnectorEnum.pineconesink:
        return PineconeSink(sink_information=sink_information)
    elif sink_name == SinkConnectorEnum.qdrantsink:
        return QdrantSink(sink_information=sink_information)
    elif sink_name == SinkConnectorEnum.singlestoresink:
        return SingleStoreSink(sink_information=sink_information)
    elif sink_name == SinkConnectorEnum.supabasesink:
        return SupabaseSink(sink_information=sink_information)
    elif sink_name == SinkConnectorEnum.weaviatesink:
        return WeaviateSink(sink_information=sink_information)
    else:
        raise InvalidSinkConnectorException(f"{sink_name} is an invalid sink connector. Available connectors: {available_sink_connectors}]")
