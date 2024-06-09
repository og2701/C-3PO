import discord
from discord import File
from PIL import Image, ImageDraw, ImageFont
from os import remove as delete_file
import io

async def translate(interaction: discord.Interaction, message: str):
    max_width = 800
    font = ImageFont.truetype("resources/Aurebesh.otf", size=30)

    def wrap_text(message, font, max_width):
        words = message.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width, _ = font.getbbox(word + ' ')[2:]
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
                
        lines.append(' '.join(current_line))
        return lines
    
    text_lines = wrap_text(message, font, max_width)
    translated = '\n'.join(text_lines)
    
    width = max_width
    height = sum(font.getbbox(line)[3] for line in text_lines) + 10 * len(text_lines)

    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    current_height = 0
    for line in text_lines:
        draw.text((0, current_height), line, (0, 0, 0), font)
        current_height += font.getbbox(line)[3] + 10

    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        await interaction.response.send_message(file=File(fp=image_binary, filename="translation.png"))
