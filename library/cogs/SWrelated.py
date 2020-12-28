from discord.ext.commands import Cog, command
from discord import Embed, File, Member

from . import dbl_update

from random import choice, randint
from urllib.request import urlopen, urlretrieve
from lxml.etree import HTMLParser, parse
from requests import get
from bs4 import BeautifulSoup
from re import sub
from PIL import Image, ImageDraw, ImageFont

quotes = []
category_exc = [
			   	[

				   	['birth','death','species','gender','height','mass','hair',
					'eyes','skin','type','creators','value','shape','size',
					'region','sector','system','terrain','manufacturer','model',
					'length','class','cost','crew','passengers','designation'],

					['colour','terrain','Average','Organization','Native','Position type']

				],

			   	['masters','apprentices','owners','ledby','headquarters',
			   	 'locations','leader','commander']
			   ]

with open("./library/resources/quotes.txt",'r',encoding="utf-8") as f:
	for quote in f.readlines():
		quotes.append(quote)

def isvoter(query):
	with open("./library/resources/voters.txt",'r',encoding="utf-8") as f:
		if str(query)+'\n' in f.readlines():
			return True
		else:
			return False

class SWrelated(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="quote", aliases=["qt"])
	async def quote(self,ctx):
		qt = choice(quotes).split(' — ')
		if isvoter(ctx.author.id):
			colour = 0xE5B233
		else:
			colour = 0x7289DA
		Mbed = Embed(colour=colour)
		Mbed.add_field(name=qt[1], value=qt[0])
		await ctx.send(embed=Mbed)

	@command(name="archive", aliases=["wiki"])
	async def archive(self,ctx, *query: str):
		print(1)
		query = ' '.join(list(query))
		print(query)
		searching = await ctx.send('Searching the archive...')
		if isvoter(ctx.author.id):
			colour = 0xE5B233
		else:
			colour = 0x7289DA
		async with ctx.typing():
			url = "https://starwars.fandom.com/wiki/Special:Search?query={}".format(query.replace(' ','+'))
			search = urlopen(url)
			tree = parse(search, HTMLParser())
			search_bar = tree.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "unified-search__result", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "unified-search__result__link", " " ))]')
			search_res = search_bar[0].text.replace('\n','').replace('\t','')

			page = urlopen(search_res)
			tree = parse(search, HTMLParser())
			soup = BeautifulSoup(page, 'lxml')

			Mbed = Embed(colour=colour, url = search_res)
			Mbed.set_footer(text=search_res)

			for ele in soup.find_all('meta'):
			    if ele.get('property') == 'og:image':
			        Mbed.set_image(url=ele.get('content'))
			        
			    if ele.get('name') == 'description':
			        Mbed.add_field(name='Description',value=ele.get('content'))

			    if ele.get('property') == 'og:title':
			        Mbed.set_author(name=ele.get('content'),url=search_res)

			info = list()
			for ele in soup.find_all('div'):
			            if ele.get('data-source') in category_exc[0]:
			                res = ele.get_text().replace('\n',' ').replace('color','colour')
			                res = sub("[\[].*?[\]]", "", res)
			                double = False
			                for i in category_exc[0][0]:
			                    if i in res:
			                        double = True
			                        break
			                if double:
			                    info.append(res
			                        .replace(' ','**',1)
			                        .replace(' ',':** ',2)
			                        .replace(':** ',' ',1)
			                        )
			                    
			                else:
			                    info.append(res
			                          .replace(' ','**',1)
			                          .replace(' ',':** ',1)
			                          )

			                
			            if ele.get('data-source') in category_exc[1]:
			                res = ele.get_text().replace('\n',' ')
			                res = sub("[\[].*?[\]]", ", ", res)
			                res = res.replace(' ','**',1).replace(' ',':** ',1)
			                res = res.split(',')[:-1]
			                info.append(', '.join(res))

			if info != []:
				Mbed.add_field(name='Information',value='\n'.join(info))
			await ctx.send(embed=Mbed)
			await searching.delete()

	@command(name="duel", aliases=["fight"])
	async def duel(self, ctx, member: Member):
		pfp1 = get(str(ctx.author.avatar_url).replace('.webp?size=1024','.png')).content
		pfp2= get(str(member.avatar_url).replace('.webp?size=1024','.png')).content

		with open("./library/resources/p1.png","wb") as p:
			p.write(pfp1)
		with open("./library/resources/p2.png","wb") as p:
			p.write(pfp2)

		if isvoter(member.id) and isvoter(ctx.author.id):
			image = Image.open("./library/resources/duel/both.png")
		elif isvoter(member.id):
			image = Image.open("./library/resources/duel/right.png")
		elif isvoter(ctx.author.id):
			image = Image.open("./library/resources/duel/left.png")
		else:
			image = Image.open("./library/resources/duel/none.png")

		draw = ImageDraw.Draw(image)
		colour = 'rgb(255,255,255)'
		font = ImageFont.truetype("./library/resources/Neonmachine.ttf", size=45)

		choice = randint(0,1)
		if choice == 0:
			draw.text((75,475,50), "Winner!", fill=colour, font=font)
		elif choice == 1:
			draw.text((1060,475,50), "Winner!", fill=colour, font=font)

		image1 = Image.open("./library/resources/p1.png").resize((200,200))
		image2 = Image.open("./library/resources/p2.png").resize((200,200))
		image.paste(image1,(75,275))
		image.paste(image2,(1060,275))
		image.save("./library/resources/duel.png")

		await ctx.send(file=File(fp="./library/resources/duel.png",filename="duel.png"))

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("SWrelated")

def setup(bot):
	bot.add_cog(SWrelated(bot))
