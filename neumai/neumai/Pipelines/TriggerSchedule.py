from .TriggerSyncTypeEnum import TriggerSyncTypeEnum
from pydantic import BaseModel

class TriggerSchedule(BaseModel):
    start_date: str
    cadence: str
    sync_type: TriggerSyncTypeEnum
    
    def as_trigger_schedule(dct:dict):
        if dct == None:
            return None
        return TriggerSchedule(
            start_date=dct.get("start_date", None),
            cadence=dct.get("cadence", None),
            sync_type=TriggerSyncTypeEnum.as_trigger_sync_type(dct.get("sync_type", None)),
        )