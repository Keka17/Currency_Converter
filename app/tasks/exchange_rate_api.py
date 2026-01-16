from celery import shared_task
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
EXTERNAL_API_URL = "https://api.currencyapi.com/v3/latest"


@shared_task(ignore_results=True)
def get_actual_rates():
    """
    Periodic task for retrieving current exchange rates via an API request.
    The request data is saved in a JSON-file.
    Runs every 12 hours by the Celery Beat service.
    """
    headers = {"apikey": API_KEY}

    response = requests.request("GET", EXTERNAL_API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        with open("app/json/rates.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    else:
        print(f"Request failed with status code: {response.status_code}")
