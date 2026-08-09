from database.connection import get_db_connection


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(
    user_id,
    brand,
    model,
    question,
    answer
):

    connection = None
    cursor = None

    try:

        print("========================================")
        print("SAVING CHAT HISTORY")
        print("User ID:", user_id)
        print("Brand:", brand)
        print("Model:", model)
        print("Question:", question)
        print("Answer:", answer)
        print("========================================")


        # ----------------------------------------------------
        # DATABASE CONNECTION
        # ----------------------------------------------------

        connection = get_db_connection()


        if connection is None:

            print(
                "ERROR: Database connection is None"
            )

            return False


        # ----------------------------------------------------
        # CURSOR
        # ----------------------------------------------------

        cursor = connection.cursor()


        # ----------------------------------------------------
        # INSERT
        # ----------------------------------------------------

        query = """
            INSERT INTO chat_history
            (
                user_id,
                brand,
                model,
                question,
                answer
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """


        values = (

            user_id,

            brand,

            model,

            question,

            answer

        )


        cursor.execute(
            query,
            values
        )


        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        connection.commit()


        print(
            "HISTORY SAVED SUCCESSFULLY"
        )


        print(
            "Inserted ID:",
            cursor.lastrowid
        )


        return True


    except Exception as error:

        print(
            "========================================"
        )

        print(
            "SAVE HISTORY DATABASE ERROR:"
        )

        print(
            error
        )

        print(
            "========================================"
        )


        if connection:

            connection.rollback()


        return False


    finally:

        if cursor:

            cursor.close()


        if connection:

            connection.close()


# ============================================================
# GET HISTORY
# ============================================================

def get_chat_history(
    user_id
):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()


        if connection is None:

            print(
                "ERROR: Database connection is None"
            )

            return []


        cursor = connection.cursor(
            dictionary=True
        )


        query = """
            SELECT
                id,
                user_id,
                brand,
                model,
                question,
                answer,
                created_at
            FROM chat_history
            WHERE user_id = %s
            ORDER BY created_at DESC
        """


        cursor.execute(
            query,
            (user_id,)
        )


        history = cursor.fetchall()


        print(
            "HISTORY LOADED:",
            history
        )


        return history


    except Exception as error:

        print(
            "GET HISTORY DATABASE ERROR:",
            error
        )

        return []


    finally:

        if cursor:

            cursor.close()


        if connection:

            connection.close()