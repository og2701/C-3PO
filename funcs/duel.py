import discord
from discord import File
from random import randint
from PIL import Image, ImageDraw, ImageFont
from uuid import uuid4
from requests import get
from os import remove as delete_file

async def duel(interaction: discord.Interaction, member: discord.Member):
    # Acknowledge the interaction immediately and defer the response
    await interaction.response.defer()

    pfp1 = get(interaction.user.avatar.url.replace('?size=1024', '')).content
    pfp2 = get(member.avatar.url.replace('?size=1024', '')).content

    p1_uuid = str(uuid4())
    with open(f"resources/{p1_uuid}.png", "wb") as p:
        p.write(pfp1)

    p2_uuid = str(uuid4())
    with open(f"resources/{p2_uuid}.png", "wb") as p:
        p.write(pfp2)

    image = Image.open("resources/duel/none.png")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("resources/Neonmachine.ttf", size=45)

    choice = randint(0, 1)
    winner_position = (75, 475) if choice == 0 else (1060, 475)
    draw.text(winner_position, "Winner!", fill='rgb(255,255,255)', font=font)

    image1 = Image.open(f"resources/{p1_uuid}.png").resize((200, 200))
    image2 = Image.open(f"resources/{p2_uuid}.png").resize((200, 200))
    image.paste(image1, (75, 275))
    image.paste(image2, (1060, 275))

    duel_uuid = str(uuid4())
    image.save(f"resources/{duel_uuid}.png")

    # Send the response after processing is complete
    await interaction.followup.send(file=discord.File(f"resources/{duel_uuid}.png", filename="duel.png"))

    delete_file(f"resources/{p1_uuid}.png")
    delete_file(f"resources/{p2_uuid}.png")
    delete_file(f"resources/{duel_uuid}.png")
