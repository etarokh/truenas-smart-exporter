import json
from typing import Any


def run_smartctl(device: str, sample_file: str | None = None) -> dict[str, Any]:
    """
    Retrieve SMART information for a disk.

    Development mode:
        Reads SMART data from a sample JSON file.

    Production mode:
        Will execute smartctl and return the parsed JSON output.
    """

    if sample_file is not None:
        with open(sample_file, "r", encoding="utf-8") as file:
            return json.load(file)

    raise NotImplementedError("Live smartctl mode is not implemented yet.")
