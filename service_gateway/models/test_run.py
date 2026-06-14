from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TestType(str, Enum):
    UI = "ui"
    API = "api"
    ALL = "all"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TestRunRequest(BaseModel):
    team: str
    type: TestType = TestType.ALL
    feature: Optional[str] = None
    tags: Optional[str] = None


class TestRunResponse(BaseModel):
    run_id: str
    status: RunStatus
    message: str


class TestRunStatus(BaseModel):
    run_id: str
    status: RunStatus
    team: str
    type: TestType
    feature: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    github_payload: Optional[dict] = None
