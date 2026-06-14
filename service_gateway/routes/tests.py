import uuid
import zipfile
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse

from service_gateway.models.test_run import (
    RunStatus,
    TestRunRequest,
    TestRunResponse,
    TestRunStatus,
)
from service_gateway.store.run_history import run_history
from service_gateway.services import test_runner

router = APIRouter(prefix="/api/v1/tests", tags=["tests"])


@router.post("/run", response_model=TestRunResponse)
async def run_tests(request: TestRunRequest):
    run_id = str(uuid.uuid4())

    run_history.create_run(
        run_id=run_id,
        team=request.team,
        test_type=request.type.value,
        feature=request.feature,
        tags=request.tags,
    )

    test_runner.execute(
        run_id=run_id,
        team=request.team,
        test_type=request.type.value,
        feature=request.feature,
        tags=request.tags,
    )

    return TestRunResponse(
        run_id=run_id,
        status=RunStatus.PENDING,
        message="Tests en cola de ejecución",
    )


@router.get("/run/{run_id}", response_model=TestRunStatus)
async def get_run_status(run_id: str):
    run = run_history.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run


@router.get("/run/{run_id}/report")
async def get_run_report(
    run_id: str,
    format: str = Query("html", enum=["html", "raw"]),
    download: bool = Query(False),
):
    run = run_history.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    if run.status not in (RunStatus.COMPLETED, RunStatus.FAILED):
        raise HTTPException(
            status_code=400,
            detail=f"Report not ready. Current status: {run.status}",
        )

    run_dir = Path("results") / run_id

    if format == "html":
        report_path = run_dir / "allure-report" / "index.html"
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="HTML report not found")
        html_content = report_path.read_text(encoding="utf-8")

        if download:
            return StreamingResponse(
                iter([html_content.encode("utf-8")]),
                media_type="text/html",
                headers={"Content-Disposition": f"attachment; filename=report-{run_id}.html"},
            )
        return HTMLResponse(content=html_content)

    allure_results = run_dir / "allure-results"
    if not allure_results.exists():
        raise HTTPException(status_code=404, detail="Allure results not found")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in allure_results.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(allure_results)
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=report-{run_id}.zip"},
    )
