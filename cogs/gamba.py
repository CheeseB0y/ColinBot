"""
Gamba cog

This cog handles all the gambling funcitonality for ColinBot.
"""

import random
import asyncio
from discord.ext import commands
from cogs import econ
from logging_config import logger


class PlayingCard:
    """
    Playing card class

    This class is used to simulate a playing card object.

    Attributes:
        suit: Playing card suit.
        rank: Playing card rank.
    """

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def power(self):
        """
        Returns the value from 1-10 that you would score for each card during blackjack.

        Args:
            None

        Returns:
            power: A value from 1-10 to be used in blackjack.
        """
        if self.rank == "Ace":
            return 1
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        return self.rank


class DeckOfCards:
    """
    Deck of cards class

    This class simulates a deck of cards using 52 card objects.

    Attributes:
        suits: Tuple containing a string of each type of suit.
        ranks: Tuple containing a string or int of each card rank.
        deck: A list of every unique playing card in a deck of cards.
    """

    suits = ("Spades", "Diamonds", "Clubs", "Hearts")
    ranks = ("Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King")

    def __init__(self):
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append(PlayingCard(suit, rank))
        self.deck = deck

    def __str__(self):
        cards = ""
        for card in self.deck:
            cards += f"{card}\n"
        return cards

    def draw(self):
        """
        Draw a card from theck deck

        Args:
            None

        Returns:
            card: Playing card object from the top of the deck. This will remove the card from the deck.
        """
        return self.deck.pop(0)

    def shuffle(self):
        """
        Shuffles the deck.

        Args:
            None

        Returns:
            None
        """
        random.shuffle(self.deck)


class Hand:
    """
    Hand class

    Simulates a hand of cards.

    Attributes:
        hand: A list of the currenty playing card objects in a hand.
    """

    def __init__(self):
        self.hand = []

    def __str__(self):
        cards = ""
        for card in self.hand:
            cards += f"{card}, "
        cards += f"{'soft ' if self.soft() else ''}{self.strength()}"
        cards += " points."
        return cards

    def draw(self, deck):
        """
        Draw a card from a deck of cards.

        Args:
            deck: Deck of cards object.

        Returns:
            drawn_card: Playing card object from the top of the deck.
        """
        drawn_card = deck.draw()
        self.hand.append(drawn_card)
        return drawn_card

    def add(self, card):
        """
        Add a card to the hand.

        Args:
            card: Playing card object to add to the hand.

        Returns:
            card: Playing card object that was added to the hand.
        """
        self.hand.append(card)
        return card

    def strength(self):
        """
        Return the blackjack score of a hand.

        Args:
            None

        Returns:
            score: Total blackjack score.
        """
        total = 0
        for card in self.hand:
            total += card.power()
        if self.has_ace() and total + 10 <= 21:
            return total + 10
        return total

    def b_strength(self):
        """
        Return the baccarat score of a hand.

        Args:
            None

        Returns:
            score: Total baccarat score.
        """
        total = 0
        for card in self.hand:
            total += card.power()
        return total % 10

    def soft(self):
        """
        Check if a hand has a "soft" score with an ace.

        Args:
            None

        Returns:
            Returns true if a hand is a soft score.
        """
        if self.has_ace():
            total = 0
            for card in self.hand:
                total += card.power()
            if total + 10 < 21:
                return True
            return False
        return False

    def has_ace(self):
        """
        Check if there is an ace in the hand.

        Args:
            None

        Returns:
            Returns true if the hand contains an ace.
        """
        for card in self.hand:
            if card.rank == "Ace":
                return True
        return False


class Blackjack:
    """
    Blackjack class

    Play a game of blackjack.

    Attributes:
        deck: Deck of cards object to play blackjack with.
        dealer: Hand object for the dealer.
        player: Hand object for the player.
        hand_number: Number of current hand.
        hand_limit: Maximum number of hands that can be played at once via splits.
    """

    def __init__(self):
        self.deck = DeckOfCards()
        self.dealer = Hand()
        self.player = [Hand()]
        self.hand_number = 0
        self.hand_limit = 4

    def __str__(self):
        return f"Dealer: {self.dealer}\nPlayer: {self.player}"

    def deal(self):
        """
        Deal cards at start of blackjack game.

        Args:
            None

        Returns:
            None
        """
        self.deck.shuffle()
        self.player[0].draw(self.deck)
        self.dealer.draw(self.deck)
        self.player[0].draw(self.deck)
        self.dealer.draw(self.deck)

    def check_splits(self):
        """
        Check if there are any more hands to be played.

        Args:
            None

        Returns:
            Returns true if there are more hands to play from splitting.
        """
        if self.hand_number < len(self.player) - 1:
            self.hand_number += 1
            return False
        return True

    async def play(self, ctx, bet: int):
        """
        Start the blackjack game.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        if len(self.player) == 1:
            self.deal()
        else:
            await ctx.send(f"Hand {self.hand_number + 1}:")
        if await econ.wager(ctx, bet, min_bet=10, max_bet=10000):
            async with ctx.typing():
                await ctx.send(
                    f"Dealer: *Face Down*, {self.dealer.hand[1]},{' soft' if self.dealer.hand[1].rank == 'Ace' else ''} {self.dealer.hand[1].power() if not self.dealer.hand[1].rank == 'Ace' else self.dealer.hand[1].power() + 10} points.\nPlayer: {self.player[self.hand_number]}"
                )
            if self.player[self.hand_number].strength() == 21:
                if self.check_splits():
                    await self.dealers_turn(ctx, bet)
                else:
                    await self.play(ctx, bet)
            elif self.dealer.strength() == 21:
                await self.game_outcome(ctx, bet)
            else:
                await self.player_choice(ctx, bet)
        else:
            await ctx.send("Try again.")

    async def player_choice(self, ctx, bet):
        """
        Give player options when it's their turn.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        async with ctx.typing():
            if (
                self.player[self.hand_number].hand[0].power()
                == self.player[self.hand_number].hand[1].power()
                and bet * 2 < econ.get_points(ctx)
                and len(self.player) < self.hand_limit
            ):
                await ctx.send("Would you like to hit, stand, double down, or split?")
            elif bet * 2 < econ.get_points(ctx):
                await ctx.send("Would you like to hit, stand, or double down?")
            else:
                await ctx.send("Would you like to hit or stand?")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            response = await ctx.bot.wait_for("message", timeout=60.0, check=check)
            if response.content.lower() in ["hit", "h"]:
                await self.hit(ctx, bet)
            elif response.content.lower() in ["stand", "s"]:
                await self.stand(ctx, bet)
            elif response.content.lower() in [
                "double down",
                "doubledown",
                "double",
                "d",
                "dd",
            ] and bet * 2 < econ.get_points(ctx):
                await self.double_down(ctx, bet)
            elif (
                response.content.lower() in ["split", "sp", "spl"]
                and self.player[self.hand_number].hand[0].power()
                == self.player[self.hand_number].hand[1].power()
                and bet * 2 < econ.get_points(ctx)
                and len(self.player) < self.hand_limit
            ):
                await self.split(ctx, bet)
            else:
                await ctx.send(f"{response.content} is not a valid input.")
                await self.player_choice(ctx, bet)
        except asyncio.TimeoutError:
            async with ctx.typing():
                await ctx.send("Time out error")

    async def hit(self, ctx, bet):
        """
        Blackjack hit.

        Draw a card for the player.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send(
                f"{self.player[self.hand_number].draw(self.deck)},{' soft' if self.player[self.hand_number].soft() else ''} {self.player[self.hand_number].strength()} points."
            )
        if self.player[self.hand_number].strength() < 21:
            await self.player_choice(ctx, bet)
        elif self.check_splits():
            await self.dealers_turn(ctx, bet)
        else:
            await self.play(ctx, bet)

    async def double_down(self, ctx, bet):
        """
        Blackjack double down.

        Draw a card and double the wager, this ends the players turn.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send(f"You bet {bet} more colin coins.")
            await ctx.send(
                f"{self.player[self.hand_number].draw(self.deck)},{' soft' if self.player[self.hand_number].soft() else ''} {self.player[self.hand_number].strength()} points."
            )
        if self.check_splits():
            await self.dealers_turn(ctx, bet * 2)
        else:
            await self.play(ctx, bet)

    async def stand(self, ctx, bet):
        """
        Blackjack stand.

        Player chooses to not draw any more cards and end their turn.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        if self.check_splits():
            await self.dealers_turn(ctx, bet)
        else:
            await self.play(ctx, bet)

    async def split(self, ctx, bet):
        """
        Split a hand if possible.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        if len(self.player) >= self.hand_limit:
            await ctx.send(f"You cannot split more that {self.hand_limit} hands.")
            await self.player_choice(ctx, bet)
        split_hand = Hand()
        split_hand.add(self.player[self.hand_number].hand.pop())
        self.player[self.hand_number].draw(self.deck)
        split_hand.draw(self.deck)
        self.player.append(split_hand)
        await ctx.send(f"Split! You now have {len(self.player)} hands:")
        for i, hand in enumerate(self.player):
            await ctx.send(f"Hand {i + 1}: {hand}")
        await self.play(ctx, bet)

    async def dealers_turn(self, ctx, bet):
        """
        Control is given over to the dealer to determine the outcome of the game.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        busts = 0
        blackjacks = 0
        for hand in self.player:
            if hand.strength() > 21:
                busts += 1
            if hand.strength() == 21:
                blackjacks += 1
        if busts + blackjacks == len(self.player):
            await self.game_outcome(ctx, bet)
        else:
            async with ctx.typing():
                await ctx.send(f"Dealer: {self.dealer}")
            while self.dealer.strength() < 17:
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(
                        f"{self.dealer.draw(self.deck)},{' soft' if self.dealer.soft() else ''} {self.dealer.strength()} points."
                    )
            await self.game_outcome(ctx, bet)

    async def game_outcome(self, ctx, bet):
        """
        Calculate if the player has won or lost the game and payout the player.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send(f"Dealer has {self.dealer}")
            for i, hand in enumerate(self.player):
                if self.hand_number > 0:
                    await ctx.send(f"Hand {i + 1}:")
                await ctx.send(f"Player has {hand}")
                if self.dealer.strength() == hand.strength():
                    await ctx.send("Push")
                elif hand.strength() == 21:
                    await ctx.send("Blackjack!")
                    await ctx.send("You win!")
                    econ.change_points(ctx, bet * 1.5)
                    await ctx.send(
                        f"{bet * 1.5} Colin Coins have been added to your wallet."
                    )
                elif hand.strength() > 21:
                    await ctx.send("Bust, you lose.")
                    econ.change_points(ctx, -bet)
                    await ctx.send(f"You lose {bet} Colin Coins.")
                elif self.dealer.strength() == 21:
                    await ctx.send("Blackjack, you lose.")
                    econ.change_points(ctx, -bet)
                    await ctx.send(f"You lose {bet} Colin Coins.")
                elif self.dealer.strength() > 21:
                    await ctx.send("Dealer busts, you win!")
                    econ.change_points(ctx, bet)
                    await ctx.send(f"{bet} Colin Coins have been added to your wallet.")
                elif self.dealer.strength() > hand.strength():
                    await ctx.send("You lose.")
                    econ.change_points(ctx, -bet)
                    await ctx.send(f"You lose {bet} Colin Coins.")
                elif self.dealer.strength() < hand.strength():
                    await ctx.send("You win!")
                    econ.change_points(ctx, bet)
                    await ctx.send(f"{bet} Colin Coins have been added to your wallet.")
                else:
                    await ctx.send(
                        "This is an edge case CheeseB0y did not account for, you win?"
                    )
                    econ.change_points(ctx, bet)
                    await ctx.send(f"{bet} Colin Coins have been added to your wallet.")
            await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")


class Reel8:
    """
    Slot machine reel with 8 symbols.

    Attributes:
        symbols: Tuple of each symbol as a discord emoji.
        weights: Probability of getting each symbol, higher value is more likely.
        symbol: Placeholder value to be updated during the spin.
    """

    def __init__(self):
        self.symbols = (
            ":cherries:",
            ":chocolate_bar:",
            ":bell:",
            ":four_leaf_clover:",
            ":star:",
            ":gem:",
            ":seven:",
            ":pregnant_man:",
        )
        self.weights = [3, 2, 3, 1, 1, 2, 2, 1]
        self.symbol = ":question:"

    def spin(self):
        """
        Select a random symbol from symbols and display it.

        Args:
            None

        Returns:
            None
        """
        self.symbol = random.choices(self.symbols, weights=self.weights, k=1)[0]


class Reel12:
    """
    Slot machine reel with 12 symbols.

    Attributes:
        symbols: Tuple of each symbol as a discord emoji.
        weights: Probability of getting each symbol, higher value is more likely.
        symbol: Placeholder value to be updated during the spin.
    """

    def __init__(self):
        self.symbols = (
            ":cherries:",
            ":chocolate_bar:",
            ":bell:",
            ":four_leaf_clover:",
            ":star:",
            ":gem:",
            ":seven:",
            ":pregnant_man:",
            ":lemon:",
            ":tangerine:",
            ":watermelon:",
            ":apple:",
        )
        self.weights = [4, 3, 3, 2, 2, 2, 1, 1, 3, 2, 2, 1]
        self.symbol = ":question:"

    def spin(self):
        """
        Select a random symbol from symbols and display it.

        Args:
            None

        Returns:
            None
        """
        self.symbol = random.choices(self.symbols, weights=self.weights, k=1)[0]


class SlotsLegacy:
    """
    Old solt machine game.

    This is not used anymore because it was way too generous to the player.

    Attributes:
        reels: List of reel objects.
        row: List of symbols displayed by the reel objects.
        points: Placeholder dict to be used later for scoring.
        prize: Placeholder value to be updated during the payout function.
    """

    def __init__(self):
        self.reels = [Reel8() for _ in range(5)]
        self.row = []
        self.points = {}
        self.prize = 0

    def __str__(self):
        return " ".join(reel.symbol for reel in self.reels)

    async def spin(self, ctx, bet: int):
        """
        Spin all reels on the virtual slot machine.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        if await econ.wager(ctx, bet, min_bet=1, max_bet=1000):
            async with ctx.typing():
                message = await ctx.send(str(self))
                for reel in self.reels:
                    reel.spin()
                    await message.edit(content=str(self))
                    await asyncio.sleep(0.5)
            self.row = [reel.symbol for reel in self.reels]
            await self.score(ctx, bet)
        else:
            async with ctx.typing():
                await ctx.send("Try again.")

    async def score(self, ctx, bet):
        """
        Scores the game based on having consecutive symbols

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        consecutive_count = 1
        for i in range(1, len(self.row)):
            if self.row[i] == self.row[i - 1]:
                consecutive_count += 1
            else:
                if consecutive_count >= 3:
                    self.points[self.row[i - 1]] = 3
                elif consecutive_count == 2:
                    self.points[self.row[i - 1]] = 2
                consecutive_count = 1
        if consecutive_count >= 3:
            self.points[self.row[-1]] = 3
        elif consecutive_count == 2:
            self.points[self.row[-1]] = 2
        await self.payout(ctx, bet)

    async def payout(self, ctx, bet):
        """
        Calculates payout value for each consecutive items determined by the score function

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        econ.change_points(ctx, -bet)
        if not self.points:
            async with ctx.typing():
                await ctx.send("You lose.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            return
        async with ctx.typing():
            await ctx.send("You win!")
        for symbol, value in self.points.items():
            if symbol == ":cherries:":
                self.prize += bet * (0.5 if value == 2 else 3 if value == 3 else 0)
            elif symbol == ":chocolate_bar:":
                self.prize += bet * (1 if value == 2 else 7 if value == 3 else 0)
            elif symbol == ":bell:":
                self.prize += bet * (1.5 if value == 2 else 10 if value == 3 else 0)
            elif symbol == ":four_leaf_clover:":
                self.prize += bet * (1.5 if value == 2 else 12 if value == 3 else 0)
            elif symbol == ":star:":
                self.prize += bet * (2 if value == 2 else 15 if value == 3 else 0)
            elif symbol == ":gem:":
                self.prize += bet * (3 if value == 2 else 20 if value == 3 else 0)
            elif symbol == ":seven:":
                self.prize += bet * (5 if value == 2 else 30 if value == 3 else 0)
            elif symbol == ":pregnant_man:":
                self.prize += bet * (20 if value == 2 else 50 if value == 3 else 0)
        econ.change_points(ctx, self.prize)
        await ctx.send(f"{self.prize} Colin Coins have been added to your wallet.")
        await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")

    async def payout_table(self, ctx):
        """
        Sends payout table for payout clarity.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        await ctx.send(
            "```Pregnant Man:\n3 Pregnant Men: 50x your bet\n2 Pregnant Men: 20x your bet\n\n7s:\n3 7s: 30x your bet\n2 7s: 5x your bet\n\nDiamonds:\n3 Diamonds: 20x your bet\n2 Diamonds: 3x your bet\n\nStars:\n3 Stars: 15x your bet\n2 Stars: 2x your bet\n\nFour-leaf clovers:\n3 Clovers: 12x your bet\n2 Clovers: 1.5x your bet\n\nBells:\n3 Bells: 10x your bet\n2 Bells: 1.5x your bet\n\nBars:\n3 Bars: 7x your bet\n2 Bars: 1x your bet\n\nCherries:\n3 Cherries: 3x your bet\n2 Cherries: 0.5x your be```"
        )


class Slots:
    """
    Solt machine game.

    Attributes:
        reels: List of reel objects.
        row: List of symbols displayed by the reel objects.
        points: Placeholder dict to be used later for scoring.
        prize: Placeholder value to be updated during the payout function.
    """

    def __init__(self):
        self.reels = [Reel12() for _ in range(5)]
        self.row = []
        self.points = {}
        self.prize = 0

    def __str__(self):
        return " ".join(reel.symbol for reel in self.reels)

    async def spin(self, ctx, bet: int):
        """
        Spin all reels on the virtual slot machine.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        if await econ.wager(ctx, bet, min_bet=1, max_bet=1000):
            async with ctx.typing():
                message = await ctx.send(str(self))
                for reel in self.reels:
                    reel.spin()
                    await message.edit(content=str(self))
                    await asyncio.sleep(0.5)
            self.row = [reel.symbol for reel in self.reels]
            await self.score(ctx, bet)
        else:
            async with ctx.typing():
                await ctx.send("Try again.")

    async def score(self, ctx, bet):
        """
        Scores the game based on having consecutive symbols

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        consecutive_count = 1
        self.points.clear()
        for i in range(1, len(self.row)):
            if self.row[i] == self.row[i - 1]:
                consecutive_count += 1
            else:
                if consecutive_count >= 3:
                    self.points[self.row[i - 1]] = 3
                elif consecutive_count == 2:
                    self.points[self.row[i - 1]] = 2
                consecutive_count = 1
        if consecutive_count >= 3:
            self.points[self.row[-1]] = 3
        elif consecutive_count == 2:
            self.points[self.row[-1]] = 2
        await self.payout(ctx, bet)

    async def payout(self, ctx, bet):
        """
        Calculates payout value for each consecutive items determined by the score function

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        econ.change_points(ctx, -bet)
        self.prize = 0
        if not self.points:
            async with ctx.typing():
                await ctx.send("You lose.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            return
        async with ctx.typing():
            await ctx.send("You win!")
        for symbol, value in self.points.items():
            if symbol == ":cherries:":
                self.prize += bet * (1 if value == 2 else 4 if value == 3 else 0)
            elif symbol == ":chocolate_bar:":
                self.prize += bet * (1 if value == 2 else 7 if value == 3 else 0)
            elif symbol == ":bell:":
                self.prize += bet * (2 if value == 2 else 12 if value == 3 else 0)
            elif symbol == ":four_leaf_clover:":
                self.prize += bet * (2 if value == 2 else 15 if value == 3 else 0)
            elif symbol == ":star:":
                self.prize += bet * (3 if value == 2 else 18 if value == 3 else 0)
            elif symbol == ":gem:":
                self.prize += bet * (4 if value == 2 else 25 if value == 3 else 0)
            elif symbol == ":seven:":
                self.prize += bet * (6 if value == 2 else 35 if value == 3 else 0)
            elif symbol == ":pregnant_man:":
                self.prize += bet * (25 if value == 2 else 50 if value == 3 else 0)
            elif symbol == ":lemon:":
                self.prize += bet * (2 if value == 2 else 6 if value == 3 else 0)
            elif symbol == ":tangerine:":
                self.prize += bet * (3 if value == 2 else 7 if value == 3 else 0)
            elif symbol == ":watermelon:":
                self.prize += bet * (3 if value == 2 else 10 if value == 3 else 0)
            elif symbol == ":apple:":
                self.prize += bet * (4 if value == 2 else 12 if value == 3 else 0)
        econ.change_points(ctx, self.prize)
        await ctx.send(f"{self.prize} Colin Coins have been added to your wallet.")
        await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")

    async def payout_table(self, ctx):
        """
        Sends payout table for payout clarity.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        await ctx.send(
            "```Pregnant Man:\n3 Pregnant Men: 50x your bet\n2 Pregnant Men: 25x your bet\n\n7s:\n3 7s: 35x your bet\n2 7s: 6x your bet\n\nGems:\n3 Gems: 25x your bet\n2 Gems: 4x your bet\n\nStars:\n3 Stars: 18x your bet\n2 Stars: 3x your bet\n\nFour-leaf clovers:\n3 Clovers: 15x your bet\n2 Clovers: 2x your bet\n\nBells:\n3 Bells: 12x your bet\n2 Bells: 2x your bet\n\nChocolate Bars:\n3 Bars: 7x your bet\n2 Bars: 1x your bet\n\nCherries:\n3 Cherries: 4x your bet\n2 Cherries: 1x your bet\n\nLemons:\n3 Lemons: 6x your bet\n2 Lemons: 2x your bet\n\nTangerines:\n3 Tangerines: 7x your bet\n2 Tangerines: 3x your bet\n\nWatermelons:\n3 Watermelons: 10x your bet\n2 Watermelons: 3x your bet\n\nApples:\n3 Apples: 12x your bet\n2 Apples: 4x your bet\n```"
        )


class Baccarat:
    """
    Baccarat class

    Play a game of baccarat.

    Attributes:
        deck: Deck of cards object to play blackjack with.
        banker: Hand object for the banker.
        player: Hand object for the player.
        third: Bool if a third card is to be drawn or not.
        third_card: Third card playing card object.
        bet: Wager amount.
        bet_banker: Player chose to bet on banker.
    """

    def __init__(self):
        self.deck = DeckOfCards()
        self.banker = Hand()
        self.player = Hand()
        self.third = False
        self.third_card = -1
        self.bet = None
        self.bet_banker = None

    async def play(self, ctx, bet: int):
        """
        Play baccarat game.

        Args:
            ctx: Discord context object.
            bet: Amount to be wagered.

        Returns:
            None
        """
        if await econ.wager(ctx, bet, min_bet=10, max_bet=10000):
            self.bet = bet
            async with ctx.typing():
                await ctx.send("Would you like to place your bet on banker or player?")

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            try:
                response = await ctx.bot.wait_for("message", timeout=60.0, check=check)
                if response.content.lower() in ["banker", "b"]:
                    self.bet_banker = True
                elif response.content.lower() in ["player", "p"]:
                    self.bet_banker = False
                else:
                    async with ctx.typing():
                        await ctx.send(f"{response.content} is not a valid input.")
                    await self.play(ctx, bet)
            except asyncio.TimeoutError:
                async with ctx.typing():
                    await ctx.send("Time out error")
            self.deck.shuffle()
            async with ctx.typing():
                await ctx.send("Player draw:")
                await asyncio.sleep(1)
                await ctx.send(self.player.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(self.player.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(f"Player hand strength: {self.player.b_strength()}")
                await asyncio.sleep(1)
                await ctx.send("Banker draw:")
                await asyncio.sleep(1)
                await ctx.send(self.banker.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(self.banker.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(f"Banker hand strength: {self.banker.b_strength()}")
                await asyncio.sleep(1)
            if self.banker.b_strength() >= 8 or self.player.b_strength() >= 8:
                await self.score(ctx)
                return
            if self.player.b_strength() <= 5:
                await self.player_hit(ctx)
            elif self.player.b_strength() > 5:
                await self.player_stand(ctx)
            else:
                async with ctx.typing():
                    await ctx.send("An error has occured.")
            if self.banker.b_strength() <= 2:
                await self.banker_hit(ctx)
            elif self.banker.b_strength() == 7:
                await self.banker_stand(ctx)
                await self.score(ctx)
            elif self.third:
                if self.banker.b_strength() == 3:
                    if self.third_card.power() != 8:
                        await self.banker_hit(ctx)
                    else:
                        await self.banker_stand(ctx)
                elif self.banker.b_strength() == 4:
                    if self.third_card.power() >= 2 and self.third_card.power() < 8:
                        await self.banker_hit(ctx)
                    else:
                        await self.banker_stand(ctx)
                elif self.banker.b_strength() == 5:
                    if self.third_card.power() >= 3 and self.third_card.power() < 8:
                        await self.banker_hit(ctx)
                    else:
                        await self.banker_stand(ctx)
                elif self.banker.b_strength() == 6:
                    if self.third_card.power() == 6 or self.third_card.power() == 7:
                        await self.banker_hit(ctx)
                    else:
                        await self.banker_stand(ctx)
                elif self.banker.b_strength() == 7:
                    await self.banker_stand(ctx)
                else:
                    async with ctx.typing():
                        await ctx.send("An error has occured.")
            elif self.banker.b_strength() <= 5:
                await self.banker_hit(ctx)
            else:
                await self.banker_stand(ctx)
            await self.score(ctx)
        else:
            async with ctx.typing():
                await ctx.send("Try again.")

    async def player_hit(self, ctx):
        """
        Player draws a card.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        self.third = True
        async with ctx.typing():
            await ctx.send("Player hits.")
            self.third_card = self.player.draw(self.deck)
            await asyncio.sleep(1)
            await ctx.send(self.third_card)
            await ctx.send(f"Player hand strength: {self.player.b_strength()}")

    async def player_stand(self, ctx):
        """
        Player does not draw a card and their turn ends.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send("Player stands.")

    async def banker_hit(self, ctx):
        """
        Banker draws a card.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send("Banker hits.")
            await ctx.send(self.banker.draw(self.deck))
            await asyncio.sleep(1)
            await ctx.send(f"Banker hand strength: {self.banker.b_strength()}")

    async def banker_stand(self, ctx):
        """
        Banker does not draw a card and their turn ends.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send("Banker stands.")

    async def score(self, ctx):
        """
        Game is scored and a winner is determined.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        if self.banker.b_strength() == self.player.b_strength():
            await self.push(ctx)
        elif self.banker.b_strength() > self.player.b_strength():
            await self.banker_win(ctx)
        elif self.banker.b_strength() < self.player.b_strength():
            await self.player_win(ctx)
        else:
            async with ctx.typing():
                await ctx.send("An error has occured.")

    async def push(self, ctx):
        """
        Game is scored a push.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        await ctx.send("Push.")

    async def banker_win(self, ctx):
        """
        Game is scored as a banker win.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send("Banker wins!")
            if self.bet_banker:
                econ.change_points(ctx, self.bet)
                await ctx.send(
                    f"You Win! {self.bet} Colin Coins have been added to your wallet."
                )
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            elif not self.bet_banker:
                econ.change_points(ctx, -self.bet)
                await ctx.send("You lose.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            else:
                await ctx.send("An error has occured.")

    async def player_win(self, ctx):
        """
        Game is scored as a player win.

        Args:
            ctx: Discord context object.

        Returns:
            None
        """
        async with ctx.typing():
            await ctx.send("Player wins!")
            if not self.bet_banker:
                econ.change_points(ctx, self.bet)
                await ctx.send(
                    f"You Win! {self.bet} Colin Coins have been added to your wallet."
                )
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            elif self.bet_banker:
                econ.change_points(ctx, -self.bet)
                await ctx.send("You lose.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            else:
                await ctx.send("An error has occured.")


@econ.verify_user
async def slots(ctx, bet):
    """
    Setup slots game

    Args:
        ctx: Discord context object.
        bet: Amount to be wagered.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !slots in {ctx.guild}")
    if bet is None:
        async with ctx.typing():
            await ctx.send(
                f"You must provide a wager, you currently have {econ.get_points(ctx)} Colin Coins."
            )
        logger.warning(
            f"{ctx.author.name} attempted to play slots without submitting a wager in {ctx.guild}."
        )
        return
    if ctx.author.id == 115928421204230149:
        game = SlotsLegacy()
        await game.spin(ctx, bet)
    else:
        game = Slots()
        await game.spin(ctx, bet)


@econ.verify_user
async def blackjack(ctx, bet):
    """
    Setup blackjack game

    Args:
        ctx: Discord context object.
        bet: Amount to be wagered.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !blackjack in {ctx.guild}")
    if bet is None:
        async with ctx.typing():
            await ctx.send(
                f"You must provide a wager, you currently have {econ.get_points(ctx)} Colin Coins."
            )
        logger.warning(
            f"{ctx.author.name} attempted to play blackjack without submitting a wager in {ctx.guild}."
        )
        return
    game = Blackjack()
    await game.play(ctx, bet)


@econ.verify_user
async def baccarat(ctx, bet):
    """
    Setup baccarat game

    Args:
        ctx: Discord context object.
        bet: Amount to be wagered.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !baccarat in {ctx.guild}")
    if bet is None:
        async with ctx.typing():
            await ctx.send(
                f"You must provide a wager, you currently have {econ.get_points(ctx)} Colin Coins."
            )
        logger.warning(
            f"{ctx.author.name} attempted to play baccarat without submitting a wager in {ctx.guild}."
        )
        return
    game = Baccarat()
    await game.play(ctx, bet)


async def payout(ctx):
    """
    Setup payout table command

    Args:
        ctx: Discord context object.

    Returns:
        None
    """
    logger.info(f"{ctx.author.name} called !payout in {ctx.guild}")
    if ctx.author.id == 115928421204230149:
        game = SlotsLegacy()
        await game.payout_table(ctx)
    else:
        game = Slots()
        await game.payout_table(ctx)


class Cog(commands.Cog, name="gamba"):
    """
    Cog class

    For initalizing all the gambling cog functions.

    Attributes:
        bot: Discord bot object.
    """

    def __init__(self, bot):
        if econ.MONGODB_CONNECTION_SUCCESS:
            try:
                self.bot = bot
                logger.info("Gamba cog successfully initialized.")
            except Exception as e:
                logger.error(f"Unable to initialize gamba cog: {e}")
        else:
            logger.warning("Gamba cog was not initalized.")

    @commands.command(name="blackjack", help="Blackjack game, bet with Colin Coins.")
    async def blackjack(self, ctx, bet: int = None):
        """Init blackjack command"""
        await blackjack(ctx, bet)

    @commands.command(name="bj", help="Short for blackjack.")
    async def bj(self, ctx, bet: int = None):
        """Init bj command"""
        await blackjack(ctx, bet)

    @commands.command(name="blowjob", help="Long for bj.")
    async def blowjob(self, ctx, bet: int = None):
        """Init blowjob command"""
        await blackjack(ctx, bet)

    @commands.command(name="baccarat", help="Baccarat game, bet with Colin Coins.")
    async def baccarat(self, ctx, bet: int = None):
        """Init baccarat command"""
        await baccarat(ctx, bet)

    @commands.command(name="b", help="Short for baccarat.")
    async def b(self, ctx, bet: int = None):
        """Init b command"""
        await baccarat(ctx, bet)

    @commands.command(name="slots", help="Slot machine game, bet with Colin Coins.")
    async def slots(self, ctx, bet: int = None):
        """Init slots command"""
        await slots(ctx, bet)

    @commands.command(name="sluts", help="Short for slots.")
    async def sluts(self, ctx, bet: int = None):
        """Init sluts command"""
        await slots(ctx, bet)

    @commands.command(name="payout", help="Displays payout amounts for slots game.")
    async def payout(self, ctx):
        """Init payout command"""
        await payout(ctx)
