import aiohttp
import asyncio
from datetime import datetime, timezone
import random

wiki_categories = [
    'Almanacs', 'Atlases', 'Biographical dictionaries', 'Dictionaries', 'Encyclopedias', 
    'Glossaries', 'Handbooks and manuals', 'Lists', 'Medical manuals', 'Reference book stubs', 
    'Reference works in the public domain', 'Style guides', 'Trivia books', 'Web sites', 
    'Classics', 'Critical theory', 'Cultural anthropology', 'Clothing', 'Folklore', 
    'Food and drink culture', 'Food and drink', 'Language', 'Literature', 'Museology', 
    'Mythology', 'Philosophy', 'Popular culture', 'Science and culture', 'Traditions', 
    'Handicrafts', 'Celebrity', 'Censorship in the arts', 'Festivals', 'Humor', 
    'Literature', 'Museums', 'Parties', 'Poetry', 'Circuses', 'Dance', 'Film', 'Music', 
    'Opera', 'Storytelling', 'Theatre', 'Board games', 'Card games', 'Dolls', 'Puppetry', 
    'Puzzles', 'Role-playing games', 'Video games', 'Earth', 'World', 'Bodies of water', 
    'Cities', 'Communities', 'Continents', 'Countries', 'Deserts', 'Lakes', 'Landforms', 
    'Mountains', 'Navigation', 'Oceans', 'Populated places', 'Protected areas', 'Regions', 
    'Rivers', 'Subterranea', 'Territories', 'Towns', 'Villages', 'Health by country', 
    'Health care', 'Health law', 'Health promotion', 'Health standards', 'Hospitals', 
    'Occupational safety and health', 'Pharmaceutical industry', 'Pharmaceuticals policy', 
    'Safety', 'Africa', 'Asia', 'Europe', 'America', 'Activism', 'Agriculture', 'Arts', 
    'Aviation', 'Commemoration', 'Communication', 'Crime', 'Design', 'Education', 
    'Entertainment', 'Fictional activities', 'Fishing', 'Food and drink preparation', 
    'Government', 'Hunting', 'Industry', 'Leisure activities', 'Navigation', 'Observation', 
    'Performing arts', 'Physical exercise', 'Planning', 'Politics', 'Recreation', 
    'Religion', 'Human spaceflight', 'Sports', 'Trade', 'Transport', 'Travel', 
    'Underwater human activities', 'Underwater diving', 'War', 'Work', 'Clothing', 
    'Employment', 'Entertainment', 'Food and drink', 'Games', 'Health', 'Hobbies', 
    'Home', 'Income', 'Interpersonal relationships', 'Leisure', 'Love', 'Motivation', 
    'Personal development', 'Pets'
]


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

async def get_articles_in_category(category):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "categorymembers",
                "cmtitle": category,
                "cmlimit": "5",
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

async def wikipedia_scraper():
    
    start_time = datetime.now()
    print(start_time)
    # Choose a specific category
    # random_category = "Category:Theatre"  # Ensure the correct format
    random_category = "Category:" + random.choice(wiki_categories)
    print(f"Selected Category: {random_category}")

    # Fetch articles from the selected category
    articles = await get_articles_in_category(random_category)
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

if __name__ == '__main__':
    asyncio.run(wikipedia_scraper())
