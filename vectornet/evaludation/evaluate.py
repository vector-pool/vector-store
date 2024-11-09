import torch
import bittensor as bt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vectornet.embedding.embed import TextToEmbedding


def evaluate_create_request(response, validator_db_manager, query):
    
    if response is None:
        # bt.logging.info("aresponse doesn't have a value")
        return 0
    if len(response) != 3:
        # bt.logging.info("response's length is not 3, it contains less or more ingegers.")
        return 0
    user_id, organization_id, namespace_id = get_ids_from_response(response)
    db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name = validator_db_manager.get_db_data(user_id, organization_id, namespace_id)
    if db_user_id:
        if db_user_name != query.user_name:
            return 0
    if db_organization_id:
        if db_organization_name != query.organization_name:
            return 0
    if db_namespace_id is not None:
        return 0
    return 1
    
        
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
        return 0
    if content == original_content:
        score = 1
    else:
        score = evaluate_similarity(original_content, content)
    return score * zero_score
        
def evaluate_similarity(original_content, content):
    
    embedding_manager = TextToEmbedding()
    original_content_embedding = embedding_manager.embed(original_content)
    content_embedding = embedding_manager.embed(original_content)
    
    original_content_embedding = np.array(original_content_embedding[0]).reshape(1, -1) #assume that we are using 8091 max token embedding model so return value is list and only has one value now.
    content_embedding = np.array(content_embedding[0]).reshape(1, -1)
        
    similarity_score = cosine_similarity(original_content_embedding, content_embedding)[0][0]

    return similarity_score
    
def get_ids_from_response(response):
    return response[0], response[1], response[2]