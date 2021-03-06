from discord.ext.commands import Cog, command, cooldown, BucketType
from discord import Embed, File

from ..db import db

from random import shuffle, randint

suits = ("Sabers","Flasks","Coins","Staves")
ranks = ('2','3','4','5','6','7','8','9','10','11','Commander','Mistress','Master','Ace')
values = {
    '2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,
    '11':11,'Commander':12,'Mistress':13,'Master':14,'Ace':15
    }

TARGET = 23



def update_points(uid):
	newpoints = db.field("SELECT XP FROM exp WHERE UserID = ?",uid)
	points = db.field("SELECT a_points FROM achievements WHERE UserID = ?",uid)
	if points == None:
		db.field("INSERT INTO achievements (UserID, a_points) VALUES (?, ?)",uid,newpoints)
	elif newpoints > points:
		db.field("UPDATE achievements SET a_points = ? WHERE UserID = ?",newpoints,uid)

def hilo_new(player):
    pcards = ""
    for i in range(len(player.cards)):
        pcards+=f"Card **{i+1}**: {player.cards[i]}\n\n"
        card = values[str(player.cards[i]).split()[0]]
    return pcards, card


def hit(deck,hand):
    hand.add_card(deck.deal())
    hand.adjust_for_ace()
    
def show_players(Mbed,player,dealer):
	pcards = ""
	for i in player.cards:
		pcards+=str(i)+'\n'
	Mbed.add_field(name="Players Hand",value=f"{pcards}\nValue: {player.value}")
	Mbed.add_field(name="Dealers Hand",value=f"<card hidden>\n<card hidden>")

def show_all(Mbed,player,dealer):
	pcards = ""
	dcards = ""
	for i in player.cards:
		pcards+=str(i)+'\n'
	for i in dealer.cards:
		dcards+=str(i)+'\n'
	Mbed.add_field(name="Players Hand",value=f"{pcards}\nValue: {player.value}")
	Mbed.add_field(name="Dealers Hand",value=f"{dcards}\nValue: {dealer.value}")

def player_busts(Mbed,player,dealer):
	Mbed.description = "Player busts!"
	Mbed.colour = 0xFF0000

def player_wins(Mbed,player,dealer):
	Mbed.description = "Player wins!"
	Mbed.colour = 0x00FF00

def dealer_busts(Mbed,player,dealer):
	Mbed.description = "Dealer went bust!"
	Mbed.colour = 0x00FF00

def dealer_wins(Mbed,player, dealer):
	Mbed.description = "Dealer wins!"
	Mbed.colour = 0xFF0000

def push(Mbed,player,dealer):
	Mbed.colour = 0xFFA500
	Mbed.description = "Tie!"

class Card:
	def __init__(self,suit,rank):
		self.suit = suit
		self.rank = rank

	def __str__(self):
		return self.rank + ' of ' + self.suit

class Deck:
    def __init__(self):
        self.deck = list()
        for suit in suits:
            for rank in ranks:
                self.deck.append(Card(suit,rank))
        shuffle(self.deck)

    def __str__(self):
        deck_comp = str()
        for card in self.deck:
            deck_comp += "\n"+card.__str__()
        return "The deck has: "+deck_comp


    def deal(self):
        single_card = self.deck.pop()
        return single_card

class Hand:
    def __init__(self):
        self.cards = list()
        self.value = 0
        self.aces = 0

    def add_card(self,card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == 'Ace':
            self.aces += 1

    def adjust_for_ace(self):
        while self.value > TARGET and self.aces:
            self.value -= 14
            self.aces -= 1

class sabacc(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="sabacc",aliases=["blackjack","sabbac","sabbacc","sabac"])
	async def blackjack(self,ctx, bet: int):
		with open("./data/usage/sabacc.0",'r+') as f:
			count = int(f.read())
			f.seek(0)
			f.truncate()
			f.write(str(count+1))

		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", ctx.author.id)
		if xp == None:
			await ctx.send("You don't have any galactic points! Use `roll` to gain your first.")
		elif int(xp) < bet:
			await ctx.send("You don't have enough galactic points to make that bet!")
		elif bet < 1:
			await ctx.send("You must bet at least 1 galactic point to play!")
		else:
			db.field("UPDATE exp SET XP = ? WHERE UserID = ?",xp-bet,ctx.author.id)
			Mbed = Embed(colour=0x7289DA,title="Sabacc",description="Get as close to 23 as you can.\n`hit` or `stand`?")

			loss = False
			player = Hand()
			dealer = Hand()
			deck = Deck()

			for i in range(2):
				player.add_card(deck.deal())
				dealer.add_card(deck.deal())

			while player.value > 23:
				player = Hand()
				player.add_card(deck.deal())
				player.add_card(deck.deal())

			while dealer.value > 23:
				dealer = Hand()
				dealer.add_card(deck.deal())
				dealer.add_card(deck.deal())

			show_players(Mbed,player,dealer)
			msg = await ctx.send(embed=Mbed)

			while True:
	
				def check(m):
					return (m.content.lower() == 'hit' or m.content.lower() == 'stand') and m.channel == ctx.channel and m.author == ctx.author

				resp = await self.bot.wait_for('message',check=check)

				if resp.content.lower() == 'hit':
					player.add_card(deck.deal())
					player.adjust_for_ace()
					Mbed = Embed(colour=0x7289DA,title="Sabacc",description="Get as close to 23 as you can.\n`hit` or `stand`?")
					show_players(Mbed,player,dealer)
					await msg.edit(embed=Mbed)

				elif resp.content.lower() == 'stand':
					break

				if player.value > TARGET:
					Mbed = Embed(colour=0xFF0000,title="Sabacc",description="You went bust!")
					show_all(Mbed,player,dealer)
					loss = True
					await msg.edit(embed=Mbed)
					break
			if player.value <= TARGET:
				Mbed = Embed(colour=0x7289DA,title="Sabacc")
				while dealer.value < randint(14,17):
					dealer.add_card(deck.deal())
					dealer.adjust_for_ace()
				show_all(Mbed,player,dealer)

				if dealer.value > TARGET:
					dealer_busts(Mbed,player,dealer)

				elif dealer.value > player.value:
					dealer_wins(Mbed,player,dealer)
					loss = True

				elif dealer.value < player.value:
					player_wins(Mbed,player,dealer)

				else:
					push(Mbed,player,dealer)
					loss = 'Tie'

				await msg.edit(embed=Mbed)

				
			if loss == True:
				db.field("UPDATE exp SET XP = ? WHERE UserId = ?", xp-bet, ctx.author.id)
				await ctx.send(f"You lost `{bet}` galactic points, bringing your total to `{xp-bet}`!")
				with open("./library/resources/total_lost.0",'r') as f:
					total_lost = int(f.read())
				with open("./library/resources/total_lost.0",'w') as f:
					f.write(str(total_lost+bet))
			elif loss == 'Tie':
				await ctx.send("Tie! Your points were returned to you.")
				db.field("UPDATE exp SET XP = ? WHERE UserID = ?",xp,ctx.author.id)
			else:
				db.field("UPDATE exp SET XP = ? WHERE UserId = ?", xp+bet, ctx.author.id)
				await ctx.send(f"You won `{bet}` galactic points, bringing your total to `{xp+bet}`!")
			update_points(ctx.author.id)

	@command(name="sabaccrules",aliases=["sabacrules","sabbacrules","sabbaccrules"])
	async def sabbacrules(self,ctx):
		await ctx.send(file=File(fp="./library/resources/Sabacc_Rules.png",filename="rules.png"))	

	@command(name="hilo", aliases=["HiLo","highlow","higherlower"])
	async def hilo(self,ctx, bet: int):
		with open("./data/usage/hilo.0",'r+') as f:
			count = int(f.read())
			f.seek(0)
			f.truncate()
			f.write(str(count+1))

		xp = db.field("SELECT XP FROM exp WHERE UserID = ?", ctx.author.id)
		if xp == None:
			await ctx.send("You don't have any galactic points! Use `roll` to gain your first.")
		elif int(xp) < bet:
			await ctx.send("You don't have enough galactic points to make that bet!")
		elif bet < 1:
			await ctx.send("You must bet at least 1 galactic point to play!")
		else:
			db.field("UPDATE exp SET XP = ? WHERE UserID = ?",xp-bet,ctx.author.id)

			Mbed = Embed(colour=0x7289DA,title="Higher or Lower",description="Guess whether the next card will be higher or lower!\n`Hi` or `Lo`")
			hand = Hand()
			deck = Deck()

			hand.add_card(deck.deal())
			cards, val = hilo_new(hand)
			Mbed.add_field(name="Cards",value=cards+"Value: "+str(val))
			msg = await ctx.send(embed=Mbed)
			win = False
			draw = False
			for i in range(2):
				def check(m):
					return (m.content.lower() in ['higher','hi'] or m.content.lower() in ['lower','lo','low']
						) and m.channel == ctx.channel and m.author == ctx.author

				resp = await self.bot.wait_for('message',check=check)

				prev_val = val
				hand.add_card(deck.deal())
				cards, val = hilo_new(hand)

				if val == prev_val:
				    draw = True
				elif val > prev_val and resp.content.lower() in ['higher','hi']:
				    win = True
				    draw = False
				elif val < prev_val and resp.content.lower() in ['lower','lo','low']:
				    win = True
				    draw = False
				else:
				    win = False
				    draw = False
				    break

				Mbed = Embed(colour=0x7289DA,title="Higher or Lower",description="Guess whether the next card will be higher or lower!\n`Hi` or `Lo`")
				Mbed.add_field(name="Cards",value=cards+"Value: "+str(val))

				await msg.edit(embed=Mbed)

			if draw == True:
				Mbed = Embed(colour=0xFFA500,title="Higher or Lower",description="Tie!")
				Mbed.add_field(name="Cards",value=cards)
				db.field("UPDATE exp SET XP = ? WHERE UserID = ?",xp,ctx.author.id)
				await ctx.send("Tie! Your points were returned to you.")

			elif win == False:
				Mbed = Embed(colour=0xFF0000,title="Higher or Lower",description="You lost!")
				Mbed.add_field(name="Cards",value=cards)
				db.field("UPDATE exp SET XP = ? WHERE UserId = ?", xp-bet, ctx.author.id)
				await ctx.send(f"You lost `{bet}` galactic points, bringing your total to `{xp-bet}`!")

			elif win == True:
				Mbed = Embed(colour=0x00FF00,title="Higher or Lower",description="You lost!")
				Mbed.add_field(name="Cards",value=cards)
				db.field("UPDATE exp SET XP = ? WHERE UserId = ?", xp+bet, ctx.author.id)
				await ctx.send(f"You won `{bet}` galactic points, bringing your total to `{xp+bet}`!")

			await msg.edit(embed=Mbed)



			



	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("sabacc")

def setup(bot):
	bot.add_cog(sabacc(bot))