import bittensor as bt
from substrateinterface.base import SubstrateInterface

def check_miner_status():
    current_block_number = bt.subtensor().get_current_block()
    substrate = SubstrateInterface(
        url="wss://archive.chain.opentensor.ai:443/",
        ss58_format=42,
        use_remote_preset=True,
    )
    netuid = 46
    result = substrate.query_map('SubtensorModule', 'BlockAtRegistration', [netuid, ])
    miner_cur_status = []
    for record in result:
        uid = record[0].value  # Accessing U16 value
        block_number = record[1].value  # Accessing U64 value
        miner_cur_status.append({'uid': uid, 'registered_block_number': block_number})
    bt.logging.debug(miner_cur_status)
    
    
    miner_pre_status = []
        # Initialize a list to store new miners' UIDs
    new_miner_uids = []

    # Check for new miners based on block_number
    for miner_pre, miner_cur in zip(miner_pre_status, miner_cur_status):
        if miner_pre['registered_block_number'] != miner_cur['registered_block_number']:
            new_miner_uids.append(miner_cur['uid'])

    # Check for miners that exist in the current list but not in the previous list
    previous_uids = {miner['uid'] for miner in miner_pre_status}
    for miner in miner_cur_status:
        if miner['uid'] not in previous_uids:
            new_miner_uids.append(miner['uid'])

    # Update previous status with current status for next comparison
    miner_pre_status = miner_cur_status.copy()

    # Output the list of new miners' UIDs
    print(new_miner_uids)
    
    miner_ages = []
    
    age_categories = {
        "very_young":36000, # assume immune period is 5 days : 7200 * 5
        "young":72000, # 10 days
        "mature": 144000, # 20 days
        "old": 216000, # 30 days
        "very_old": 324000 # 45 days
    }

    miner_ages = []
    for miner in miner_cur_status:
        age = current_block_number - miner['registered_block_number']
        
        # Determine the category based on age
        category = None
        for cat, threshold in age_categories.items():
            if age < threshold:
                category = cat
                break
        if category is None:  # If age exceeds the highest threshold
            category = "very_old"

        miner_ages.append({'uid': miner['uid'], 'age': age, 'category': category})
    bt.logging.debug(miner_ages)

    return new_miner_uids, miner_ages

if __name__ == '__main__':
    check_miner_status()
    