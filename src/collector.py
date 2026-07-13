from discovery import discover_disks
from parser import parse_smart_file


def collect():
    disks = discover_disks("samples/lsblk.json")

    for disk in disks:
        print("=" * 60)
        print(f"Disk : {disk['name']}")
        print(f"Model: {disk['model']}")
        print(f"Serial: {disk['serial']}")


if __name__ == "__main__":
    collect()
