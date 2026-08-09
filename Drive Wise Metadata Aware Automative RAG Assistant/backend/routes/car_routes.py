from flask import Blueprint, jsonify

from database.connection import get_db_connection


# ============================================================
# VEHICLE BLUEPRINT
# ============================================================

vehicle_bp = Blueprint(
    "vehicle",
    __name__,
    url_prefix="/api"
)


# ============================================================
# BRAND NAME MAPPING
# ============================================================

BRAND_NAMES = {
    1: "Mahindra",
    2: "Hyundai",
    3: "Kia",
    4: "Tata",
    5: "Toyota"
}


# ============================================================
# GET ALL BRANDS
# ============================================================

@vehicle_bp.route("/brands", methods=["GET"])
def get_brands():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT DISTINCT
                brand_id
            FROM cars
            WHERE brand_id IS NOT NULL
            ORDER BY brand_id
            """
        )

        rows = cursor.fetchall()

        brands = []

        for row in rows:

            brand_id = row["brand_id"]

            brands.append({
                "id": brand_id,
                "name": BRAND_NAMES.get(
                    brand_id,
                    f"Brand {brand_id}"
                )
            })

        print("Brands loaded:", brands)

        return jsonify({
            "success": True,
            "brands": brands
        }), 200

    except Exception as e:

        print(
            "Error loading brands:",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to load brands.",
            "brands": []
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GET CARS / MODELS BY BRAND
# ============================================================

@vehicle_bp.route(
    "/cars/<int:brand_id>",
    methods=["GET"]
)
def get_cars(brand_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

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

        cars = cursor.fetchall()

        print(
            f"Models for brand {brand_id}:",
            cars
        )

        return jsonify({
            "success": True,
            "cars": cars
        }), 200

    except Exception as e:

        print(
            "Error loading cars:",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Unable to load models.",
            "cars": []
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()