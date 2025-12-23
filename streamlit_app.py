import streamlit as st
import functions
from io import StringIO

st.set_page_config(page_title="PGN Player Viewer")

st.title("Performance Rating Calculator")
# Upload PGN file
uploaded_file = st.file_uploader("Upload a PGN file", type=["pgn"])

if uploaded_file is not None:
    # Read PGN content
    pgn_text = uploaded_file.read().decode("utf-8")
    
    df1 = functions.parse_pgn_file(pgn_text)
    
    df2 = functions.games_to_player_rows(df1)
    
    st.write("PGN file parsed and CSVs saved.")
    
    df3 = functions.build_player_opponent_elo_table("output2.csv")
    
    st.write("Player opponent ELO table created.")

    # Test player detail function
    players = df2["Player"].unique()

    # Dropdown with player names
    selected_player = st.selectbox(
        "Select a player to view performance:",
        sorted(players)
    )

    # 4️⃣ Display something related to the player
    st.subheader(f"Information for {selected_player}")
    
    df4 = df2.copy() #Get a list of all the games
    df4 = df4[df4["Player"] == selected_player] #Filter for the test player
    test_player = functions.player_detail(name = selected_player, player_games = df4) #create player detail
    st.write("Player details retrieved for player:", test_player.player_name)
    st.write(test_player.player_games)

    #Calculate the performance rating for the test player
    test_player.calculate_performance_rating(boundary_value= 0.01)
    st.write("Calculated performance rating based on average method:", test_player.performance_average)
    st.write("Calculated performance rating based on minimisation method:", test_player.performance)

else:
    st.warning("Please upload a PGN file to proceed.")
    st.stop()

    
