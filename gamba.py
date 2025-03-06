import random
import asyncio
import econ
from logging_config import logger
from discord.ext import commands

class PlayingCard:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def power(self):
        if self.rank == "Ace":
            return 1
        if self.rank in ["Jack", "Queen", "King"]:
            return 10
        else:
            return self.rank
    
class DeckOfCards:

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
        return self.deck.pop(0)
    
    def shuffle(self):
        random.shuffle(self.deck)

class Hand:
    def __init__(self):
        self.hand = []

    def __str__(self):
        cards = ""
        for card in self.hand:
            cards += f"{card}, "
        cards += f"{'soft ' if self.soft() else ''}{self.strength()}"
        cards +=  " points."
        return cards

    def draw(self, deck):
        drawn_card = deck.draw()
        self.hand.append(drawn_card)
        return drawn_card
    
    def add(self, card):
        self.hand.append(card)
        return card

    def strength(self):
        total = 0
        for card in self.hand:
            total += card.power()
        if self.has_ace() and total + 10 <= 21:
            return total + 10
        return total
    
    def bStrength(self):
        total = 0
        for card in self.hand:
            total += card.power()
        return total % 10
    
    def soft(self):
        if self.has_ace():
            total = 0
            for card in self.hand:
                total += card.power()
            if total + 10 < 21:
                return True
        else:
            return False
    
    def has_ace(self):
        for card in self.hand:
            if(card.rank == "Ace"):
                return True
        return False

class Blackjack:
    def __init__(self):
        self.deck = DeckOfCards()
        self.dealer = Hand()
        self.player = [Hand()]
        self.played = 0
        self.hand_limit = 4
        self.dealer_played = False

    def __str__(self):
        return f"Dealer: {self.dealer}\nPlayer: {self.player}"
    
    def deal(self):
        self.deck.shuffle()
        self.player[0].draw(self.deck)
        self.dealer.draw(self.deck)
        self.player[0].draw(self.deck)
        self.dealer.draw(self.deck)

    def check_splits(self):
        if self.played < len(self.player) - 1:
            self.played += 1
            return False
        else:
            return True

    async def play(self, ctx, bet: int, current_hand=0):
        if len(self.player) == 1:
            self.deal()
        else:
            await ctx.send(f"Hand {current_hand + 1}:")
        if await econ.wager(ctx, bet, min_bet=10, max_bet=10000):
            async with ctx.typing():
                await ctx.send(f"Dealer: *Face Down*, {self.dealer.hand[1]},{' soft' if self.dealer.hand[1].rank == 'Ace' else ''} {self.dealer.hand[1].power() if not self.dealer.hand[1].rank == 'Ace' else self.dealer.hand[1].power() + 10} points.\nPlayer: {self.player[current_hand]}")
            if self.player[current_hand].strength() == 21:
                if self.check_splits():
                    await self.dealers_turn(ctx, bet)
                else:
                    await self.play(ctx, bet, self.played)
            elif self.dealer.strength() == 21:
                await self.game_outcome(ctx, bet)
            else:
                await self.player_choice(ctx, bet, current_hand)
        else:
            await ctx.send("Try again.")
    
    async def player_choice(self, ctx, bet, current_hand):
        async with ctx.typing():
            if self.player[current_hand].hand[0].power() == self.player[current_hand].hand[1].power() and bet*2 < econ.get_points(ctx) and len(self.player) < self.hand_limit:
                await ctx.send(f"Would you like to hit, stand, double down, or split?")
            elif bet*2 < econ.get_points(ctx):
                await ctx.send(f"Would you like to hit, stand, or double down?")
            else:
                await ctx.send(f"Would you like to hit or stand?")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        try:
            response = await ctx.bot.wait_for('message', timeout=60.0, check=check)
            if response.content.lower() in ["hit", "h"]:
                await self.hit(ctx, bet, current_hand)
            elif response.content.lower() in ["stand", "s"]:
                await self.stand(ctx, bet)
            elif response.content.lower() in ["double down", "doubledown", "double", "d", "dd"] and bet*2 < econ.get_points(ctx):
                await self.double_down(ctx, bet, current_hand)
            elif response.content.lower() in ["split", "sp", "spl"] and self.player[current_hand].hand[0].power() == self.player[current_hand].hand[1].power() and bet*2 < econ.get_points(ctx) and len(self.player) < self.hand_limit:
                await self.split(ctx, bet, current_hand)
            else:
                await ctx.send(f"{response.content} is not a valid input.")
                await self.player_choice(ctx, bet, current_hand)
        except asyncio.TimeoutError:
            async with ctx.typing():
                await ctx.send("Time out error")

    async def hit(self, ctx, bet, current_hand):
        async with ctx.typing():
            await ctx.send(f"{self.player[current_hand].draw(self.deck)},{' soft' if self.player[current_hand].soft() else ''} {self.player[current_hand].strength()} points.")
        if self.player[current_hand].strength() < 21:
            await self.player_choice(ctx, bet, current_hand)
        elif self.check_splits():
            await self.dealers_turn(ctx, bet)
        else:
            await self.play(ctx, bet, self.played)

    async def double_down(self, ctx, bet, current_hand):
        async with ctx.typing():
            await ctx.send(f"You bet {bet} more colin coins.")
            await ctx.send(f"{self.player[current_hand].draw(self.deck)},{' soft' if self.player[current_hand].soft() else ''} {self.player[current_hand].strength()} points.")
        if self.check_splits():
            await self.dealers_turn(ctx, bet * 2)
        else:
            await self.play(ctx, bet, self.played)

    async def stand(self, ctx, bet):
        if self.check_splits():
            await self.dealers_turn(ctx, bet)
        else:
            await self.play(ctx, bet, self.played)

    async def split(self, ctx, bet, current_hand): 
        if len(self.player) >= self.hand_limit:
            await ctx.send(f"You cannot split more that {self.hand_limit} hands.")
            await self.player_choice(ctx, bet)
        split_hand = Hand()
        split_hand.add(self.player[current_hand].hand.pop())
        self.player[current_hand].draw(self.deck)
        split_hand.draw(self.deck)
        self.player.append(split_hand)
        await ctx.send(f"Split! You now have {len(self.player)} hands:")
        for i, hand in enumerate(self.player):
            await ctx.send(f"Hand {i + 1}: {hand}")
        await self.play(ctx, bet, self.played)

        
    async def dealers_turn(self, ctx, bet):
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
                    await ctx.send(f"{self.dealer.draw(self.deck)},{' soft' if self.dealer.soft() else ''} {self.dealer.strength()} points.")
            await self.game_outcome(ctx, bet)
        
    async def game_outcome(self, ctx, bet):
        async with ctx.typing():
            await ctx.send(f"Dealer has {self.dealer}")
            for i, hand in enumerate(self.player):
                if self.played > 0:
                    await ctx.send(f"Hand {i + 1}:")
                await ctx.send(f"Player has {hand}")
                if self.dealer.strength() == hand.strength():
                    await ctx.send("Push")
                elif hand.strength() == 21:
                    await ctx.send("Blackjack!")
                    await ctx.send("You win!")
                    econ.change_points(ctx, bet*1.5)
                    await ctx.send(f"{bet*1.5} Colin Coins have been added to your wallet.")
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
                    await ctx.send("This is an edge case CheeseB0y did not account for, you win?")
                    econ.change_points(ctx, bet)
                    await ctx.send(f"{bet} Colin Coins have been added to your wallet.")
            await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
class Reel_8:
    def __init__(self):
        self.symbols = (":cherries:", ":chocolate_bar:", ":bell:", ":four_leaf_clover:", ":star:", ":gem:", ":seven:", ":pregnant_man:")
        self.weights = [3, 2, 3, 1, 1, 2, 2, 1]
        self.symbol = ":question:"

    def spin(self):
        self.symbol = random.choices(self.symbols, weights=self.weights, k=1)[0]

class Reel_12:
    def __init__(self):
        self.symbols = (":cherries:", ":chocolate_bar:", ":bell:", ":four_leaf_clover:", ":star:", ":gem:", ":seven:", ":pregnant_man:", ":lemon:", ":tangerine:", ":watermelon:", ":apple:")
        self.weights = [4, 3, 3, 2, 2, 2, 1, 1, 3, 2, 2, 1]  
        self.symbol = ":question:"

    def spin(self):
        self.symbol = random.choices(self.symbols, weights=self.weights, k=1)[0]

class Slots_Legacy:
    def __init__(self):
        self.reels = [Reel_8() for _ in range(5)]
        self.row = []
        self.points = {}
        self.prize = 0

    def __str__(self):
        return " ".join(reel.symbol for reel in self.reels)

    async def spin(self, ctx, bet: int):
        if await econ.wager(ctx, bet, min_bet=1, max_bet=1000):
            async with ctx.typing():
                message = await ctx.send(self.__str__())
                for reel in self.reels:
                    reel.spin()
                    await message.edit(content=self.__str__())
                    await asyncio.sleep(0.5)
            self.row = [reel.symbol for reel in self.reels]
            await self.score(ctx, bet)
        else:
            async with ctx.typing():
                await ctx.send("Try again.")

    async def score(self, ctx, bet):
        consecutive_count = 1
        for i in range(1, len(self.row)):
            if self.row[i] == self.row[i - 1]:
                consecutive_count += 1
            else:
                if consecutive_count >= 3:
                    self.points[self.row[i-1]] = 3
                elif consecutive_count == 2:
                    self.points[self.row[i-1]] = 2
                consecutive_count = 1
        if consecutive_count >= 3:
            self.points[self.row[-1]] = 3
        elif consecutive_count == 2:
            self.points[self.row[-1]] = 2
        await self.payout(ctx, bet)

    async def payout(self, ctx, bet):
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

    async def payout_table(ctx):
        await ctx.send(f"```Pregnant Man:\n3 Pregnant Men: 50x your bet\n2 Pregnant Men: 20x your bet\n\n7s:\n3 7s: 30x your bet\n2 7s: 5x your bet\n\nDiamonds:\n3 Diamonds: 20x your bet\n2 Diamonds: 3x your bet\n\nStars:\n3 Stars: 15x your bet\n2 Stars: 2x your bet\n\nFour-leaf clovers:\n3 Clovers: 12x your bet\n2 Clovers: 1.5x your bet\n\nBells:\n3 Bells: 10x your bet\n2 Bells: 1.5x your bet\n\nBars:\n3 Bars: 7x your bet\n2 Bars: 1x your bet\n\nCherries:\n3 Cherries: 3x your bet\n2 Cherries: 0.5x your be```")

class Slots:
    def __init__(self):
        self.reels = [Reel_12() for _ in range(5)]
        self.row = []
        self.points = {}
        self.prize = 0

    def __str__(self):
        return " ".join(reel.symbol for reel in self.reels)

    async def spin(self, ctx, bet: int):
        if await econ.wager(ctx, bet, min_bet=1, max_bet=1000):
            async with ctx.typing():
                message = await ctx.send(self.__str__())
                for reel in self.reels:
                    reel.spin()
                    await message.edit(content=self.__str__())
                    await asyncio.sleep(0.5)
            self.row = [reel.symbol for reel in self.reels]
            await self.score(ctx, bet)
        else:
            async with ctx.typing():
                await ctx.send("Try again.")

    async def score(self, ctx, bet):
        consecutive_count = 1
        self.points.clear()
        for i in range(1, len(self.row)):
            if self.row[i] == self.row[i - 1]:
                consecutive_count += 1
            else:
                if consecutive_count >= 3:
                    self.points[self.row[i-1]] = 3
                elif consecutive_count == 2:
                    self.points[self.row[i-1]] = 2
                consecutive_count = 1
        if consecutive_count >= 3:
            self.points[self.row[-1]] = 3
        elif consecutive_count == 2:
            self.points[self.row[-1]] = 2
        await self.payout(ctx, bet)

    async def payout(self, ctx, bet):
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

    async def payout_table(ctx):
        await ctx.send(f"```Pregnant Man:\n3 Pregnant Men: 50x your bet\n2 Pregnant Men: 25x your bet\n\n7s:\n3 7s: 35x your bet\n2 7s: 6x your bet\n\nGems:\n3 Gems: 25x your bet\n2 Gems: 4x your bet\n\nStars:\n3 Stars: 18x your bet\n2 Stars: 3x your bet\n\nFour-leaf clovers:\n3 Clovers: 15x your bet\n2 Clovers: 2x your bet\n\nBells:\n3 Bells: 12x your bet\n2 Bells: 2x your bet\n\nChocolate Bars:\n3 Bars: 7x your bet\n2 Bars: 1x your bet\n\nCherries:\n3 Cherries: 4x your bet\n2 Cherries: 1x your bet\n\nLemons:\n3 Lemons: 6x your bet\n2 Lemons: 2x your bet\n\nTangerines:\n3 Tangerines: 7x your bet\n2 Tangerines: 3x your bet\n\nWatermelons:\n3 Watermelons: 10x your bet\n2 Watermelons: 3x your bet\n\nApples:\n3 Apples: 12x your bet\n2 Apples: 4x your bet\n```")

class Baccarat:
    def __init__(self):
        self.deck = DeckOfCards()
        self.banker = Hand()
        self.player = Hand()
        self.third = False
        self.thirdCard = -1
    async def play(self, ctx, bet: int):
        if await econ.wager(ctx, bet, min_bet=10, max_bet=10000):
            self.bet = bet
            async with ctx.typing():
                await ctx.send(f"Would you like to place your bet on banker or player?")
            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            try:
                response = await ctx.bot.wait_for('message', timeout=60.0, check=check)
                if response.content.lower() in ["banker", "b"]:
                    self.betBanker = True
                elif response.content.lower() in ["player", "p"]:
                    self.betBanker = False
                else:
                    async with ctx.typing():
                        await ctx.send(f"{response.content} is not a valid input.")
                    await self.play(self, ctx, bet)
            except asyncio.TimeoutError:
                async with ctx.typing():
                    await ctx.send("Time out error")
            self.deck.shuffle()
            async with ctx.typing():
                await ctx.send(f"Player draw:")
                await asyncio.sleep(1)
                await ctx.send(self.player.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(self.player.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(f"Player hand strength: {self.player.bStrength()}")
                await asyncio.sleep(1)
                await ctx.send(f"Banker draw:")
                await asyncio.sleep(1)
                await ctx.send(self.banker.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(self.banker.draw(self.deck))
                await asyncio.sleep(1)
                await ctx.send(f"Banker hand strength: {self.banker.bStrength()}")
                await asyncio.sleep(1)
            if (self.banker.bStrength() >= 8 or self.player.bStrength() >= 8):
                await self.score(ctx)
                return
            if (self.player.bStrength() <= 5):
                await self.playerHit(ctx)
            elif (self.player.bStrength() > 5):
                await self.playerStand(ctx)
            else:
                async with ctx.typing():
                    await ctx.send("An error has occured.")
            if (self.banker.bStrength() <= 2):
                await self.bankerHit(ctx)
            elif (self.banker.bStrength() == 7):
                await self.bankerStand(ctx)
                await self.score(ctx)
            elif (self.third == True):
                if (self.banker.bStrength() == 3):
                    if (self.thirdCard.power() != 8):
                        await self.bankerHit(ctx)
                    else:
                        await self.bankerStand(ctx)
                elif (self.banker.bStrength() == 4):
                    if (self.thirdCard.power() >= 2 and self.thirdCard.power() < 8):
                        await self.bankerHit(ctx)
                    else:
                        await self.bankerStand(ctx)
                elif (self.banker.bStrength() == 5):
                    if (self.thirdCard.power() >= 3 and self.thirdCard.power() < 8):
                        await self.bankerHit(ctx)
                    else:
                        await self.bankerStand(ctx)
                elif (self.banker.bStrength() == 6):
                    if (self.thirdCard.power() == 6 or self.thirdCard.power() == 7):
                        await self.bankerHit(ctx)
                    else:
                        await self.bankerStand(ctx)
                elif (self.banker.bStrength() == 7):
                    await self.bankerStand(ctx)
                else:
                    async with ctx.typing():
                        await ctx.send("An error has occured.")
            elif (self.banker.bStrength() <= 5):
                await self.bankerHit(ctx)
            else:
                await self.bankerStand(ctx)
            await self.score(ctx)
        else:
            async with ctx.typing():
                await ctx.send("Try again.")

    async def playerHit(self, ctx):
        self.third = True
        async with ctx.typing():
            await ctx.send(f"Player hits.")
            self.thirdCard = self.player.draw(self.deck)
            await asyncio.sleep(1)
            await ctx.send(self.thirdCard)
            await ctx.send(f"Player hand strength: {self.player.bStrength()}")

    async def playerStand(self, ctx):
        async with ctx.typing():
            await ctx.send(f"Player stands.")

    async def bankerHit(self, ctx):
        async with ctx.typing():
            await ctx.send(f"Banker hits.")
            await ctx.send(self.banker.draw(self.deck))
            await asyncio.sleep(1)
            await ctx.send(f"Banker hand strength: {self.banker.bStrength()}")
    async def bankerStand(self, ctx):
        async with ctx.typing():
            await ctx.send(f"Banker stands.")
    
    async def score(self, ctx):
        if (self.banker.bStrength() == self.player.bStrength()):
            await self.push(ctx)
        elif (self.banker.bStrength() > self.player.bStrength()):
            await self.bankerWin(ctx)
        elif (self.banker.bStrength() < self.player.bStrength()):
            await self.playerWin(ctx)
        else:
            async with ctx.typing():
                await ctx.send("An error has occured.")

    async def push(self, ctx):
        await ctx.send("Push.")

    async def bankerWin(self, ctx):
        async with ctx.typing():
            await ctx.send(f"Banker wins!")
            if (self.betBanker == True):
                econ.change_points(ctx, self.bet)
                await ctx.send(f"You Win! {self.bet} Colin Coins have been added to your wallet.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            elif (self.betBanker == False):
                econ.change_points(ctx, -self.bet)
                await ctx.send(f"You lose.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            else:
                await ctx.send(f"An error has occured.")

    async def playerWin(self, ctx):
        async with ctx.typing():
            await ctx.send(f"Player wins!")
            if (self.betBanker == False):
                econ.change_points(ctx, self.bet)
                await ctx.send(f"You Win! {self.bet} Colin Coins have been added to your wallet.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            elif (self.betBanker == True):
                econ.change_points(ctx, -self.bet)
                await ctx.send(f"You lose.")
                await ctx.send(f"You now have {econ.get_points(ctx)} Colin Coins.")
            else:
                await ctx.send(f"An error has occured.")
    
@econ.verify_user
async def slots(ctx, bet):
    logger.info(f"{ctx.author.name} called !slots in {ctx.guild}")
    if bet == None:
        async with ctx.typing():
            await ctx.send(f"You must provide a wager, you currently have {econ.get_points(ctx)} Colin Coins.")
        logger.warning(f"{ctx.author.name} attempted to play slots without submitting a wager in {ctx.guild}.")
        return
    if ctx.author.id == 115928421204230149:
        game = Slots_Legacy()
        await game.spin(ctx, bet)
    else:
        game = Slots()
        await game.spin(ctx, bet)
        
@econ.verify_user
async def blackjack(ctx, bet):
    logger.info(f"{ctx.author.name} called !blackjack in {ctx.guild}")
    if bet == None:
        async with ctx.typing():
            await ctx.send(f"You must provide a wager, you currently have {econ.get_points(ctx)} Colin Coins.")
        logger.warning(f"{ctx.author.name} attempted to play blackjack without submitting a wager in {ctx.guild}.")
        return
    game = Blackjack()
    await game.play(ctx, bet)

@econ.verify_user
async def baccarat(ctx, bet):
    logger.info(f"{ctx.author.name} called !baccarat in {ctx.guild}")
    if bet == None:
        async with ctx.typing():
            await ctx.send(f"You must provide a wager, you currently have {econ.get_points(ctx)} Colin Coins.")
        logger.warning(f"{ctx.author.name} attempted to play baccarat without submitting a wager in {ctx.guild}.")
        return
    game = Baccarat()
    await game.play(ctx, bet)

async def payout(ctx):
    logger.info(f"{ctx.author.name} called !payout in {ctx.guild}")
    if ctx.author.id == 115928421204230149:
        await Slots_Legacy.payout_table(ctx)
    else:
        await Slots.payout_table(ctx)

class Cog(commands.Cog, name="gamba"):
    def __init__(self, bot):
        try:
            self.bot = bot
            logger.info(f"Gamba cog successfully initialized.")
        except Exception as e:
            logger.error(f"Unable to initialize gamba cog: {e}")

    @commands.command(name="blackjack", help="Blackjack game, bet with Colin Coins.")
    async def blackjack(self, ctx, bet: int=None):
        await blackjack(ctx, bet)

    @commands.command(name="bj", help="Short for blackjack.")
    async def bj(self, ctx, bet: int=None):
        await blackjack(ctx, bet)

    @commands.command(name="blowjob", help="Long for bj.")
    async def blowjob(self, ctx, bet: int=None):
        await blackjack(ctx, bet)

    @commands.command(name="baccarat", help="Baccarat game, bet with Colin Coins.")
    async def baccarat(self, ctx, bet: int=None):
        await baccarat(ctx, bet)

    @commands.command(name="b", help="Short for baccarat.")
    async def baccarat(self, ctx, bet: int=None):
        await baccarat(ctx, bet)

    @commands.command(name="slots", help="Slot machine game, bet with Colin Coins.")
    async def slots(self, ctx, bet: int=None):
        await slots(ctx, bet)

    @commands.command(name="sluts", help="Short for slots.")
    async def sluts(self, ctx, bet: int=None):
        await slots(ctx, bet)

    @commands.command(name="payout", help="Sends payout amounts for slots game.")
    async def payout(self, ctx):
        await payout(ctx)