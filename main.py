import discord
from discord import app_commands

from lib.commands import quote, archive, duel, lightsaber, sabacc_rules, sabacc, translate
from lib.settings import token, test_token

class aclient(discord.AutoShardedClient):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f"Logged in as {self.user}")

client = aclient()
tree = app_commands.CommandTree(client)
tree.sync
@tree.command(name="quote", description="Retrieves a random quote from the films")
async def quote_command(interaction: discord.Interaction):
    await quote(interaction)

@tree.command(name="archive", description="Searches the Star Wars wiki")
async def archive_command(interaction: discord.Interaction, query: str):
	await archive(interaction, query)

@tree.command(name = "duel", description = "Initiates a duel between two users")
async def duel_command(interaction: discord.Interaction, member: discord.Member):
	await duel(interaction, member)

@tree.command(name="translate", description="Translates a given message to Aurebesh")
async def translate_command(interaction: discord.Interaction, message: str):
	await translate(interaction, message)

@tree.command(name="lightsaber", description="Creates a custom lightsaber image")
async def lightsaber_command(interaction: discord.Interaction, emitter: int, switch: int, power_cell: int, crystal_chamber: int):
	await lightsaber(interaction, emitter, switch, power_cell, crystal_chamber)

@tree.command(name="sabacc_rules", description="Displays the rules for Sabacc")
async def sabacc_rules_command(interaction: discord.Interaction):
	await sabacc_rules(interaction)

@tree.command(name="sabacc", description="Starts a game of Sabacc")
async def sabacc_command(interaction: discord.Interaction):
	await sabacc(interaction)

tree.sync

client.run(token)


