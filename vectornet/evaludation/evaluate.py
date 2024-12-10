# import torch
# import bittensor as bt
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from vectornet.embedding.embed import TextToEmbedding
# from vectornet.wiki_integraion.wiki_scraper import get_wiki_article_content_with_pageid
# from vectornet.search_engine.search import SearchEngine
# import asyncio

# def evaluate_create_request(response, validator_db_manager, query, pageids):
    
#     if response is None:
#         bt.logging.error("The response is missing a value.")
#         return 0
#     if len(response) != 4:
#         bt.logging.error("The response does not have the expected length of 4; it contains either too few or too many integers.")
#         return 0
#     if not response[3]:
#         bt.logging.error("The validator_id list is empty in the response, which could lead to the validator sending empty index_data.")
#     user_id, organization_id, namespace_id, vector_ids = get_ids_from_response(response)
#     db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name = validator_db_manager.get_db_data(user_id, organization_id, namespace_id)
#     if db_user_id:
#         if db_user_name != query.user_name:
#             bt.logging.error("The user_name of query and user_name of response are different.")
#             return 0
#     if db_organization_id:
#         if db_organization_name != query.organization_name:
#             bt.logging.error("The organization_name of query and organization_name of response are different.")
#             return 0
#     if db_namespace_id is not None:
#         return 0
#     if len(pageids) != len(vector_ids):
#         return 0
#     return 1
    
        
# def evaluate_update_request(query, response, query_user_id, query_organization_id, query_namespace_id, pageids):
    
#     if response is None:
#         bt.logging.error("The response from the update request is missing a value.")
#         return 0
#     if len(response) != 4:
#         bt.logging.error("The response does not have the expected length of 3; it contains either too few or too many integers.")
#         return 0
#     response_user_id, response_organization_id, response_namespace_id, vector_ids = get_ids_from_response(response)
#     if (
#         response_user_id != query_user_id or
#         response_organization_id != query_organization_id or
#         response_namespace_id != query_namespace_id
#     ):
#         bt.logging.error("The id pairs are not same in the update request response.")
#         return 0
#     if len(pageids) != len(vector_ids):
#         return 0
    
#     return 1

# def evaluate_delete_request(query, response, query_user_id, query_organization_id, query_namespace_id,):
    
#     if response is None:
#         return 0
#     if len(response) != 3:
#         return 0
#     response_user_id, response_organization_id, response_namespace_id = response
    
#     if (
#         query_user_id != response_user_id or
#         query_organization_id != response_organization_id or
#         query_namespace_id != response_namespace_id
#     ):
#         return 0
    
#     return 1
    
# def evaluate_read_request(query_user_id, query_organization_id, query_namespace_id, pageids_info, response, original_content):
#     zero_score = 1
#     score = 0
    
#     if len(response) != 5:
#         return 0
    
#     response_user_id, response_organization_id, response_namespace_id, response_vector_id, response_content = response
    
#     vectorid_to_pageid = {v: p for p, v in pageids_info.items()}
#     pageid = vectorid_to_pageid.get(response_vector_id)
    
#     if pageid is None:
#         return 0
#     else :
#         content = asyncio.run(get_wiki_article_content_with_pageid(pageid))
#         if response_content != content:
#             bt.logging.debug(f"The original content and response content are different, pageid = {pageid}, the read_request_score is zero.")
#             return 0
    
#     if (
#         response_user_id != query_user_id or
#         response_organization_id != query_organization_id or
#         response_namespace_id != query_namespace_id
#     ):
#         return 0
        
#     if response_content == original_content:
#         bt.logging.debug(f"The response is perfect, The original and response content are exactly same. Giving score one")
#         score = 1
#     else:
#         score = evaluate_similarity(original_content, response_content)
#     return score * zero_score
        
# def evaluate_similarity(original_content, content):
    
#     embedding_manager = TextToEmbedding()
#     original_embedding_tensor = embedding_manager.embed([original_content])[1][0]
#     content_embedding_tensor = embedding_manager.embed([content])[1][0]
#     print(content_embedding_tensor)
#     original_content_embedding_np = np.array(content_embedding_tensor).reshape(1, -1)
#     content_embedding_np = np.array(original_embedding_tensor).reshape(1, -1)
        
#     similarity_score = cosine_similarity(original_content_embedding_np, content_embedding_np)[0][0]

#     return similarity_score
    
# def get_ids_from_response(response):
#     return response[0], response[1], response[2], response[3]

# if __name__ == '__main__':
#     original_content = ["education is very", "processors is good", "hello, nice to meet you"]
#     content = "hello, nice to meet you"
#     embedding_manager = TextToEmbedding()
#     embeded_data, embeddings, original_data = embedding_manager.embed(original_content)
#     content_embedding = embedding_manager.embed([content])[1][0]
#     vectors = []
#     for text, embedding, original_text in zip(embeded_data, embeddings, original_data):
#         vectors.append({"text": text, 'original_text': original_text, 'embedding': embedding})
#     search = SearchEngine()
#     results = search.cosine_similarity_search(content_embedding, vectors, 3)
#     for result in results:
#         print(result['original_text'], result['text'], result['similarity'])
    
    
    
    
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
        bt.logging.error("The response is missing a value.")
        return 0
    if len(response) != 4:
        bt.logging.error("The response does not have the expected length of 4; it contains either too few or too many integers.")
        return 0
    if not response[3]:
        bt.logging.error("The validator_id list is empty in the response, which could lead to the validator sending empty index_data.")
    
    user_id, organization_id, namespace_id, vector_ids = get_ids_from_response(response)
    db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name = validator_db_manager.get_db_data(user_id, organization_id, namespace_id)
    
    if db_user_id:
        if db_user_name != query.user_name:
            bt.logging.error("The user_name of query and user_name of response are different.")
            return 0
    
    if db_organization_id:
        if db_organization_name != query.organization_name:
            bt.logging.error("The organization_name of query and organization_name of response are different.")
            return 0
    
    if db_namespace_id is not None:
        return 0
    
    if len(pageids) != len(vector_ids):
        bt.logging.error("The length of pageids does not match the length of vector_ids.")
        return 0
    
    return 1
    

def evaluate_update_request(query, response, query_user_id, query_organization_id, query_namespace_id, pageids):
    
    if response is None:
        bt.logging.error("The response from the update request is missing a value.")
        return 0
    if len(response) != 4:
        bt.logging.error("The response does not have the expected length of 4; it contains either too few or too many integers.")
        return 0
    
    response_user_id, response_organization_id, response_namespace_id, vector_ids = get_ids_from_response(response)
    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        bt.logging.error("The id pairs are not the same in the update request response.")
        return 0
    
    if len(pageids) != len(vector_ids):
        bt.logging.error("The length of pageids does not match the length of vector_ids.")
        return 0
    
    return 1

def evaluate_delete_request(query, response, query_user_id, query_organization_id, query_namespace_id,):
    
    if response is None:
        bt.logging.error("The delete request response is missing a value.")
        return 0
    
    if len(response) != 3:
        bt.logging.error("The delete request response does not have the expected length of 3.")
        return 0
    
    response_user_id, response_organization_id, response_namespace_id = response
    
    if (
        query_user_id != response_user_id or
        query_organization_id != response_organization_id or
        query_namespace_id != response_namespace_id
    ):
        bt.logging.error("The delete request ids do not match the expected values.")
        return 0
    
    return 1
    

def evaluate_read_request(query_user_id, query_organization_id, query_namespace_id, pageids_info, response, original_content):
    zero_score = 1
    score = 0
    
    if len(response) != 5:
        bt.logging.error("The response from the read request does not have the expected length of 5.")
        return 0
    
    response_user_id, response_organization_id, response_namespace_id, response_vector_id, response_content = response
    vectorid_to_pageid = {v: p for p, v in pageids_info.items()}
    pageid = vectorid_to_pageid.get(response_vector_id)
    
    if pageid is None:
        bt.logging.error("No corresponding pageid found for the response vector_id.")
        return 0
    else:
        content = asyncio.run(get_wiki_article_content_with_pageid(pageid))
        if response_content != content:
            bt.logging.debug(f"The original content and response content are different, pageid = {pageid}, the read_request_score is zero.")
            return 0
    
    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        bt.logging.error("The response identifiers do not match the query identifiers.")
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
    
    bt.logging.info(f"Evaluating similarity. Original content embedding: {original_embedding_tensor}, Response content embedding: {content_embedding_tensor}")
    
    original_content_embedding_np = np.array(original_embedding_tensor).reshape(1, -1)
    content_embedding_np = np.array(content_embedding_tensor).reshape(1, -1)
        
    similarity_score = cosine_similarity(original_content_embedding_np, content_embedding_np)[0][0]
    return similarity_score

def get_ids_from_response(response):
    return response[0], response[1], response[2], response[3]

    
    
    
    