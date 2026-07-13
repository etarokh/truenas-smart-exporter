import json
import subprocess


def discover_disks(
    file_path: str | None = None,
) -> list[dict[str, str]]:
    if file_path is not None:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        result = subprocess.run(
            [
                "lsblk",
                "-J",
                "-o",
                "NAME,TYPE,MODEL,SERIAL",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"lsblk failed: {result.stderr.strip()}"
            )

        data = json.loads(result.stdout)

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
