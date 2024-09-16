import discord
import aiohttp
from bs4 import BeautifulSoup
import re

async def archive(interaction: discord.Interaction, query: str):
    search_url = f"https://starwars.fandom.com/wiki/Special:Search?query={query.replace(' ', '+')}"
    
    async with aiohttp.ClientSession() as session:
        search_response = await session.get(search_url)
        search_page = await search_response.text()

        soup = BeautifulSoup(search_page, 'lxml')
        search_result_link = soup.find(class_="unified-search__result__link")
        
        if not search_result_link:
            await interaction.response.send_message("No results found.")
            return
        
        page_url = search_result_link.get('href')
        page_response = await session.get(page_url)
        page_content = await page_response.text()

    page_soup = BeautifulSoup(page_content, 'lxml')

    embed = discord.Embed(colour=0x7289DA, url=page_url)
    embed.set_footer(text=page_url)

    for meta_tag in page_soup.find_all('meta'):
        if meta_tag.get('property') == 'og:image':
            embed.set_image(url=meta_tag.get('content'))

        if meta_tag.get('property') == 'og:description':
            description = meta_tag.get('content').replace(
                "Please update the article to reflect recent events, and remove this template when finished. ", '')
            if len(description) > 100:
                description += "..."
            embed.add_field(name='Description', value=description, inline=True)

        if meta_tag.get('property') == 'og:title':
            embed.set_author(name=meta_tag.get('content'), url=page_url)

    info = []
    for div in page_soup.find_all('div', {'data-source': True}):
        text = re.sub("[\[].*?[\]]", ", ", div.get_text().replace("color", "colour").replace('\n', ': **'))
        info.append(text[2:-6])

    while sum(len(i) for i in info) > 1024:
        info.pop()

    if info:
        embed.add_field(name='Information', value='\n'.join(info), inline=True)

    await interaction.response.send_message(embed=embed)
