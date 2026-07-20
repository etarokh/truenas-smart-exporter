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



def collect_pool_list() -> dict[str, dict[str, Any]]:
    try:
        result = subprocess.run(
            ["zpool", "list", "-Hp"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {}

    pools: dict[str, dict[str, Any]] = {}

    for line in result.stdout.splitlines():
        columns = line.split()

        if len(columns) < 10:
            continue

        name = columns[0]

        if name == "boot-pool":
            continue

        try:
            pools[name] = {
                "size_bytes": int(columns[1]),
                "allocated_bytes": int(columns[2]),
                "free_bytes": int(columns[3]),
                "fragmentation_percent": float(columns[6]),
                "capacity_percent": float(columns[7]),
                "dedup_ratio": float(columns[8]),
                "health": columns[9],
            }
        except ValueError:
            continue

    return pools


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

    pool_list = collect_pool_list()

    for name, pool in pools_data.items():
        pool_info = pool_list.get(name, {})
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
                "size_bytes": pool_info.get("size_bytes", 0),
		"allocated_bytes": pool_info.get("allocated_bytes", 0),
		"free_bytes": pool_info.get("free_bytes", 0),
		"capacity_percent": pool_info.get("capacity_percent", 0.0),
		"fragmentation_percent": pool_info.get("fragmentation_percent", 0.0),
		"health": pool_info.get("health", "UNKNOWN"),
		"progress_percent": progress,
            }
        )

    return pools
