
import logging

from app.ingestion.job_ingestion import main as ingest_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/pipeline.log",
    filemode="a"
)

if __name__ == "__main__":
    try:
        logging.info("Job pipeline started.")

        ingest_jobs()

        logging.info("Job pipeline completed successfully.")

    except Exception:
        logging.exception("Job pipeline failed.")
        raise
