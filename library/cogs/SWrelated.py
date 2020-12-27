from discord.ext.commands import Cog, command
from discord import Embed
from random import choice

quotes = []
with open("./library/resources/quotes.txt",'r',encoding="utf-8") as f:
	for quote in f.readlines():
		quotes.append(quote)

class SWrelated(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.qt = "placeholder"

	@command(name="quote", aliases=["qt"])
	async def quote(self,ctx):
		qt = choice(quotes).split(' — ')
		Mbed = Embed(colour=0x7289DA)
		Mbed.add_field(name=qt[1], value=qt[0])
		await ctx.send(embed=Mbed)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("SWrelated")

def setup(bot):
	bot.add_cog(SWrelated(bot))
