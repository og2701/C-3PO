import discord
from discord import Embed

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from lib.settings import games
from lib.classes import SabaccGame, DrawButton, StandButton


async def sabacc(interaction: discord.Interaction):
    if interaction.user.id in games:
        game = games[interaction.user.id]
        if not game.game_over:
            await interaction.response.send_message("You already have a game in progress.")
            return
    game = SabaccGame(interaction.user)
    games[interaction.user.id] = game
    game.start_game()

    embed = discord.Embed(title="Sabacc", color=0x7289DA)

    embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
    embed.add_field(name="Your Total", value=str(sum(game.player_hand)), inline=False)
    embed.add_field(name="Bot's Hand", value="??", inline=False)
    embed.add_field(name="Bot's Total", value="??", inline=False)

    embed.set_thumbnail(url="https://i.imgur.com/3Fa2eXV.png")
    embed.set_footer(text=game.stats.format_stats())

    draw_button = DrawButton()
    stand_button = StandButton()

    view = discord.ui.View()
    view.add_item(draw_button)
    view.add_item(stand_button)

    await interaction.response.send_message(embed=embed, view=view)

    if game.game_over:
        for item in view.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=view)

async def sabacc_rules(interaction: discord.Interaction):
    embed = discord.Embed(title="Sabacc Rules", color=0x7289DA)
    embed.add_field(name="Goal", value="Get as close to 23 or -23 as possible without going over.")
    embed.add_field(name="Draw", value="Take another card from the deck.")
    embed.add_field(name="Stand", value="Stick with your current hand.")
    embed.add_field(name="Winning", value="If your total is closer to 23 or -23 than the dealer's")

    await interaction.response.send_message(embed=embed)