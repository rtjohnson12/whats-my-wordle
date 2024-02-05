import pickle
from src.data import get_wordsets
from src.game import WordGuesser

import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

valid_solutions, valid_guesses = get_wordsets()


def run_experiment(n_trials=1000, method="random", overwrite=False):
    if method not in ["random", "highest_frequency"]:
        raise ValueError("Method must be either 'random' or 'highest_frequency'")

    if not overwrite:
        try:
            with open(f"data/{method}_method_n{n_trials}.pkl", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            pass

    if method == "random":
        quick_game = True
    else:
        quick_game = False

    experiments = dict()
    for solution in tqdm(valid_solutions):
        experiments[solution] = list()
        for i in range(n_trials):
            game = WordGuesser(
                answer=solution, print_enabled=False, quick_game=quick_game
            )
            while not game.game_over:
                game.guess_word(game.suggest_word(method=method))
            experiments[solution] = experiments[solution] + [game.guess_count]

    with open(f"data/{method}_method_n{n_trials}.pkl", "wb") as f:
        pickle.dump(experiments, f)

    return experiments


random_experiments = run_experiment(n_trials=1000, method="random")
highest_frequency_experiments = run_experiment(n_trials=1, method="highest_frequency")


sns.displot(random_experiments["storm"], kde=False)
plt.show()
random_experiments["storm"]
highest_frequency_experiments["storm"]
