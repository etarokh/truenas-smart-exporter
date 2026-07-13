import json

from discovery import discover_disks
from parser import parse_smart_data


def collect():
    disks = discover_disks("samples/lsblk.json")

    with open("samples/sata-hdd.json", "r", encoding="utf-8") as file:
        smart_data = json.load(file)

    parsed_smart = parse_smart_data(smart_data)

    for disk in disks:
        print("=" * 60)
        print(f"Disk : {disk['name']}")
        print(f"Model: {disk['model']}")
        print(f"Serial: {disk['serial']}")
        print(parsed_smart)


if __name__ == "__main__":
    collect()
