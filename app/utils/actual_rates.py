import json
from pathlib import Path

current_path = Path(__file__).parent
file_path = current_path / ".." / "json" / "rates.json"


def get_actual_rates_data():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return data["data"]
