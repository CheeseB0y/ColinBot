import random


class Reel:
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
        self.symbol = random.choices(self.symbols, weights=self.weights, k=1)[0]


class Slots:
    def __init__(self):
        self.reels = [Reel() for _ in range(5)]
        self.row = []
        self.points = {}
        self.prize = 0

    def spin(self):
        for reel in self.reels:
            reel.spin()
        self.row = [reel.symbol for reel in self.reels]

    def score(self):
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

    def payout(self, bet):
        self.prize = 0
        for symbol, value in self.points.items():
            if symbol == ":cherries:":
                if value == 2:
                    self.prize += bet * 1
                elif value == 3:
                    self.prize += bet * 4
            elif symbol == ":chocolate_bar:":
                if value == 2:
                    self.prize += bet * 1
                elif value == 3:
                    self.prize += bet * 7
            elif symbol == ":bell:":
                if value == 2:
                    self.prize += bet * 2
                elif value == 3:
                    self.prize += bet * 12
            elif symbol == ":four_leaf_clover:":
                if value == 2:
                    self.prize += bet * 2
                elif value == 3:
                    self.prize += bet * 15
            elif symbol == ":star:":
                if value == 2:
                    self.prize += bet * 3
                elif value == 3:
                    self.prize += bet * 18
            elif symbol == ":gem:":
                if value == 2:
                    self.prize += bet * 4
                elif value == 3:
                    self.prize += bet * 25
            elif symbol == ":seven:":
                if value == 2:
                    self.prize += bet * 6
                elif value == 3:
                    self.prize += bet * 35
            elif symbol == ":pregnant_man:":
                if value == 2:
                    self.prize += bet * 25
                elif value == 3:
                    self.prize += bet * 50
            elif symbol == ":lemon:":
                if value == 2:
                    self.prize += bet * 2
                elif value == 3:
                    self.prize += bet * 6
            elif symbol == ":tangerine:":
                if value == 2:
                    self.prize += bet * 3
                elif value == 3:
                    self.prize += bet * 7
            elif symbol == ":watermelon:":
                if value == 2:
                    self.prize += bet * 3
                elif value == 3:
                    self.prize += bet * 10
            elif symbol == ":apple:":
                if value == 2:
                    self.prize += bet * 4
                elif value == 3:
                    self.prize += bet * 12
        return self.prize


def simulate_slot_machine(spins, bet):
    total_bet = 0
    total_prize = 0
    for _ in range(spins):
        game = Slots()
        game.spin()
        game.score()
        prize = game.payout(bet)
        total_bet += bet
        total_prize += prize
    return total_bet, total_prize


if __name__ == "__main__":
    SPINS = 1000000
    BET = 1
    results = simulate_slot_machine(SPINS, BET)
    print(f"Total Bet: {results[0]}, Total Prize: {results[1]}")
