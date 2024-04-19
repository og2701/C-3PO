import discord
from random import choice

quotes = []

with open("resources/quotes.txt", 'r') as f:
    quotes = f.read().splitlines()

async def quote(interaction: discord.Interaction):
    qt = choice(quotes).split(' — ')
    embed = discord.Embed(color=0x7289DA)
    embed.add_field(name=f"__**{qt[1]}**__", value=qt[0])
    await interaction.response.send_message(embed=embed)
