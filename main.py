import tournament_import
import table_per_player
import calculate_expected_score
import functions
import pandas as pd

def main():
    # read pgn file and create dataframe that contains all games
    file_name = "C:\\Users\\emili\\OneDrive\\Documents\\Administrative\\Privat\\Performance_rating\\andorra2025_edited.pgn"
    
    df1 = functions.parse_pgn_file(file_name)
    df1.to_csv("output1.csv", index=False)
    df2 = functions.games_to_player_rows(df1)
    df2.to_csv("output2.csv", index=False)    
    print("PGN file parsed and CSVs saved.")

    # create table where there are two rows for each game (one per player)
    #table_per_player.main("output_player_rows.csv", "player_opponent_elos")
    
    df3 = functions.build_player_opponent_elo_table("output2.csv")
    df3.to_csv("output3.csv", index=False)

    #calculate_expected_score.main("player_opponent_elos.csv")
    
    # Test player detail function
    test_name = "Alvarez Albiol, Victor"
    df4 = df2.copy() #Get a list of all the games
    df4 = df4[df4["Player"] == test_name] #Filter for the test player
    test_player = functions.player_detail(name = test_name, player_games = df4) #create player detail
    print("Player details retrieved for player:", test_player.player_name)
    print(test_player.player_games)

    #Calculate the performance rating for the test player
    test_player.calculate_performance_rating(boundary_value= 0.01)
    print("Calculated performance rating based on average method:", test_player.performance_average)
    print("Calculated performance rating based on minimisation method:", test_player.performance)
    
    # run_save_table_to_csv()
    # run_print_tournament_table()
    # run_print_player_table()
    print("This is the end of the main function.")
    pass

if __name__ == "__main__":
    main()