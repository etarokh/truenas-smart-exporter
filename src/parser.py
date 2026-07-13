import json
from typing import Any


def parse_smart_data(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "model": data["model_name"],
        "serial": data["serial_number"],
        "smart_passed": data["smart_status"]["passed"],
        "temperature_celsius": data["temperature"]["current"],
        "power_on_hours": data["power_on_time"]["hours"],
    }


if __name__ == "__main__":
    with open("samples/sata-hdd.json", "r", encoding="utf-8") as file:
        smart = json.load(file)

    print(parse_smart_data(smart))
