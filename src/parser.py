import json
from typing import Any


def parse_smart_file(file_path: str) -> dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        "model": data["model_name"],
        "serial": data["serial_number"],
        "smart_passed": data["smart_status"]["passed"],
        "temperature_celsius": data["temperature"]["current"],
        "power_on_hours": data["power_on_time"]["hours"],
    }


if __name__ == "__main__":
    result = parse_smart_file("samples/sata-hdd.json")
    print(result)
