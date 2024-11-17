import aiohttp
import asyncio
from datetime import datetime
import re
import logging
import bittensor as bt
import yaml

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

wiki_categories = config['wiki_categories']

async def get_article_extracts(pageid):
    # print(pageid)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "pageids": pageid,
                "explaintext": "1",
                "format": "json"
            },
        ) as response:
            data = await response.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                # print(page)
                extract = page.get("extract", None)
                # Remove newlines, extra spaces, and quotes
                if extract:
                    cleaned_extract = re.sub(r'[\'\"\\\n]', '', re.sub(r'\s+', ' ', extract)).strip()
                return cleaned_extract if extract else None
            
async def get_articles_in_category(category, k):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": k,
                "format": "json"
            },
        ) as response:
            data = await response.json()
            # print(data)
            articles = []
            if 'query' in data and 'categorymembers' in data['query'] and len(data['query']['categorymembers']) != 0:
                for article in data['query']['categorymembers']:
                    # print(article)
                    pageid = article['pageid']
                    content = await get_article_extracts(pageid)  # Await the async function
                    # print(content)
                    articles.append({
                        'title': article['title'],
                        'pageid': article['pageid'],
                        'content': content,
                    })
            else:
                print("Wrong category name")
            return articles

async def get_articles_in_category_with_max_size(category):
    async with aiohttp.ClientSession() as session:
        articles = []
        continuation = None
        
        while True:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category,
                # "cmpageid": "8966941",
                "cmlimit": "max",  # Use max to get the maximum number of results per request
                "format": "json"
            }
            if continuation:
                # print("continuation is as :::  ", continuation)
                params['cmcontinue'] = continuation
            
            async with session.get("https://en.wikipedia.org/w/api.php", params=params) as response:
                data = await response.json()
                # print(data)
                if 'query' in data and 'categorymembers' in data['query']:
                    articles.extend(data['query']['categorymembers'])
                    continuation = data.get('continue', {}).get('cmcontinue')
                    
                    if not continuation:
                        break  # Exit the loop if there's no continuation token
                else:
                    break  # Exit the loop if the response is not as expected

        # Now, fetch extracts for all articles
        results = []
        for article in articles:
            pageid = article['pageid']
            # content = await get_article_extracts(pageid)  # Await the async function
            results.append({
                'title': article['title'],
                'pageid': pageid,
                # 'content': content,
            })
        # print(results)
        return results
    
async def get_random_articles(count):
    articles = []
    should_break = False
    while True:
        async with aiohttp.ClientSession() as session:
            params = {
                "action": "query",
                "list": "random",
                'cmtype': "page",
                "rnlimit": count,  # Number of random pages to retrieve
                "format": "json"
            }
            
            async with session.get("https://en.wikipedia.org/w/api.php", params=params) as response:
                data = await response.json()
                
                # print(data)
                if 'query' in data and 'random' in data['query']:
                    # for article in data['query']['categorymembers']:
                    #     print(article)
                    #     pageid = article['pageid']
                    #     content = await get_article_extracts(pageid)  # Await the async function
                    #     # print(content)
                    #     articles.append({
                    #         'title': article['title'],
                    #         'pageid': article['pageid'],
                    #         'content': content,
                    #     })                
                    
                    for page in data['query']['random']:
                        # print("pageid = ", page['id'])
                        content = await get_article_extracts(page['id'])
                        # print(content)
                        if content:    
                            articles.append({
                                'title': page['title'],
                                'pageid' : page['id'],
                                'content': content
                                })
                            if len(articles) >= count:
                                should_break = True
                                break
            if should_break == True:
                break
    return articles

async def wikipedia_scraper(k : int, category: str):
    
    start_time = datetime.now()
    category = "Category:" + category
    bt.logging.info(f"Selected Category: {category}")

    articles = await get_articles_in_category(category)
    bt.logging.info(f"Fetched {len(articles)} articles.")

    # with open('result_wiki.txt', 'w', encoding='utf-8') as f:
    #     for result in results:
    #         f.write(f"{result}\n")  # Write each result as a dictionary

    elasped_time = datetime.now() - start_time
    logging.info(elasped_time.total_seconds())
    print("wiki_contents are scraped correctly")
    # print(articles)
    return articles

async def get_wiki_article_content_with_pageid(pageid):
    content = await get_article_extracts(pageid)
    return content
 
# if __name__ == '__main__':
#     with open("bad_category.txt", "w", encoding = 'utf-8') as f:
#         for category in wiki_categories:
#             print(f"SELECTED CATEGORY: {category}")
#             articles = asyncio.run(wikipedia_scraper(3, category))
#             if len(articles) != 3:
#                 f.write(f"{category}\n")
#             for article in articles:
#                 if not article['content']:
#                     f.write(f"{category}\n")
#                 else:
#                     pass
#                     print(article['content'][:10])
#             print("*******************************************************************************************************************")

if __name__ == '__main__':
    articles = asyncio.run(get_random_articles(3))
    for article in articles:
        print(article)
        print("***************************")




pageid =  16812604
