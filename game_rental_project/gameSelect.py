import pandas as pd
from database import DatabaseManager
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class GameSelect:
    def __init__(self):
        """
        Initializes the GameSelect object with a DatabaseManager instance.
        """
        self.db_manager = DatabaseManager("GameRental.db")  # Initialize the DatabaseManager

    def select_games_by_popularity(self, show_plot=True):
        """
        Retrieves a DataFrame of games ordered by popularity.

        Returns:
        - DataFrame: A DataFrame containing columns "Title", "Genre", and "Popularity".
                    Returns None if the DataFrame is empty.
        """
        self.db_manager.connect()

        query = """
            SELECT G.TITLE, G.GENRE, COUNT(R.ID) as Popularity
            FROM GAMES G
            LEFT JOIN RENTAL R ON G.ID = R.ID
            GROUP BY G.TITLE, G.GENRE
            ORDER BY Popularity DESC
        """

        popularity_df = pd.DataFrame(self.db_manager.execute(query), columns=["Title", "Genre", "Popularity"])
        

        self.db_manager.close()

                # Create a bar chart to visualize genre popularity
        plt.figure(figsize=(10, 6))
        plt.bar(popularity_df["Title"], popularity_df["Popularity"])
        plt.xlabel('Title')
        plt.ylabel('Popularity')
        plt.title('Most popular games')
        plt.xticks(rotation=45)

        if not popularity_df.empty and show_plot:
            plt.show()
            plt.clf()
            plt.close()
        elif not popularity_df.empty:
            plt.clf()
            plt.close()

        return popularity_df

    def select_popular_genres(self, show_plot=True):
        """
        Retrieves a DataFrame of popular genres and creates a bar chart to visualize genre popularity.

        Returns:
        - DataFrame: A DataFrame containing columns "Genre" and "Popularity".
                    Returns None if the DataFrame is empty.
        """
        self.db_manager.connect()

        query = """
           SELECT G.GENRE, COUNT(R.ID) AS Popularity
           FROM GAMES G
           LEFT JOIN RENTAL R ON G.ID = R.ID
           GROUP BY G.GENRE
           ORDER BY Popularity DESC; 

        """

        popular_genres_df = pd.DataFrame(self.db_manager.execute(query), columns=["Genre", "Popularity"])
        
        

        self.db_manager.close()
        

        # Create a bar chart to visualize genre popularity
        plt.figure(figsize=(10, 6))
        plt.bar(popular_genres_df["Genre"], popular_genres_df["Popularity"])
        plt.xlabel('Genre')
        plt.ylabel('Popularity')
        plt.title('Genre Popularity')
        plt.xticks(rotation=45)

        if not popular_genres_df.empty and show_plot:

            plt.show()
            plt.clf()
            plt.close()
        elif not popular_genres_df.empty:
            plt.clf()
            plt.close()

        return popular_genres_df

    def select_games_for_purchase(self, budget):
        # Retrieve popularity of games and genres
        popular_games = self.select_games_by_popularity(show_plot=False)
        

        if popular_games is None:
            return "No purchase recommendations found."

        # Total number of rentals
        total_rentals = popular_games["Popularity"].sum()

        # Calculate the proportion of rentals for each game
        popular_games["PopularityProportion"] = popular_games["Popularity"] / total_rentals

        popular_games["Budget"] = popular_games["PopularityProportion"] * budget

        game_price = self.get_purchase_price(popular_games["Title"])

        # Apply the get_purchase_price function to each row
        popular_games["PurchasePrice"] = popular_games.apply(lambda row: self.get_purchase_price(row["Title"]), axis=1)


            # Calculate the number of copies to buy for each game based on the budget
        popular_games["CopiesToBuy"] = (popular_games["Budget"] / popular_games["PurchasePrice"]).astype(int)

        

        if not popular_games.empty:
            return popular_games[["Title", "Genre", "PurchasePrice", "CopiesToBuy"]]
        else:
            return "No purchase recommendations found."
 
    def get_purchase_price(self, title):
        """
        Retrieves the purchase price of a game based on its title.

        Parameters:
        - title (str): The title of the game.

        Returns:
        - float: The purchase price of the game. Returns 0 if not found.
        """
        # Query the database for the purchase price based on title
        self.db_manager.connect()
        query = """
            SELECT PURCHASEPRICE
            FROM GAMES
            WHERE TITLE = ?
        """
        result = self.db_manager.execute(query, (title,))
        self.db_manager.close()

        if result:
            return result[0][0]
        else:
            return 0
        
    def add_purchased_games(self, title, genre, platform, copies, purchase_price):
        """
        Adds purchased games to the database.

        Parameters:
        - title (str): The title of the game.
        - genre (str): The genre of the game.
        - copies (int): The number of copies to be added to the database.
        - purchase_price (float): The purchase price of the game.

        Returns:
        - str: A message indicating whether the operation was successful or not.
        """
        # Generate a new game ID
        new_game_id = self.generate_new_game_id()

        # current date

        purchase_date = datetime.now().strftime("%d/%m/%Y")


        #convert to int

        copies = int(copies)

        #convert to float
        purchase_price = float(purchase_price)

        # Insert the new game into the database for each copy
        success = self.insert_new_game(new_game_id, title, genre, platform, purchase_date, copies, purchase_price)

        if success:
            return f"{copies} copies of game '{title}' added to the database ."
        else:
            return "Failed to add the game to the database."


    def generate_new_game_id(self):

        """
        Generates a new unique game ID for inserting into the database.

        This method queries the database to find the maximum existing game ID, 
        increments it by 1, and returns the new game ID.

        Returns:
        - int: The newly generated game ID.
        """
        # Query the database to find the next available game ID
        self.db_manager.connect()
        query = "SELECT MAX(ID) FROM GAMES"
        result = self.db_manager.execute(query)
        self.db_manager.close()

        max_id = result[0][0] if result and result[0][0] else 0
        new_game_id = max_id + 1

        return new_game_id

    def insert_new_game(self, new_game_id, title, genre, platform, purchase_date, copies, purchase_price):
        """
        Inserts a new game into the database.

        Parameters:
        - new_game_id (int): The ID of the new game.
        - title (str): The title of the game.
        - genre (str): The genre of the game.
        - copies (int): The number of copies to be added to the database.
        - purchase_price (float): The purchase price of the game.

        Returns:
        - bool: True if the insertion was successful, False otherwise.
        """

        # REFORMATTING

        # Convert copies to an integer
        copies = int(copies)

        # Convert purchase_price to a float
        purchase_price = float(purchase_price)

        title = title.lower().replace(" ", "_").replace("'", "")
        genre = genre.lower().replace(" ", "_").replace("'", "")
        platform = platform.lower().replace(" ", "_").replace("'", "")

        # Insert the new game into the database for each copy
        self.db_manager.connect()
    
        try:
            for _ in range(copies):
                query = "INSERT INTO GAMES (ID, TITLE, GENRE, PLATFORM, PURCHASEDATE, PURCHASEPRICE) VALUES (?, ?, ?, ?, ?, ?)"
                self.db_manager.execute(query, (new_game_id, title, genre, platform, purchase_date, purchase_price))
                new_game_id += 1  # Increment the game ID for the next copy
        
            self.db_manager.commit()
            return True

        except Exception as e:
            print(f"Error inserting new game: {e}")
            self.db_manager.rollback()
            return False

        finally:
            self.db_manager.close()



if __name__ == "__main__":
    game_select = GameSelect()

    #price = game_select.get_purchase_price("game_1")
    #print(price)
    #popularity_df = game_select.select_games_for_purchase(3000)
   # print(popularity_df)

    result = game_select.add_purchased_games("gta", "action", 2, 50.0)
    print(result)

    







