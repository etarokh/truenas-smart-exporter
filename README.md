# TrueNAS SMART Exporter

A lightweight, read-only Prometheus exporter for collecting SMART information from physical disks on **TrueNAS SCALE**.

The exporter is designed specifically for TrueNAS SCALE and exposes SMART metrics in Prometheus format for Grafana dashboards and alerting.

---

## Features

- Read-only SMART data collection
- Supports SATA HDDs
- Supports SATA SSDs
- Supports NVMe SSDs
- Prometheus compatible metrics
- Docker image published on GitHub Container Registry (GHCR)
- Designed for TrueNAS SCALE
- Lightweight and container friendly

---

## Currently Exported Metrics

- SMART Status
- Disk Temperature
- Power-On Hours

---

## Installation

Pull the latest Docker image:

```bash
docker pull ghcr.io/etarokh/truenas-smart-exporter:latest
```

Or pull a specific release:

```bash
docker pull ghcr.io/etarokh/truenas-smart-exporter:v1.0.1
```

---

## Example Metrics

```text
# HELP truenas_smart_status SMART health status
# TYPE truenas_smart_status gauge
truenas_smart_status{disk="sda",model="WDC WD40EFRX-68N32N0"} 1
truenas_smart_status{disk="nvme0n1",model="Lexar SSD THOR PRO 1TB"} 1

# HELP truenas_smart_temperature_celsius Current disk temperature
# TYPE truenas_smart_temperature_celsius gauge
truenas_smart_temperature_celsius{disk="sda"} 31
truenas_smart_temperature_celsius{disk="nvme0n1"} 34

# HELP truenas_smart_power_on_hours Total disk power-on hours
# TYPE truenas_smart_power_on_hours gauge
truenas_smart_power_on_hours{disk="sda"} 45969
truenas_smart_power_on_hours{disk="nvme0n1"} 38
```

---

## Tested Environment

- TrueNAS SCALE 25.10.3
- SATA HDD
- SATA SSD
- NVMe SSD
- Docker / Custom App
- Prometheus

---

## Docker Image

```
ghcr.io/etarokh/truenas-smart-exporter
```

---

## Roadmap

### v1.1.0

- Additional SMART attributes
- Reallocated Sectors
- Pending Sectors
- UDMA CRC Errors
- Power Cycle Count

### v1.2.0

- SMART Self-Test metrics
- SMART Error Log metrics

### v2.0.0

- Complete Grafana dashboard
- Prometheus alert rules
- Documentation improvements

---

## License

This project is currently under development.

License will be added before the first production release.
