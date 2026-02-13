import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

current_path = Path(__file__).parent
file_path = current_path / ".." / "json" / "rates.json"


def get_actual_rates_data():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    unix_timestamp = data["updated"]
    utc_datetime = datetime.fromtimestamp(unix_timestamp, tz=ZoneInfo("UTC"))
    target_timezone = ZoneInfo("Europe/Moscow")
    msk_datetime = utc_datetime.astimezone(target_timezone)

    rates = {"updated": f"{msk_datetime} (MSK)"} | data["rates"]

    return rates
