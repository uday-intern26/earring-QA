from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.application import utcnow


class TestRun(SQLModel, table=True):
    __tablename__ = "test_runs"

    id: str = Field(primary_key=True)
    test_id: str = Field(index=True, foreign_key="tests.id")
    status: str = "pending"
    progress: float = 0
    stage: str = "pending"
    stage_message: str = ""
    steps_json: str | None = None
    overall_status: str | None = None
    error: str | None = None
    reason: str | None = None
    recommended_action: str | None = None
    statistics_json: str | None = None
    layers_json: str | None = None
    report_json: str | None = None
    capture_path: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)


class PlacementResultRow(SQLModel, table=True):
    __tablename__ = "placement_results"

    id: str = Field(primary_key=True)
    test_run_id: str = Field(index=True, foreign_key="test_runs.id")
    side: str
    status: str
    summary_json: str


class ReportRow(SQLModel, table=True):
    __tablename__ = "reports"

    id: str = Field(primary_key=True)
    test_run_id: str = Field(index=True, foreign_key="test_runs.id")
    path: str
    overall_status: str
    created_at: datetime = Field(default_factory=utcnow)
