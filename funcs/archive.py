import discord

import aiohttp
from bs4 import BeautifulSoup
import re

async def archive(interaction: discord.Interaction, query: str):

    url = "https://starwars.fandom.com/wiki/Special:Search?query={}".format(query.replace(' ','+'))

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            search_page = await resp.text()

    soup = BeautifulSoup(search_page, 'lxml')
    search_bar = soup.find(class_="unified-search__result__link")
    search_res = search_bar.get('href')

    async with aiohttp.ClientSession() as session:
        async with session.get(search_res) as resp:
            page = await resp.text()

    soup = BeautifulSoup(page, 'lxml')

    Mbed = discord.Embed(colour=0x7289DA, url = search_res)
    Mbed.set_footer(text=search_res)

    for ele in soup.find_all('meta'):
        if ele.get('property') == 'og:image':
            Mbed.set_image(url=ele.get('content'))

        if ele.get('property') == 'og:description':
            Mbed.add_field(name='Description',value=ele.get('content').replace(
                "Please update the article to reflect recent events, and remove this template when finished. ", '')+"...",inline=True)

        if ele.get('property') == 'og:title':
            Mbed.set_author(name=ele.get('content'),url=search_res)

    info = list()
    for ele in soup.find_all('div'):
        if ele.get('data-source') != None:
            info.append(re.sub(

                            "[\[].*?[\]]", ", ",ele.get_text().replace("color","colour").replace('\n',': **')

                            )[2:-6])
    while sum([len(i) for i in info])>1024:
        info = info[:-1]
    if info != []:
        Mbed.add_field(name='Information',value='\n'.join(info),inline=True)

    await interaction.response.send_message(embed=Mbed)