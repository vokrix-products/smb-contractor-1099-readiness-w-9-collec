import os
import json
import csv

os.environ["MOCK_EXTRACTION"] = "1"

from contractor_processor import process_contractors
from constants import INPUT_DIR, OUTPUT_DIR, DASHBOARD_FILE

def main():
    os.makedirs("data/input", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    csv_path = "data/input/sample.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["contractor_name", "payment_total", "w9_pdf_path"])
        writer.writerow(["Alice", "2500", "alice_w9.pdf"])
        writer.writerow(["Bob", "1500", ""])
        writer.writerow(["Charlie", "3000", "bob_w9.pdf"])
        writer.writerow(["Dave", "500", "charlie_w9.pdf"])

    records = process_contractors(csv_path)

    with open("data/output/dashboard.json", "w") as out:
        json.dump(records, out, indent=2)

    print("Dashboard ready on http://localhost:8000")

if __name__ == "__main__":
    main()
