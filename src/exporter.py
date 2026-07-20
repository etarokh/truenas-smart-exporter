import json
import logging
import os
from pathlib import Path

from flask import Flask, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Gauge,
    generate_latest,
)

from collector import collect
from pool import collect_pools
from sensors import get_memory_temperatures, get_system_temperature


app = Flask(__name__)
logger = logging.getLogger(__name__)


CONFIG_DIR = Path(
    os.environ.get("TRUENAS_SMART_CONFIG_DIR", "/config")
)


def load_device_bay_names() -> dict[str, str]:
    bay_map_path = CONFIG_DIR / "bay-map.json"
    device_paths_path = CONFIG_DIR / "device-paths.json"

    try:
        with bay_map_path.open("r", encoding="utf-8") as file:
            path_to_bay = json.load(file)

        with device_paths_path.open("r", encoding="utf-8") as file:
            path_to_device = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        logger.warning(
            "Unable to load physical bay mapping: %s",
            error,
        )
        return {}

    device_to_bay = {}

    for physical_path, bay_name in path_to_bay.items():
        device_name = path_to_device.get(physical_path)

        if device_name:
            device_to_bay[device_name] = bay_name

    return device_to_bay


smart_status = Gauge(
    "truenas_smart_status",
    "SMART health status: 1 = passed, 0 = failed",
    ["disk", "bay", "device", "model", "serial"],
)

disk_temperature = Gauge(
    "truenas_smart_temperature_celsius",
    "Current disk temperature in Celsius",
    ["disk", "bay", "device", "model", "serial"],
)

disk_power_on_hours = Gauge(
    "truenas_smart_power_on_hours",
    "Total disk power-on hours",
    ["disk", "bay", "device", "model", "serial"],
)

disk_life_remaining = Gauge(
    "truenas_disk_life_remaining_percent",
    "Estimated remaining SSD or NVMe life in percent",
    ["disk", "bay", "device", "model", "serial"],
)

disk_health_score = Gauge(
    "truenas_disk_health_score",
    "Heuristic disk health score from 0 to 100",
    ["disk", "bay", "device", "model", "serial"],
)

nvme_media_errors = Gauge(
    "truenas_nvme_media_errors_total",
    "Total NVMe media and data integrity errors",
    ["disk", "bay", "device", "model", "serial"],
)

nvme_unsafe_shutdowns = Gauge(
    "truenas_nvme_unsafe_shutdowns_total",
    "Total NVMe unsafe shutdowns",
    ["disk", "bay", "device", "model", "serial"],
)

nvme_error_log_entries = Gauge(
    "truenas_nvme_error_log_entries_total",
    "Total NVMe error information log entries",
    ["disk", "bay", "device", "model", "serial"],
)

nvme_critical_warning = Gauge(
    "truenas_nvme_critical_warning",
    "NVMe critical warning bitmask; 0 means no warning",
    ["disk", "bay", "device", "model", "serial"],
)

ata_reallocated_sectors = Gauge(
    "truenas_ata_reallocated_sectors_total",
    "Total number of reallocated sectors reported by ATA SMART",
    ["disk", "bay", "device", "model", "serial"],
)

ata_pending_sectors = Gauge(
    "truenas_ata_pending_sectors_total",
    "Total number of current pending sectors reported by ATA SMART",
    ["disk", "bay", "device", "model", "serial"],
)

ata_offline_uncorrectable = Gauge(
    "truenas_ata_offline_uncorrectable_total",
    "Total number of offline uncorrectable sectors reported by ATA SMART",
    ["disk", "bay", "device", "model", "serial"],
)

ata_crc_errors = Gauge(
    "truenas_ata_crc_errors_total",
    "Total number of UDMA CRC errors reported by ATA SMART",
    ["disk", "bay", "device", "model", "serial"],
)

exporter_up = Gauge(
    "truenas_smart_exporter_up",
    "Whether the exporter collection succeeded",
)

system_temperature = Gauge(
    "truenas_system_temperature_celsius",
    "System temperature reported by the ACPI thermal sensor",
)

memory_temperature = Gauge(
    "truenas_memory_temperature_celsius",
    "Current DDR5 memory module temperature in Celsius",
    ["dimm", "sensor"],
)

pool_scan_state = Gauge(
    "truenas_pool_scan_state",
    "Pool scan state: 0 none, 1 scanning, 2 finished, 3 canceled, -1 unknown",
    ["pool"],
)

pool_scan_function = Gauge(
    "truenas_pool_scan_function",
    "Pool scan function: 0 none, 1 scrub, 2 resilver, -1 unknown",
    ["pool"],
)

pool_scan_progress = Gauge(
    "truenas_pool_scan_progress_percent",
    "Pool scan progress percentage",
    ["pool"],
)

pool_scan_errors = Gauge(
    "truenas_pool_scan_errors",
    "Number of errors reported by the pool scan",
    ["pool"],
)

pool_scan_examined_bytes = Gauge(
    "truenas_pool_scan_examined_bytes",
    "Bytes examined during the pool scan",
    ["pool"],
)

pool_scan_total_bytes = Gauge(
    "truenas_pool_scan_total_bytes",
    "Total bytes to examine during the pool scan",
    ["pool"],
)

pool_scan_issued_bytes = Gauge(
    "truenas_pool_scan_issued_bytes",
    "Bytes issued during the pool scan",
    ["pool"],
)

pool_scan_start_timestamp = Gauge(
    "truenas_pool_scan_start_timestamp",
    "Pool scan start time as a Unix timestamp",
    ["pool"],
)

pool_scan_end_timestamp = Gauge(
    "truenas_pool_scan_end_timestamp",
    "Pool scan end time as a Unix timestamp",
    ["pool"],
)

pool_size_bytes = Gauge(
    "truenas_pool_size_bytes",
    "Total pool size in bytes",
    ["pool"],
)

pool_allocated_bytes = Gauge(
    "truenas_pool_allocated_bytes",
    "Allocated bytes in the pool",
    ["pool"],
)

pool_free_bytes = Gauge(
    "truenas_pool_free_bytes",
    "Free bytes in the pool",
    ["pool"],
)

pool_capacity_percent = Gauge(
    "truenas_pool_capacity_percent",
    "Pool capacity percentage",
    ["pool"],
)

pool_fragmentation_percent = Gauge(
    "truenas_pool_fragmentation_percent",
    "Pool fragmentation percentage",
    ["pool"],
)

pool_health = Gauge(
    "truenas_pool_health",
    "Pool health: 1=ONLINE, 0=other",
    ["pool"],
)


def update_metrics() -> None:
    smart_status.clear()
    disk_temperature.clear()
    disk_power_on_hours.clear()
    disk_life_remaining.clear()
    disk_health_score.clear()
    nvme_media_errors.clear()
    nvme_unsafe_shutdowns.clear()
    nvme_error_log_entries.clear()
    nvme_critical_warning.clear()
    ata_reallocated_sectors.clear()
    ata_pending_sectors.clear()
    ata_offline_uncorrectable.clear()
    ata_crc_errors.clear()

    pool_scan_state.clear()
    pool_scan_function.clear()
    pool_scan_progress.clear()
    pool_scan_errors.clear()
    pool_scan_examined_bytes.clear()
    pool_scan_total_bytes.clear()
    pool_scan_issued_bytes.clear()
    pool_scan_start_timestamp.clear()
    pool_scan_end_timestamp.clear()

    disks = collect()
    device_bay_names = load_device_bay_names()
    temperature = get_system_temperature()
    memory_temperatures = get_memory_temperatures()

    if temperature is not None:
        system_temperature.set(temperature)

    memory_temperature.clear()

    for index, memory_sensor in enumerate(memory_temperatures, start=1):
        memory_temperature.labels(
            dimm=str(index),
            sensor=str(memory_sensor["sensor"]),
        ).set(float(memory_sensor["temperature_celsius"]))

    for disk in disks:
        labels = {
            "disk": disk["name"],
            "bay": device_bay_names.get(
                disk["name"],
                disk["name"].upper(),
            ),
            "device": disk["device"],
            "model": disk["model"],
            "serial": disk["serial"],
        }

        if disk["smart_passed"] is not None:
            smart_status.labels(**labels).set(
                1 if disk["smart_passed"] else 0
            )

        if disk["temperature_celsius"] is not None:
            disk_temperature.labels(**labels).set(
                disk["temperature_celsius"]
            )

        if disk["power_on_hours"] is not None:
            disk_power_on_hours.labels(**labels).set(
                disk["power_on_hours"]
            )

        if disk["life_remaining_percent"] is not None:
            disk_life_remaining.labels(**labels).set(
                disk["life_remaining_percent"]
            )

        if disk["health_score"] is not None:
            disk_health_score.labels(**labels).set(
                disk["health_score"]
            )

        if disk["media_errors"] is not None:
            nvme_media_errors.labels(**labels).set(
                disk["media_errors"]
            )

        if disk["unsafe_shutdowns"] is not None:
            nvme_unsafe_shutdowns.labels(**labels).set(
                disk["unsafe_shutdowns"]
            )

        if disk["error_log_entries"] is not None:
            nvme_error_log_entries.labels(**labels).set(
                disk["error_log_entries"]
            )

        if disk["critical_warning"] is not None:
            nvme_critical_warning.labels(**labels).set(
                disk["critical_warning"]
            )

        if disk["reallocated_sectors"] is not None:
            ata_reallocated_sectors.labels(**labels).set(
                disk["reallocated_sectors"]
            )

        if disk["pending_sectors"] is not None:
            ata_pending_sectors.labels(**labels).set(
                disk["pending_sectors"]
            )

        if disk["offline_uncorrectable"] is not None:
            ata_offline_uncorrectable.labels(**labels).set(
                disk["offline_uncorrectable"]
            )

        if disk["crc_errors"] is not None:
            ata_crc_errors.labels(**labels).set(
                disk["crc_errors"]
            )

    state_map = {
        "NONE": 0,
        "SCANNING": 1,
        "FINISHED": 2,
        "CANCELED": 3,
        "CANCELLED": 3,
    }

    function_map = {
        "NONE": 0,
        "SCRUB": 1,
        "RESILVER": 2,
    }

    for pool in collect_pools():
        pool_name = pool["name"]
        scan_state = str(pool["scan_state"]).upper()
        scan_function = str(pool["scan_function"]).upper()

        pool_scan_state.labels(pool=pool_name).set(
            state_map.get(scan_state, -1)
        )

        pool_scan_function.labels(pool=pool_name).set(
            function_map.get(scan_function, -1)
        )

        pool_scan_progress.labels(pool=pool_name).set(
            pool["progress_percent"]
        )

        pool_scan_errors.labels(pool=pool_name).set(
            pool["scan_errors"]
        )

        pool_scan_examined_bytes.labels(pool=pool_name).set(
            pool["examined_bytes"]
        )

        pool_scan_total_bytes.labels(pool=pool_name).set(
            pool["total_bytes"]
        )

        pool_scan_issued_bytes.labels(pool=pool_name).set(
            pool["issued_bytes"]
        )

        pool_scan_start_timestamp.labels(pool=pool_name).set(
            pool["start_timestamp"]
        )

        pool_scan_end_timestamp.labels(pool=pool_name).set(
            pool["end_timestamp"]
        )

        pool_size_bytes.labels(pool=pool_name).set(
            pool["size_bytes"]
        )

        pool_allocated_bytes.labels(pool=pool_name).set(
            pool["allocated_bytes"]
        )

        pool_free_bytes.labels(pool=pool_name).set(
            pool["free_bytes"]
        )

        pool_capacity_percent.labels(pool=pool_name).set(
            pool["capacity_percent"]
        )

        pool_fragmentation_percent.labels(pool=pool_name).set(
            pool["fragmentation_percent"]
        )

        pool_health.labels(pool=pool_name).set(
            1 if pool["health"] == "ONLINE" else 0
        )


@app.get("/metrics")
def metrics() -> Response:
    try:
        update_metrics()
        exporter_up.set(1)
    except Exception:
        exporter_up.set(0)
        logger.exception("Exporter collection failed")

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=9111,
    )
