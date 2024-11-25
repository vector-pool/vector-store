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

def get_rewards(
    self,
    create_request_zero_score: float,
    update_request_zero_scores: float,
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
        initial_create_score = 0.5
        
    if delete_request_zero_score == 0:
        initial_delete_score = 0.5
    
    if any(score == 0 for score in update_request_zero_scores):
        initial_update_score = 0.5
        
    miner_reward = reward(initial_create_score * initial_delete_score * initial_update_score * read_score, weight)
    
    return np.array(miner_reward)
