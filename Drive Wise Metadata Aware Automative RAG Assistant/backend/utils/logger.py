import os
import json
import logging
from datetime import datetime


# ============================================================
# LOG DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# ============================================================
# LOG FILES
# ============================================================

QUERY_LOG = os.path.join(
    LOG_DIR,
    "queries.jsonl"
)

ERROR_LOG = os.path.join(
    LOG_DIR,
    "errors.log"
)

PERFORMANCE_LOG = os.path.join(
    LOG_DIR,
    "performance.log"
)


# ============================================================
# ERROR LOGGER
# ============================================================

error_logger = logging.getLogger(
    "drive_wise_errors"
)

error_logger.setLevel(
    logging.ERROR
)

if not error_logger.handlers:

    error_handler = logging.FileHandler(
        ERROR_LOG,
        encoding="utf-8"
    )

    error_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    error_handler.setFormatter(
        error_formatter
    )

    error_logger.addHandler(
        error_handler
    )


# ============================================================
# PERFORMANCE LOGGER
# ============================================================

performance_logger = logging.getLogger(
    "drive_wise_performance"
)

performance_logger.setLevel(
    logging.INFO
)

if not performance_logger.handlers:

    performance_handler = logging.FileHandler(
        PERFORMANCE_LOG,
        encoding="utf-8"
    )

    performance_formatter = logging.Formatter(
        "%(asctime)s | %(message)s"
    )

    performance_handler.setFormatter(
        performance_formatter
    )

    performance_logger.addHandler(
        performance_handler
    )


# ============================================================
# LOG QUERY
# ============================================================

def log_query(
    query,
    brand,
    model,
    response_time=None,
    retrieved_chunks=0,
    status="success",
    error=None
):

    record = {

        "timestamp": datetime.now().isoformat(),

        "query": str(query),

        "brand": str(brand),

        "model": str(model),

        "response_time_seconds": (
            round(response_time, 4)
            if response_time is not None
            else None
        ),

        "retrieved_chunks": retrieved_chunks,

        "status": status,

        "error": error
    }


    with open(
        QUERY_LOG,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )


# ============================================================
# LOG ERROR
# ============================================================

def log_error(
    error,
    query=None,
    brand=None,
    model=None
):

    message = (
        f"Query={query} | "
        f"Brand={brand} | "
        f"Model={model} | "
        f"Error={error}"
    )

    error_logger.error(
        message
    )


# ============================================================
# LOG PERFORMANCE
# ============================================================

def log_performance(
    retrieval_time,
    reranking_time,
    context_time,
    generation_time,
    total_time
):

    message = (

        f"retrieval={retrieval_time:.4f}s | "

        f"reranking={reranking_time:.4f}s | "

        f"context={context_time:.4f}s | "

        f"generation={generation_time:.4f}s | "

        f"total={total_time:.4f}s"
    )

    performance_logger.info(
        message
    )

