import torch
import bittensor as bt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vectornet.embedding.embed import TextToEmbedding
from vectornet.wiki_integraion.wiki_scraper import get_wiki_article_content_with_pageid
from vectornet.search_engine.search import SearchEngine
import asyncio

def evaluate_create_request(response, validator_db_manager, query, pageids):
    
    if response is None:
        bt.logging.debug("The response is missing a value.")
        return 0
    if len(response) != 4:
        bt.logging.debug("The response does not have the expected length of 4; it contains either too few or too many integers.")
        return 0
    if not response[3]:
        bt.logging.debug("The validator_id list is empty in the response, which could lead to the validator sending empty index_data.")
    
    user_id, organization_id, namespace_id, vector_ids = get_ids_from_response(response)
    db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name = validator_db_manager.get_db_data(user_id, organization_id, namespace_id)
    
    if db_user_id:
        if db_user_name != query.user_name:
            bt.logging.debug("The user_name of query and user_name of response are different.")
            return 0
    
    if db_organization_id:
        if db_organization_name != query.organization_name:
            bt.logging.debug("The organization_name of query and organization_name of response are different.")
            return 0
    
    if db_namespace_id is not None:
        return 0
    
    if len(pageids) != len(vector_ids):
        bt.logging.debug("The length of pageids does not match the length of vector_ids.")
        return 0
    
    return 1

def evaluate_update_request(query, response, query_user_id, query_organization_id, query_namespace_id, pageids):
    
    if response is None:
        bt.logging.debug("None response of UpdateRequest")
        return 0
    
    if len(response) != 4:
        bt.logging.debug("The response does not have the expected length of 4; it contains either too few or too many integers.")
        return 0
    
    response_user_id, response_organization_id, response_namespace_id, vector_ids = get_ids_from_response(response)
    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        bt.logging.debug("The id pairs are not the same in the update request response.")
        return 0
    
    if len(pageids) != len(vector_ids):
        bt.logging.debug("The length of pageids does not match the length of vector_ids.")
        return 0
    
    return 1

def evaluate_delete_request(query, response, query_user_id, query_organization_id, query_namespace_id,):
    
    if response is None:
        bt.logging.debug("None response of DeleteRequest.")
        return 0
    
    if len(response) != 3:
        bt.logging.debug("The delete request response does not have the expected length of 3.")
        return 0
    
    response_user_id, response_organization_id, response_namespace_id = response
    
    if (
        query_user_id != response_user_id or
        query_organization_id != response_organization_id or
        query_namespace_id != response_namespace_id
    ):
        bt.logging.debug("The delete request ids do not match the expected values.")
        return 0
    
    return 1
    
def evaluate_read_request(query_user_id, query_organization_id, query_namespace_id, pageids_info, response, original_content, max_len):
    zero_score = 1
    score = 0
    
    if response is None:
        bt.logging.debug("None response of ReadRequest.")
        return 0
    
    if len(response) != 5:
        bt.logging.debug("The response from the read request does not have the expected length of 5.")
        return 0
    
    response_user_id, response_organization_id, response_namespace_id, response_vector_id, response_content = response
    vectorid_to_pageid = {v: p for p, v in pageids_info.items()}
    pageid = vectorid_to_pageid.get(response_vector_id)
    
    if pageid is None:
        bt.logging.debug("No corresponding pageid found for the response vector_id.")
        return 0

    content = asyncio.run(get_wiki_article_content_with_pageid(pageid))

    if response_content != content[:min(len(content), max_len)]:
        bt.logging.debug(f"The original content and response content are different, pageid = {pageid}, the read_request_score is zero.")
        return 0

    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        bt.logging.debug("User, organization, or namespace mismatch, setting score to zero.")
        return 0  
    
    if response_content == original_content:
        bt.logging.info("The response is perfect, The original and response content are exactly the same. Giving score one.")
        score = 1
    else:
        score = evaluate_similarity(original_content, response_content)
    
    return score * zero_score
    
def evaluate_similarity(original_content, content):
    embedding_manager = TextToEmbedding()
    original_embedding_tensor = embedding_manager.embed([original_content])[1][0]
    content_embedding_tensor = embedding_manager.embed([content])[1][0]
    
    # bt.logging.info(f"Evaluating similarity. Original content embedding: {original_embedding_tensor}, Response content embedding: {content_embedding_tensor}")
    
    original_content_embedding_np = np.array(original_embedding_tensor).reshape(1, -1)
    content_embedding_np = np.array(content_embedding_tensor).reshape(1, -1)
        
    similarity_score = cosine_similarity(original_content_embedding_np, content_embedding_np)[0][0]
    bt.logging.info(f"Calculated similarity_score: {similarity_score}.")
    return similarity_score

def get_ids_from_response(response):
    return response[0], response[1], response[2], response[3]

    
    
    
    
