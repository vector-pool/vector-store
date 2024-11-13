
from vectornet.miner_group.check_new_miners import check_miner_status


def weight_controller(miner_uid, count):
 
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
    
    count_to_weight = {
        "very_young": 0.6,
        "young": 0.7,
        "mature": 0.8,
        "old": 0.9,
        "very_old": 1.0
    }
    
    miner_age = get_age_from_count(count)
    weight = get_age_from_count(miner_age)
    
    return weight

def get_age_from_count(count):
    
    if count < 20:
        age = "very_young"
    elif count < 40:
        age = "young"
    elif count < 60:
        age = "mature"
    elif count < 80:
        age = "old"
    else: 
        age = "very_old"
    
    return age