from discord import Intents, Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import (Bot, CommandNotFound, Context, when_mentioned_or,
								 command, has_permissions, AutoShardedBot, CommandNotFound,
								 CommandOnCooldown, BadArgument, MissingRequiredArgument)

from ..db import db

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from glob import glob
from asyncio import sleep

OWNER_IDS = list()
COGS = [path.split("/")[-1][:-3] for path in glob("./library/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

with open("./library/resources/helpers.txt",'r',encoding="utf-8") as f:
	for i in f.readlines():
		OWNER_IDS.append(i)

def get_prefix(bot, message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	if prefix == None:
		db.field("INSERT INTO guilds (GuildID, Prefix) VALUES (?, ?)", message.guild.id, '%')
		return get_prefix(bot, message) 
	return when_mentioned_or(prefix)(bot, message)

class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f"-cogs-[i] {cog} ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])

class Bot(AutoShardedBot):
	def __init__(self):
		self.ready = False
		self.guild = None
		self.cogs_ready = Ready()
		self.scheduler = AsyncIOScheduler()
		

		db.autosave(self.scheduler)

		super().__init__(
			command_prefix=get_prefix,
			owner_ids=OWNER_IDS )

	def setup(self):
		for cog in COGS:
			self.load_extension(f"library.cogs.{cog}")
			print(f"-cogs-[i] Loaded {cog} cog")

	def run(self, version):
		self.VERSION = version
		print("[i] Running setup...")
		self.setup()

		with open("./library/bot/token.0",'r',encoding="utf-8") as tkn:
			self.TOKEN = tkn.read()

		print("[i] Executing...")
		super().run(self.TOKEN, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)
		self.stdout = self.get_channel(464133106497224708)

		if ctx.command is not None and ctx.guild is not None:
			if self.ready:
				await self.invoke(ctx)
				await self.stdout.send(f"{ctx.author.name} used {message.content} in {ctx.guild.name}")

	async def on_connect(self):
		print("[i] Connected")
	async def on_disconnect(self):
		print("[!] Disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("`There was an error!`")

		raise

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("One or more required arguments are missing.")

		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(f"That command is on cooldown. Try again in {exc.retry_after//60:,.0f} minutes.")
		elif hasattr(exc, "original"):

			if isinstance(exc.original, Forbidden):
				await ctx.send("I do not have permission to do that.")

			else:
				raise exc.original

		else:
			raise exc

	async def on_ready(self):
		self.scheduler.start()
		if not self.ready:
			if not self.cogs_ready.all_ready():
				await sleep(5)
			print("[i] Ready")
			self.ready = True


		else:
			print("[i] Reconnected")


	async def on_message(self,message):
		if not message.author.bot:
			await self.process_commands(message)

bot = Bot()