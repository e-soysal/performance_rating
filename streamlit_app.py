import streamlit as st
import functions
from io import StringIO
import numpy

st.set_page_config(page_title="PGN Player Viewer")

st.title("Performance Rating Calculator")
st.write("This app allows you to upload a PGN file and view player performance rating calculated by different methods.")

# Upload PGN file
uploaded_file = st.file_uploader("Upload a PGN file", type=["pgn"])

if uploaded_file is not None:
    # Read PGN content
    pgn_text = uploaded_file.read().decode("utf-8")
    
    df1 = functions.parse_pgn_file(pgn_text)
    
    df2 = functions.games_to_player_rows(df1)
    
    df3 = functions.build_player_opponent_elo_table(df2)
    
    st.write("PGN file parsed successfully.")
    
    if "view" not in st.session_state:
        st.session_state.view = None   # ← nothing selected yet
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Tournament view"):
            st.session_state.view = "tournament"

    with col2:
        if st.button("Player view"):
            st.session_state.view = "player"

    st.divider()

    if st.session_state.view == "tournament":
        st.header("Tournament view")
        st.write(df3)

    elif st.session_state.view == "player":
        st.header("Player view")
        
        # Test player detail function
        players = df2["Player"].unique()

        # Dropdown with player names
        selected_player = st.selectbox(
            "Select a player to view performance:",
            sorted(players)
        )

        # Display something related to the player
        df4 = df2.copy() #Get a list of all the games
        df4 = df4[df4["Player"] == selected_player] #Filter for the test player
        test_player = functions.player_detail(name = selected_player, player_games = df4) #create player detail
        st.write("Player details retrieved for player:", test_player.player_name)
        st.write("Elo rating:", test_player.player_rating, "Score:", test_player.score, "Rounds played:", test_player.player_rounds)
        
        #Calculate the performance rating for the test player
        test_player.calculate_performance_rating(boundary_value= 0.01, reference_rating="elo")
        st.write("Calculated performance - average method:", numpy.round(test_player.performance_average))
        st.write("Calculated performance - minimisation method:", numpy.round(test_player.performance))
        
        st.write(test_player.player_games)

    else:
        # Optional: placeholder message, or leave empty
        st.info("Please choose a view to continue")
else:
    st.warning("Please upload a PGN file to proceed.")
    st.stop()

    
