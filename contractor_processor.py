import os
import csv
import logging
from constants import (
    THRESHOLD_AMOUNT,
    STATUS_MISSING_W9_CRITICAL,
    STATUS_W9_COLLECTED_GOOD,
    STATUS_ABOVE_THRESHOLD_CRITICAL,
    STATUS_WITHIN_THRESHOLD_GOOD,
)
from w9_extractor import extract_w9_from_pdf

logger = logging.getLogger(__name__)


def parse_payment_total(val: str) -> float:
    if not val or val.strip() == "":
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0


def determine_status(w9_collected: bool, payment_total: float) -> str:
    above = payment_total >= THRESHOLD_AMOUNT
    if w9_collected:
        if above:
            return STATUS_ABOVE_THRESHOLD_CRITICAL
        else:
            return STATUS_W9_COLLECTED_GOOD
    else:
        if above:
            return STATUS_MISSING_W9_CRITICAL
        else:
            return STATUS_WITHIN_THRESHOLD_GOOD


def process_contractors(csv_path: str) -> list:
    records = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contractor_name = row.get("contractor_name", "").strip()
            payment_total = parse_payment_total(row.get("payment_total", ""))
            w9_pdf_path_raw = row.get("w9_pdf_path", "").strip()

            w9_collected = False
            w9_data = None

            if w9_pdf_path_raw:
                try:
                    w9_data = extract_w9_from_pdf(w9_pdf_path_raw)
                    w9_collected = True
                except Exception as e:
                    logger.error(f"Extraction failed for {contractor_name}: {e}")
                    w9_collected = False
                    w9_data = None

            status = determine_status(w9_collected, payment_total)

            records.append({
                "contractor_name": contractor_name,
                "payment_total": payment_total,
                "w9_collected": w9_collected,
                "w9_data": w9_data,
                "status": status,
            })
    return records
