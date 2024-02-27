from database import DatabaseManager
import subscriptionManager
import pandas as pd
from datetime import datetime

class GameRent:

    def __init__(self):
        """
        Initializes the GameRent object with a DatabaseManager instance.
        """
        self.db_manager = DatabaseManager("GameRental.db")  # Initialize the DatabaseManager

    def rent_game(self, customer_id, game_id):
        """
        Rents a game to a customer, updating the rental information in the database.

        Parameters:
        - customer_id (str): The ID of the customer renting the game.
        - game_id (str): The ID of the game to be rented.

        Returns:
        - str: A message indicating the result of the rental attempt.
        """
        self.db_manager.connect()
        # Load subscription information
        subscriptions = subscriptionManager.load_subscriptions("/Users/georgebrown/Documents/MASTERS/programming_project/Subscription_Info.txt") #USE OWN PATH HERE

        # Check if the customer's subscription is active
        if subscriptionManager.check_subscription(customer_id, subscriptions):
            if self.has_reached_rental_limit(customer_id):
                return "Rental limit reached. Cannot rent more games."
            else:
                if self.is_game_available(game_id):
                    # Mark the game as rented in the database
                    rent_date = datetime.now().strftime("%d/%m/%Y")
                    self.db_manager.execute("INSERT INTO Rental (ID, RENTALDATE, RETURNDATE, CUSTOMERID) VALUES (?, ?, ?, ?)",
                                            (game_id, rent_date, None, customer_id))
                    
                    self.db_manager.commit()
                    self.db_manager.close()
                    
                    return "Game rented successfully."
                
                else:
                    self.db_manager.close()
                    
                    return "Game is not available for rent."
        else:

            self.db_manager.close()
            
            return "Customer subscription is not active."

    def is_game_available(self, game_id):
        """
        Checks if a game is available for rent (not currently rented).

        Parameters:
        - game_id (str): The ID of the game.

        Returns:
        - bool: True if the game is available, False if it is currently rented or does not exist.
        """
        self.db_manager.connect()

        # Check if the game exists in the database
        game_exists_query = "SELECT ID FROM Games WHERE ID = ?"
        game_exists_result = self.db_manager.execute(game_exists_query, (game_id,))

        if not game_exists_result:
            return False  # Game does not exist in the database

        # Check if the game is available for rent (e.g., not currently rented)
        rental_query = "SELECT ID FROM Rental WHERE ID = ? AND RETURNDATE IS NULL"
        rental_result = self.db_manager.execute(rental_query, (game_id,))
        self.db_manager.close()

        # If there is a result, the game is currently rented and not available
        if rental_result:
            return False
        else:
            return True

    def has_reached_rental_limit(self, customer_id):
        """
        Checks if a customer has reached their rental limit based on subscription type.

        Parameters:
        - customer_id (str): The ID of the customer.

        Returns:
        - bool: True if the customer has reached the rental limit, False otherwise.
        """
        # Load subscription information
        subscriptions = subscriptionManager.load_subscriptions("/Users/georgebrown/Documents/MASTERS/programming_project/Subscription_Info.txt")

        # Check if the customer's subscription is active
        if customer_id in subscriptions:
            # Get the customer's subscription type
            subscription_type = subscriptions[customer_id]["SubscriptionType"]

            # Get the rental limit based on the subscription type
            rental_limit = subscriptionManager.get_rental_limit(subscription_type)

            # Count the number of games rented by the customer
            query = "SELECT COUNT(*) FROM Rental WHERE CUSTOMERID = ? AND RETURNDATE IS NULL"
            result = self.db_manager.execute(query, (customer_id,))

            if result:
                games_rented = result[0][0]  # The count of rented games
                return games_rented >= rental_limit  # True if the limit is reached, False otherwise
            else:
                return False  # An error occurred while querying the database
        else:
            return False  # Customer does not exist in subscription data or does not have a subscription

    def view_rental_history(self):
        """
        Retrieves and returns the rental history as a DataFrame.

        Returns:
        - pd.DataFrame: Rental history DataFrame with columns: ID, Rental Date, Return Date, Customer ID.
        """
        self.db_manager.connect()

        query = "SELECT ID, RENTALDATE, RETURNDATE, CUSTOMERID FROM RENTAL;"
        rental_history_df = pd.DataFrame(self.db_manager.execute(query), columns=["ID", "Rental Date", "Return Date", "Customer ID"])
        rental_history_df.set_index("ID", inplace=True)

        self.db_manager.close()

        return rental_history_df


# Example usage
if __name__ == "__main__":
    db_manager = DatabaseManager()
    game_rent_manager = GameRent()

    # Provide customer_id and game_id to rent a game
    customer_id = "1234"
    game_id = "1"

    result = game_rent_manager.rent_game(customer_id, game_id)

    query = "SELECT * FROM Rental;"
    
    db_manager.connect()
    db_manager.initialize_databases("/Users/georgebrown/Documents/MASTERS/programming_project/Game_Info.txt", "/Users/georgebrown/Documents/MASTERS/programming_project/Rental_History.txt" )
    results = db_manager.execute(query)
    df = pd.DataFrame(results, columns=["ID", "RENTALDATE", "RETURNDATE", "CUSTOMERID"])
    print(df)
    db_manager.close()




    
    

   

   

    

   
   




