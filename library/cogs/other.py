from discord.ext.commands import Cog, CheckFailure, command, has_permissions
from discord import Embed

from ..db import db

INVITE_URL = "https://discordapp.com/oauth2/authorize?client_id=495122047714721793&scope=bot&permissions=34816"
SUPPORT_SRVR = "https://discord.gg/vV24DgR"
VOTE_URL = "https://top.gg/bot/495122047714721793/vote"


help1 = list()
help2 = list()
help3 = list()
with open("./library/resources/help/swrelated.txt",'r', encoding="utf-8") as f:
	for i in f.readlines():
		help1.append(i)
with open("./library/resources/help/rank.txt",'r', encoding="utf-8") as f:
	for i in f.readlines():
		help2.append(i)
with open("./library/resources/help/misc.txt",'r', encoding="utf-8") as f:
	for i in f.readlines():
		help3.append(i)

def get_prefix(message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	return prefix

class other(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.remove_command("help")

	@command(name="help")
	async def help_cmd(self,ctx):
		with open("./data/usage/help.0",'r+') as f:
			count = int(f.read())
			f.seek(0)
			f.truncate()
			f.write(str(count+1))

		Mbed = Embed(colour=0x7289DA)
		Mbed.set_author(name=f"Current prefix: {get_prefix(ctx)}")
		Mbed.set_thumbnail(url=self.bot.user.avatar_url)
		Mbed.add_field(name="__Star Wars Related__",value=''.join(help1),inline=False)
		Mbed.add_field(name="__Rank system__",value=''.join(help2),inline=False)
		Mbed.add_field(name="__Other__",value=''.join(help3),inline=False)
		Mbed.set_footer(text="[optional] <required>")

		await ctx.send(embed=Mbed)

	@command(name="changeprefix", aliases=["prefix"])
	@has_permissions(manage_guild=True)
	async def change_prefix(self, ctx, new: str):
		if len(new) > 10:
			await ctx.send("`The prefix cannot be longer than 10 characters`")
		else:
			db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?",new,ctx.guild.id)
			await ctx.send(f"`Prefix set to {new}`")

	@change_prefix.error
	async def change_prefix_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("`Only users with manage server permissions can perform this command`")

	@command(name="invite", aliases=["inv"])
	async def invite(self, ctx):
		Mbed = Embed(colour=0x7289DA)
		Mbed.set_thumbnail(url=self.bot.user.avatar_url)
		Mbed.add_field(name="Add the bot to your server",value=INVITE_URL)
		Mbed.add_field(name="Support server",value=SUPPORT_SRVR)

		await ctx.send(embed=Mbed)

	@command(name="vote")
	async def vote(self, ctx):
		await ctx.send(VOTE_URL)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("other")

def setup(bot):
	bot.add_cog(other(bot))