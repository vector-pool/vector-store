from vectornet.wiki_integraion.wiki_scraper import wikipedia_scraper


def generate_create_request(article_size = 30):
    len_limit = 31e4
    
    
    articles = wikipedia_scraper(k = article_size)
    contents = []
    for article in articles:
        contents.append(article['content'][len_limit])
def generate_read_request():
    pass

def generate_update_request():
    pass

def generate_delete_request():
    pass