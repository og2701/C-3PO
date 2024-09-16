import discord
from discord import Embed
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from lib.settings import games
from lib.classes import SabaccGame, DrawButton, StandButton, RulesButton

async def sabacc(interaction: discord.Interaction):
    if interaction.user.id in games:
        game = games[interaction.user.id]
        if not game.game_over:
            await interaction.response.send_message("You already have a game in progress.", ephemeral=True)
            return
    game = SabaccGame(interaction.user)
    games[interaction.user.id] = game
    game.start_game()

    embed = discord.Embed(title="Sabacc", color=0x7289DA)
    embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
    embed.add_field(name="Your Total", value=str(sum(game.player_hand)), inline=False)
    embed.add_field(name="C-3PO's Hand", value="??", inline=False)
    embed.add_field(name="C-3PO's Total", value="??", inline=False)
    embed.add_field(name="Mode", value=game.mode_description, inline=False)
    embed.add_field(name="C-3PO's Draws", value=game.bot_draw_count, inline=False)

    embed.set_thumbnail(url="https://i.imgur.com/3Fa2eXV.png")
    embed.set_footer(text=game.stats.format_stats())

    draw_button = DrawButton()
    stand_button = StandButton()
    rules_button = RulesButton()

    view = discord.ui.View()
    view.add_item(draw_button)
    view.add_item(stand_button)
    view.add_item(rules_button)

    await interaction.response.send_message(embed=embed, view=view)

    if game.game_over:
        for item in view.children:
            item.disabled = True
        await interaction.edit_original_response(embed=embed, view=view)
