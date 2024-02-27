from database import DatabaseManager
from gameRent import GameRent
import pandas as pd

class GameSearch:

    def __init__(self):
        """
        Initializes the GameSearch object with a DatabaseManager instance and a GameRent instance.
        """
        self.db_manager = DatabaseManager()
        self.game_rent = GameRent()
        self.db_manager.initialize_databases("Game_Info.txt", "Rental_History.txt")

    def search_games_by_title(self, title):
        """
        Searches for games by title in the database and displays the results, including rental status.

        Parameters:
        - title (str): The title of the game to search for.

        Returns:
        - None
        """
        self.db_manager.connect()
        formatted_title = self.format_title(title)  # Format the title
        query = "SELECT * FROM Games WHERE TITLE LIKE ?;"
        parameters = ('%' + formatted_title + '%',)  # Use the formatted title

        results = self.db_manager.execute(query, parameters)

        if results:
            print("Available Games:")
            df = pd.DataFrame(results, columns=["ID", "Platform", "Genre", "Title", "Purchase Price", "Purchase Date"])
            df.set_index("ID", inplace=True)  # Set "ID" as the index
            pd.set_option('display.width', 1000)
            pd.set_option('display.multi_sparse', False)

            rented_games = set()  # Initialize an empty set for rented game IDs

            # Check if each game has been rented and update the "Rented" column
            for i, row in df.iterrows():
                game_id = i
                if self.game_rent.is_game_available(game_id):
                    df.at[i, "Rented"] = "No"  # Game is available for rent
                else:
                    df.at[i, "Rented"] = "Yes"  # Game is already rented
                    rented_games.add(game_id)  # Add the rented game ID to the set

            print(df)
            self.db_manager.close()
        else:
            print("No available games with the title:", title)
            self.db_manager.close()

    def format_title(self, title):
        """
        Formats the title by replacing spaces with underscores and removing single quotes.

        Parameters:
        - title (str): The title of the game.

        Returns:
        - str: The formatted title.
        """
        # Replace spaces with underscores and remove single quotes
        formatted_title = title.replace(" ", "_").replace("'", "")
        return formatted_title

        














