import json


def discover_disks(file_path: str) -> list[dict[str, str]]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    disks = []

    for device in data["blockdevices"]:
        if device.get("type") != "disk":
            continue

        if not device.get("serial"):
            continue

        disks.append(
            {
                "name": device["name"],
                "device": f"/dev/{device['name']}",
                "model": device["model"],
                "serial": device["serial"],
            }
        )

    return disks


if __name__ == "__main__":
    result = discover_disks("samples/lsblk.json")

    for disk in result:
        print(disk)
