from discord.ext import commands, tasks
from discord.ext.commands import Cog

import dbl

class TopGG(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./library/resources/dbltoken.0",'r',encoding="utf-8") as tkn:
            self.token = tkn.read()
        self.dblpy = dbl.DBLClient(self.bot, self.token)
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        try:
            server_count = len(self.bot.guilds)
            await self.dblpy.post_guild_count(server_count)
            print("[i] Posted server count ({})".format(server_count))
            with open("./library/resources/voters.txt",'w',encoding="utf-8") as f:
                for i in await self.dblpy.get_bot_upvotes():
                    f.write(i["id"])
                    f.write('\n')
            print("[i] Updated voter list")

        except Exception as e:
            print('[!] Failed to post server count\n{}: {}'.format(type(e).__name__, e))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("DBL")


def setup(bot):
    bot.add_cog(TopGG(bot))