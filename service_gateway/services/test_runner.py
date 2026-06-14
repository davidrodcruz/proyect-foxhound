import shutil
import subprocess
import sys
import threading
from pathlib import Path

from service_gateway.store.run_history import run_history
from service_gateway.models.test_run import RunStatus


def execute(
    run_id: str,
    team: str,
    test_type: str,
    feature: str = None,
    tags: str = None,
):
    def _run():
        run_history.update_status(run_id, RunStatus.RUNNING)

        cmd = [sys.executable, "run_tests.py", "-t", team, "--type", test_type]

        if feature:
            cmd.extend(["-f", feature])
        if tags:
            cmd.extend(["--tags", tags])

        results_dir = Path("results") / run_id
        results_dir.mkdir(parents=True, exist_ok=True)

        output_file = results_dir / "output.log"

        try:
            with open(output_file, "w") as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=str(Path(__file__).parent.parent.parent),
                )

            exit_code = result.returncode

            allure_results_src = Path("results/allure-results")
            allure_results_dst = results_dir / "allure-results"
            if allure_results_src.exists():
                if allure_results_dst.exists():
                    shutil.rmtree(allure_results_dst)
                shutil.copytree(allure_results_src, allure_results_dst)

            allure_report_src = Path("results/allure-report")
            allure_report_dst = results_dir / "allure-report"
            if allure_report_src.exists():
                if allure_report_dst.exists():
                    shutil.rmtree(allure_report_dst)
                shutil.copytree(allure_report_src, allure_report_dst)

            if exit_code == 0:
                run_history.update_status(run_id, RunStatus.COMPLETED, exit_code)
            else:
                run_history.update_status(run_id, RunStatus.FAILED, exit_code)

        except Exception as e:
            run_history.update_status(run_id, RunStatus.FAILED, exit_code=-1)
            with open(output_file, "a") as f:
                f.write(f"\n\nException: {str(e)}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
