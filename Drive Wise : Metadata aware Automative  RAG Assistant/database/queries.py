from database.connection import get_db_connection


def get_all_brands():

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                name
            FROM brands
            ORDER BY name
            """
        )

        return cursor.fetchall()

    finally:

        if cursor:
            cursor.close()

        connection.close()


def get_cars_by_brand(brand_id):

    connection = get_db_connection()

    if not connection:
        return []

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                model_name,
                model_code,
                brochure
            FROM cars
            WHERE brand_id = %s
            ORDER BY model_name
            """,
            (brand_id,)
        )

        return cursor.fetchall()

    finally:

        if cursor:
            cursor.close()

        connection.close()


def get_car_by_model(model_code):

    connection = get_db_connection()

    if not connection:
        return None

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                c.id,
                c.model_name,
                c.model_code,
                c.brochure,
                b.name AS brand
            FROM cars c
            JOIN brands b
                ON c.brand_id = b.id
            WHERE c.model_code = %s
            """,
            (model_code,)
        )

        return cursor.fetchone()

    finally:

        if cursor:
            cursor.close()

        connection.close()


def save_query_log(
    user_id,
    brand,
    model,
    question,
    answer,
    retrieved_chunks=0,
    response_time=0,
    retrieval_time=0,
    reranking_time=0,
    context_time=0,
    generation_time=0,
    status="success",
    error_message=None
):

    connection = get_db_connection()

    if not connection:
        return False

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO query_logs
            (
                brand,
                model,
                question,
                answer,
                retrieved_chunks,
                response_time,
                retrieval_time,
                reranking_time,
                context_time,
                generation_time,
                status,
                error_message
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """,
            (
                brand,
                model,
                question,
                answer,
                retrieved_chunks,
                response_time,
                retrieval_time,
                reranking_time,
                context_time,
                generation_time,
                status,
                error_message
            )
        )

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print("Query log error:", e)

        return False

    finally:

        if cursor:
            cursor.close()

        connection.close()