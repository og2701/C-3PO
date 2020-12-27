from discord.ext.commands import Cog, CheckFailure, command, has_permissions
from ..db import db

class other(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="prefix")
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

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("other")

def setup(bot):
	bot.add_cog(other(bot))