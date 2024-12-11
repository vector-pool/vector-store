import aiohttp
import asyncio
from datetime import datetime
import re
import logging
import bittensor as bt
import yaml
from typing import Optional, Any, Callable
from functools import partial

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

wiki_categories = config['wiki_categories']

async def retry_async_request(func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries - 1:  # Last attempt
                raise  # Re-raise the last exception
            bt.logging.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    return None

async def get_article_extracts(pageid):
    async def _make_request(session, pageid):
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "pageids": pageid,
                "explaintext": "1",
                "format": "json"
            },
            timeout = 10,
        ) as response:
            data = await response.json()
            pages = data.get("query", {}).get("pages", {})
            if pages:    
                for page in pages.values():
                    extract = page.get("extract", None)
                    if extract:
                        cleaned_extract = re.sub(r'[\'\"\\\n]', '', re.sub(r'\s+', ' ', extract)).strip()
                        return cleaned_extract
            return None

    async with aiohttp.ClientSession() as session:
        return await retry_async_request(_make_request, session, pageid)

async def get_articles_in_category(category, k):
    async def _make_request(session, category, k):
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
            return await response.json()

    async with aiohttp.ClientSession() as session:
        data = await retry_async_request(_make_request, session, category, k)
        articles = []
        if 'query' in data and 'categorymembers' in data['query'] and len(data['query']['categorymembers']) != 0:
            for article in data['query']['categorymembers']:
                pageid = article['pageid']
                content = await get_article_extracts(pageid)
                articles.append({
                    'title': article['title'],
                    'pageid': article['pageid'],
                    'content': content,
                })
        else:
            print("Wrong category name")
            return None
        return articles

async def get_articles_in_category_with_max_size(category):
    async def _make_request(session, params):
        async with session.get("https://en.wikipedia.org/w/api.php", params=params) as response:
            return await response.json()

    async with aiohttp.ClientSession() as session:
        articles = []
        continuation = None
        
        while True:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "max",
                "format": "json"
            }
            if continuation:
                params['cmcontinue'] = continuation
            
            data = await retry_async_request(_make_request, session, params)
            if 'query' in data and 'categorymembers' in data['query']:
                articles.extend(data['query']['categorymembers'])
                continuation = data.get('continue', {}).get('cmcontinue')
                
                if not continuation:
                    break
            else:
                break

        results = []
        for article in articles:
            pageid = article['pageid']
            results.append({
                'title': article['title'],
                'pageid': pageid,
            })
        return results

async def get_random_articles(count, min_len):
    async def _make_request(session, params):
        async with session.get("https://en.wikipedia.org/w/api.php", params=params) as response:
            return await response.json()

    articles = []
    should_break = False
    while True:
        async with aiohttp.ClientSession() as session:
            params = {
                "action": "query",
                "list": "random",
                'cmtype': "page",
                "rnlimit": count,
                "format": "json"
            }
            
            data = await retry_async_request(_make_request, session, params)
            if 'query' in data and 'random' in data['query']:
                for page in data['query']['random']:
                    content = await get_article_extracts(page['id'])
                    if content:    
                        if len(content) >= min_len:
                            articles.append({
                                'title': page['title'],
                                'pageid': page['id'],
                                'content': content,
                                'length': len(content)
                            })
                            if len(articles) >= count:
                                should_break = True
                                break
            if should_break == True:
                break
    return articles

async def wikipedia_scraper(k: int, min_len: int, category: str):
    if category == "random":
        return await get_random_articles(k, min_len)
    else :
        bt.logging.error("category in current subnet structure should be random, not the certain one.")

async def get_wiki_article_content_with_pageid(pageid):
    content = await get_article_extracts(pageid)
    return content[:len_limit]

if __name__ == "__main__":
    articles = asyncio.run(wikipedia_scraper(5))
    with open('result_wiki.txt', 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(f"{article}\n\n, {len(article['content'])}\n")  # Write each result as a dictionary
    print(articles)
