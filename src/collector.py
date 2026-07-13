from discovery import discover_disks
from parser import parse_smart_data
from smartctl import run_smartctl


def collect():
    disks = discover_disks("samples/lsblk.json")

    for disk in disks:
        smart_data = run_smartctl(
            device=disk["device"],
            sample_file="samples/sata-hdd.json",
        )

        parsed_smart = parse_smart_data(smart_data)

        print("=" * 60)
        print(f"Disk : {disk['name']}")
        print(f"Model: {disk['model']}")
        print(f"Serial: {disk['serial']}")
        print(parsed_smart)


if __name__ == "__main__":
    collect()
