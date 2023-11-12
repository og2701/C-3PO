import discord
from discord import app_commands
import logging
import json
from discord.ext import tasks

from lib.commands import quote, archive, duel, lightsaber, sabacc, translate
from lib.settings import token, test_token

logging.basicConfig(filename='command_usage.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

command_usage_counts = {
    "quote": 0,
    "archive": 0,
    "duel": 0,
    "translate": 0,
    "lightsaber": 0,
    "sabacc": 0
}

usage_file = 'command_usage.json'

def save_command_usage():
    with open(usage_file, 'w') as file:
        json.dump(command_usage_counts, file)

def load_command_usage():
    try:
        with open(usage_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return command_usage_counts

class aclient(discord.AutoShardedClient):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        global command_usage_counts
        command_usage_counts = load_command_usage()
        if not self.synced:
            await tree.sync()
            self.synced = True
            self.send_command_usage.start()
        print(f"Logged in as {self.user}")

    @tasks.loop(hours=24)
    async def send_command_usage(self):
        channel = self.get_channel(464133106497224708)
        if channel:
            embed = discord.Embed(title="Command Usage Statistics", color=0x00ff00)
            for command, count in command_usage_counts.items():
                embed.add_field(name=command.capitalize(), value=f"Used {count} times", inline=True)
            await channel.send(embed=embed)

    @send_command_usage.before_loop
    async def before_send_command_usage(self):
        await self.wait_until_ready()

client = aclient()
tree = app_commands.CommandTree(client)

def log_command_usage(command_name, user):
    command_usage_counts[command_name] += 1
    save_command_usage()
    logging.info(f"Command '{command_name}' used by {user} (ID: {user.id}). Count: {command_usage_counts[command_name]}")


client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(name="quote", description="Retrieves a random quote from the films")
async def quote_command(interaction: discord.Interaction):
    log_command_usage("quote", interaction.user)
    await quote(interaction)

@tree.command(name="archive", description="Searches the Star Wars wiki")
async def archive_command(interaction: discord.Interaction, query: str):
    log_command_usage("archive", interaction.user)
    await archive(interaction, query)

@tree.command(name = "duel", description = "Initiates a duel between two users")
async def duel_command(interaction: discord.Interaction, member: discord.Member):
    log_command_usage("duel", interaction.user)
    await duel(interaction, member)

@tree.command(name="translate", description="Translates a given message to Aurebesh")
async def translate_command(interaction: discord.Interaction, message: str):
    log_command_usage("translate", interaction.user)
    await translate(interaction, message)

@tree.command(name="lightsaber", description="Creates a custom lightsaber image")
async def lightsaber_command(interaction: discord.Interaction):
    log_command_usage("lightsaber", interaction.user)
    await lightsaber(interaction)

@tree.command(name="sabacc", description="Starts a game of Sabacc")
async def sabacc_command(interaction: discord.Interaction):
    log_command_usage("sabacc", interaction.user)
    await sabacc(interaction)

client.run(token)
