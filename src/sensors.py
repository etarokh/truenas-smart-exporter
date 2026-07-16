import re
import subprocess


def get_system_temperature() -> float | None:
    try:
        result = subprocess.run(
            ["sensors"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout

        match = re.search(
            r"acpitz-acpi-0.*?temp1:\s+\+?([0-9.]+)",
            output,
            re.DOTALL,
        )

        if match:
            return float(match.group(1))

    except Exception:
        return None

    return None
