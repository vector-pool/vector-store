from vectornet.miner_group.check_new_miners import check_miner_status
from typing import Dict
import bittensor as bt


def weight_controller(count: int) -> float:
    """Determine the weight for a miner based on their age derived from count.

    Args:
        miner_uid (str): Unique identifier for the miner.
        count (int): Count used to determine the miner's age.

    Returns:
        float: The weight associated with the miner's age.
    """

    count_to_weight: Dict[str, float] = {
        "squire": 0.6,
        "knight": 0.7,
        "champion": 0.8,
        "paladin": 0.9,
        "lord": 1.0,
    }
    
    miner_age = get_age_from_count(count)
    weight = count_to_weight.get(miner_age)
    bt.logging.info(f"weight = {weight}")
    return weight


def get_age_from_count(count: int) -> str:
    """Get the age category based on the count.

    Args:
        count (int): The count to evaluate.

    Returns:
        str: The age category corresponding to the count.
    """
    if count < 500:
        return "squire"
    elif count < 2000:
        return "knight"
    elif count < 4000:
        return "champion"
    elif count < 6000:
        return "paladin"
    else:
        return "lord"

