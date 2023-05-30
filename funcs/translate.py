import discord
from discord import File

from PIL import Image, ImageDraw, ImageFont
from os import remove as delete_file

async def translate(interaction: discord.Interaction, message: str):

    text = list()
    for i in range(0, len(message.split()), 4):
        text.append(' '.join(message.split()[i:i+4]))
    translated = '\n'.join(text)

    font = ImageFont.truetype("resources/Aurebesh.otf", size=30)
    width = font.getsize(max(text,key=len))[0]
    height = 23*(len(text))+5

    img = Image.new("RGBA", (width, height), (255,255,255,0))
    draw = ImageDraw.Draw(img)
    draw.text((0,0), translated, (0,0,0), font)
    img.save(f"resources/{interaction.user.id}.png")

    await interaction.response.send_message(file=File(fp=f"resources/{interaction.user.id}.png",filename="translation.png"))

    delete_file(f"resources/{interaction.user.id}.png")