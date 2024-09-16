import discord
from discord import File
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import io
import textwrap
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_WIDTH = 800
FONT_SIZE = 30
PADDING = 20
LINE_SPACING = 10
BG_COLOR = (255, 255, 255, 255)
TEXT_COLOR = (0, 0, 0)
MAX_CHAR = 2000
FONT_PATH = Path(__file__).parent / 'resources' / 'Aurebesh.otf'

try:
    FONT = ImageFont.truetype(str(FONT_PATH), size=FONT_SIZE)
except IOError:
    FONT = ImageFont.load_default()
    logger.warning(f"Failed to load font at {FONT_PATH}, using default font.")

def wrap_text(message: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    lines = []
    paragraphs = message.split('\n')
    for para in paragraphs:
        wrapped = textwrap.wrap(para, width=100)
        for line in wrapped:
            while font.getsize(line)[0] > max_width:
                for i in range(len(line), 0, -1):
                    if font.getsize(line[:i])[0] <= max_width:
                        break
                lines.append(line[:i])
                line = line[i:]
            lines.append(line)
    return lines

def calculate_image_size(text_lines: list, font: ImageFont.FreeTypeFont, max_width: int, padding: int = PADDING, line_spacing: int = LINE_SPACING) -> tuple:
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + line_spacing
    height = line_height * len(text_lines) + padding * 2
    return max_width, height

def create_image(text_lines: list, font: ImageFont.FreeTypeFont, max_width: int, padding: int = PADDING, line_spacing: int = LINE_SPACING, bg_color: tuple = BG_COLOR, text_color: tuple = TEXT_COLOR) -> Image.Image:
    width, height = calculate_image_size(text_lines, font, max_width, padding, line_spacing)
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + line_spacing
    current_height = padding
    for line in text_lines:
        shadow_color = (100, 100, 100)
        draw.text((padding + 1, current_height + 1), line, shadow_color, font=font)
        draw.text((padding, current_height), line, text_color, font=font)
        current_height += line_height
    return img

async def translate(interaction: discord.Interaction, message: str):
    logger.info(f"Received message for translation: {message}")

    if len(message) > MAX_CHAR:
        await interaction.response.send_message(
            content=f"Your message is too long. Please limit it to {MAX_CHAR} characters.",
            ephemeral=True
        )
        logger.warning("Message exceeds maximum character limit.")
        return

    try:
        text_lines = wrap_text(message, FONT, MAX_WIDTH)
        logger.debug(f"Wrapped text lines: {text_lines}")
        img = create_image(text_lines, FONT, MAX_WIDTH)
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.response.send_message(
                content="Here is your translation:",
                file=File(fp=image_binary, filename="translation.png")
            )
            logger.info("Translation image sent successfully.")
    except Exception as e:
        logger.error(f"Error during translation: {e}", exc_info=True)
        await interaction.response.send_message(
            content=f"An error occurred while processing the translation: {e}",
            ephemeral=True
        )
