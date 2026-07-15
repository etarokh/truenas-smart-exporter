import logging

from flask import Flask, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Gauge,
    generate_latest,
)

from collector import collect


app = Flask(__name__)
logger = logging.getLogger(__name__)


smart_status = Gauge(
    "truenas_smart_status",
    "SMART health status: 1 = passed, 0 = failed",
    ["disk", "device", "model", "serial"],
)

disk_temperature = Gauge(
    "truenas_smart_temperature_celsius",
    "Current disk temperature in Celsius",
    ["disk", "device", "model", "serial"],
)

disk_power_on_hours = Gauge(
    "truenas_smart_power_on_hours",
    "Total disk power-on hours",
    ["disk", "device", "model", "serial"],
)

disk_life_remaining = Gauge(
    "truenas_disk_life_remaining_percent",
    "Estimated remaining SSD or NVMe life in percent",
    ["disk", "device", "model", "serial"],
)

nvme_media_errors = Gauge(
    "truenas_nvme_media_errors_total",
    "Total NVMe media and data integrity errors",
    ["disk", "device", "model", "serial"],
)

nvme_unsafe_shutdowns = Gauge(
    "truenas_nvme_unsafe_shutdowns_total",
    "Total NVMe unsafe shutdowns",
    ["disk", "device", "model", "serial"],
)

nvme_error_log_entries = Gauge(
    "truenas_nvme_error_log_entries_total",
    "Total NVMe error information log entries",
    ["disk", "device", "model", "serial"],
)

nvme_critical_warning = Gauge(
    "truenas_nvme_critical_warning",
    "NVMe critical warning bitmask; 0 means no warning",
    ["disk", "device", "model", "serial"],
)

ata_reallocated_sectors = Gauge(
    "truenas_ata_reallocated_sectors_total",
    "Total number of reallocated sectors reported by ATA SMART",
    ["disk", "device", "model", "serial"],
)

ata_pending_sectors = Gauge(
    "truenas_ata_pending_sectors_total",
    "Total number of current pending sectors reported by ATA SMART",
    ["disk", "device", "model", "serial"],
)

exporter_up = Gauge(
    "truenas_smart_exporter_up",
    "Whether the SMART exporter collection succeeded",
)


def update_metrics() -> None:
    smart_status.clear()
    disk_temperature.clear()
    disk_power_on_hours.clear()
    disk_life_remaining.clear()
    nvme_media_errors.clear()
    nvme_unsafe_shutdowns.clear()
    nvme_error_log_entries.clear()
    nvme_critical_warning.clear()
    ata_reallocated_sectors.clear()
    ata_pending_sectors.clear()

    disks = collect()

    for disk in disks:
        labels = {
            "disk": disk["name"],
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


@app.get("/metrics")
def metrics() -> Response:
    try:
        update_metrics()
        exporter_up.set(1)
    except Exception:
        exporter_up.set(0)
        logger.exception("SMART exporter collection failed")

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST,
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=9111,
    )
