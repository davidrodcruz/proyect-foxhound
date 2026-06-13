import argparse
import sys

from core.run_tests_utils import run_tests


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
