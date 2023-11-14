from enum import Enum

class TriggerSyncTypeEnum(str, Enum):
    delta = "delta"
    full = "full"

    def as_trigger_sync_type(trigger_sync_type: str):
        if trigger_sync_type == None or trigger_sync_type == "":
            return None
        try:
            enum_to_return = TriggerSyncTypeEnum[trigger_sync_type.lower()]
            return enum_to_return
        except KeyError as e:
            return None