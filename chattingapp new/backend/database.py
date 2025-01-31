import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Replace with your MySQL username
                password='',  # Replace with your MySQL password
                database='chat_app'  # Replace with your database name
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error: {e}")
            self.connection = None

    def execute_query(self, query, params=None):
        """Executes a single query."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(f"Error executing query: {e}")

    def fetch_all(self, query, params=None):
        """Fetches all results from a query."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []

    def fetch_one(self, query, params=None):
        """Fetches a single result from a query."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

    def close(self):
        """Closes the cursor and connection."""
        if hasattr(self, 'cursor') and hasattr(self, 'connection'):
            if self.cursor and self.connection:
                self.cursor.close()
                print("Cursor closed.")
                
            if self.connection.is_connected():
                self.connection.close()
                print("MySQL connection closed.")
