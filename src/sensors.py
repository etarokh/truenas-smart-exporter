import re
import subprocess


def get_sensors_output() -> str | None:
    try:
        result = subprocess.run(
            ["sensors"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except Exception:
        return None


def get_system_temperature() -> float | None:
    output = get_sensors_output()

    if output is None:
        return None

    match = re.search(
        r"acpitz-acpi-0.*?temp1:\s+\+?([0-9.]+)",
        output,
        re.DOTALL,
    )

    if match:
        return float(match.group(1))

    return None


def get_memory_temperatures() -> list[dict[str, str | float]]:
    output = get_sensors_output()

    if output is None:
        return []

    temperatures: list[dict[str, str | float]] = []

    pattern = re.compile(
        r"^(spd5118-[^\n]+)\n"
        r".*?"
        r"^temp1:\s+\+?([0-9.]+)°C",
        re.MULTILINE | re.DOTALL,
    )

    for sensor_name, temperature in pattern.findall(output):
        temperatures.append(
            {
                "sensor": sensor_name.strip(),
                "temperature_celsius": float(temperature),
            }
        )

    return temperatures
