import discord
from random import shuffle
from pathlib import Path
import sys
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('SabaccGame')

sys.path.append(str(Path(__file__).resolve().parent.parent))

from lib.settings import games
from lib.sabacc_stats import Stats

CPU_PLAYER_NAME = "C-3PO"


class SabaccGame:
    MAX_DRAW_LIMIT = 5

    def __init__(self, player):
        self.deck = [i for i in range(-10, 11)] * 4
        shuffle(self.deck)
        self.player = player
        self.bot_hand = []
        self.player_hand = []
        self.player_stands = False
        self.game_over = False
        self.draw_count = 0
        self.bot_draw_count = 0 
        self.stats = Stats(player.id)

    def draw_card(self, hand):
        if len(hand) >= 12:
            logger.debug('Cannot draw more cards; absolute hand size limit reached.')
            return None
        if not self.deck:
            self.deck = [i for i in range(-10, 11)] * 4
            shuffle(self.deck)
            logger.debug('Deck was empty. Reshuffled the deck.')
        card = self.deck.pop()
        hand.append(card)
        logger.debug(f'Drew card: {card} | New hand: {hand}')
        return card

    def start_game(self):
        for _ in range(2):
            self.draw_card(self.player_hand)
            self.draw_card(self.bot_hand)
        logger.debug(f'Game started. Player Hand: {self.player_hand} | Bot Hand: {self.bot_hand}')

    def hand_total(self, hand):
        total = sum(hand)
        logger.debug(f'Calculated hand total for {hand}: {total}')
        return total

    def distance_from_target(self, total):
        distance = min(abs(23 - total), abs(-23 - total))
        logger.debug(f'Distance from target for total {total}: {distance}')
        return distance

    def should_draw(self, current_total):
        safe_min = -23 - current_total
        safe_max = 23 - current_total

        safe_cards = [card for card in self.deck if safe_min <= card <= safe_max]
        probability_safe = len(safe_cards) / len(self.deck) if self.deck else 0

        logger.debug(f'Bot should_draw assessment: Safe Cards={safe_cards}, Probability Safe={probability_safe:.2f}')

        return probability_safe > 0.5

    def bot_turn(self):
        logger.debug('Bot turn started.')
        while not self.game_over:
            bot_total = self.hand_total(self.bot_hand)
            player_total = self.hand_total(self.player_hand)

            bot_distance = self.distance_from_target(bot_total)
            player_distance = self.distance_from_target(player_total)

            if bot_distance > player_distance + 2:
                if self.bot_draw_count < self.MAX_DRAW_LIMIT and self.should_draw(bot_total):
                    logger.debug('Bot decides to draw (significantly worse).')
                    self.draw_card(self.bot_hand)
                    self.bot_draw_count += 1
                    logger.debug(f'Bot Draw Count: {self.bot_draw_count}')
                else:
                    logger.debug('Bot decides to stand (significantly worse but chose not to draw).')
                    break

            elif bot_distance > 1:
                if bot_total < 20 and self.bot_draw_count < self.MAX_DRAW_LIMIT and self.should_draw(bot_total):
                    logger.debug('Bot decides to draw (slightly worse and total < 20).')
                    self.draw_card(self.bot_hand)
                    self.bot_draw_count += 1
                    logger.debug(f'Bot Draw Count: {self.bot_draw_count}')
                else:
                    logger.debug('Bot decides to stand (slightly worse but chooses not to draw).')
                    break

            else:
                logger.debug('Bot decides to stand (close enough to target).')
                break

            bot_total_after_draw = self.hand_total(self.bot_hand)
            if bot_total_after_draw > 23 or bot_total_after_draw < -23:
                logger.debug('Bot busts after drawing.')
                self.game_over = True
                break

        logger.debug('Bot turn ended.')
        self.game_over = True

    def player_draw(self):
        if not self.game_over:
            if self.draw_count < self.MAX_DRAW_LIMIT:
                logger.debug('Player decides to draw a card.')
                self.draw_card(self.player_hand)
                self.draw_count += 1
                logger.debug(f'Player Draw Count: {self.draw_count}')
                if self.hand_total(self.player_hand) > 23 or self.hand_total(self.player_hand) < -23:
                    logger.debug('Player busts.')
                    self.game_over = True
            else:
                logger.debug('Player has reached the maximum number of additional draws.')
                self.game_over = True

        if self.draw_count >= self.MAX_DRAW_LIMIT or self.hand_total(self.player_hand) > 23 or self.hand_total(self.player_hand) < -23:
            logger.debug('Game over due to player draw limit or bust.')
            self.game_over = True

    def player_stand(self):
        if not self.game_over:
            logger.debug('Player stands. Bot\'s turn begins.')
            self.player_stands = True
            self.bot_turn()

    def get_winner(self):
        if self.game_over:
            player_total = self.hand_total(self.player_hand)
            bot_total = self.hand_total(self.bot_hand)
            player_distance = self.distance_from_target(player_total)
            bot_distance = self.distance_from_target(bot_total)

            logger.debug(f'Final Totals - Player: {player_total}, Bot: {bot_total}')
            logger.debug(f'Final Distances - Player: {player_distance}, Bot: {bot_distance}')

            if player_distance < bot_distance:
                logger.debug('Player wins.')
                self.stats.increment_wins()
                return self.player.display_name
            elif bot_distance < player_distance:
                logger.debug('Bot wins.')
                self.stats.increment_losses()
                return CPU_PLAYER_NAME
            else:
                logger.debug('Game is a tie.')
                self.stats.increment_ties()
                return "It's a tie!"
        return None

    def format_p_hand(self):
        return " ".join([str(i) for i in self.player_hand])

    def format_b_hand(self):
        return " ".join([str(i) for i in self.bot_hand])



class DrawButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Draw", style=discord.ButtonStyle.primary, custom_id="draw")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id not in games:
            await interaction.response.send_message("You don't have a game in progress.", ephemeral=True)
            return

        game = games[interaction.user.id]

        if game.game_over:
            await interaction.response.send_message("The game is already over.", ephemeral=True)
            return

        game.player_draw()

        if game.game_over:
            winner = game.get_winner()
            embed = discord.Embed(
                title="Game Over!",
                description=f"Winner: {winner}",
                color=0xFF0000 if winner == CPU_PLAYER_NAME else (0x00FF00 if winner == interaction.user.display_name else 0xFFFF00)
            )
            embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
            embed.add_field(name="Your Total", value=str(game.hand_total(game.player_hand)), inline=False)
            embed.add_field(name="C-3PO's Hand", value=game.format_b_hand(), inline=False)
            embed.add_field(name="C-3PO's Total", value=str(game.hand_total(game.bot_hand)), inline=False)
            embed.set_footer(text=game.stats.format_stats())

            if winner == CPU_PLAYER_NAME:
                embed.set_thumbnail(url="https://i.imgur.com/bc0yumE.png")
            elif winner == interaction.user.display_name:
                embed.set_thumbnail(url="https://i.imgur.com/UNKFLb1.png")
            else:
                embed.set_thumbnail(url="https://i.imgur.com/tie.png")

            disabled_draw = DrawButton()
            disabled_draw.disabled = True

            disabled_stand = StandButton()
            disabled_stand.disabled = True

            disabled_rules = RulesButton()
            disabled_rules.disabled = True

            view = discord.ui.View()
            view.add_item(disabled_draw)
            view.add_item(disabled_stand)
            view.add_item(disabled_rules)

            await interaction.response.edit_message(embed=embed, view=view)
            del games[interaction.user.id]
        else:
            embed = discord.Embed(title="Sabacc", color=0x7289DA)
            embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
            embed.add_field(name="Your Total", value=str(game.hand_total(game.player_hand)), inline=False)
            embed.add_field(name="C-3PO's Hand", value="??", inline=False)
            embed.add_field(name="C-3PO's Total", value="??", inline=False)
            embed.set_footer(text=game.stats.format_stats())
            embed.set_thumbnail(url="https://i.imgur.com/3Fa2eXV.png")

            view = discord.ui.View()
            view.add_item(self)
            view.add_item(StandButton())
            view.add_item(RulesButton())

            await interaction.response.edit_message(embed=embed, view=view)



class StandButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stand", style=discord.ButtonStyle.secondary, custom_id="stand")

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id not in games:
            await interaction.response.send_message("You don't have a game in progress.", ephemeral=True)
            return

        game = games[interaction.user.id]

        if game.game_over:
            await interaction.response.send_message("The game is already over.", ephemeral=True)
            return

        game.player_stand()
        winner = game.get_winner()

        embed = discord.Embed(
            title="Game Over!",
            description=f"Winner: {winner}",
            color=0xFF0000 if winner == CPU_PLAYER_NAME else (0x00FF00 if winner == interaction.user.display_name else 0xFFFF00)
        )
        embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
        embed.add_field(name="Your Total", value=str(game.hand_total(game.player_hand)), inline=False)
        embed.add_field(name="C-3PO's Hand", value=game.format_b_hand(), inline=False)
        embed.add_field(name="C-3PO's Total", value=str(game.hand_total(game.bot_hand)), inline=False)
        embed.set_footer(text=game.stats.format_stats())

        if winner == CPU_PLAYER_NAME:
            embed.set_thumbnail(url="https://i.imgur.com/bc0yumE.png")
        elif winner == interaction.user.display_name:
            embed.set_thumbnail(url="https://i.imgur.com/UNKFLb1.png")
        else:
            embed.set_thumbnail(url="https://i.imgur.com/tie.png")

        disabled_draw = DrawButton()
        disabled_draw.disabled = True

        disabled_stand = StandButton()
        disabled_stand.disabled = True

        disabled_rules = RulesButton()
        disabled_rules.disabled = True

        view = discord.ui.View()
        view.add_item(disabled_draw)
        view.add_item(disabled_stand)
        view.add_item(disabled_rules)

        await interaction.response.edit_message(embed=embed, view=view)
        del games[interaction.user.id]



class RulesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Rules", style=discord.ButtonStyle.primary, custom_id="rules")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Sabacc Rules", color=0x7289DA)
        embed.add_field(name="Goal", value="Achieve a hand total as close to **23** or **-23** as possible without exceeding these limits.", inline=False)
        embed.add_field(name="Gameplay", value=(
            "- Both players start with **two cards**.\n"
            "- **Draw:** Take another card from the deck to add to your hand.\n"
            "- **Stand:** End your turn, keeping your current hand.\n"
            "- **Winning:** After both players have finished drawing, the player whose hand total is closest to **23** or **-23** wins.\n"
            "- **Tie:** If both players are equally close to the target numbers, the game is a tie.\n"
            "- **Bust:** If a player's hand total exceeds **23** or drops below **-23**, they lose immediately.\n"
            "- **Max Draws:** You can draw a maximum of **five additional cards**."
        ), inline=False)
        
        embed.add_field(
            name="Deck Details",
            value=(
                "The deck consists of **80 cards** in total:\n"
                "- **Card Values:** Each card is numbered from **-10** to **10**.\n"
                "- **Quantity:** There are **4 copies** of each card value.\n"
                "- **Total Cards:** 21 unique card values × 4 copies each = 84 cards.\n\n"
                "**Gameplay Notes:**\n"
                "- At the start of the game, both players are dealt **2 cards** each.\n"
                "- Players can **draw up to 5 additional cards** during their turn."
            ),
            inline=False
        )
        
        embed.set_footer(text="Good luck!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

