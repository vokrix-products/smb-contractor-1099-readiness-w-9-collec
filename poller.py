import os
import time
import json
import logging
from constants import INPUT_DIR, OUTPUT_DIR, DASHBOARD_FILE
from contractor_processor import process_contractors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_dirs():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def poll():
    ensure_dirs()
    processed_files = set()
    logger.info("Poller started. Watching %s", INPUT_DIR)
    while True:
        try:
            files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]
            for fname in files:
                if fname in processed_files:
                    continue
                csv_path = os.path.join(INPUT_DIR, fname)
                logger.info("Processing %s", csv_path)
                records = process_contractors(csv_path)
                with open(DASHBOARD_FILE, "w") as out:
                    json.dump(records, out, indent=2)
                processed_files.add(fname)
                logger.info("Dashboard updated at %s", DASHBOARD_FILE)
        except Exception as e:
            logger.error("Poll cycle error: %s", e)
        time.sleep(60)


if __name__ == "__main__":
    poll()
