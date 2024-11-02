import torch


def evaluate_create_request(responses):
    
    scores = torch.ones(len(responses))
    
    for i, response in enumerate(responses):
        if response is None:
            scores