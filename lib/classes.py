import discord
from random import shuffle, randint
from lib.settings import games
from lib.sabacc_stats import Stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CPU_PLAYER_NAME = "C-3PO"

class SabaccGame:
    MAX_BOT_DRAWS = 5

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
        self.mode = self.select_mode()
        self.mode_description = self.get_mode_description()

    def select_mode(self):
        modes = ['Easy', 'Medium', 'Hard']
        selected_mode = modes[randint(0, 2)]
        logger.info(f"Selected game mode: {selected_mode}")
        return selected_mode

    def get_mode_description(self):
        descriptions = {
            'Easy': "Easy Mode: C-3PO draws cards randomly.",
            'Medium': "Medium Mode: C-3PO draws until a decent total is reached.",
            'Hard': "Hard Mode: C-3PO employs optimal strategy using probabilities."
        }
        return descriptions[self.mode]

    def draw_card(self, hand):
        if not self.deck:
            logger.info("Deck exhausted. Cannot draw more cards.")
            self.game_over = True
            return None
        card = self.deck.pop()
        hand.append(card)
        logger.info(f"Drew card: {card}. New total: {sum(hand)}")
        return card

    def start_game(self):
        for _ in range(2):
            self.draw_card(self.player_hand)
            self.draw_card(self.bot_hand)
        logger.info(f"Game started. Player's hand: {self.player_hand}, Bot's hand: {self.bot_hand}")

    def hand_total(self, hand):
        return sum(hand)

    def bot_turn(self):
        if self.mode == 'Easy':
            self.bot_turn_easy()
        elif self.mode == 'Medium':
            self.bot_turn_medium()
        elif self.mode == 'Hard':
            self.bot_turn_hard()
        self.game_over = True
        logger.info("Bot's turn ended.")

    def bot_turn_easy(self):
        while self.bot_draw_count < self.MAX_BOT_DRAWS and not self.player_stands:
            if randint(0, 1) == 1:
                self.draw_card(self.bot_hand)
                self.bot_draw_count += 1
                logger.info(f"Bot drew a card in Easy Mode. Draw count: {self.bot_draw_count}")
            else:
                logger.info("Bot decides to stop drawing in Easy Mode.")
                break

    def bot_turn_medium(self):
        logger.info(f"Draw count: {self.bot_draw_count}, Max draws: {self.MAX_BOT_DRAWS}, Bot's hand: {self.bot_hand}, Total: {sum(self.bot_hand)}")
        while self.bot_draw_count < self.MAX_BOT_DRAWS and sum(self.bot_hand) < 15 and not self.player_stands:
            self.draw_card(self.bot_hand)
            self.bot_draw_count += 1
            logger.info(f"Bot drew a card in Medium Mode. Draw count: {self.bot_draw_count}")

    def bot_turn_hard(self):
        player_total = sum(self.player_hand)
        while self.bot_draw_count < self.MAX_BOT_DRAWS:
            bot_total = sum(self.bot_hand)
            remaining_cards = self.deck

            logger.info(f"Player's final total: {player_total}")
            logger.info(f"C-3PO's current total in Hard Mode: {bot_total}")

            if (bot_total > player_total and bot_total <= 23) or (bot_total < player_total and bot_total >= -23):
                if abs(23 - bot_total) <= 3 or abs(-23 - bot_total) <= 3:
                    logger.info("C-3PO stops drawing as its total is close to target and beats the player.")
                    break

            distance_to_23 = 23 - bot_total
            distance_to_neg23 = -23 - bot_total

            logger.info(f"Distance to 23: {distance_to_23}")
            logger.info(f"Distance to -23: {distance_to_neg23}")

            beneficial_cards = [card for card in remaining_cards if (23 - bot_total) * card > 0 or (-23 - bot_total) * card > 0]
            beneficial_probability = len(beneficial_cards) / len(remaining_cards) if remaining_cards else 0

            logger.info(f"Probability of drawing a beneficial card: {beneficial_probability}")

            if beneficial_probability >= 0.5 or abs(distance_to_23) > 3 or abs(distance_to_neg23) > 3:
                self.draw_card(self.bot_hand)
                self.bot_draw_count += 1
                logger.info(f"C-3PO draws a card. New total: {sum(self.bot_hand)}")
            else:
                logger.info("C-3PO stops drawing due to low probability.")
                break




    def player_draw(self):
        if not self.game_over:
            if self.draw_count < 5:
                self.draw_card(self.player_hand)
                self.draw_count += 1
                logger.info(f"Player drew a card. Draw count: {self.draw_count}")
            else:
                logger.info("Player has reached the maximum number of draws.")
            if sum(self.player_hand) > 23 or sum(self.player_hand) < -23:
                logger.info("Player has busted.")
                self.game_over = True

    def player_stand(self):
        if not self.game_over:
            self.player_stands = True
            logger.info("Player stands. Bot will take its turn.")
            self.bot_turn()

    def get_winner(self):
        if self.game_over:
            player_total = sum(self.player_hand)
            bot_total = sum(self.bot_hand)
            player_distance = min(abs(23 - player_total), abs(-23 - player_total))
            bot_distance = min(abs(23 - bot_total), abs(-23 - bot_total))
            logger.info(f"Player Total: {player_total}, Bot Total: {bot_total}")
            logger.info(f"Player Distance: {player_distance}, Bot Distance: {bot_distance}")
            if player_distance < bot_distance:
                self.stats.increment_wins()
                logger.info("Player wins.")
                return self.player.display_name
            elif player_distance > bot_distance:
                self.stats.increment_losses()
                logger.info("Bot wins.")
                return CPU_PLAYER_NAME
            else:
                logger.info("It's a tie.")
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
        game = games.get(interaction.user.id)
        if not game or game.game_over:
            await interaction.response.send_message("No active game found.", ephemeral=True)
            return

        game.player_draw()

        if game.draw_count >= 5:
            embed = discord.Embed(
                title="Maximum cards drawn!",
                description="Click Stand to end the game.",
                color=0x7289DA
            )
        else:
            embed = discord.Embed(title="Sabacc", color=0x7289DA)

        embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
        embed.add_field(name="Your Total", value=str(sum(game.player_hand)), inline=False)
        embed.add_field(name="C-3PO's Hand", value="??", inline=False)
        embed.add_field(name="C-3PO's Total", value="??", inline=False)
        embed.add_field(name="Mode", value=game.mode_description, inline=False)

        embed.set_footer(text=game.stats.format_stats())
        embed.set_thumbnail(url="https://i.imgur.com/3Fa2eXV.png")

        view = discord.ui.View()
        draw_button = DrawButton()
        draw_button.disabled = game.game_over
        stand_button = StandButton()
        stand_button.disabled = game.game_over
        rules_button = RulesButton()
        rules_button.disabled = False
        view.add_item(draw_button)
        view.add_item(stand_button)
        view.add_item(rules_button)

        await interaction.response.edit_message(embed=embed, view=view)

        if game.game_over:
            await self.disable_buttons_and_update(interaction, game, embed, view)

    async def disable_buttons_and_update(self, interaction, game, embed, view):
        for item in view.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=view)

class StandButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Stand", style=discord.ButtonStyle.success, custom_id="stand")

    async def callback(self, interaction: discord.Interaction):
        game = games.get(interaction.user.id)
        if not game or game.game_over:
            await interaction.response.send_message("No active game found.", ephemeral=True)
            return

        game.player_stand()
        winner = game.get_winner()

        embed = discord.Embed(title="Game Over!", description=f"Winner: {winner}", color=0x7289DA)

        embed.add_field(name="Your Hand", value=game.format_p_hand(), inline=False)
        embed.add_field(name="Your Total", value=str(sum(game.player_hand)), inline=False)
        embed.add_field(name="C-3PO's Hand", value=game.format_b_hand(), inline=False)
        embed.add_field(name="C-3PO's Total", value=str(sum(game.bot_hand)), inline=False)
        embed.add_field(name="Mode", value=game.mode_description, inline=False)

        embed.set_footer(text=game.stats.format_stats())

        if winner == CPU_PLAYER_NAME:
            embed.set_thumbnail(url="https://i.imgur.com/bc0yumE.png")
        elif winner == game.player.display_name:
            embed.set_thumbnail(url="https://i.imgur.com/UNKFLb1.png")
        else:
            embed.set_thumbnail(url="https://i.imgur.com/neutral.png")

        view = discord.ui.View()
        draw_button = DrawButton()
        draw_button.disabled = True
        stand_button = StandButton()
        stand_button.disabled = True
        rules_button = RulesButton()
        rules_button.disabled = False
        view.add_item(draw_button)
        view.add_item(stand_button)
        view.add_item(rules_button)

        await interaction.response.edit_message(embed=embed, view=view)

class RulesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Rules", style=discord.ButtonStyle.secondary, custom_id="rules")

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Sabacc Rules", color=0x7289DA)
        embed.add_field(name="Goal", value="Get as close to **23** or **-23** as possible without going over.", inline=False)
        embed.add_field(name="Game Modes", value="Each game randomly selects a difficulty level that affects C-3PO's strategy.", inline=False)
        embed.add_field(name="Draw", value="Take another card from the deck to add to your hand.", inline=False)
        embed.add_field(name="Stand", value="Stick with your current hand and end your turn.", inline=False)
        embed.add_field(name="Winning", value="If your total is closer to **23** or **-23** than C-3PO's, you win!", inline=False)
        embed.add_field(name="Limits", value="You can draw a maximum of **5** cards. Exceeding the total range of **-23** to **23** results in an immediate loss.", inline=False)
        embed.add_field(name="Tie", value="If both you and C-3PO are equally close to the target, the game is a tie.", inline=False)
        embed.add_field(name="AI Behavior", value="In **Hard Mode**, C-3PO uses probability to maximize its chances of winning.", inline=False)
        embed.set_footer(text="Good luck!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
