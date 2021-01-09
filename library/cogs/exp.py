from discord.ext.commands import Cog, CheckFailure, command, cooldown, BucketType
from discord import File, Member, Embed

from ..db import db

from datetime import datetime
from random import randint, choice
from PIL import Image, ImageDraw, ImageFont
from requests import get
from typing import Optional
from os import remove as delete_file
from uuid import uuid4

RANKS = [1,1,1,5,5,10,15,20,30,20,25,40,50,50,50,100,100,200]
CUMU_RANKS = [sum(RANKS[:i]) for i in range(1, len(RANKS)+1)]


def update_points(uid):
	newpoints = db.field("SELECT XP FROM exp WHERE UserID = ?",uid)
	points = db.field("SELECT a_points FROM achievements WHERE UserID = ?",uid)
	if points == None:
		db.field("INSERT INTO achievements (UserID, a_points) VALUES (?, ?)",uid,newpoints)
	elif newpoints > points:
		db.field("UPDATE achievements SET a_points = ? WHERE UserID = ?",newpoints,uid)


class Exp(Cog):
	def __init__(self, bot):
		self.bot = bot

	@cooldown(1, 1.5, BucketType.user)
	@command(name="rank")
	async def showexp(self, ctx, target: Optional[Member]):
		target = target or ctx.author
		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", target.id)
		if xp != None:
			update_points(target.id)
			lb = db.column("SELECT UserID FROM exp ORDER BY XP DESC")
			rank = lb.index(target.id)+1

			for i in range(len(CUMU_RANKS)):
				if rank <= CUMU_RANKS[i]:
					pos = len(CUMU_RANKS)+1-i
					break
				elif rank > CUMU_RANKS[-1]:
					pos = 1
					break

			pfp_uuid = str(uuid4())
			pfp = get(str(target.avatar_url).replace('.webp?size=1024','.png')).content
			with open(f"./library/resources/{pfp_uuid}.png","wb") as p:
				p.write(pfp)

			points = db.field("SELECT a_points FROM achievements WHERE UserID = ?",target.id)
			rscum = db.field("SELECT a_rebelscum FROM achievements WHERE UserID = ?",target.id)

			if points >= 100000:
				pImg = "p100000"
			elif points >= 10000:
				pImg = "p10000"
			elif points >= 1000:
				pImg = "p1000"
			elif points >= 100:
				pImg = "p100"
			else:
				pImg = "0"

			if rscum == None:
				rImg = "0"
			else:
				if rscum >= 1000:
					rImg = "r1000"
				elif rscum >= 250:
					rImg = "r250"
				elif rscum >= 50:
					rImg = "r50"
				elif rscum >= 10:
					rImg = "r10"
				else:
					rImg = "0"

			pImg = Image.open(f"./library/resources/achievements/{pImg}.png")
			rImg = Image.open(f"./library/resources/achievements/{rImg}.png")
			img = Image.open("./library/resources/rankp.png").resize((321,321))
			card = Image.open(f"./library/resources/rank_cards/{pos}.png")

			card.paste(img, (70,205))
			card.paste(pImg, (840,544))
			card.paste(rImg, (663,544))

			draw = ImageDraw.Draw(card)
			font = ImageFont.truetype("./library/resources/Neonmachine.ttf", size=50)
			colour = "rgb(0,0,0)"
			draw.text((420,205), f"Name: {target.name}\n\nRank: {rank}\n\nGalactic Points: {xp}", fill=colour, font=font)
			img_uuid = str(uuid4())
			card.save(f"./library/resources/{img_uuid}.png")

			await ctx.send(file=File(fp=f"./library/resources/{img_uud}.png",filename="rank.png"))

			delete_file(f"./library/resources/{img_uuid}.png")
			delete_file(f"./library/resources/{pfp_uuid}.png")

		else:
			await ctx.send("That user doesn't have any galactic points! Use `roll` to gain your first.")

##	@command(name="leaderboard", aliases=["lb"])
##	async def leaderboard(self, ctx):
##		lb_res = db.records("SELECT UserID,XP FROM exp ORDER BY XP DESC")
##		lb = list(lb_res)
##		print(lb)
##
##		Mbed = Embed(colour=0x7289DA)
##
##		top10 = ""
##		for i in range(10):
##			top10+=f"{i+1} - {lb[i][0]}, Points: {lb[i][1]}\n"
##		
##		Mbed.add_field(name=f"Top 10",value=top10)
##		Mbed.set_thumbnail(url=self.bot.user.avatar_url)
##
##		await ctx.send(embed=Mbed)

	@command(name="roll")
	@cooldown(1, 600, BucketType.user)
	async def roll(self, ctx):
		xp_add = randint(20,50)
		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", ctx.author.id)
		if xp == None:
			db.field("INSERT INTO exp (UserID, XP) VALUES (?, ?)", ctx.author.id, xp_add)
			await ctx.send(f"You gained `{xp_add}` galactic points, bringing your total to `{xp_add}`!")
		else:
			db.field("UPDATE exp SET XP = ? WHERE UserId = ?", xp+xp_add, ctx.author.id)
			await ctx.send(f"You gained `{xp_add}` galactic points, bringing your total to `{xp+xp_add}`!")
		update_points(ctx.author.id)

	@command(name="rebelscum",aliases=["rebel scum"])
	@cooldown(1,1800, BucketType.user)
	async def rebelscum(self,ctx):
		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", ctx.author.id)
		if xp == None:
			await ctx.send("You don't have any galactic points! Use `roll` to gain your first.")
		else:
			points = [randint(20,70),randint(20,70),-randint(1,25)]
			res = choice(points)

			Mbed = Embed()

			if res < 0:
				Mbed.colour = 0xFF0000
				Mbed.add_field(name="Failure.",value=f"You fired at the rebel scum, but missed. You lost `{-res}` galactic points. The Empire expects you to do better next time.")
			elif res > 0:
				Mbed.colour = 0x00FF00
				Mbed.add_field(name="Success!",value=f"You fired at the rebel scum with insane accuracy! You earned `{res}` galactic points! The Empire is pleased with you.")
			await ctx.send(embed=Mbed)
			db.field("UPDATE exp SET XP = ? WHERE UserID = ?",xp+res,ctx.author.id)
			rscum = db.field("SELECT a_rebelscum FROM achievements WHERE UserID = ?", ctx.author.id)
			if rscum == None:
				db.field("INSERT INTO achievements (UserID, a_rebelscum) VALUES (?, ?)", ctx.author.id, 1)
			else:
				db.field("UPDATE achievements SET a_rebelscum = ? WHERE UserID = ?",rscum+1,ctx.author.id)
			update_points(ctx.author.id)




	@Cog.listener()
	async def on_ready(self):
			self.bot.cogs_ready.ready_up("Exp")

def setup(bot):
	bot.add_cog(Exp(bot))


	