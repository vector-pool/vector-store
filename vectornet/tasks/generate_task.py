import yaml
import random
import bittensor as bt
from traceback import print_exception
import openai
import os
import asyncio

from vectornet.utils.config import len_limit
from vectornet.wiki_integraion.wiki_scraper import wikipedia_scraper
from vectornet.protocol import(
    CreateSynapse,
    ReadSynapse,
    UpdateSynapse,
    DeleteSynapse,
)
from vectornet.utils.version import get_version
from vectornet.wiki_integraion.wiki_scraper import get_wiki_article_content_with_pageid
from vectornet.database_manage.validator_db_manager import ValidatorDBManager
from dotenv import load_dotenv

load_dotenv()


with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

wiki_categories = config['wiki_categories']
organization_names = config['organization_names']
user_names = config['user_names']

async def generate_create_request(validator_db_manager, article_size = 10) -> CreateSynapse:
    
    user_name, organization_name, namespace_name = None, None, None
    while True:
        user_name = random.choice(user_names)
        organization_name = random.choice(organization_names)
        namespace_name = random.choice(wiki_categories)
        uniquness = validator_db_manager.check_uniquness(user_name, organization_name, namespace_name)
        print("user_name, organization_name, category, uniquness        :        ", user_name, organization_name, namespace_name, uniquness)
        if uniquness:
            break
    print("user_name, organization_name, category, uniquness : ", user_name, organization_name, namespace_name, uniquness)
    category = "random"
    articles = await wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][:len_limit])
    version = get_version()
    query = CreateSynapse(
        version = version,
        type = 'CREATE',
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = namespace_name,
        index_data = contents,
    )
    
    return category, articles, query
    
async def generate_read_request(validator_db_manager):

    result = validator_db_manager.get_random_unit_ids()
    print("This is random uids: ", result)
    if result is not None:
        user_id, organization_id, namespace_id, user_name, organization_name, namespace_name, category, pageids_info = result
    else:
        return None, None, None, None, None, None
    # pageid, vector_id = random.choice(list(pageids_info.items()))
    pageids = list(pageids_info.keys())
    pageid = random.choice(pageids)
    
    content = await get_wiki_article_content_with_pageid(pageid)
    
    if content is None:
        bt.logging.error("The wiki-scraper with pageid doesn't work when creating ReadRequest.")
    print("OPENAIKEY = ", os.getenv("OPENAI_API_KEY"))
    llm_client = openai.OpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        max_retries = 3,
    )
    
    query_content = generate_query_content(llm_client, content)
    
    bt.logging.debug(query_content)
    
    if query_content is None:
        bt.logging.error("The query_content is None for ReadRequest, Check again openai operation.")
    
    version = get_version()
    
    query = ReadSynapse(
        version = version,
        type = 'READ',
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = namespace_name,
        size = 1,
        query_data = query_content,
    )
    
    return query, content, user_id, organization_id, namespace_id, pageids_info

async def generate_update_request(article_size, validator_db_manager):
    
    result = validator_db_manager.get_random_unit_ids()
    print("This is random uids: ", result)
    if result is not None:
        user_id, organization_id, namespace_id, user_name, organization_name, namespace_name, category, pageids_info = result
    else:
        return None, None, None, None, None, None
    print("Starting wiki-scraper")
    articles = await wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][:len_limit])
    
    version = get_version() 
    
    # performs = ['ADD', 'REPLACE']
    # perform = random.choice(performs)
    
    query = UpdateSynapse(
        version = version,
        type = 'UPDATE',
        perform = "ADD",
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = namespace_name,
        index_data = contents,
    )
    
    return user_id, organization_id, namespace_id, category, articles, query
    
async def generate_delete_request(validator_db_manager):
    
    result = validator_db_manager.get_random_unit_ids()
    
    if result is not None:
        user_id, organization_id, namespace_id, user_name, organization_name, namespace_name, category, pageids_info = result
    else:
        return None
    
    version = get_version()
    
    query = DeleteSynapse(
        version = version,
        type = 'DELETE',
        perform = 'namespace',
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = namespace_name,
    )
    
    return user_id, organization_id, namespace_id, query

def generate_query_content(llm_client, content):
    prompt = (
        """You are an embedding evaluator. Your task is to generate a query from the given original content to assess how well the embedding engines perform.
        You will be provided with the original content as your source of information. Your job is to create a summarized version of this content.
        This summary will be used to evaluate the performance quality of different embedding engines by comparing the embeddings of the query content with the results from each engine."""
    )
    prompt += content + " "
    prompt += (
        """Generate a summary of the original content using approximately 700-900 characters. Provide only the generated summary in plain text, without any additional context, explanation, or formatting. single and double quotes or new lines."""
    )

    print(f"Prompt: {prompt}")

    try:
        output = llm_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=1.5,
            timeout=30,
        )

        bt.logging.debug(
            f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
        )
        return output.choices[0].message.content
    except Exception as e:
        print(f"Error during LLM completion: {e}")
        print(print_exception(type(e), e, e.__traceback__))
        return None
        

if __name__ == '__main__':
    pass
    
