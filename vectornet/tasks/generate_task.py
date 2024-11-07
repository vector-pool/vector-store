import yaml
import random
import bittensor as bt
from traceback import print_exception
import openai
import os

from vectornet.wiki_integraion.wiki_scraper import wikipedia_scraper
from vectornet.protocol import(
    CreateSynapse,
    ReadSynapse,
    UpdateSynapse,
    DeleteSynapse,
)
from vectornet.utils.version import get_version

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


wiki_categories = config['wiki_categories']
organization_names = config['organization_names']
user_names = config['user_names']

len_limit = 31e4

llm_client = openai.OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    max_retries=3,
)


def generate_create_request(article_size = 30) -> CreateSynapse:
    
    category = random.choice(wiki_categories)
    organization_name = random.choice(organization_names)
    user_name = random.choice(user_names)
    
    
    articles = wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][len_limit])
    version = get_version()
    query = CreateSynapse(
        version = version,
        type = 'CREATE',
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = category,
        index_data = contents,
    )
    
    return category, articles, query
    
        
def generate_read_request(miner_uid):
    
    namespace_data = get_namespace_data(miner_uid)

    user_id, organization_id, namespace_id, category, pageids = random.choice(namespace_data) # this line and above should be one method and this returns the list of pageids, not namespace id

    pageid = random.choice(pageids)
    
    content = get_wiki_article_content_with_pageid(pageid)
    
    query_content = generate_query_content()
    
    version = get_version()
    
    query = ReadSynapse(
        version = version,
        type = 'READ',
        user_id = user_id,
        organization_id = organization_id,
        namespace_id = namespace_id,
        query_data = query_content,
    )
    
    return query, content

def generate_update_request(article_size, miner_uid):
    
    namespace_data = get_namespace_data(miner_uid)
        
    user_id, organization_id, namespaace_id, category = random.choice(namespace_data)
    
    articles = wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][len_limit])
    
    version = get_version() 
    
    performs = ['ADD', 'REPLACE']
    
    query = UpdateSynapse(
        version = version,
        type = 'UPDATE',
        perform = "ADD",
        user_id = user_id,
        organization_id = organization_id,
        namespace_id = namespaace_id,
        index_data = contents,
    )
    
    return category, articles, query
    
def generate_delete_request(miner_uid):
    
    namespace_data = get_namespace_data(miner_uid)
    
    user_id, organization_id, namespace_id = random.choice(namespace_data)
    
    version = get_version()
    
    return DeleteSynapse(
        version = version,
        type = 'DELETE',
        perform = 'namespace',
        user_id = user_id,
        organization_id = organization_id,
        namespace_id = namespace_id,
    )
    

def generate_query_content(llm_client, content):
    prompt = (
        "you are embedding evaludator, you have to generate the query content from original content for check how embedding performed well," 
        "you will be given a original content as your source of knowledge. "
        "Your job is to generate the sumerized content of given content for evaluating every embedding engines performance quality by comparing query content embedding and every engine's embdding results"
        "below are original content"
    )
    prompt += content
    prompt += (
        "generate the content with about 300-500 letters "
        "Please give the generated content only, without any additional context or explanation."
    )

    bt.logging.debug(f"Prompt: {prompt}")

    try:
        output = llm_client.chat.completions.create(
            model="gpt-4-turbo",
            # response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=1.5,
            timeout=60,
        )

        bt.logging.debug(
            f"generation questions LLM response: {output.choices[0].message.content}"
        )
        bt.logging.debug(
            f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
        )
        return output.choices[0].message.content
    except Exception as e:
        bt.logging.error(f"Error during LLM completion: {e}")
        bt.logging.debug(print_exception(type(e), e, e.__traceback__))