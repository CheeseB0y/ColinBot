import random
import asyncio
import econ

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

    def strength(self):
        total = 0
        for card in self.hand:
            total += card.power()
        if self.has_ace() and total + 10 <= 21:
            return total + 10
        return total
    
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
        self.player = Hand()

    def __str__(self):
        return f"Dealer: {self.dealer}\nPlayer: {self.player}"
    
    def deal(self):
        self.deck.shuffle()
        self.player.draw(self.deck)
        self.dealer.draw(self.deck)
        self.player.draw(self.deck)
        self.dealer.draw(self.deck)

    async def play(self, ctx, bet):
        self.deal()
        if await econ.wager(ctx, bet, min_bet=10, max_bet=10000):
            async with ctx.typing():
                await ctx.send(f"Dealer: *Face Down*, {self.dealer.hand[1]},{' soft' if self.dealer.soft() else ''} {self.dealer.hand[1].power() if not self.dealer.has_ace() else self.dealer.hand[1].power() + 10} points.\nPlayer: {self.player}")
            if self.player.strength() == 21:
                await self.game_outcome(ctx, bet)
            else:
                await self.player_choice(ctx, bet)
        else:
            await ctx.send("Try again.")
    
    async def player_choice(self, ctx, bet):
        async with ctx.typing():
            await ctx.send(f"Would you like to hit or stand?")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        try:
            response = await ctx.bot.wait_for('message', timeout=30.0, check=check)
            if response.content.lower() in ["hit", "h"]:
                await self.hit(ctx, bet)
            elif response.content.lower() in ["stand", "s"]:
                await self.stand(ctx, bet)
            else:
                await ctx.send(f"{response.content} is not a valid input.")
                await self.player_choice(ctx, bet)
        except asyncio.TimeoutError:
            async with ctx.typing():
                await ctx.send("Time out error")

    async def hit(self, ctx, bet):
        async with ctx.typing():
            await ctx.send(f"{self.player.draw(self.deck)},{' soft' if self.player.soft() else ''} {self.player.strength()} points.")
        if self.player.strength() > 21:
            await self.game_outcome(ctx, bet)
        elif self.player.strength() < 21:
            await self.player_choice(ctx, bet)
        else:
            await self.game_outcome(ctx, bet)

    async def stand(self, ctx, bet):
        await self.dealers_turn(ctx, bet)
        
    async def dealers_turn(self, ctx, bet):
        async with ctx.typing():
            await ctx.send(f"Dealer: {self.dealer}")
        while self.dealer.strength() < 17:
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(f"{self.dealer.draw(self.deck)},{' soft' if self.dealer.soft() else ''} {self.dealer.strength()} points.")
        await self.game_outcome(ctx, bet)
        
    async def game_outcome(self, ctx, bet):
        async with ctx.typing():
            await ctx.send(f"Dealer has {self.dealer}\nPlayer has {self.player}")
            if self.dealer.strength() == self.player.strength():
                await ctx.send("Push")
            elif self.player.strength == 21:
                await ctx.send("Blackjack!")
                await ctx.send("You win!")
                await econ.add_points(ctx, bet)
            elif self.player.strength() > 21:
                await ctx.send("Bust, you lose.")
                await econ.lose_points(ctx, bet)
            elif self.dealer.strength() == 21:
                await ctx.send("Blackjack, you lose.")
                await econ.lose_points(ctx, bet)
            elif self.dealer.strength() > 21:
                await ctx.send("Dealer busts, you win!")
                await econ.add_points(ctx, bet)
            elif self.dealer.strength() > self.player.strength():
                await ctx.send("You lose.")
                await econ.lose_points(ctx, bet)
            elif self.dealer.strength() < self.player.strength():
                await ctx.send("You win!")
                await econ.add_points(ctx, bet)
            else:
                await ctx.send("This is an edge case CheeseB0y did not account for, you win?")
                await econ.add_points(ctx, bet)
        
    
async def blackjack(ctx, bet):
    game = Blackjack()
    await game.play(ctx, bet)