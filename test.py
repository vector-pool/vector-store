import aiohttp
import asyncio

async def get_category_info(category):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": category,
                "prop": "categories",
                "format": "json",
                "cllimit": "max"  # Get all categories
            },
        ) as response:
            data = await response.json()
            pages = data['query']['pages']
            parent_categories = []
            for page_id, page in pages.items():
                if 'categories' in page:
                    for cat in page['categories']:
                        parent_categories.append(cat['title'])
            return parent_categories

async def get_top_category(parent_categories):
    return parent_categories[0] if parent_categories else None

async def get_articles_in_category(category):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "100",  # Limit to 100 articles
                "format": "json"
            },
        ) as response:
            data = await response.json()
            articles = []
            if 'query' in data and 'categorymembers' in data['query']:
                for article in data['query']['categorymembers']:
                    articles.append({
                        'title': article['title'],
                        'pageid': article['pageid']
                    })
            return articles

async def get_article_content(pageid):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "pageids": pageid,
                "format": "json",
                "explaintext": "true"  # Change to string "true"
            },
        ) as response:
            data = await response.json()
            page = next(iter(data['query']['pages'].values()))
            return page.get('extract', '')

async def main():
    initial_category = "Category:0s BC"
    
    parent_categories = await get_category_info(initial_category)
    top_category = await get_top_category(parent_categories)
    
    articles = await get_articles_in_category(top_category)
    
    for article in articles:
        content = await get_article_content(article['pageid'])
        article['content'] = content  # Add content to article dict

    for article in articles:
        print({
            'title': article['title'],
            'content': article['content']
        })

if __name__ == '__main__':
    asyncio.run(main())
