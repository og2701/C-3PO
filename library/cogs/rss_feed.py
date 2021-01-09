from discord.ext.commands import Cog, command
from discord.ext import tasks
from discord import Embed, Client

from feedparser import parse


client = Client()

class RSS(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.SWnews.start()


	@tasks.loop(seconds=3600)
	async def SWnews(self):

		nf = parse("https://www.starwars.com/news/feed").entries[0]

		with open("./data/rss_feed.txt","r") as f:
			old_feed = f.read()
		
		if old_feed != str(nf):
			with open("./data/rss_feed.txt","w") as f:
				f.write(str(nf))

			Mbed = Embed(colour=0xE5B233, description=nf.summary+f"\n[Link to article]({nf.link})")

			Mbed.set_author(name=nf.title)
			Mbed.set_thumbnail(url=nf.media_thumbnail[0]["url"])
			Mbed.set_footer(text='Author: '+nf.author+' | Published: '+nf.published)

			try:
				await self.stdout.send(embed=Mbed)
			except AttributeError as exc:
				print(f"[!] {exc}")

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.stdout = self.bot.get_channel(797266342822412338)
			self.bot.cogs_ready.ready_up("RSS")
			self.SWnews.start()

def setup(bot):
	bot.add_cog(RSS(bot))
