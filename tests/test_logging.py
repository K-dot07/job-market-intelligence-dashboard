import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/app.log",
    filemode="a"
)

logging.info("Application started.")
logging.warning("No quotes found.")
logging.error("Database connection failed.")