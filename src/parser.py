import json
from typing import Any


def parse_smart_data(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": data.get("model_name"),
        "serial": data.get("serial_number"),
        "smart_passed": data.get("smart_status", {}).get("passed"),
        "temperature_celsius": data.get("temperature", {}).get("current"),
        "power_on_hours": data.get("power_on_time", {}).get("hours"),
    }


if __name__ == "__main__":
    with open("samples/sata-hdd.json", "r", encoding="utf-8") as file:
        smart = json.load(file)

    print(parse_smart_data(smart))
