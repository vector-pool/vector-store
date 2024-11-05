import torch


def evaluate_create_request(responses):
    
    scores = torch.ones(len(responses))
    
    for i, response in enumerate(responses):
        if response is None:
            print(f"{i}th response doesn't have a value")
            scores[i] = 0
        if len(response) != 3:
            print(f"{i}th response's length is not 3, it contains less or more ingegers.")
        uniqueness = evaluate_qniqueness(response)
        if uniqueness == 0:
            scores[i] = 0
        