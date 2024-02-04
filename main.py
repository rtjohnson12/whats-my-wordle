from src.game import WordGuesser

game = WordGuesser()
game.guess_word("tears")

game.suggest_word(method="random")
print(game.possible_answers)
