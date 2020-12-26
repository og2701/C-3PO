from discord.ext.commands import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

PREFIX = "%"
OWNER_IDS = [404634271861571584]

class Bot(Bot):
	def __init__(self):
		self.PREFIX = PREFIX
		self.guild = None
		self.scheduler = AsyncIOScheduler()
		self.ready = False

		super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

		def run():
			self.VERSION = VERSION

			with open("./library/bot/token",'r',encoding="utf-8") as token:
				self.TOKEN = token.read()

			print("[i] Executing...")
			super().run(self.TOKEN, reconnect=True)

		async def on_connect():
			print("[i] Connected")
		async def on_disconnect():
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