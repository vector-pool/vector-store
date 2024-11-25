"""
This scripts is suspected to be a part of the organization module of the vectornet package    
arguments:

"""
from typing import Optional, Dict, List
import pydantic
from vectornet.base.neuron import BaseNeuron

class Organization(BaseNeuron):
    """
    Organization class for Bittensor miners.
    """

    neuron_type: str = "OrganizationNeuron"

    name: Optional[str] = None

