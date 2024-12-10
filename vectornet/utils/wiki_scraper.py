import aiohttp
import asyncio
from datetime import datetime
import re
import logging
import bittensor as bt
import yaml
import httpx
from typing import Tuple
async def get_wiki_content_for_page(pageid: int) -> Tuple[str, str]:
    """
    Get the content for a Wikipedia page by the page ID asynchronously.

    Args:
        pageid (int): The ID of the Wikipedia page to get the content for.

    Returns:
        Tuple[str, str]: The content and title of the Wikipedia page.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "pageids": pageid,
                "prop": "extracts",
                "explaintext": "true",
                "exsectionformat": "plain",
            },
        ) as response:
            data = await response.json()
            page = data["query"]["pages"][str(pageid)]
            return page["extract"], page["title"]


async def sync_articles():
    bt.logging.debug(f"syncing articles")
    articles = []

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmpageid": "8966941",
                "cmprop": "ids",
                "cmlimit": "max",
            },
        )
        response = res.json()

        articles.extend(
            [page["pageid"] for page in response["query"]["categorymembers"]]
        )
        continuation = response.get("continue")
        while continuation is not None:
            res = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "list": "categorymembers",
                    "cmpageid": "8966941",
                    "cmprop": "ids",
                    "cmlimit": "max",
                    "cmcontinue": continuation.get("cmcontinue"),
                },
            )
            response = res.json()
            continuation = response.get("continue")
            articles.extend(
                [
                    page["pageid"]
                    for page in response["query"]["categorymembers"]
                ]
            )
    with open('result_wiki.txt', 'w', encoding='utf-8') as f:

        f.write(f"{articles}\n")  # Write each result as a dictionary

    
if __name__ =="__main__":
    asyncio.run(sync_articles())
    # asyncio.run(get_wiki_content_for_page(23284357))