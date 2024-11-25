
def make_miner_group(miner_status):
    very_young_miers, young_miners, mature_miners, old_miners, very_old_miners = [], [], [], [], []
    
    for miner in miner_status:
        if miner['category'] == 'very_young':
            very_young_miers.append(miner['uid'])
        elif miner['category'] == 'young':
            young_miners.append(miner['uid'])
        elif miner['category'] == 'mature':
            mature_miners.append(miner['uid'])
        elif miner['category'] == 'old':
            old_miners.append(miner['uid'])
        else :
            very_old_miners.append(miner['uid'])
    
    return very_young_miers, young_miners, mature_miners, old_miners, very_old_miners
    