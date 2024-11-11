
from vectornet.miner_group.check_new_miners import check_miner_status


def weight_controller(miner_uid):
    new_miner_uids, miner_ages = check_miner_status()
    miner_age = None
    for miner in miner_ages:
        if miner_uid == miner['uid']:
            miner_age = miner['age']
    age_to_weight = {
        "very_young": 0.6,
        "young": 0.7,
        "mature": 0.8,
        "old": 0.9,
        "very_old": 1.0
    }
    weight = age_to_weight.get(miner_age)
    return weight
