from celery import shared_task
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
from app.core.config import get_settings

settings = get_settings()

API_KEY = settings.API_KEY
EXTERNAL_API_URL = "https://currencyapi.net/api/v1/rates"


@shared_task(ignore_results=True)
def get_actual_rates():
    """
    Periodic task for retrieving current exchange rates via an API request.
    The request data is saved in a JSON-file.
    Runs every 3 hours by the Celery Beat service.
    """
    params = {"key": API_KEY, "base": "USD", "output": "JSON"}

    response = requests.get(EXTERNAL_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        with open("app/json/rates.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    else:
        print(f"Request failed with status code: {response.status_code}")
