import torch
import bittensor as bt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vectornet.embedding.embed import TextToEmbedding
from vectornet.wiki_integraion.wiki_scraper import get_wiki_article_content_with_pageid
import asyncio

def evaluate_create_request(response, validator_db_manager, query, pageids):
    
    if response is None:
        bt.logging.error("aresponse doesn't have a value")
        return 0
    if len(response) != 4:
        bt.logging.error("response's length is not 4, it contains less or more ingegers.")
        return 0
    if not response[3]:
        bt.logging.error("It returns empty validator_id list, it may cause validator sent empty index_data")
    user_id, organization_id, namespace_id, vector_ids = get_ids_from_response(response)
    db_user_id, db_user_name, db_organization_id, db_organization_name, db_namespace_id, db_namespace_name = validator_db_manager.get_db_data(user_id, organization_id, namespace_id)
    if db_user_id:
        if db_user_name != query.user_name:
            return 0
    if db_organization_id:
        if db_organization_name != query.organization_name:
            return 0
    if db_namespace_id is not None:
        return 0
    if len(pageids) != len(vector_ids):
        return 0
    return 1
    
        
def evaluate_update_request(query, response, query_user_id, query_organization_id, query_namespace_id, pageids):
    
    if response is None:
        bt.logging.error("update request response doesn't have a value")
        return 0
    if len(response) != 4:
        bt.logging.error("response's length is not 3, it contains less or more ingegers.")
        return 0
    response_user_id, response_organization_id, response_namespace_id, vector_ids = get_ids_from_response(response)
    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        return 0
    if len(pageids) != len(vector_ids):
        return 0
    
    return 1

def evaluate_delete_request(query, response, query_user_id, query_organization_id, query_namespace_id,):
    
    if response is None:
        return 0
    if len(response) != 3:
        return 0
    response_user_id, response_organization_id, response_namespace_id = response
    
    if (
        query_user_id != response_user_id or
        query_organization_id != response_organization_id or
        query_namespace_id != response_namespace_id
    ):
        return 0
    
    return 1
    
def evaluate_read_request(query_user_id, query_organization_id, query_namespace_id, pageids_info, response, original_content):
    
    zero_score = 1
    score = 0
    
    if len(response) != 5:
        return 0
    
    response_user_id, response_organization_id, response_namespace_id, response_vector_id, response_content = response
    
    vector_to_pageid = {v: k for k, v in pageids_info.items()}
    pageid = vector_to_pageid.get(response_vector_id)
    
    if vector_to_pageid is None:
        return 0
    else :
        content = asyncio.run(get_wiki_article_content_with_pageid(pageid))
        if response_content != content:
            return 0
    
    if (
        response_user_id != query_user_id or
        response_organization_id != query_organization_id or
        response_namespace_id != query_namespace_id
    ):
        return 0
        
    if response_content == original_content:
        score = 1
    else:
        score = evaluate_similarity(original_content, response_content)
    return score * zero_score
        
def evaluate_similarity(original_content, content):
    
    embedding_manager = TextToEmbedding()
    original_embedding_tensor = embedding_manager.embed([original_content])[1][0]
    content_embedding_tensor = embedding_manager.embed([content])[1][0]
    print(content_embedding_tensor)
    # original_content_embedding_np = original_embedding_tensor.cpu().detach().numpy().reshape(1, -1)
    # content_embedding_np = content_embedding_tensor.cpu().detach().numpy().reshape(1, -1)
    original_content_embedding_np = np.array(content_embedding_tensor).reshape(1, -1)
    content_embedding_np = np.array(original_embedding_tensor).reshape(1, -1)
        
    similarity_score = cosine_similarity(original_content_embedding_np, content_embedding_np)[0][0]

    return similarity_score
    
def get_ids_from_response(response):
    return response[0], response[1], response[2], response[3]

if __name__ == '__main__':
    # original_content = "The following outline is provided as an ov"
    original_content = "Education and Technology pushes creativeness Teaching comes with a creative mind. Technology also brings out the best in the ways teachers teach. I always find it very attractive for teachers to have lessons presented in a way that entertains me visually, emotionally and socially. And I think that in this kind of generation that we are in, it is an edge for teachers to be very innovative in presenting their lessons to the class. People change. And so as the teaching process. It is highly recommended to at least change the means of teaching with a new one that best suites the kind of youth or children we have today brought by the fast ageing modern civilization. Involving technological teachings may also help the learners learn in a creative way and being competent in all aspect. The activity was actually refreshing to me. It gave me ideas on how to really facilitate an effective classroom management using the different and new instructional materials. I really find it very exciting to actualize instructional materials from ideas to the finish products. It’s also fulfilling to be making something new for the students to have fun while learning. With all the ready materials that involves technology. I can access all my teaching memorabilia anytime and at the same time handy. The activity gave way to the right of the students to be taught in a better way. I always believe that when a student step foot inside a classroom, he/she has the right now to be taught regardless of the school (public o private). And also, I think it is very vital for teachers to be using the appropriate teaching materials always. Words alone can be very misleading. And that is why it is necessary to have supplementing materials that would help students grasp the concepts as presented in class. Regardless of the outcome, what is really important is for the material to be effective. And what I mean by effectiveness is the goal of achieving successful transfer of knowledge to the students. Education and Technology pushes creativeness Teaching comes with a creative mind. Technology also brings out the best in the ways teachers teach. I always find it very attractive for teachers to have lessons presented in a way that entertains me visually, emotionally and socially. And I think that in this kind of generation that we are in, it is an edge for teachers to be very innovative in presenting their lessons to the class. People change. And so as the teaching process. It is highly recommended to at least change the means of teaching with a new one that best suites the kind of youth or children we have today brought by the fast ageing modern civilization. Involving technological teachings may also help the learners learn in a creative way and being competent in all aspect. The activity was actually refreshing to me. It gave me ideas on how to really facilitate an effective classroom management using the different and new instructional materials. I really find it very exciting to actualize instructional materials from ideas to the finish products. It’s also fulfilling to be making something new for the students to have fun while learning. With all the ready materials that involves technology. I can access all my teaching memorabilia anytime and at the same time handy. The activity gave way to the right of the students to be taught in a better way. I always believe that when a student step foot inside a classroom, he/she has the right now to be taught regardless of the school (public o private). And also, I think it is very vital for teachers to be using the appropriate teaching materials always. Words alone can be very misleading. And that is why it is necessary to have supplementing materials that would help students grasp the concepts as presented in class. Regardless of the outcome, what is really important is for the material to be effective. And what I mean by effectiveness is the goal of achieving successful transfer of knowledge to the students."
    
    content = " What are the exact timestamps and sequence of warning templates added by user Excirial to the O&B Athens Boutique Hotel article, including dated prod and speedy deletion notices?"
    
    similarity = evaluate_similarity(original_content, content)
    print(similarity)
    
    
    
    
    
    
    
    
    
    
    