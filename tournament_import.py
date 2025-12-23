import csv
import pandas as pd
import re

def main(file_name: str):
    df = parse_pgn_file(file_name)
    df.to_csv("output.csv", index=False)
    df = pd.read_csv("output.csv")
    df_player_rows = games_to_player_rows(df)
    df_player_rows.to_csv("output_player_rows.csv", index=False)    
    print("PGN file parsed and CSVs saved.")
    pass

