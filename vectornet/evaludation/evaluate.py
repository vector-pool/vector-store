import torch
import bittensor as bt

def evaluate_create_request(response):
    
    score = 1
        
    if response is None:
        # bt.logging.info("aresponse doesn't have a value")
        score = 0
    if len(response) != 3:
        # bt.logging.info("response's length is not 3, it contains less or more ingegers.")
        score = 0
    uniqueness = evaluate_uniqueness(response) #from db read all the tripple pairs. compare if the new pair is duplcated.
    if uniqueness == 0:
        score = 0
        
    return score
        
def evaluate_update_request(query, response):
    
    score = 1
    
    if response is None:
        # bt.logging.info("update request response doesn't have a value")
        score = 0
    if len(response) != 3:
        # bt.logging.info("response's length is not 3, it contains less or more ingegers.")
        score = 0
    if (
        query.user_id != response[0] or
        query.organization_id != response[1] or
        query.namespace_id != response[2]
    ):
        score = 0
    
    return score

def evaluate_delete_request(query, response):
    
    score = 1
    
    if response is None:
        score = 0
    if len(response) != 3:
        score = 0
    if (
        query.user_id != response[0] or
        query.organization_id != response[1] or
        query.namespace_id != response[2]
    ):
        score = 0
    
    return score
    
def evaluate_read_request(query, response, original_content):
    
    zero_score = 1
    score = 0
    
    ids = response[0]
    content = response[1]
    
    if (
        ids is None or
        content is None
    ):
        zero_score = 0
    if (
        ids[0] != query.user_id or
        ids[1] != query.organization_id or
        ids[2] != query.namespace_id
    ):
        zero_score = 0
    contents = get_wiki_contents(ids)
    if content not in contents:
        zero_score = 0
    if content == original_content:
        score = 1
    else:
        score = evaluate_similarity(original_content, content)