import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from service_gateway.models.test_run import RunStatus, TestRunStatus


class RunHistory:
    def __init__(self):
        self._runs: dict[str, TestRunStatus] = {}
        self._storage_path = Path("results/runs.json")
        self._load()

    def _load(self):
        if self._storage_path.exists():
            with open(self._storage_path, "r") as f:
                data = json.load(f)
                for run_id, run_data in data.items():
                    self._runs[run_id] = TestRunStatus(**run_data)

    def _save(self):
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for run_id, run in self._runs.items():
            data[run_id] = run.model_dump(mode="json")
        with open(self._storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def create_run(
        self,
        run_id: str,
        team: str,
        test_type: str,
        feature: Optional[str] = None,
        tags: Optional[str] = None,
        github_payload: Optional[dict] = None,
    ) -> TestRunStatus:
        run = TestRunStatus(
            run_id=run_id,
            status=RunStatus.PENDING,
            team=team,
            type=test_type,
            feature=feature,
            tags=tags,
            created_at=datetime.now(),
            github_payload=github_payload,
        )
        self._runs[run_id] = run
        self._save()
        return run

    def update_status(
        self,
        run_id: str,
        status: RunStatus,
        exit_code: Optional[int] = None,
    ) -> Optional[TestRunStatus]:
        run = self._runs.get(run_id)
        if not run:
            return None

        run.status = status
        if status == RunStatus.RUNNING:
            run.started_at = datetime.now()
        elif status in (RunStatus.COMPLETED, RunStatus.FAILED):
            run.finished_at = datetime.now()
            run.exit_code = exit_code

        self._save()
        return run

    def get_run(self, run_id: str) -> Optional[TestRunStatus]:
        return self._runs.get(run_id)

    def get_all_runs(self) -> list[TestRunStatus]:
        return list(self._runs.values())


run_history = RunHistory()
