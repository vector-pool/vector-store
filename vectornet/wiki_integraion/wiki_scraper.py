import aiohttp
import asyncio
from datetime import datetime, timezone
import random
import yaml


async def get_article_extracts(pageid):
    extracts = {}
    async with aiohttp.ClientSession() as session:
        print("pageids == ", pageid)
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
                extract = page.get("extract", "No extract available")
                extracts[page['pageid']] = extract if extract else "No extract available"
    
    return extracts

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
                    print(content)
                    articles.append({
                        'title': article['title'],
                        'pageid': article['pageid'],
                        'content': content,
                    })
            return articles

async def wikipedia_scraper(k : int, category: str):
    
    start_time = datetime.now()
    print(start_time)
    # Choose a specific category
    # random_category = "Category:Theatre"  # Ensure the correct format
    
    category = "Category:" + category
    print(f"Selected Category: {category}")

    # Fetch articles from the selected category
    articles = await get_articles_in_category(category, k)
    print(f"Fetched {len(articles)} articles.")

    # Write the articles to result.txt in dict format
    results = []
    for article in articles:
        results.append({
            'title': article['title'],
            'pageid': article['pageid'],
            'extract': article['content']
        })

    with open('result.txt', 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"{result}\n")  # Write each result as a dictionary

    print("Results have been written to result.txt.")
    elasped_time = datetime.now() - start_time
    print(datetime.now())
    print(elasped_time.total_seconds())

    return articles
 
if __name__ == '__main__':
    asyncio.run(wikipedia_scraper())
