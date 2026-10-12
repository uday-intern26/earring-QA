"""Temporal stability across selected frames. One frame never decides the video."""

from __future__ import annotations

from dataclasses import dataclass


SEVERITY = {"PASS": 0, "WARNING": 1, "FAIL": 2, "NOT_RUN": 3}


@dataclass
class TemporalSummary:
    status: str
    total_frames: int
    valid_frames: int
    passed_frames: int
    warning_frames: int
    failed_frames: int
    pass_rate: float
    max_consecutive_failures: int
    critical_detection_failures: int
    reason: str


def max_consecutive_failures(statuses: list[str]) -> int:
    longest = 0
    current = 0
    for status in statuses:
        if status == "FAIL":
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def summarize_temporal(
    statuses: list[str],
    *,
    minimum_pass_rate: float,
    maximum_consecutive_failures: int,
    detection_failures: int,
) -> TemporalSummary:
    total = len(statuses)
    passed = sum(1 for status in statuses if status == "PASS")
    warnings = sum(1 for status in statuses if status == "WARNING")
    failed = sum(1 for status in statuses if status == "FAIL")
    valid = passed + warnings + failed
    rate = (passed / total) if total else 0.0
    consecutive = max_consecutive_failures(statuses)
    reasons: list[str] = []
    if total == 0:
        reasons.append("No selected frames were available for temporal validation.")
    if rate < minimum_pass_rate:
        reasons.append(
            f"Pass rate {rate:.1%} is below the configured minimum {minimum_pass_rate:.1%}."
        )
    if consecutive > maximum_consecutive_failures:
        reasons.append(
            f"Maximum consecutive failures {consecutive} exceeds the limit {maximum_consecutive_failures}."
        )
    if detection_failures:
        reasons.append(f"Critical detection failures: {detection_failures}.")
    if reasons:
        status = "FAIL"
        reason = " ".join(reasons)
    elif warnings:
        status = "WARNING"
        reason = "Placement stayed inside the outer zone, with one or more warning frames."
    else:
        status = "PASS"
        reason = "Pass rate and consecutive failures are within configuration."
    return TemporalSummary(
        status=status,
        total_frames=total,
        valid_frames=valid,
        passed_frames=passed,
        warning_frames=warnings,
        failed_frames=failed,
        pass_rate=rate,
        max_consecutive_failures=consecutive,
        critical_detection_failures=detection_failures,
        reason=reason,
    )


def combine_statuses(statuses: list[str]) -> str:
    if not statuses:
        return "NOT_RUN"
    if any(status == "FAIL" for status in statuses):
        return "FAIL"
    if any(status == "WARNING" for status in statuses):
        return "WARNING"
    if all(status == "NOT_RUN" for status in statuses):
        return "NOT_RUN"
    return "PASS"
