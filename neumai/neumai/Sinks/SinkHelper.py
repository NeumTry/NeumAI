from Sinks import (
    PineconeSink,
    WeaviateSink,
    QdrantSink,
    SingleStoreSink,
    SupabaseSink
)
from Sinks.SinkConnector import SinkConnector
from Shared.Selector import Selector
from starlette.exceptions import HTTPException

def as_sink(dct:dict):
    if dct == None:
        raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
    sink_name = dct.get("sink_name", None)
    sink_information = dct.get("sink_information", None)
    if sink_name == "PineconeSink":
        return PineconeSink(sink_information=sink_information)
    elif sink_name == "WeaviateSink":
        return WeaviateSink(sink_information=sink_information)
    elif sink_name == "QdrantSink":
        return QdrantSink(sink_information=sink_information)
    elif sink_name == "SingleStoreSink":
        return SingleStoreSink(sink_information=sink_information)
    elif sink_name == "SupabaseSink":
        return SupabaseSink(sink_information=sink_information)
    return None