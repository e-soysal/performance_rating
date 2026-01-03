from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import csv
import re
from scipy.optimize import minimize
import numpy as np

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


def parse_pgn_file(file_text: str) -> pd.DataFrame:
    """
    Parse a full PGN file with one or more games into a DataFrame.
    Each row = one game, index = GameId if available.
    """
    text = file_text.strip()

    # Split games by blank line before a header `[`
    games_raw = re.split(r'\n\s*\n(?=\[)', text)

    games = [parse_pgn(game_text) for game_text in games_raw if game_text.strip()]

    df = pd.DataFrame(games)
    
    df_small = df[["Event", "Date", "White","Round", "Black", "Result", "WhiteElo", "BlackElo"]]
    df_small.loc[:,"WhiteElo"] = pd.to_numeric(df["WhiteElo"])
    df_small.loc[:,"BlackElo"] = pd.to_numeric(df["BlackElo"])

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

def build_player_opponent_elo_table(df: pd.DataFrame) -> pd.DataFrame:
    
    # Extract first part of the round (e.g. 10.3 → 10)
    df["RoundInt"] = df["Round"].astype(str).str.split(".").str[0]
    df["RoundCol"] = "Round " + df["RoundInt"]

    # Pivot table
    pivot = df.pivot_table(
        index=["Player", "PlayerElo"],
        columns="RoundCol",
        values="OpponentElo",
        aggfunc="first"
    ).reset_index()

    # Optional: sort round columns numerically
    round_cols = sorted(
        [c for c in pivot.columns if c.startswith("Round ")],
        key=lambda x: int(x.split()[1])
    )

    # Calculate total points:
    points_sum = (
    df.groupby(["Player", "PlayerElo"])["Points"]
      .sum()
      .reset_index(name="TotalPoints")
    )
    # Merge total points into pivot table
    pivot = pivot.merge(
        points_sum,
        on=["Player", "PlayerElo"],
        how="left"
        )
    
    #Find number of rounds played
    rounds_played = (
        df.groupby(["Player", "PlayerElo"])["OpponentElo"]
          .count()   # counts non-null values
          .reset_index(name="RoundsPlayed")
        )
    #Merge rounds played into pivot table
    pivot = pivot.merge(
        rounds_played,
        on=["Player", "PlayerElo"],
        how="left"
    )
    pivot = pivot[["Player", "PlayerElo", "TotalPoints", "RoundsPlayed"] + round_cols]

    return pivot

@dataclass
class Player:
    player_name: str
    player_rating: int
    player_games: pd.DataFrame = field(default_factory=pd.DataFrame)
    performance: Optional[float] = None
    performance_average: Optional[float] = None
    player_rounds: int = None
    score: Optional[float]= None    
    score_percent: Optional[float]= None

    def calculate_performance_rating(self, boundary_value: float, rule: bool) -> float:
        """
        Calculate performance rating based on player's games.
        """

        if self.player_rounds is None or 0:
            print("Player has no rounds played to calculate performance rating.")
            return None

        self.calculate_expected_score(reference_rating= "Current_Elo")
        
        if self.score == 0: 
            print("Player lost all rounds; performance rating is undefined. Using boundary value.")
            resultCorrected = boundary_value * self.player_rounds

        elif self.score == self.player_rounds:
            print("Player won all rounds; performance rating is undefined. Using boundary value.")
            resultCorrected = self.score - boundary_value * self.player_rounds

        else:
            resultCorrected = self.score
        score_percent = resultCorrected / self.player_rounds
        
        opponent_ratings = self.player_games["OpponentElo"].dropna()

        if rule:
            #apply 400-rule
            adjusted_opponent_ratings = opponent_ratings.copy()
            for i, opp_rating in enumerate(opponent_ratings):
                if self.player_rating - opp_rating >= 400:
                    adjusted_opponent_ratings.iat[i] = self.player_rating - 400
                elif opp_rating - self.player_rating >= 400:
                    adjusted_opponent_ratings.iat[i] = self.player_rating + 400
            opponent_ratings = adjusted_opponent_ratings

        if not opponent_ratings.empty:
            #calculate performance rating using average opponent rating
            opponent_average = opponent_ratings.mean()
            self.performance_average = opponent_average - 400 * np.log10(1/score_percent - 1)

            #calculate performance rating using minimisation
            initial_guess = opponent_average
            performanceRating = minimize(target_function, initial_guess,
                                          args= (resultCorrected, 
                                                 opponent_ratings,)).x[0]
            self.performance = np.round(performanceRating) 

        else:
            print("No opponent ratings available to calculate performance average.")
        
        self.calculate_expected_score(reference_rating = "Performance_Average")
        self.calculate_expected_score(reference_rating = "Performance_Minimisation")
        
        return self.performance, self.performance_average
    
    def calculate_expected_score(self, reference_rating: str) -> Optional[float]:
        """
        Calculate expected score based on player's rating and opponent ratings.
        Reference rating can be 'Current_Elo', 'Performance_Average', or 'Performance_Minimisation'.

        """
        if self.player_games.empty:
            print("No games available to calculate expected score.")
            return None
        
        if reference_rating == "Current_Elo":
            rating = self.player_rating
        
        elif reference_rating == "Performance_Average":
            rating = self.performance_average

        elif reference_rating == "Performance_Minimisation":
            rating = self.performance

        expected_scores = logistic(rating, self.player_games["OpponentElo"])
        col_name = "Expected_Score_" + reference_rating
        self.player_games.loc[:, col_name] = expected_scores

        return self.player_games[col_name].sum()


def player_detail(name: str, player_games: pd.DataFrame):
    """
    Extract results for a specific player in a set of games. player games is the games the specific player has playes
    """    
    #Calculate score
    if len(player_games) >0 :
        
        #Find player rating
        rating = player_games.iloc[0]["PlayerElo"]
        player = Player(player_name=name, player_rating = rating)
        
        #Retrieve info about games, score, and number of rounds played
        player_games_small = player_games[["Round", "Opponent", "OpponentElo", "Points"]].copy()
        player_games_small.set_index("Round", inplace=True)
        player.player_games = player_games_small
        player.score = player.player_games["Points"].sum()
        player.player_rounds = len(player.player_games)
        
        return player
    else:
        print("This player is not in the file.")
        return


def target_function(perform_rating, score, opponentElo):
    #this is the target function for minimisation - minimising the squared error)
    return (score - logistic(perform_rating, opponentElo).sum())**2

def logistic(perform_rating, opponentElo):
    return 1 / (1 + 10**((opponentElo - perform_rating) / 400))

