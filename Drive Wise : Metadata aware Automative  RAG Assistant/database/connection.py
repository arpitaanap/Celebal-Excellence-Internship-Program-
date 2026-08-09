import os

import mysql.connector
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def get_db_connection():
    """
    Create and return a MySQL database connection.
    """

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        return connection

    except mysql.connector.Error as e:
        print(f"MySQL connection failed: {e}")
        return None


# Test connection when this file is executed directly
if __name__ == "__main__":

    connection = get_db_connection()

    if connection:
        print("MySQL database connected successfully")
        print("Database:", connection.database)

        connection.close()

        print("Connection closed.")