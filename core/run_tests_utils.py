import concurrent.futures
import shutil
import subprocess
import sys
from pathlib import Path


def clean_allure_results() -> None:
    """Remove previous allure results and reports to start fresh."""
    for folder in ["results/allure-results", "results/allure-report"]:
        path = Path(folder)
        if path.exists():
            shutil.rmtree(path)


def build_behave_command(
    team: str,
    test_type: str,
    feature: str = None,
    tags: str = None,
) -> list[str]:
    cmd = [sys.executable, "-m", "behave"]

    cmd.extend(["--format", "allure_behave.formatter:AllureFormatter"])
    cmd.extend(["--outfile", "results/allure-results"])

    if tags:
        cmd.extend(["--tags", tags])

    paths = []
    if test_type in ("ui", "all"):
        ui_path = Path("tests/webui") / "teams" / team
        if ui_path.exists():
            if feature:
                feature_file = ui_path / "features" / feature
                if feature_file.exists():
                    paths.append(str(feature_file))
            else:
                paths.append(str(ui_path / "features"))

    if test_type in ("api", "all"):
        api_path = Path("tests/api") / "teams" / team
        if api_path.exists():
            if feature:
                feature_file = api_path / "features" / feature
                if feature_file.exists():
                    paths.append(str(feature_file))
            else:
                paths.append(str(api_path / "features"))

    if not paths:
        print(f"No features found for team '{team}' with type '{test_type}'")
        sys.exit(1)

    cmd.extend(paths)
    return cmd


def generate_report() -> None:
    allure_results = Path("results/allure-results")
    allure_report = Path("results/allure-report")

    if not allure_results.exists():
        print("No allure-results found, skipping report generation")
        return

    try:
        subprocess.run(
            ["allure", "--version"],
            capture_output=True,
            check=True,
            shell=(sys.platform == "win32")
        )
    except FileNotFoundError:
        print("\n⚠️  Allure CLI not installed. Skipping report generation.")
        print("   Install: npm install -g allure")
        print(f"   Raw results available at: {allure_results.absolute()}")
        return

    print("\n📊 Generating Allure report...")
    result = subprocess.run([
        "allure", "awesome",
        str(allure_results),
        "-o", str(allure_report),
        "--single-file"
    ], shell=(sys.platform == "win32"))

    if result.returncode == 0:
        report_path = allure_report / "index.html"
        if report_path.exists():
            print(f"✅ Report generated: {report_path.absolute()}")
    else:
        print("❌ Failed to generate report")


def run_single(team: str, test_type: str, feature: str = None, tags: str = None) -> int:
    total_exit_code = 0
    teams = [t.strip() for t in team.split(",")]

    for t in teams:
        cmd = build_behave_command(t, test_type, feature, tags)
        print(f"\n{'='*60}")
        print(f"Running: {' '.join(cmd)}")
        print(f"{'='*60}\n")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            total_exit_code = 1

    return total_exit_code


def run_parallel(teams: list[str], test_type: str, feature: str, tags: str, parallel: int) -> int:
    def run_team(t):
        cmd = build_behave_command(t, test_type, feature, tags)
        print(f"\n[PARALLEL] Running team: {t}")
        result = subprocess.run(cmd)
        return result.returncode

    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = {executor.submit(run_team, t): t for t in teams}
        results = {}
        for future in concurrent.futures.as_completed(futures):
            team_name = futures[future]
            results[team_name] = future.result()

    total_exit_code = 0
    for team_name, exit_code in results.items():
        status = "PASSED" if exit_code == 0 else "FAILED"
        print(f"\n[RESULT] Team '{team_name}': {status}")
        if exit_code != 0:
            total_exit_code = 1

    return total_exit_code


def run_tests(
    team: str,
    test_type: str,
    feature: str = None,
    tags: str = None,
    parallel: int = 1,
) -> int:
    clean_allure_results()
    teams = [t.strip() for t in team.split(",")]

    if len(teams) > 1 and parallel > 1:
        exit_code = run_parallel(teams, test_type, feature, tags, parallel)
    else:
        exit_code = run_single(team, test_type, feature, tags)

    generate_report()
    return exit_code
