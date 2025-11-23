import time
import requests

API_BASE = "http://localhost:8000"
API_KEY = "changeme123"   # replace if needed

HEADERS = {
    "X-API-Key": API_KEY
}

TEST_FILE = "3C_testdaten_pdf/230072869L_Splitt.pdf"   # <-- adjust path


def upload_file():
    print("📤 Uploading file...")

    with open(TEST_FILE, "rb") as f:
        files = {"file": f}
        res = requests.post(f"{API_BASE}/upload", files=files, headers=HEADERS)

    res.raise_for_status()
    file_id = res.json()["file_id"]

    print(f"✅ File uploaded: {file_id}")
    return file_id


def trigger_processing(file_id):
    print("⚙️  Triggering processing...")

    payload = {"file_id": file_id}
    res = requests.post(f"{API_BASE}/process", json=payload, headers=HEADERS)

    res.raise_for_status()
    data = res.json()

    job_id = data["job_id"]
    print(f"🧵 Job created: {job_id}")

    return job_id


def poll_job(job_id):
    print("🔄 Polling job status...")

    while True:
        res = requests.get(f"{API_BASE}/job/{job_id}", headers=HEADERS)
        data = res.json()

        status = data["status"]
        print(f"   → Status: {status}")

        if status == "finished":
            print("🎉 Job finished!")
            print("📄 Result:")
            print(data["result"])
            print(type(data["result"]))
            return

        if status == "failed":
            print("❌ Job failed!")
            print(data.get("error"))
            return

        time.sleep(10)


if __name__ == "__main__":
    file_id = upload_file()
    job_id = trigger_processing(file_id)
    poll_job(job_id)