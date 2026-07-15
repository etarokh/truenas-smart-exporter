from typing import Any


def numeric_value(
    disk: dict[str, Any],
    key: str,
) -> float | None:
    value = disk.get(key)

    if isinstance(value, (int, float)):
        return max(0.0, float(value))

    return None


def calculate_health_score(
    disk: dict[str, Any],
) -> float | None:
    """
    Calculate a heuristic SMART health score from 0 to 100.

    Returns None when no meaningful SMART health information is available.
    """

    smart_passed = disk.get("smart_passed")

    reallocated = numeric_value(
        disk,
        "reallocated_sectors",
    )
    pending = numeric_value(
        disk,
        "pending_sectors",
    )
    uncorrectable = numeric_value(
        disk,
        "offline_uncorrectable",
    )
    crc_errors = numeric_value(
        disk,
        "crc_errors",
    )
    media_errors = numeric_value(
        disk,
        "media_errors",
    )
    critical_warning = numeric_value(
        disk,
        "critical_warning",
    )
    life_remaining = numeric_value(
        disk,
        "life_remaining_percent",
    )

    health_values = (
        smart_passed,
        reallocated,
        pending,
        uncorrectable,
        crc_errors,
        media_errors,
        critical_warning,
        life_remaining,
    )

    if all(value is None for value in health_values):
        return None

    if smart_passed is False:
        return 0.0

    score = 100.0

    if critical_warning is not None and critical_warning > 0:
        score -= 50.0

    if pending is not None and pending > 0:
        score -= min(45.0, 20.0 + pending * 5.0)

    if uncorrectable is not None and uncorrectable > 0:
        score -= min(
            45.0,
            20.0 + uncorrectable * 5.0,
        )

    if media_errors is not None and media_errors > 0:
        score -= min(
            40.0,
            15.0 + media_errors * 2.0,
        )

    if reallocated is not None and reallocated > 0:
        score -= min(
            30.0,
            5.0 + reallocated * 1.5,
        )

    if crc_errors is not None and crc_errors > 0:
        score -= min(
            10.0,
            2.0 + crc_errors * 0.25,
        )

    if life_remaining is not None:
        life_remaining = min(100.0, life_remaining)

        if life_remaining < 10:
            score -= 50.0
        elif life_remaining < 20:
            score -= 35.0
        elif life_remaining < 40:
            score -= 20.0
        elif life_remaining < 60:
            score -= 10.0

    return round(max(0.0, min(100.0, score)), 1)
