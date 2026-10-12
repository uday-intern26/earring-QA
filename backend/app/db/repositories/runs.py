"""Persistence for test definitions, runs, frames, and reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.db.database import allocate_id
from app.models.frame import FrameRecord, FrameResult
from app.models.result import PlacementResultRow, ReportRow, TestRun
from app.models.test import TestDefinition


def list_tests(session: Session) -> list[TestDefinition]:
    return list(session.exec(select(TestDefinition).order_by(TestDefinition.created_at.desc())).all())


def get_test(session: Session, test_id: str) -> TestDefinition | None:
    return session.get(TestDefinition, test_id)


def latest_run(session: Session, test_id: str) -> TestRun | None:
    statement = (
        select(TestRun)
        .where(TestRun.test_id == test_id)
        .order_by(TestRun.created_at.desc())
    )
    return session.exec(statement).first()


def list_runs(session: Session, limit: int = 50) -> list[TestRun]:
    statement = select(TestRun).order_by(TestRun.created_at.desc()).limit(limit)
    return list(session.exec(statement).all())


def get_run(session: Session, run_id: str) -> TestRun | None:
    return session.get(TestRun, run_id)


def create_run(session: Session, test_id: str, steps: list[dict]) -> TestRun:
    run = TestRun(
        id=allocate_id(session, "RUN", TestRun),
        test_id=test_id,
        status="pending",
        stage="pending",
        stage_message="Waiting to start.",
        steps_json=json.dumps(steps),
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def save_run(session: Session, run: TestRun) -> TestRun:
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def add_frame(session: Session, frame: FrameRecord) -> None:
    session.add(frame)


def add_frame_result(session: Session, result: FrameResult) -> None:
    session.add(result)


def add_placement(session: Session, row: PlacementResultRow) -> None:
    session.add(row)


def add_report(session: Session, row: ReportRow) -> None:
    session.add(row)


def frames_for_run(session: Session, run_id: str) -> list[FrameRecord]:
    statement = select(FrameRecord).where(FrameRecord.test_run_id == run_id).order_by(FrameRecord.frame_number)
    return list(session.exec(statement).all())


def results_for_run(session: Session, run_id: str) -> list[FrameResult]:
    statement = select(FrameResult).where(FrameResult.test_run_id == run_id)
    return list(session.exec(statement).all())


def get_frame(session: Session, frame_id: str) -> FrameRecord | None:
    return session.get(FrameRecord, frame_id)


def results_for_frame(session: Session, frame_id: str) -> list[FrameResult]:
    statement = select(FrameResult).where(FrameResult.frame_id == frame_id)
    return list(session.exec(statement).all())
