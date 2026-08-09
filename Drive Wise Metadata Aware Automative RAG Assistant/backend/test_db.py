from database.connection import get_db_connection


connection = get_db_connection()

if connection:
    cursor = connection.cursor()

    cursor.execute("SELECT DATABASE();")

    result = cursor.fetchone()

    print("Connected database:", result[0])

    cursor.close()
    connection.close()