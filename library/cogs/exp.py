from discord.ext.commands import Cog, CheckFailure, command, cooldown, BucketType
from discord import File, Member

from ..db import db

from datetime import datetime
from random import randint
from PIL import Image, ImageDraw, ImageFont
from requests import get
from typing import Optional

RANKS = [1,1,1,5,5,10,15,20,30,20,25,40,50,50,50,100,100,200]
CUM_RANKS = [sum(RANKS[:i]) for i in range(1, len(RANKS)+1)]
class Exp(Cog):
	def __init__(self, bot):
		self.bot = bot


	@command(name="showexp")
	async def showexp(self, ctx, target: Optional[Member]):
		target = target or ctx.author
		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", target.id)
		if xp != None:
			lb = db.column("SELECT UserID FROM exp ORDER BY XP DESC")
			rank = lb.index(target.id)+1

			for i in range(len(CUM_RANKS)):
				if rank <= CUM_RANKS[i]:
					pos = len(CUM_RANKS)+1-i
					break
				elif rank > CUM_RANKS[-1]:
					pos = 1
					break

			pfp = get(str(target.avatar_url).replace('.webp?size=1024','.png')).content
			with open("./library/resources/rankp.png","wb") as p:
				p.write(pfp)

			img = Image.open("./library/resources/rankp.png").resize((321,321))
			card = Image.open(f"./library/resources/rank_cards/{pos}.png")

			card.paste(img, (70,205))

			draw = ImageDraw.Draw(card)
			font = ImageFont.truetype("./library/resources/Neonmachine.ttf", size=50)
			colour = "rgb(0,0,0)"
			draw.text((420,205), f"Name: {target.name}\n\nRank: {rank}\n\nGalactic Points: {xp}", fill=colour, font=font)

			card.save("./library/resources/rank.png")

			await ctx.send(file=File(fp="./library/resources/rank.png",filename="rank.png"))
		else:
			await ctx.send("That user doesn't have any galactic points! Use `roll` to gain your first.")

	@command(name="roll")
	@cooldown(1, 10, BucketType.user)
	async def roll(self, ctx):
		xp_add = randint(20,50)
		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", ctx.author.id)
		if xp == None:
			db.field("INSERT INTO exp (UserID, XP) VALUES (?, ?)", ctx.author.id, xp_add)
			await ctx.send(f"You gained `{xp_add}` galactic points, bringing your total to `{xp_add}`!")
		else:
			db.field("UPDATE exp SET XP = ? WHERE UserId = ?", xp+xp_add, ctx.author.id)
			await ctx.send(f"You gained `{xp_add}` galactic points, bringing your total to `{xp+xp_add}`!")


	@Cog.listener()
	async def on_ready(self):
			self.bot.cogs_ready.ready_up("Exp")

def setup(bot):
	bot.add_cog(Exp(bot))