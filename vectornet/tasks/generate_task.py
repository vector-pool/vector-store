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

def generate_create_request(article_size = 30) -> CreateSynapse:
    
    len_limit = 31e4
    
    
    category = random.choice(wiki_categories)
    organization_name = random.choice(organization_names)
    user_name = random.choice(user_names)
    
    
    articles = wikipedia_scraper(article_size, category)
    contents = []
    for article in articles:
        contents.append(article['content'][len_limit])
    version = get_version
    return CreateSynapse(
        version = version,
        type = 'CREATE',
        user_name = user_name,
        organization_name = organization_name,
        namespace_name = category,
        index_data = contents,
    )
    
        
def generate_read_request():
    pass

def generate_update_request():
    pass

def generate_delete_request():
    pass