import json
import subprocess
from typing import Any


def run_smartctl(
    device: str,
    sample_file: str | None = None,
) -> dict[str, Any]:
    """
    Retrieve SMART information for a disk.

    Development mode:
        Reads SMART data from a sample JSON file.

    Production mode:
        Executes smartctl and returns the parsed JSON output.

    smartctl uses a bitmask exit status. A non-zero status can indicate
    SMART warnings while still returning valid JSON, so stdout is parsed
    whenever it contains valid JSON.
    """

    if sample_file is not None:
        with open(sample_file, "r", encoding="utf-8") as file:
            return json.load(file)

    result = subprocess.run(
        ["smartctl", "-a", "-j", device],
        capture_output=True,
        text=True,
        check=False,
    )

    if not result.stdout.strip():
        raise RuntimeError(
            f"smartctl returned no JSON for {device}: "
            f"{result.stderr.strip()}"
        )

    try:
        data: dict[str, Any] = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"smartctl returned invalid JSON for {device}: "
            f"{result.stderr.strip()}"
        ) from error

    return data
