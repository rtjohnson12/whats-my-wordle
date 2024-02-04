import pandas as pd


def get_wordsets():
    # Seems like some of the valid guesses are missing, e.g. "teddy"
    valid_solutions = set(pd.read_csv("data/valid_solutions.csv")["word"])
    valid_guesses = set(pd.read_csv("data/valid_guesses.csv")["word"])

    # Union `valid_solutions` and `valid_guesses` to get a set of all valid words
    valid_guesses = valid_guesses.union(valid_solutions)
    valid_guesses = list(valid_guesses)
    valid_solutions = list(valid_solutions)

    return valid_solutions, valid_guesses
