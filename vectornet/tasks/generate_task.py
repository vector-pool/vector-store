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

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


wiki_categories = config['wiki_categories']
organization_names = config['organization_names']
user_names = config['user_names']

async def generate_create_request(validator_db_manager, article_size = 30) -> CreateSynapse:
    
    user_name, organization_name, category = None, None, None
    while True:
        user_name = random.choice(user_names)
        organization_name = random.choice(organization_names)
        category = random.choice(wiki_categories)
        uniquness = validator_db_manager.check_uniquness(user_name, organization_name, category)
        print("user_name, organization_name, category, uniquness", user_name, organization_name, category, uniquness)
        if uniquness:
            break
    articles = await wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][:len_limit])
    version = get_version()
    print("version =", version)
    query = CreateSynapse(
        version = version,
        type = 'CREATE',
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = category,
        index_data = contents,
    )
    print(contents[2])
    
    return category, articles, query
    
async def generate_read_request(validator_db_manager):

    user_id, organization_id, namespace_id, category, pageids = validator_db_manager.get_random_unit_ids()
    
    pageid = random.choice(pageids)
    
    content = get_wiki_article_content_with_pageid(pageid)
    
    llm_client = openai.OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        max_retries=3,
    )
    
    query_content = generate_query_content(llm_client, content)
    
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

async def generate_update_request(article_size, validator_db_manager):
    
    user_id, organization_id, namespace_id, category, pageids = validator_db_manager.get_random_unit_ids()
    
    articles = wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][len_limit])
    
    version = get_version() 
    
    # performs = ['ADD', 'REPLACE']
    # perform = random.choice(performs)
    
    query = UpdateSynapse(
        version = version,
        type = 'UPDATE',
        perform = "ADD",
        user_id = user_id,
        organization_id = organization_id,
        namespace_id = namespace_id,
        index_data = contents,
    )
    
    return category, articles, query
    
async def generate_delete_request(validator_db_manager):
    
    user_id, organization_id, namespace_id, category, pageids = validator_db_manager.get_random_unit_ids()
    
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
        "You are an embedding evaluator. Your task is to generate a query from the given original content to assess how well the embedding engines perform.",
        "You will be provided with the original content as your source of information. Your job is to create a summarized version of this content.",
        "This summary will be used to evaluate the performance quality of different embedding engines by comparing the embeddings of the query content with the results from each engine.",
    )
    prompt += content
    prompt += (
        "Generate a summary of the original content using approximately 700-900 characters."
        "Provide only the generated summary in plain text, without any additional context, explanation, or formatting. single and double quotes or new lines."
    )

    bt.logging.debug(f"Prompt: {prompt}")

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
            f"generation questions LLM response: {output.choices[0].message.content}"
        )
        bt.logging.debug(
            f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
        )
        return output.choices[0].message.content
    except Exception as e:
        bt.logging.error(f"Error during LLM completion: {e}")
        bt.logging.debug(print_exception(type(e), e, e.__traceback__))
        

if __name__ == '__main__':
    print(len_limit)
    miner_uid = 15
    validator_db_manager = ValidatorDBManager(miner_uid)
    request = generate_create_request(validator_db_manager, 3)
    print(request[3])
    print(request[3].__dict__)