import os
import unittest
import tempfile
import csv
import json

os.environ["MOCK_EXTRACTION"] = "1"

from constants import (
    THRESHOLD_AMOUNT,
    STATUS_MISSING_W9_CRITICAL,
    STATUS_W9_COLLECTED_GOOD,
    STATUS_ABOVE_THRESHOLD_CRITICAL,
    STATUS_WITHIN_THRESHOLD_GOOD,
)
from contractor_processor import process_contractors


def make_csv(rows):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    writer = csv.DictWriter(
        tmp,
        fieldnames=["contractor_name", "payment_total", "w9_pdf_path"],
    )
    writer.writeheader()
    writer.writerows(rows)
    tmp.close()
    return tmp.name


class TestStatusLogic(unittest.TestCase):
    def test_missing_w9_critical(self):
        csv_path = make_csv([
            {"contractor_name": "Test1", "payment_total": "3000", "w9_pdf_path": ""},
        ])
        records = process_contractors(csv_path)
        self.assertEqual(records[0]["status"], STATUS_MISSING_W9_CRITICAL)
        os.unlink(csv_path)

    def test_within_threshold_good(self):
        csv_path = make_csv([
            {"contractor_name": "Test2", "payment_total": "500", "w9_pdf_path": ""},
        ])
        records = process_contractors(csv_path)
        self.assertEqual(records[0]["status"], STATUS_WITHIN_THRESHOLD_GOOD)
        os.unlink(csv_path)

    def test_above_threshold_critical(self):
        csv_path = make_csv([
            {"contractor_name": "Test3", "payment_total": "2500", "w9_pdf_path": "some.pdf"},
        ])
        records = process_contractors(csv_path)
        self.assertEqual(records[0]["status"], STATUS_ABOVE_THRESHOLD_CRITICAL)
        os.unlink(csv_path)

    def test_w9_collected_good(self):
        csv_path = make_csv([
            {"contractor_name": "Test4", "payment_total": "1000", "w9_pdf_path": "some.pdf"},
        ])
        records = process_contractors(csv_path)
        self.assertEqual(records[0]["status"], STATUS_W9_COLLECTED_GOOD)
        os.unlink(csv_path)

    def test_mock_extraction_output(self):
        csv_path = make_csv([
            {"contractor_name": "Mock", "payment_total": "100", "w9_pdf_path": "dummy.pdf"},
        ])
        records = process_contractors(csv_path)
        self.assertTrue(records[0]["w9_collected"])
        self.assertIsNotNone(records[0]["w9_data"])
        self.assertEqual(records[0]["w9_data"]["contractor_name"], "John Doe")
        os.unlink(csv_path)

    def test_csv_parsing_edge_cases(self):
        csv_path = make_csv([
            {"contractor_name": "Edge", "payment_total": "", "w9_pdf_path": ""},
        ])
        records = process_contractors(csv_path)
        self.assertEqual(records[0]["payment_total"], 0.0)
        self.assertFalse(records[0]["w9_collected"])
        os.unlink(csv_path)


if __name__ == "__main__":
    unittest.main()
