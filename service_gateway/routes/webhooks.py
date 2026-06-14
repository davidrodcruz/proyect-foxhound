import hashlib
import hmac
import os
import uuid

from fastapi import APIRouter, HTTPException, Request

from service_gateway.models.test_run import RunStatus, TestRunResponse
from service_gateway.store.run_history import run_history
from service_gateway.services import test_runner

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        return False

    if not signature_header:
        return False

    expected_signature = "sha256=" + hmac.new(
        secret.encode(), payload_body, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature_header)


@router.post("/github", response_model=TestRunResponse)
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not verify_github_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    if event_type == "ping":
        return TestRunResponse(
            run_id="",
            status=RunStatus.PENDING,
            message="Webhook ping received",
        )

    action = payload.get("action", "")
    if action not in ("opened", "synchronize", "push"):
        return TestRunResponse(
            run_id="",
            status=RunStatus.PENDING,
            message=f"Ignored action: {action}",
        )

    run_id = str(uuid.uuid4())

    repository = payload.get("repository", {})
    repo_name = repository.get("full_name", "unknown")
    branch = payload.get("ref", "unknown").replace("refs/heads/", "")
    commit = payload.get("after", "unknown")

    run_history.create_run(
        run_id=run_id,
        team="team1",
        test_type="all",
        github_payload={
            "event": event_type,
            "action": action,
            "repository": repo_name,
            "branch": branch,
            "commit": commit,
        },
    )

    test_runner.execute(
        run_id=run_id,
        team="team1",
        test_type="all",
    )

    return TestRunResponse(
        run_id=run_id,
        status=RunStatus.PENDING,
        message=f"Tests triggered by {event_type} on {repo_name}",
    )
