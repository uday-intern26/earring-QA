import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.api.dependencies import get_app_settings, get_db
from app.core.config import Settings
from app.db.repositories import runs as run_repo
from app.schemas.test import StepStatus, TestRunAccepted, TestRunRequest, TestStatusRead
from app.services.test_runner import TestRunner, initial_steps

router = APIRouter(prefix="/tests", tags=["execution"])


@router.post("/{test_id}/run", response_model=TestRunAccepted, status_code=202)
async def run_test(
    test_id: str,
    payload: TestRunRequest,
    background: BackgroundTasks,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> TestRunAccepted:
    test = run_repo.get_test(session, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Test was not found."})
    from app.models.application import Application

    application = session.get(Application, test.application_id)
    if application is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Application was not found."})
    if application.type == "web" and not payload.password:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "CREDENTIALS_REQUIRED",
                "message": "A password is required to run a web application test and is kept only for this execution.",
            },
        )
    active = run_repo.latest_run(session, test_id)
    if active and active.status in {"pending", "running"}:
        raise HTTPException(
            status_code=409,
            detail={"code": "RUN_IN_PROGRESS", "message": "This test already has a run in progress."},
        )
    run = run_repo.create_run(session, test_id, initial_steps())
    username = payload.username if payload.username is not None else application.username
    runner = TestRunner(settings)
    background.add_task(runner.execute, run.id, username, payload.password)
    return TestRunAccepted(test_id=test_id, test_run_id=run.id, status=run.status)


@router.get("/{test_id}/status", response_model=TestStatusRead)
def test_status(test_id: str, session: Session = Depends(get_db)) -> TestStatusRead:
    if run_repo.get_test(session, test_id) is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Test was not found."})
    run = run_repo.latest_run(session, test_id)
    if run is None:
        return TestStatusRead(
            test_id=test_id,
            test_run_id=None,
            status="not_run",
            progress=0,
            stage="not_run",
            stage_message="This test has not been run.",
            steps=[],
        )
    steps = [StepStatus.model_validate(item) for item in json.loads(run.steps_json or "[]")]
    return TestStatusRead(
        test_id=test_id,
        test_run_id=run.id,
        status=run.status,
        progress=run.progress,
        stage=run.stage,
        stage_message=run.stage_message,
        overall_status=run.overall_status,
        steps=steps,
        error=run.error,
        reason=run.reason,
        recommended_action=run.recommended_action,
    )
