
from vectornet.miner_group.check_new_miners import check_miner_status
from typing import Dict


def weight_controller(miner_uid: str, count: int) -> float:
    """Determine the weight for a miner based on their age derived from count.

    Args:
        miner_uid (str): Unique identifier for the miner.
        count (int): Count used to determine the miner's age.

    Returns:
        float: The weight associated with the miner's age.
    """

    # new_miner_uids, miner_ages = check_miner_status()

    # miner_age = None

    # for miner in miner_ages:
    #     if miner_uid == miner['uid']:
    #         miner_age = miner['age']

    # age_to_weight = {
    #     "very_young": 0.6,
    #     "young": 0.7,
    #     "mature": 0.8,
    #     "old": 0.9,
    #     "very_old": 1.0
    # }

    # weight = age_to_weight.get(miner_age)    

    count_to_weight: Dict[str, float] = {
        "very_young": 0.6,
        "young": 0.7,
        "mature": 0.8,
        "old": 0.9,
        "very_old": 1.0,
    }
    
    miner_age = get_age_from_count(count)
    weight = count_to_weight.get(miner_age)
    
    return weight


def get_age_from_count(count: int) -> str:
    """Get the age category based on the count.

    Args:
        count (int): The count to evaluate.

    Returns:
        str: The age category corresponding to the count.
    """
    if count < 20:
        return "very_young"
    elif count < 40:
        return "young"
    elif count < 60:
        return "mature"
    elif count < 80:
        return "old"
    else:
        return "very_old"


# Example usage
if __name__ == "__main__":
    miner_uid_example = "miner_123"
    count_example = 35
    weight = weight_controller(miner_uid_example, count_example)
    print(f"Weight for miner {miner_uid_example}: {weight}")
