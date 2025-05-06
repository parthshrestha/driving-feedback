import requests
import json
import os
from datetime import datetime

# Replace with your actual deployed API endpoint
RATING_ENDPOINT = "https://tbp98oea2e.execute-api.us-east-1.amazonaws.com/dev/rating"
OUTPUT_PATH = "frontend/rating.json"

def fetch_rating():
    try:
        response = requests.get(RATING_ENDPOINT)
        response.raise_for_status()
        data = response.json()

        with open(OUTPUT_PATH, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[✔] rating.json updated at {datetime.now()} -> {OUTPUT_PATH}")

    except requests.RequestException as e:
        print(f"[✘] Failed to fetch or write rating data: {e}")

if __name__ == "__main__":
    fetch_rating()
