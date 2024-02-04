from src.game import WordGuesser, WordGuesserAssist

game = WordGuesser(print_enabled=False)
while not game.game_over:
    game.guess_word(game.suggest_word(method="highest_frequency"))

game.print()
