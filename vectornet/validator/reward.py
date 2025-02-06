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
    create_score: float,
    update_scores: List[float],
    delete_score: float,
    read_score: float,
    weight: float,
) -> np.ndarray:
    """Calculate rewards based on request scores and weight.

    Args:
        create_score (float): Score for create requests.
        update_scores (List[float]): Scores for update requests.
        delete_score (float): Score for delete requests.
        read_score (float): Score for read operations.
        weight (float): Weight to apply in the reward calculation.

    Returns:
        np.ndarray: The calculated miner reward as a NumPy array.
    """
    create_multiplier = 0.5 if create_score == 0 else 1.0
    delete_multiplier = 0.5 if delete_score == 0 else 1.0
    update_multiplier = 1.0

    for score in update_scores:
        if score == 0:
            update_multiplier *= 0.5

    adjusted_read_score = read_score ** 5

    total_score = (
        create_multiplier * delete_multiplier * update_multiplier * adjusted_read_score
    )
    miner_reward = reward(total_score, weight)

    return np.array(miner_reward)
