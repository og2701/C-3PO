import discord
from discord import app_commands, File, Embed

from os import remove as delete_file
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from lib.utils import merge

async def lightsaber(interaction: discord.Interaction, emitter: int, switch: int, power_cell: int, crystal_chamber: int):
    choices = [emitter, switch, power_cell, crystal_chamber]
    notInRange = any(choice < 1 or choice > 6 for choice in choices)

    if len(choices) != 4:
        await interaction.response.send_message("You need to include options for all 4 parts of the lightsaber\nExample: `/lightsaber 1 6 3 4`")
    elif notInRange:
        await interaction.response.send_message("Your options need to be between 1 and 6")
    else:
        merge(choices, interaction.user.id)
        await interaction.response.send_message(file=discord.File(fp=f"resources/{interaction.user.id}.png",filename="lightsaber.png"))
        delete_file(f"resources/{interaction.user.id}.png")