import discord

from random import shuffle

from settings import games
from sabacc_stats import Stats

CPU_PLAYER_NAME = "C-3PO"

class SabaccGame:
    def __init__(self, player):
        self.deck = [i for i in range(-10, 11)] * 4
        shuffle(self.deck)
        self.player = player
        self.bot_hand = []
        self.player_hand = []
        self.player_stands = False
        self.game_over = False
        self.draw_count = 0
        self.stats = Stats(player.id)

    def draw_card(self, hand):
        card = self.deck.pop()
        hand.append(card)
        return card

    def start_game(self):
        self.draw_card(self.player_hand)
        self.draw_card(self.player_hand)
        self.draw_card(self.bot_hand)
        self.draw_card(self.bot_hand)

    def hand_total(self, hand):
        return sum(hand)

    def bot_turn(self):
        while sum(self.bot_hand) < 15 and not self.player_stands:
            self.draw_card(self.bot_hand)
        self.game_over = True

    def player_draw(self):
        if not self.game_over:
            if self.draw_count < 5:
                self.draw_card(self.player_hand)
                self.draw_count += 1
            if sum(self.player_hand) > 23 or sum(self.player_hand) < -23:
                self.game_over = True

    def player_stand(self):
        if not self.game_over:
            self.player_stands = True
            self.bot_turn()

    def get_winner(self):
        if self.game_over:
            player_total = sum(self.player_hand)
            bot_total = sum(self.bot_hand)
            player_distance = min(abs(23 - player_total), abs(-23 - player_total))
            bot_distance = min(abs(23 - bot_total), abs(-23 - bot_total))
            if player_distance < bot_distance:
                self.stats.increment_wins()
                return self.player.display_name
            else:
                self.stats.increment_losses()
                return CPU_PLAYER_NAME
        return None

    def format_p_hand(self):
        return " ".join([str(i) for i in self.player_hand])

    def format_b_hand(self):
        return " ".join([str(i) for i in self.bot_hand])



class DrawButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Draw", custom_id="draw")

    async def callback(self, interaction: discord.Interaction):
        game = games[interaction.user.id]
        game.player_draw()

        

        if game.draw_count >= 5:
            embed = discord.Embed(title="Maximum cards drawn!", description="Click Stand to end the game.", color=0x7289DA)
        else:
            embed = discord.Embed(title="Sabacc", color=0x7289DA)

        embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
        embed.add_field(name="Your Total", value=str(sum(game.player_hand)), inline=False)
        embed.add_field(name="Bot's Hand", value="??", inline=False)
        embed.add_field(name="Bot's Total", value="??", inline=False)

        embed.set_footer(text=game.stats.format_stats())

        embed.set_thumbnail(url="https://i.imgur.com/3Fa2eXV.png")



        await interaction.response.edit_message(embed=embed)

class StandButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stand", custom_id="stand")

    async def callback(self, interaction: discord.Interaction):
        game = games[interaction.user.id]
        game.player_stand()
        winner = game.get_winner()
        embed = discord.Embed(title="Game over!", description=f"Winner: {winner}", color=0x7289DA)

        embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
        embed.add_field(name="Your Total", value=str(sum(game.player_hand)), inline=False)
        embed.add_field(name="Bot's Hand", value=game.format_b_hand(), inline=False)
        embed.add_field(name="Bot's Total", value=str(sum(game.bot_hand)), inline=False)

        embed.set_footer(text=game.stats.format_stats())

        if winner == CPU_PLAYER_NAME:
            embed.set_thumbnail(url="https://i.imgur.com/bc0yumE.png")
        elif winner == interaction.user.display_name:
            embed.set_thumbnail(url="https://i.imgur.com/UNKFLb1.png")
            

        await interaction.response.edit_message(embed=embed)
