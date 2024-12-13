from pydantic import BaseModel
from typing import List, Optional

class Operation(BaseModel):
    request_type: str
    S_F: str
    score: float
    timestamp: str

class MinerData(BaseModel):
    miner_uid: str
    total_storage_size: float
    operations: List[Operation]
    request_cycle_score: float
    weight: float
    passed_request_cycle: int