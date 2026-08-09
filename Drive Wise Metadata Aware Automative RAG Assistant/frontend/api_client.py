import requests


BACKEND_URL = "http://127.0.0.1:5000"


def ask_question(
    brand,
    model,
    question
):
    """
    Send user question to Flask backend.
    """

    url = f"{BACKEND_URL}/api/chat/"

    payload = {
        "brand": brand,
        "model": model,
        "question": question
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        return {
            "success": False,
            "error": (
                "Could not connect to the "
                "Drive Wise backend. "
                "Please make sure Flask is running."
            )
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "error": (
                "The request took too long. "
                "Please try again."
            )
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": str(error)
        }