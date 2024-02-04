import random
import pandas as pd

from rich.console import Console
from rich.table import Table

from src.data import expand_letters


class WordGuesser:
    def __init__(self, answer="", **kwargs):
        # Seems like some of the valid guesses are missing, e.g. "teddy"
        self.valid_solutions = set(pd.read_csv("data/valid_solutions.csv")["word"])
        self.valid_guesses = set(pd.read_csv("data/valid_guesses.csv")["word"])
        self.valid_guesses = self.valid_guesses.union(self.valid_solutions)
        self.valid_solutions = list(self.valid_solutions)
        self.valid_guesses = list(self.valid_guesses)

        self.guess_count = 0
        self.curr_info = [""] * 5
        self.info = {"positions": [""] * 5, "matches": set()}
        self.__dict__.update(kwargs)

        self.console = Console()
        self.table = Table(
            title="Word Guesser Game", show_header=False, show_lines=True
        )
        self.table.add_column("Letter 1", justify="center")
        self.table.add_column("Letter 2", justify="center")
        self.table.add_column("Letter 3", justify="center")
        self.table.add_column("Letter 4", justify="center")
        self.table.add_column("Letter 5", justify="center")

        if answer == "":
            self.answer = random.choice(self.valid_solutions)

    def guess_word(self, word):
        self.guess_count += 1
        word = word.lower()
        if word not in self.valid_guesses:
            raise ValueError(f"`{word}` is not a valid guess")

        for idx in range(5):
            if word[idx] == self.answer[idx]:
                self.curr_info[idx] = "[green]"
                self.info["positions"][idx] = word[idx]
            elif word[idx] in self.answer:
                self.curr_info[idx] = "[yellow]"
                self.info["matches"].add(word[idx])
            else:
                self.curr_info[idx] = ""

        formatted_args = [
            (self.curr_info[i] + word[i]) if self.curr_info[i] else word[i]
            for i in range(5)
        ]
        self.table.add_row(*formatted_args)
        self.console.print(self.table)

        if self.curr_info == ["[green]"] * 5:
            print(f"Congratulations! You guessed the word in {self.guess_count} tries.")


game = WordGuesser()
game.guess_word("tears")
game.guess_word(game.answer)
