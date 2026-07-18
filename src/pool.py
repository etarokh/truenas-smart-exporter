import json
import subprocess
from datetime import datetime
from typing import Any


UNITS = {
    "B": 1,
    "K": 1024,
    "M": 1024**2,
    "G": 1024**3,
    "T": 1024**4,
    "P": 1024**5,
}


def parse_size(value: str | None) -> int:
    if not value or value in ("-", "0B"):
        return 0

    value = value.strip()

    try:
        if value.endswith("B") and len(value) > 1:
            unit = value[-2]
            number = float(value[:-2])
        else:
            unit = value[-1]
            number = float(value[:-1])
    except (TypeError, ValueError):
        return 0

    return int(number * UNITS.get(unit.upper(), 1))


def parse_time(value: str | None) -> int:
    if not value or value == "-":
        return 0

    try:
        return int(
            datetime.strptime(
                value,
                "%a %b %d %H:%M:%S %Z %Y",
            ).timestamp()
        )
    except ValueError:
        return 0


def collect_pools() -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["zpool", "status", "-j"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    pools_data = data.get("pools", {})

    if not isinstance(pools_data, dict):
        return []

    pools = []

    for name, pool in pools_data.items():
        if name == "boot-pool":
            continue

        scan = pool.get("scan_stats") or {}

        examined = parse_size(scan.get("examined"))
        total = parse_size(scan.get("to_examine"))

        progress = 0.0

        if total:
            progress = min(examined / total * 100, 100.0)

        try:
            scan_errors = int(scan.get("errors") or 0)
        except (TypeError, ValueError):
            scan_errors = 0

        pools.append(
            {
                "name": name,
                "state": pool.get("state"),
                "scan_function": scan.get("function") or "NONE",
                "scan_state": scan.get("state") or "NONE",
                "scan_errors": scan_errors,
                "start_timestamp": parse_time(
                    scan.get("start_time")
                ),
                "end_timestamp": parse_time(
                    scan.get("end_time")
                ),
                "examined_bytes": examined,
                "total_bytes": total,
                "issued_bytes": parse_size(
                    scan.get("issued")
                ),
                "progress_percent": progress,
            }
        )

    return pools
