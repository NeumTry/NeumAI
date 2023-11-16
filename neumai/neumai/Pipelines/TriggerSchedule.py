from .TriggerSyncTypeEnum import TriggerSyncTypeEnum

class TriggerSchedule(object):
    def __init__(self, start_date: str, cadence: str, sync_type: TriggerSyncTypeEnum):
        self.start_date = start_date
        self.cadence = cadence
        self.sync_type = sync_type

    def toJson(self):
        """Python does not have built in serialization. We need this logic to be able to respond in our API.

        Returns:
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['start_date'] = self.start_date
        json_to_return['cadence'] = self.cadence
        json_to_return['sync_type'] = self.sync_type
        return json_to_return
    
    def to_model(self):
        """Convert to model for serialization
            _type_: the json to return
        """
        json_to_return = {}
        json_to_return['start_date'] = self.start_date
        json_to_return['cadence'] = self.cadence
        json_to_return['sync_type'] = self.sync_type

        return json_to_return
    
    def as_trigger_schedule(dct:dict):
        if dct == None:
            return None
        return TriggerSchedule(
            start_date=dct.get("start_date", None),
            cadence=dct.get("cadence", None),
            sync_type=TriggerSyncTypeEnum.as_trigger_sync_type(dct.get("sync_type", None)),
        )