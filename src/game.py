import random
import pandas as pd
from collections import Counter

import logging
from rich.console import Console
from rich.table import Table
from src.data import get_wordsets

logging.basicConfig(level=logging.WARN)

valid_solutions, valid_guesses = get_wordsets()

class WordGuesser:
    def __init__(self, answer="", print_enabled=True, quick_game=False, **kwargs):
        self.__dict__.update(kwargs)
        self.print_enabled = print_enabled
        self.valid_solutions = valid_solutions
        self.valid_guesses = valid_guesses
        self.possible_answers = valid_solutions.copy()

        self.quick_game = quick_game
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
            "does_contain": set(),
            "guesses": [],
        }
        if not self.quick_game:
            self.calculate_word_stats()

        self.console = Console()
        self.table = Table(
            title="Word Guesser Game", show_header=False, show_lines=True
        )
        self.table.add_column("Letter 1", justify="center")
        self.table.add_column("Letter 2", justify="center")
        self.table.add_column("Letter 3", justify="center")
        self.table.add_column("Letter 4", justify="center")
        self.table.add_column("Letter 5", justify="center")

        answer = answer.lower()
        if answer == "":
            self.answer = random.choice(self.valid_solutions)
        else:
            self.answer = answer
        
    def print(self):        
        self.console.print(self.table)

    def suggest_word(self, method="random"):
        if method == "random":
            return random.choice(self.possible_answers)
        elif method == "highest_frequency":
            return self.get_highest_frequency_words(n=1)[0]
        else:
            pass

    def guess_word(self, word):
        word = word.lower()
        self.guess_count += 1
        self.info["guesses"].append(word)
        if word not in self.valid_guesses:
            raise ValueError(f"`{word}` is not a valid guess")

        for idx in range(5):
            if word[idx] == self.answer[idx]:
                self.curr_info[idx] = "[green]"
                self.info["positions"][idx]["match"] = word[idx]
            elif word[idx] in self.answer:
                self.curr_info[idx] = "[yellow]"
                self.info["does_contain"].add(word[idx])
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
        if self.print_enabled:
            self.print()

        if self.curr_info == ["[green]"] * 5:
            logging.info(f"Congratulations! You guessed the word in {self.guess_count} tries.")
            self.game_over = True

        self.narrow_possible_answers()

    def narrow_possible_answers(self):
        # Check 1: If there are near-match, use only words that contain those letters        
        if self.info["does_contain"]:
            logging.info(
                f"Filtering for words with the letters {self.info["does_contain"]}"
            )
            self.possible_answers = [
                word
                for word in self.possible_answers
                if bool(self.info["does_contain"].intersection(set(word)))
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

        if not self.quick_game:
            self.calculate_word_stats()  

    def remove_word(self, word):
        self.info["does_not_contain"] = self.info["does_not_contain"].union(
            set(list(word.lower()))
        )
        self.narrow_possible_answers()

    def calculate_word_stats(self):
        self.position_counters = [Counter() for _ in range(5)]
        for word in self.possible_answers:
            for idx, letter in enumerate(word):
                self.position_counters[idx][letter] += 1

        self.position_percentages = []
        for counter in self.position_counters:
            total = sum(counter.values())
            percentages = {k: v / total for k, v in counter.items()}
            self.position_percentages.append(percentages)

        self.word_stats = {}
        for word in self.possible_answers:
            self.word_stats[word] = {}
            self.word_stats[word]['freq'] = tuple([self.position_percentages[idx][word[idx]] for idx in range(5)])
            self.word_stats[word]['total_freq'] = sum(self.word_stats[word]['freq'])

        self.word_stats = sorted(self.word_stats.items(), key=lambda x: x[1]['total_freq'], reverse=True)

    def get_highest_frequency_words(self, n = 5):
        return [x[0] for x in self.word_stats[:n]]


class WordGuesserAssist(WordGuesser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def new_guess(self, word, colors: tuple = ("", "", "", "", "")):
        word = word.lower()
        if word not in self.valid_guesses:
            raise ValueError(f"`{word}` is not a valid guess")
        self.guess_count += 1
        self.info["guesses"].append(word)

        for idx in range(5):
            if colors[idx] == "green":
                self.curr_info[idx] = "[green]"
                self.info["positions"][idx]["match"] = word[idx]
            elif colors[idx] == "yellow":
                self.curr_info[idx] = "[yellow]"
                self.info["does_contain"].add(word[idx])
                self.info["positions"][idx]["miss"].add(word[idx])
            else:
                
                valid_elsewhere = False
                for jdx in range(5):
                    if jdx != idx and colors[jdx] == "green" and word[jdx] == word[idx]:
                        valid_elsewhere = True
                self.curr_info[idx] = ""
                self.info["positions"][idx]["miss"].add(word[idx])
                if not valid_elsewhere:
                    self.info["does_not_contain"].add(word[idx])

        formatted_args = [
            (self.curr_info[i] + word[i]) if self.curr_info[i] else word[i]
            for i in range(5)
        ]
        self.table.add_row(*formatted_args)
        if self.print_enabled:
            self.print()

        if self.curr_info == ["[green]"] * 5:
            logging.info(f"Congratulations! You guessed the word in {self.guess_count} tries.")
            self.game_over = True

        self.narrow_possible_answers()
