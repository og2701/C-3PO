import discord
from discord import Embed

from random import choice

quotes = []

with open("resources/quotes.txt",'r') as f:
    for quote in f.readlines():
        quotes.append(quote)

async def quote(interaction: discord.Interaction):
    qt = choice(quotes).split(' — ')
    colour = 0x7289DA
    embed = discord.Embed(color=colour)
    embed.add_field(name=f"__**{qt[1]}**__", value=qt[0])
    await interaction.response.send_message(embed=embed)