from database import DatabaseManager
from datetime import datetime

class GameReturn:

    def __init__(self):
        """
        Initializes the GameReturn object with a DatabaseManager instance.
        """
        self.db_manager = DatabaseManager("GameRental.db")  # Initialize the DatabaseManager

    def return_game(self, customer_id, game_id):
        """
        Returns a rented game, updating the return date in the database.

        Parameters:
        - customer_id (str): The ID of the customer returning the game.
        - game_id (str): The ID of the game to be returned.

        Returns:
        - str: A message indicating the result of the return attempt.
        """
        # Check if the game is currently rented by the customer
        if self.is_game_rented_by_customer(customer_id, game_id):
            # Update the return date in the database
            current_date = datetime.now().strftime("%d/%m/%Y")
            query = "UPDATE Rental SET RETURNDATE = ? WHERE ID = ? AND CUSTOMERID = ? AND RETURNDATE IS NULL"
            self.db_manager.execute(query, (current_date, game_id, customer_id))
            return "Game returned successfully."
        else:
            return "Game is not rented by this customer."

    def is_game_rented_by_customer(self, customer_id, game_id):
        """
        Checks if a game is currently rented by the specified customer.

        Parameters:
        - customer_id (str): The ID of the customer.
        - game_id (str): The ID of the game.

        Returns:
        - bool: True if the game is rented by the customer, False otherwise.
        """
        self.db_manager.connect()
        # Check if the game is currently rented by the customer
        query = "SELECT ID FROM Rental WHERE ID = ? AND CUSTOMERID = ? AND RETURNDATE IS NULL"
        result = self.db_manager.execute(query, (game_id, customer_id))
        return bool(result)

# Example usage
if __name__ == "__main__":
    db_manager = DatabaseManager()
    game_return_manager = GameReturn()

    # Provide customer_id and game_id to return a game
    customer_id = "1234"
    game_id = "1"

    result = game_return_manager.return_game(customer_id, game_id)

    print(result)

