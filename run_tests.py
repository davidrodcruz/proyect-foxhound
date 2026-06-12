import argparse
import subprocess
import sys
from pathlib import Path


def build_behave_command(
    team: str,
    test_type: str,
    feature: str = None,
    tags: str = None,
    parallel: int = 1,
) -> list[str]:
    cmd = [sys.executable, "-m", "behave"]

    cmd.extend(["--format", "allure_behave.formatter:AllureFormatter"])
    cmd.extend(["--outfile", "results/allure-results"])

    if tags:
        cmd.extend(["--tags", tags])

    paths = []
    if test_type in ("ui", "all"):
        ui_path = Path("webui") / "teams" / team
        if ui_path.exists():
            if feature:
                feature_file = ui_path / "features" / feature
                if feature_file.exists():
                    paths.append(str(feature_file))
            else:
                paths.append(str(ui_path / "features"))

    if test_type in ("api", "all"):
        api_path = Path("api") / "teams" / team
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


def run_tests(
    team: str,
    test_type: str,
    feature: str = None,
    tags: str = None,
    parallel: int = 1,
) -> int:
    teams = [t.strip() for t in team.split(",")]

    if len(teams) > 1 and parallel > 1:
        return run_parallel(teams, test_type, feature, tags, parallel)

    total_exit_code = 0
    for t in teams:
        cmd = build_behave_command(t, test_type, feature, tags)
        print(f"\n{'='*60}")
        print(f"Running: {' '.join(cmd)}")
        print(f"{'='*60}\n")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            total_exit_code = 1

    return total_exit_code


def run_parallel(
    teams: list[str],
    test_type: str,
    feature: str,
    tags: str,
    parallel: int,
) -> int:
    import concurrent.futures

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


def main():
    parser = argparse.ArgumentParser(
        description="Foxhound Test Framework - CLI Orchestrator"
    )
    parser.add_argument(
        "-t", "--team", required=True, help="Team name (comma-separated for multiple)"
    )
    parser.add_argument(
        "-f", "--feature", help="Feature file name (e.g., login.feature)"
    )
    parser.add_argument("--tags", help="Behave tags filter (e.g., @smoke)")
    parser.add_argument(
        "-p", "--parallel", type=int, default=1, help="Parallel execution count"
    )
    parser.add_argument(
        "--type",
        choices=["ui", "api", "all"],
        default="all",
        help="Test type: ui, api, or all (default: all)",
    )

    args = parser.parse_args()
    exit_code = run_tests(args.team, args.type, args.feature, args.tags, args.parallel)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
