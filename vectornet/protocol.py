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
from typing import Dict, List, Optional


class Version(pydantic.BaseModel):
    major: int
    minor: int
    patch: int


class CreateSynapse(bt.Synapse):
    """
    Create protocal is represent to require to create db to miners.
    """
    version: Optional[Version] = None
    
    user_name: Optional[str] = None
    
    organization_name: Optional[str] = None
    
    namespace_name: Optional[str] = None
    
    index_data: Optional[List[str]] = None
    
    results = Optional[Dict] = None

class ReadSynapse(bt.Synapse):
    """
    Read protocal is represent to require to read db to miners.
    """
    version: Optional[Version] = None
    
    index_type : Optional[str] = None # organization, namespace or index
    
    index_name : Optional[str] = None
    
    query = Optional[Dict] = None


class DeleteSynapse(bt.Synapse):
    """
    Delete protocal is represent to require to delete db to miners.
    """
    version: Optional[Version] = None
    
    index_type : Optional[str] = None # organization, namespace or index
    
    index_name : Optional[str] = None
    
    
class UpdateSynapse(bt.Synapse):
    """
    Update protocal is represent to require to update db to miners.
    """
    version: Optional[Version] = None
    
    index_type : Optional[str] = None # organization, namespace or index
    
    index_name : Optional[str] = None
    
    update_data : Optional[Dict] = None
