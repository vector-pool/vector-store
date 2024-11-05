import yaml
import random

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
    
        
def generate_read_request():
    pass

def generate_update_request(article_size, miner_uid):
    
    namespace_data = get_namespace_data(miner_uid)
        
    user_id, organization_id, namespaace_id, category = random.choice(namespace_data)
    
    articles = wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][len_limit])
    
    version = get_version() 
    
    performs = ['ADD', 'REPLACE']
    perform = random.choice(performs)
    
    query = UpdateSynapse(
        version = version,
        type = 'UPDATE',
        perform = perform,
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
    
    