import logging
from typing import Any

from discovery import discover_disks
from parser import parse_smart_data
from smartctl import run_smartctl


logger = logging.getLogger(__name__)


def collect() -> list[dict[str, Any]]:
    collected_disks: list[dict[str, Any]] = []

    disks = discover_disks()

    for disk in disks:
        parsed_smart: dict[str, Any] = {
            "model": None,
            "serial": None,
            "smart_passed": None,
            "temperature_celsius": None,
            "power_on_hours": None,
            "life_remaining_percent": None,
            "media_errors": None,
            "unsafe_shutdowns": None,
            "error_log_entries": None,
            "critical_warning": None,
        }

        try:
            smart_data = run_smartctl(
                device=disk["device"],
            )
            parsed_smart = parse_smart_data(smart_data)
        except Exception:
            logger.exception(
                "SMART collection failed for device %s",
                disk["device"],
            )

        collected_disks.append(
            {
                "name": disk["name"],
                "device": disk["device"],
                "model": parsed_smart["model"] or disk["model"] or "unknown",
                "serial": parsed_smart["serial"] or disk["serial"] or "unknown",
                "smart_passed": parsed_smart["smart_passed"],
                "temperature_celsius": parsed_smart["temperature_celsius"],
                "power_on_hours": parsed_smart["power_on_hours"],
                "life_remaining_percent": parsed_smart[
                    "life_remaining_percent"
                ],
                "media_errors": parsed_smart["media_errors"],
                "unsafe_shutdowns": parsed_smart["unsafe_shutdowns"],
                "error_log_entries": parsed_smart["error_log_entries"],
                "critical_warning": parsed_smart["critical_warning"],
            }
        )

    return collected_disks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(collect())
