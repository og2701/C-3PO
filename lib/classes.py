import discord
from random import shuffle, randint
from lib.settings import games
from lib.sabacc_stats import Stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CPU_PLAYER_NAME = "C-3PO"

class BotStrategy:
    def decide_draw(self, game):
        raise NotImplementedError

class EasyStrategy(BotStrategy):
    def decide_draw(self, game):
        bot_total = sum(game.bot_hand)
        if bot_total < 10:
            draw_probability = 0.7
        elif bot_total < 15:
            draw_probability = 0.5
        else:
            draw_probability = 0.3
        decision = randint(1, 100) <= int(draw_probability * 100)
        logger.debug(f"EasyStrategy Decision: {'Draw' if decision else 'Stand'}")
        return decision

class MediumStrategy(BotStrategy):
    def decide_draw(self, game):
        bot_total = sum(game.bot_hand)
        player_total = sum(game.player_hand)
        player_distance = min(abs(23 - player_total), abs(-23 - player_total))
        
        if player_distance <= 5:
            draw_threshold = 15
        else:
            draw_threshold = 18
        
        decision = bot_total < draw_threshold
        logger.debug(f"MediumStrategy Decision: {'Draw' if decision else 'Stand'} (Threshold: {draw_threshold})")
        return decision

class HardStrategy(BotStrategy):
    def monte_carlo_simulation(self, game, trials=1000):
        successes = 0
        for _ in range(trials):
            simulated_deck = game.deck.copy()
            simulated_bot_hand = game.bot_hand.copy()
            simulated_bot_draw_count = len(simulated_bot_hand)
            simulated_game_over = False

            while simulated_bot_draw_count < game.MAX_BOT_DRAWS and not simulated_game_over:
                bot_total = sum(simulated_bot_hand)
                player_total = sum(game.player_hand)
                player_distance = min(abs(23 - player_total), abs(-23 - player_total))
                bot_distance = min(abs(23 - bot_total), abs(-23 - bot_total))

                if bot_distance < player_distance:
                    simulated_game_over = True
                    break
                elif bot_distance == player_distance:
                    should_draw = True
                else:
                    beneficial_cards = [card for card in simulated_deck if
                                        (23 - bot_total) * card > 0 or
                                        (-23 - bot_total) * card > 0]
                    beneficial_probability = len(beneficial_cards) / len(simulated_deck) if simulated_deck else 0

                    should_draw = beneficial_probability > 0.55

                if should_draw and simulated_deck:
                    drawn_card = simulated_deck.pop(randint(0, len(simulated_deck) - 1))
                    simulated_bot_hand.append(drawn_card)
                    simulated_bot_draw_count += 1

                    new_total = sum(simulated_bot_hand)
                    if new_total > 23 or new_total < -23:
                        simulated_game_over = True
                        break
                else:
                    simulated_game_over = True
                    break

            final_bot_total = sum(simulated_bot_hand)
            final_player_total = sum(game.player_hand)
            if final_bot_total > 23 or final_bot_total < -23:
                continue
            final_bot_distance = min(abs(23 - final_bot_total), abs(-23 - final_bot_total))
            final_player_distance = min(abs(23 - final_player_total), abs(-23 - final_player_total))

            if final_bot_distance < final_player_distance:
                successes += 1

        return successes / trials if trials > 0 else 0

    def decide_draw(self, game):
        bot_total = sum(game.bot_hand)
        player_total = sum(game.player_hand)
        player_distance = min(abs(23 - player_total), abs(-23 - player_total))
        bot_distance = min(abs(23 - bot_total), abs(-23 - bot_total))
        
        if bot_distance < player_distance:
            logger.debug("HardStrategy Decision: Stand (Better than player)")
            return False
        elif bot_distance == player_distance:
            decision = True
        else:
            win_probability = self.monte_carlo_simulation(game)
            logger.debug(f"HardStrategy Monte Carlo Win Probability: {win_probability:.2%}")
            decision = win_probability > 0.55
        
        logger.debug(f"HardStrategy Decision: {'Draw' if decision else 'Stand'}")
        return decision

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
        self.strategy = self.select_strategy()

    def select_mode(self):
        modes = ['Easy', 'Medium', 'Hard']
        selected_mode = modes[randint(0, 2)]
        logger.info(f"Selected game mode: {selected_mode}")
        return selected_mode

    def get_mode_description(self):
        descriptions = {
            'Easy': "Easy Mode: C-3PO draws cards based on a simple probability.",
            'Medium': "Medium Mode: C-3PO draws based on basic strategic thresholds.",
            'Hard': "Hard Mode: C-3PO uses advanced strategies and simulations."
        }
        return descriptions[self.mode]

    def select_strategy(self):
        if self.mode == 'Easy':
            return EasyStrategy()
        elif self.mode == 'Medium':
            return MediumStrategy()
        elif self.mode == 'Hard':
            return HardStrategy()

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
        logger.info(f"C-3PO's turn started in {self.mode} Mode.")
        while self.bot_draw_count < self.MAX_BOT_DRAWS and not self.game_over:
            should_draw = self.strategy.decide_draw(self)
            if should_draw:
                self.draw_card(self.bot_hand)
                self.bot_draw_count += 1
                logger.info(f"Bot drew a card in {self.mode} Mode. Draw count: {self.bot_draw_count}")
            else:
                logger.info(f"Bot decides to stop drawing in {self.mode} Mode.")
                self.game_over = True
                break

        if not self.game_over:
            logger.info(f"Bot reached the maximum number of draws ({self.MAX_BOT_DRAWS}).")
            self.game_over = True
        logger.info("Bot's turn ended.")


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
