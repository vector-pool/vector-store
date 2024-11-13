import aiohttp
import asyncio
from datetime import datetime
import re
import logging

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
                print(page)
                extract = page.get("extract", "No extract available")
                # Remove newlines, extra spaces, and quotes
                cleaned_extract = re.sub(r'[\'\"\\\n]', '', re.sub(r'\s+', ' ', extract)).strip()
                return cleaned_extract if cleaned_extract else "No extract available"
            
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
            articles = []
            if 'query' in data and 'categorymembers' in data['query']:
                for article in data['query']['categorymembers']:
                    pageid = article['pageid']
                    content = await get_article_extracts(pageid)  # Await the async function
                    # print(content)
                    articles.append({
                        'title': article['title'],
                        'pageid': article['pageid'],
                        'content': content,
                    })
            return articles

async def wikipedia_scraper(k : int, category: str):
    
    start_time = datetime.now()
    category = "Category:" + category
    logging.info(f"Selected Category: {category}")

    articles = await get_articles_in_category(category, k)
    logging.info(f"Fetched {len(articles)} articles.")

    results = []
    for article in articles:
        results.append({
            'title': article['title'],
            'pageid': article['pageid'],
            'extract': article['content']
        })

    with open('result_wiki.txt', 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"{result}\n")  # Write each result as a dictionary

    elasped_time = datetime.now() - start_time
    logging.info(elasped_time.total_seconds())
    print("wiki_contents are scraped correctly")
    return articles

async def get_wiki_article_content_with_pageid(pageid):
    content = await get_article_extracts(pageid)
    return content
 
if __name__ == '__main__':
    asyncio.run(wikipedia_scraper(5, "Dance"))
