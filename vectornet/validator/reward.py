import numpy as np
from typing import List

def reward(score: float, weight: float) -> float:
    """Calculate miner reward based on score and weight.

    Args:
        score (float): The score to be used in the calculation.
        weight (float): The weight to be applied.

    Returns:
        float: The calculated miner reward.
    """
    low_reward = (0.8 * (score ** 7) + 
                  0.1 * (score ** 5) + 
                  0.1 * (score ** 3))
    
    miner_reward = weight * low_reward
    
    return miner_reward

async def get_rewards(
    create_request_zero_score: float,
    update_request_zero_scores: List[float],
    delete_request_zero_score: float,
    read_score: float,
    weight: float,
) -> np.ndarray:
    """Calculate rewards based on request scores and weight.

    Args:
        create_request_zero_score (float): Score for create requests.
        update_request_zero_score (float): Score for update requests.
        delete_request_zero_score (float): Score for delete requests.
        read_score (float): Score for read operations.
        weight (float): Weight to apply in the reward calculation.

    Returns:
        np.ndarray: The calculated miner reward as a NumPy array.
    """
    initial_create_score, initial_delete_score, initial_update_score = 1.0, 1.0, 1.0
    
    zero_scores = [
        create_request_zero_score,
        delete_request_zero_score,
    ]
    
    if create_request_zero_score == 0:
        initial_create_score = 0.3
        
    if delete_request_zero_score == 0:
        initial_delete_score = 0.3
    
    # if any(score == 0 for score in update_request_zero_scores):
    #     initial_update_score = 0.5
    for score in update_request_zero_scores:
        if score == 0:
            initial_update_score = initial_update_score * 0.3
    miner_reward = reward(initial_create_score * initial_delete_score * initial_update_score * read_score, weight)
    return np.array(miner_reward)
