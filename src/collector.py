import json

from discovery import discover_disks
from parser import parse_smart_data


def get_smart_json():
    """
    Load SMART data from a sample JSON file.

    This function will later be replaced with a real smartctl call,
    but the rest of the collector will not need to change.
    """
    with open("samples/sata-hdd.json", "r", encoding="utf-8") as file:
        return json.load(file)


def collect():
    disks = discover_disks("samples/lsblk.json")

    smart_data = get_smart_json()

    parsed_smart = parse_smart_data(smart_data)

    for disk in disks:
        print("=" * 60)
        print(f"Disk : {disk['name']}")
        print(f"Model: {disk['model']}")
        print(f"Serial: {disk['serial']}")
        print(parsed_smart)


if __name__ == "__main__":
    collect()
