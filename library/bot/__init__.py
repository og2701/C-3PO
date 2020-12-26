from discord.ext.commands import Bot as BotBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler

PREFIX = "%"
OWNER_IDS = [404634271861571584]

class Bot(BotBase):
	def __init__(self):
		self.PREFIX = PREFIX
		self.ready = False
		self.guild = None
		self.scheduler = AsyncIOScheduler()

		super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

	def run(self, version):
		self.VERSION = version

		with open("./library/bot/token.0",'r',encoding="utf-8") as tkn:
			self.TOKEN = tkn.read()

		print("[i] Executing...")
		super().run(self.TOKEN, reconnect=True)

	async def on_connect(self):
		print("[i] Connected")
	async def on_disconnect(self):
		print("[!] Disconnected")

	async def on_ready(self):
		if not self.ready:
			print("[i] Ready")
			self.ready = True
		else:
			print("[i] Reconnected")

	async def on_message(self,message):
		pass

bot = Bot()