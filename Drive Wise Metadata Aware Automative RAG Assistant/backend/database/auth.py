import bcrypt

from database.connection import get_db_connection


# ============================================================
# REGISTER USER
# ============================================================

def register_user(name, email, password):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # CHECK EXISTING EMAIL
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return False, "An account with this email already exists."

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ----------------------------------------------------
        # INSERT USER
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                password_hash
            )
        )

        connection.commit()

        return True, "Registration successful."

    except Exception as e:

        print(
            f"❌ Registration error: {e}"
        )

        if connection:
            connection.rollback()

        return False, "Registration failed."

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# LOGIN USER
# ============================================================

def login_user(email, password):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        if connection is None:
            return None

        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            return None

        # ----------------------------------------------------
        # CHECK PASSWORD
        # ----------------------------------------------------

        password_valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if not password_valid:

            return None

        # ----------------------------------------------------
        # REMOVE PASSWORD HASH
        # ----------------------------------------------------

        user.pop(
            "password_hash",
            None
        )

        return user

    except Exception as e:

        print(
            f"❌ Login error: {e}"
        )

        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()