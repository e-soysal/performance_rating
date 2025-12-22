import pandas as pd
import re

def main(file_name: str):
    df = parse_pgn_file(file_name)
    df.to_csv("output.csv", index=False)
    df_player_rows = games_to_player_rows(df)
    df_player_rows.to_csv("output_player_rows.csv", index=False)    
    print("PGN file parsed and CSVs saved.")
    pass

def parse_pgn(pgn_text: str) -> dict:
    """
    Parse a single PGN game into a dictionary.
    """
    game_data = {}

    # Extract [Key "Value"] lines
    header_pattern = re.compile(r'\[(\w+)\s+"([^"]*)"\]')
    for key, value in header_pattern.findall(pgn_text):
        game_data[key] = value.strip().strip('"')

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
    
    df_small = df[["Event", "Date", "White","Round", "Black", "Result", "WhiteElo", "BlackElo"]]
    return df_small

def games_to_player_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert one-game-per-row DataFrame into
    two-rows-per-game (one per player).
    """
    rows = []

    for _, game in df.iterrows():
        result = game["Result"]

        # Determine points
        if result == "1-0":
            white_pts, black_pts = 1.0, 0.0
        elif result == "0-1":
            white_pts, black_pts = 0.0, 1.0
        else:  # "1/2-1/2"
            white_pts = black_pts = 0.5

        # White player row
        rows.append({
            "Event": game["Event"],
            "Date": game["Date"],
            "Round": game["Round"],
            "Player": game["White"],
            "Color": "White",
            "Points": white_pts,
            "PlayerElo": game["WhiteElo"],
            "Opponent": game["Black"],
            "OpponentElo": game["BlackElo"],
        })

        # Black player row
        rows.append({
            "Event": game["Event"],
            "Date": game["Date"],
            "Round": game["Round"],
            "Player": game["Black"],
            "Color": "Black",
            "Points": black_pts,
            "PlayerElo": game["BlackElo"],
            "Opponent": game["White"],
            "OpponentElo": game["WhiteElo"],
        })

    return pd.DataFrame(rows)