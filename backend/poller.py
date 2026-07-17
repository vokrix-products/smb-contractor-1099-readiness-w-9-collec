import os
import time
import requests
import json

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PRODUCT_ID = os.environ["PRODUCT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}


def poll_jobs():
    params = {
        "status": "eq.pending",
        "job_type": "eq.process_upload",
        "product_id": f"eq.{PRODUCT_ID}"
    }
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/jobs", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


def download_file(bucket, file_path):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.content


def upload_result(bucket, file_path, data):
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    resp = requests.post(url, headers=HEADERS, files={"file": data})
    resp.raise_for_status()
    return resp.json()


def process_file(content):
    # Dummy processing logic – replace with actual extraction
    # This just returns a list of records as an example
    lines = content.decode().splitlines()
    records = []
    for line in lines:
        if line.strip():
            records.append({
                "title": f"Contractor record from {line[:30]}...",
                "status": "missing_w9:critical",  # default
                "details": {"raw": line},
                "source_file_path": "uploaded_file.csv"
            })
    return records


def insert_records(records, customer_id, source_file_path):
    payload = [{
        "product_id": PRODUCT_ID,
        "customer_id": customer_id,
        "title": rec["title"],
        "status": rec["status"],
        "details": rec["details"],
        "source_file_path": source_file_path,
        "due_date": None
    } for rec in records]
    url = f"{SUPABASE_URL}/rest/v1/records"
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()


def update_job(job_id, status, output_file_path=None, result_summary=None):
    patch = {"status": status}
    if output_file_path:
        patch["output_file_path"] = output_file_path
    if result_summary:
        patch["result_summary"] = result_summary
    if status in ("completed", "failed"):
        patch["completed_at"] = "now()"
    url = f"{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}"
    resp = requests.patch(url, headers=HEADERS, json=patch)
    resp.raise_for_status()


def main():
    while True:
        try:
            jobs = poll_jobs()
            for job in jobs:
                job_id = job["id"]
                customer_id = job.get("customer_id", "unknown")
                file_path = job.get("input_file_path")
                if not file_path:
                    update_job(job_id, "failed", result_summary="No input file path")
                    continue

                try:
                    content = download_file("uploads", file_path)
                except Exception as e:
                    update_job(job_id, "failed", result_summary=f"Download error: {str(e)}")
                    continue

                try:
                    records = process_file(content)
                    insert_records(records, customer_id, file_path)
                    # Upload result placeholder
                    result_path = f"results/{job_id}.json"
                    upload_result("results", result_path, json.dumps(records).encode())
                    update_job(job_id, "completed", output_file_path=result_path, result_summary=f"Inserted {len(records)} records")
                except Exception as e:
                    update_job(job_id, "failed", result_summary=f"Processing error: {str(e)}")

        except Exception as e:
            print(f"Polling error: {e}")

        time.sleep(60)


if __name__ == "__main__":
    main()
