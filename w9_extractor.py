import os
import base64
import json
import requests

SYSTEM_PROMPT = (
    "Extract the contractor\u2019s W-9 data. The primary entity is the contractor name. "
    "Extract the contractor name as the title field."
)


def extract_w9_from_pdf(pdf_path: str) -> dict:
    mock_mode = os.environ.get("MOCK_EXTRACTION", "0") == "1"
    if mock_mode:
        return {"contractor_name": "John Doe", "tin": "123-45-6789"}

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    with open(pdf_path, "rb") as f:
        pdf_content = f.read()
    pdf_b64 = base64.b64encode(pdf_content).decode("utf-8")

    payload = {
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract W-9 information from the following PDF (base64):\n{pdf_b64}"},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    try:
        extracted = json.loads(content)
    except json.JSONDecodeError:
        extracted = {"contractor_name": "", "tin": ""}

    return extracted
