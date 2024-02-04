import random
import pandas as pd
import logging

from rich.console import Console
from rich.table import Table

logging.basicConfig(level=logging.WARN)


class WordGuesser:
    def __init__(self, answer="", **kwargs):
        self.__dict__.update(kwargs)
        # Seems like some of the valid guesses are missing, e.g. "teddy"
        self.valid_solutions = set(pd.read_csv("data/valid_solutions.csv")["word"])
        self.valid_guesses = set(pd.read_csv("data/valid_guesses.csv")["word"])
        self.valid_guesses = self.valid_guesses.union(self.valid_solutions)
        self.valid_solutions = list(self.valid_solutions)
        self.valid_guesses = list(self.valid_guesses)
        self.possible_answers = self.valid_solutions.copy()

        self.game_over = False
        self.guess_count = 0
        self.curr_info = [""] * 5
        self.info = {
            "positions": {
                0: {"match": "", "miss": set()},
                1: {"match": "", "miss": set()},
                2: {"match": "", "miss": set()},
                3: {"match": "", "miss": set()},
                4: {"match": "", "miss": set()},
            },
            "does_not_contain": set(),
            "matches": set(),
            "guesses": [],
        }

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
        else:
            self.answer = answer

    def print(self):
        self.console.print(self.table)

    def suggest_word(self, method="random"):
        if method == "random":
            return random.choice(self.possible_answers)
        else:
            pass

    def guess_word(self, word):
        self.guess_count += 1
        self.info["guesses"].append(word)
        word = word.lower()
        if word not in self.valid_guesses:
            raise ValueError(f"`{word}` is not a valid guess")

        for idx in range(5):
            if word[idx] == self.answer[idx]:
                self.curr_info[idx] = "[green]"
                self.info["positions"][idx]["match"] = word[idx]
            elif word[idx] in self.answer:
                self.curr_info[idx] = "[yellow]"
                self.info["matches"].add(word[idx])
                self.info["positions"][idx]["miss"].add(word[idx])
            else:
                self.curr_info[idx] = ""
                self.info["positions"][idx]["miss"].add(word[idx])
                self.info["does_not_contain"].add(word[idx])

        formatted_args = [
            (self.curr_info[i] + word[i]) if self.curr_info[i] else word[i]
            for i in range(5)
        ]
        self.table.add_row(*formatted_args)
        self.print()

        if self.curr_info == ["[green]"] * 5:
            print(f"Congratulations! You guessed the word in {self.guess_count} tries.")
            self.game_over = True

        self.narrow_possible_answers()

    def narrow_possible_answers(self):
        # Check 1: If there are near-match, use only words that contain those letters
        if self.info["matches"]:
            logging.info(
                f"Filtering for words with the letters {self.info["matches"]}"
            )
            self.possible_answers = [
                word
                for word in self.possible_answers
                if bool(self.info["matches"].intersection(set(word)))
            ]

        # Check 2: If there are `does_not_contain` letters, use only words without those letters
        if self.info["does_not_contain"]:
            logging.info(
                f"Filtering for words without the letters {self.info["does_not_contain"]}"
            )
            self.possible_answers = [
                word
                for word in self.possible_answers
                if not bool(self.info["does_not_contain"].intersection(set(word)))
            ]

        for idx in range(5):
            # Check 3: If the position has a match, use only words with that letter in that position
            if self.info["positions"][idx]["match"]:
                logging.info(
                    f"Filtering for words with {self.info['positions'][idx]['match']} at position {idx}"
                )
                self.possible_answers = [
                    word
                    for word in self.possible_answers
                    if word[idx] == self.info["positions"][idx]["match"]
                ]

            # Check 4: If the position has misses, use only words that do not contain those letters in that position
            if self.info["positions"][idx]["miss"]:
                logging.info(
                    f"Filtering for words without the letters {self.info['positions'][idx]['miss']} at position {idx}"
                )
                self.possible_answers = [
                    word
                    for word in self.possible_answers
                    if word[idx] not in self.info["positions"][idx]["miss"]
                ]
