import discord
import aiohttp
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

session = aiohttp.ClientSession()

async def fetch(url: str) -> str:
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"HTTP error occurred: {e}")
        return None

def parse_meta(page_soup: BeautifulSoup) -> dict:
    meta = {
        'image': None,
        'description': None,
        'title': None
    }
    og_image = page_soup.find('meta', property='og:image')
    og_description = page_soup.find('meta', property='og:description')
    og_title = page_soup.find('meta', property='og:title')
    
    if og_image:
        meta['image'] = og_image.get('content')
    if og_description:
        description = og_description.get('content').replace(
            "Please update the article to reflect recent events, and remove this template when finished. ", ''
        )
        meta['description'] = (description[:100] + '...') if len(description) > 100 else description
    if og_title:
        meta['title'] = og_title.get('content')
    
    return meta

def extract_information(page_soup: BeautifulSoup) -> str:
    info = []
    for div in page_soup.find_all('div', {'data-source': True}):
        text = re.sub(r"\[.*?\]", ", ", div.get_text())
        text = text.replace("color", "colour").replace('\n', ': **').strip(': **')
        if text:
            info.append(text)
    total_length = 0
    filtered_info = []
    for item in info:
        if total_length + len(item) + 1 > 1024:
            break
        filtered_info.append(item)
        total_length += len(item) + 1
    
    return '\n'.join(filtered_info)

async def archive(interaction: discord.Interaction, query: str):
    encoded_query = quote_plus(query)
    search_url = f"https://starwars.fandom.com/wiki/Special:Search?query={encoded_query}"
    
    search_page = await fetch(search_url)
    if not search_page:
        await interaction.response.send_message("Failed to fetch search results.")
        return

    soup = BeautifulSoup(search_page, 'lxml')
    search_result_link = soup.find(class_="unified-search__result__link")
    
    if not search_result_link or not search_result_link.get('href'):
        await interaction.response.send_message("No results found.")
        return
    
    page_url = search_result_link.get('href')
    page_content = await fetch(page_url)
    if not page_content:
        await interaction.response.send_message("Failed to fetch the page content.")
        return

    page_soup = BeautifulSoup(page_content, 'lxml')
    meta = parse_meta(page_soup)
    information = extract_information(page_soup)
    
    embed = discord.Embed(colour=0x7289DA, url=page_url)
    embed.set_footer(text=page_url)
    
    if meta['title']:
        embed.set_author(name=meta['title'], url=page_url)
    if meta['description']:
        embed.add_field(name='Description', value=meta['description'], inline=True)
    if meta['image']:
        embed.set_image(url=meta['image'])
    if information:
        embed.add_field(name='Information', value=information, inline=False)
    
    try:
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        await interaction.response.send_message("Failed to send embed. It might be too large.")
        print(f"Discord embed error: {e}")