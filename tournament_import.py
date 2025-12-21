import pandas as pd
import re

def main(file_name: str):
    df = parse_pgn_file(file_name)
    df.to_csv("output.csv", index=False)
    pass

def parse_pgn(pgn_text: str) -> dict:
    """
    Parse a single PGN game into a dictionary.
    """
    game_data = {}

    # Extract [Key "Value"] lines
    header_pattern = re.compile(r'\[(\w+)\s+"([^"]*)"\]')
    for key, value in header_pattern.findall(pgn_text):
        game_data[key] = value

    # Extract moves (everything after the headers)
    moves_start = pgn_text.strip().split("\n\n", 1)
    game_data["Moves"] = moves_start[1].strip() if len(moves_start) > 1 else ""

    return game_data


def parse_pgn_file(filename: str) -> pd.DataFrame:
    """
    Parse a full PGN file with one or more games into a DataFrame.
    Each row = one game, index = GameId if available.
    """
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Split games by blank line before a header `[`
    games_raw = re.split(r'\n\s*\n(?=\[)', content)

    games = [parse_pgn(game_text) for game_text in games_raw if game_text.strip()]

    df = pd.DataFrame(games)
    
    # If GameId exists, set as index
    if "Round" in df.columns:
        df.set_index("Round", inplace=True)
    
    df_small = df[["Event", "Date", "White", "Black", "Result", "WhiteElo", "BlackElo"]]

    return df_small

