import logging

from app.scraper.scraper import scrape_quotes
from app.database.database import insert_quotes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/pipeline.log",
    filemode="a"
)

try:
    logging.info("Pipeline started.")

    quotes = scrape_quotes()
    logging.info("Collected %d quotes.", len(quotes))

    inserted_count = insert_quotes(quotes)
    logging.info("Inserted %d new quotes.", inserted_count)

    logging.info("Pipeline completed successfully.")

except Exception:
    logging.exception("Pipeline failed.")
    raise