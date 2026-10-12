from sqlmodel import Field, SQLModel


class FrameRecord(SQLModel, table=True):
    __tablename__ = "frames"

    id: str = Field(primary_key=True)
    test_run_id: str = Field(index=True, foreign_key="test_runs.id")
    frame_number: int
    timestamp_ms: int
    path: str
    annotated_path: str | None = None
    selected: bool = False
    rejected: bool = False
    rejection_reasons: str | None = None
    quality_json: str | None = None


class FrameResult(SQLModel, table=True):
    __tablename__ = "frame_results"

    id: str = Field(primary_key=True)
    frame_id: str = Field(index=True, foreign_key="frames.id")
    test_run_id: str = Field(index=True, foreign_key="test_runs.id")
    side: str
    status: str
    normalized_distance: float | None = None
    result_json: str
    automated_result: str
    manual_result: str | None = None
    reviewer: str | None = None
    review_reason: str | None = None
