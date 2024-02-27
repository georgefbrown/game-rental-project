import sqlite3
from datetime import datetime

class DatabaseManager:

    def __init__(self, gamerental_db_file="GameRental.db"):
        """
        Initializes the DatabaseManager with the specified database file.
        """
        self.gamerental_db_file = gamerental_db_file

    def connect(self):
        """
        Connects to the database.
        """
        self.connection = sqlite3.connect(self.gamerental_db_file)
        self.cursor = self.connection.cursor()

    def commit(self):
        """
        Commits changes to the database if a connection exists.
        """
        if self.connection:
            self.connection.commit()

    def create_tables(self):
        """
        Creates database tables if they do not exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Games (
                ID INTEGER,
                PLATFORM TEXT,
                GENRE TEXT,
                TITLE TEXT,
                PURCHASEPRICE REAL,
                PURCHASEDATE DATE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Rental (
                ID INTEGER,
                RENTALDATE DATE,
                RETURNDATE DATE,
                CUSTOMERID INTEGER
            )
        ''')

        self.connection.commit()

    def close(self):
        """
        Closes the database connection if it exists.
        """
        if self.connection:
            self.connection.close()

    def format_date(self, date_str):
        """
        Formats the date string to the desired format.

        Parameters:
        - date_str (str): The date string to be formatted.

        Returns:
        - str or None: The formatted date string or None if the input is None.
        """
        if date_str is None:
            return None

        formats_to_try = ["%d/%m/%Y", "%m/%d/%Y"]

        for date_format in formats_to_try:
            try:
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                continue

        # If none of the formats match, assume it's already in the desired format
        return date_str

    def clear_tables(self):
        """
        Clears existing data in both tables.
        """
        self.cursor.execute("DELETE FROM Games")
        self.cursor.execute("DELETE FROM Rental")
        self.connection.commit()

    def initialize_databases(self, games_info_file, rental_history_file):
        """
        Initializes the databases by creating tables, clearing existing data, and populating them with cleaned data from files.

        Parameters:
        - games_info_file (str): The file containing games information.
        - rental_history_file (str): The file containing rental history information.
        """
        self.connect()
        self.create_tables()

        self.clear_tables()

        # SPLITTING INTO FIELDS

        with open(games_info_file, "r") as file:
            lines = file.readlines()
            for line in lines[1:]:
                fields = [field.strip() if field.strip() != '' else None for field in line.split(",")]  # Splitting each field by ","

                if len(fields) == 6:
                    game_id, platform, genre, title, purchase_price, purchase_date = fields

                    # Formatting the date
                    purchase_date = self.format_date(purchase_date)  


                    # Handing missing purchase price value (setting to 0 if missing)
                    try:
                        purchase_price = float(purchase_price) 
                    except (ValueError, TypeError):
                        purchase_price = 0.0

                    # Normalizing by putting everything in lowercase and removing "'"
                    platform = platform.lower().replace("'", "")  
                    genre = genre.lower().replace("'", "")
                    title = title.lower().replace("'", "")

                    self.cursor.execute('''
                        INSERT INTO Games (ID, PLATFORM, GENRE, TITLE, PURCHASEPRICE, PURCHASEDATE)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (game_id, platform, genre, title, float(purchase_price), purchase_date))

        with open(rental_history_file, "r") as file:
            lines = file.readlines()
            for line in lines[1:]:
                fields = [field.strip() if field.strip() != '' else None for field in line.split(",")]

                if len(fields) == 4:
                    game_id, rental_date, return_date, customer_id = fields

                    #Formatting dates
                    rental_date = self.format_date(rental_date)
                    return_date = self.format_date(return_date)

                    self.cursor.execute('''
                        INSERT INTO Rental (ID, RENTALDATE, RETURNDATE, CUSTOMERID)
                        VALUES (?, ?, ?, ?)
                    ''', (game_id, rental_date, return_date, customer_id))

        self.connection.commit()
        self.close()

    def execute(self, query, parameters=None):
        """
        Executes a SQL query with optional parameters.

        Parameters:
        - query (str): The SQL query to be executed.
        - parameters (tuple): The parameters to be used in the query.

        Returns:
        - list or None: The result of the query as a list or None in case of an error.
        """
        self.connect()

        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)

            result = self.cursor.fetchall()
            self.connection.commit()
            return result
        except sqlite3.Error as e:
            print("Error executing query:", e)
            return None

       


            









        



        
  


