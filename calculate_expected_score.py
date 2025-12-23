import pandas as pd
import re

def main(file_name: str):
    df = pd.read_csv(file_name)
    df = calculate_expected_scores(df)
    df.to_csv("player_expected_scores.csv", index=False)
    pass

def calculate_expected_scores(df: pd.DataFrame) -> pd.DataFrame:
    # Calculate expected scores for each player
    
    return df

def expected_score(player_elo, opponent_elo):
        return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))
