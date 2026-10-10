import logging
from datetime import datetime, timedelta, timezone
import os

from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from core.config import PROJECT_ROOT, settings

logs_dir = PROJECT_ROOT / "LOGS"

COLORS = {
    "DEBUG": "\033[92m",
    "INFO": "\033[94m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[95m",
    "RESET": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, COLORS["RESET"])
        reset = COLORS["RESET"]

        message = super().format(record)
        return f"{log_color}{message}{reset}"


def ist_time(*args):
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).timetuple()


def log_separator(section_name=None, char="*", line_length=50, spacer_lines=2):
    blank_line = " "
    separator_line = char * line_length

    for _ in range(spacer_lines):
        logger.info(blank_line)

    logger.info(separator_line)
    if section_name:
        logger.info(f"{section_name.center(line_length)}")
        logger.info(separator_line)

    for _ in range(spacer_lines):
        logger.info(blank_line)


def setup_logger():

    os.makedirs(logs_dir, exist_ok=True)

    logs_format = f"{datetime.now().strftime('%d-%m-%Y')}.log"

    log_file = os.path.join(logs_dir, logs_format)

    debug_mode = str(settings.debug).strip().lower() == "true"
    log_level = logging.DEBUG if debug_mode else logging.INFO

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # avoid duplicate handlers (important for FastAPI reload)
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
    )
    file_formatter.converter = ist_time
    file_handler.setFormatter(file_formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
    )
    console_formatter.converter = ist_time
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Silence noisy logs
    for noisy in [
    "azure",
    "google",
    "google.cloud",
    "google.auth",
    "googleapiclient",
    "urllib3",
    "urllib3.connectionpool",
    "grpc",
    "httpx",
    "httpcore",
    "_client",
]:
        logging.getLogger(noisy).setLevel(logging.ERROR)

    return logger


class LogRequest(BaseModel):
    date: str = Field(
        pattern=r"^\d{2}-\d{2}-\d{4}$",
        description="Log date in DD-MM-YYYY format",
    )


def get_logs(request: LogRequest):
    """
    Fetch log file content for a given date (DD-MM-YYYY).
    """

    logger.info("Request received: getLogs | date=%s", request.date)

    try:
        # Validate the date.
        parsed_date = datetime.strptime(request.date, "%d-%m-%Y")
        file_name = f"{parsed_date.strftime('%d-%m-%Y')}.log"

        file_path = os.path.join(logs_dir, file_name)

        if not os.path.isfile(file_path):
            logger.warning("Log file not found | path=%s", file_path)
            raise HTTPException(
                status_code=404,
                detail="Log file not found",
            )

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        logger.info(
            "Log file served | date=%s | size=%d bytes",
            request.date,
            len(content.encode("utf-8")),
        )

        return PlainTextResponse(
            content=content,
            media_type="text/plain",
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date. Use DD-MM-YYYY format.",
        )

    except HTTPException:
        raise

    except OSError:
        logger.exception("Filesystem error while retrieving logs")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve log file",
        )

    except Exception:
        logger.exception("Unexpected error in getLogs")

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

#delete logs 
def delete_all_logs():

    logger.info(
        "Request received: deleteAllLogs"
    )

    try:

        deleted_count = 0

        for file in os.listdir(logs_dir):

            if file.endswith(".log"):

                os.remove(
                    os.path.join(logs_dir, file)
                )

                deleted_count += 1

        logger.info(
            f"Deleted {deleted_count} log files"
        )

        return {
            "status": "success",
            "deleted_files": deleted_count
        }

    except Exception as e:

        logger.exception(
            "Unexpected error in deleteAllLogs"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# Initialize logger
logger = setup_logger()