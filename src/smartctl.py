import json
import subprocess
from typing import Any


def run_smartctl(device: str, sample_file: str | None = None) -> dict[str, Any]:
    """
    Retrieve SMART information for a disk.

    Development mode:
        Reads SMART data from a sample JSON file.

    Production mode:
        Executes smartctl and returns the parsed JSON output.
    """

    if sample_file is not None:
        with open(sample_file, "r", encoding="utf-8") as file:
            return json.load(file)

    result = subprocess.run(
        ["smartctl", "-a", "-j", device],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"smartctl failed for {device}: {result.stderr.strip()}"
        )

    return json.loads(result.stdout)
