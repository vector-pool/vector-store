# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

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
