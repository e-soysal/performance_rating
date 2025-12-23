import streamlit as st
import functions
from io import StringIO

st.set_page_config(page_title="PGN Player Viewer")

st.title("PGN Performance Rating Calculator")
# Upload PGN file
uploaded_file = st.file_uploader("Upload a PGN file", type=["pgn"])
if uploaded_file is not None:
    # Read PGN content
    pgn_text = uploaded_file.read().decode("utf-8")
df1 = functions.parse_pgn_file(pgn_text)
df2 = functions.games_to_player_rows(df1)
st.write("PGN file parsed and CSVs saved.")

# create table where there are two rows for each game (one per player)
#table_per_player.main("output_player_rows.csv", "player_opponent_elos")
    
df3 = functions.build_player_opponent_elo_table("output2.csv")
st.write("Player opponent ELO table created.")