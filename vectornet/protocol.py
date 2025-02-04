import typing
import bittensor as bt
import pydantic
from typing import Dict, List, Optional, Tuple

class Version(pydantic.BaseModel):
    major: int
    minor: int
    patch: int

class CreateSynapse(bt.Synapse):
    version: Optional[Version] = None
    type: str = pydantic.Field("CREATE")
    user_name: Optional[str] = None
    organization_name: Optional[str] = None
    namespace_name: Optional[str] = None
    index_data: Optional[List[str]] = None
    results: Optional[Tuple[int, int, int, List[int]]] = None  

    def deserialize(self):
        return self.results

class ReadSynapse(bt.Synapse):
    version: Optional[Version] = None
    type: str = pydantic.Field("READ")
    user_name: Optional[str] = None
    organization_name: Optional[str] = None
    namespace_name: Optional[str] = None
    query_data: Optional[str] = None
    size: int = pydantic.Field(3, ge=1, le=50)
    results: Optional[Tuple[int, int, int, int, str]] = None  

    def deserialize(self):
        return self.results

class UpdateSynapse(bt.Synapse):
    version: Optional[Version] = None
    type: str = pydantic.Field("UPDATE")
    perform: Optional[str] = None
    user_name: Optional[str] = None
    organization_name: Optional[str] = None
    namespace_name: Optional[str] = None
    index_data: Optional[List[str]] = None
    results: Optional[Tuple[int, int, int, List[int]]] = None  

    def deserialize(self):
        return self.results

class DeleteSynapse(bt.Synapse):
    version: Optional[Version] = None
    type: str = pydantic.Field("DELETE")
    perform: Optional[str] = None
    user_name: Optional[str] = None
    organization_name: Optional[str] = None
    namespace_name: Optional[str] = None
    results: Optional[Tuple[int, int, int]] = None  

    def deserialize(self):
        return self.results
