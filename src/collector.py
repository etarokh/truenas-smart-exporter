from typing import Any

from discovery import discover_disks
from parser import parse_smart_data
from smartctl import run_smartctl


def collect() -> list[dict[str, Any]]:
    collected_disks: list[dict[str, Any]] = []

    disks = discover_disks()

    for disk in disks:
        smart_data = run_smartctl(
            device=disk["device"],
        )

        parsed_smart = parse_smart_data(smart_data)

        collected_disks.append(
            {
                "name": disk["name"],
                "device": disk["device"],
                **parsed_smart,
            }
        )

    return collected_disks


if __name__ == "__main__":
    print(collect())
