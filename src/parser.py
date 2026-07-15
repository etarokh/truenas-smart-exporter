import json
from typing import Any


DIRECT_REMAINING_ATTRIBUTE_NAMES = {
    "Percent_Lifetime_Remain",
    "SSD_Life_Left",
    "Media_Wearout_Indicator",
}

USED_ATTRIBUTE_NAMES = {
    "Percent_Lifetime_Used",
}


def clamp_percent(value: int | float) -> float:
    return max(0, min(100, float(value)))


def get_nvme_health_log(data: dict[str, Any]) -> dict[str, Any]:
    health_log = data.get("nvme_smart_health_information_log", {})

    if isinstance(health_log, dict):
        return health_log

    return {}


def get_nvme_life_remaining(data: dict[str, Any]) -> float | None:
    percentage_used = get_nvme_health_log(data).get("percentage_used")

    if not isinstance(percentage_used, (int, float)):
        return None

    return clamp_percent(100 - percentage_used)


def get_nvme_media_errors(data: dict[str, Any]) -> int | float | None:
    media_errors = get_nvme_health_log(data).get("media_errors")

    if not isinstance(media_errors, (int, float)):
        return None

    return max(0, media_errors)


def get_nvme_critical_warning(data: dict[str, Any]) -> int | None:
    critical_warning = get_nvme_health_log(data).get("critical_warning")

    if not isinstance(critical_warning, int):
        return None

    return max(0, critical_warning)


def get_sata_life_remaining(data: dict[str, Any]) -> float | None:
    model = data.get("model_name") or ""

    attributes = data.get(
        "ata_smart_attributes",
        {},
    ).get("table", [])

    for attribute in attributes:
        name = attribute.get("name")
        value = attribute.get("value")

        if not isinstance(value, (int, float)):
            continue

        if name in DIRECT_REMAINING_ATTRIBUTE_NAMES:
            return clamp_percent(value)

        if name in USED_ATTRIBUTE_NAMES:
            return clamp_percent(100 - value)

        if (
            model.startswith("Fanxiang S101")
            and name == "Wear_Leveling_Count"
        ):
            return clamp_percent(value)

    return None


def parse_smart_data(data: dict[str, Any]) -> dict[str, Any]:
    life_remaining_percent = get_nvme_life_remaining(data)

    if life_remaining_percent is None:
        life_remaining_percent = get_sata_life_remaining(data)

    return {
        "model": data.get("model_name"),
        "serial": data.get("serial_number"),
        "smart_passed": data.get("smart_status", {}).get("passed"),
        "temperature_celsius": data.get("temperature", {}).get("current"),
        "power_on_hours": data.get("power_on_time", {}).get("hours"),
        "life_remaining_percent": life_remaining_percent,
        "media_errors": get_nvme_media_errors(data),
        "critical_warning": get_nvme_critical_warning(data),
    }


if __name__ == "__main__":
    with open("samples/sata-hdd.json", "r", encoding="utf-8") as file:
        smart = json.load(file)

    print(parse_smart_data(smart))
