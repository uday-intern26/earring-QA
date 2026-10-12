from app.services.temporal_validator import max_consecutive_failures, summarize_temporal


def test_pass_rate_and_consecutive_failures():
    statuses = ["PASS", "PASS", "FAIL", "FAIL", "PASS", "WARNING"]
    assert max_consecutive_failures(statuses) == 2
    summary = summarize_temporal(
        statuses,
        minimum_pass_rate=0.95,
        maximum_consecutive_failures=2,
        detection_failures=0,
    )
    assert summary.passed_frames == 3
    assert summary.failed_frames == 2
    assert summary.warning_frames == 1
    assert summary.pass_rate == 0.5
    assert summary.status == "FAIL"
    assert summary.max_consecutive_failures == 2


def test_overall_pass_when_rate_and_streak_are_inside_limits():
    summary = summarize_temporal(
        ["PASS", "PASS", "PASS", "PASS"],
        minimum_pass_rate=0.95,
        maximum_consecutive_failures=2,
        detection_failures=0,
    )
    assert summary.status == "PASS"
    assert summary.pass_rate == 1


def test_critical_detection_failure_forces_fail():
    summary = summarize_temporal(
        ["PASS", "PASS"],
        minimum_pass_rate=0.5,
        maximum_consecutive_failures=2,
        detection_failures=1,
    )
    assert summary.status == "FAIL"
    assert "Critical" in summary.reason
