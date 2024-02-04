import pandas as pd


def expand_letters(df):
    return df.assign(
        letter_1=lambda df: df["word"].str[0],
        letter_2=lambda df: df["word"].str[1],
        letter_3=lambda df: df["word"].str[2],
        letter_4=lambda df: df["word"].str[3],
        letter_5=lambda df: df["word"].str[4],
    )
