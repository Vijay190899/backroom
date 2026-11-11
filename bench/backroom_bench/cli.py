"""`backroom-bench`: benchmark harness and provider capability probe."""

import argparse
import sys

from backroom_bench import probe


def main() -> None:
    parser = argparse.ArgumentParser(prog="backroom-bench")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", help="check which LLM features the active provider supports")
    sub.add_parser("all", help="run benchmarks B1-B5 (milestone M4)")
    args = parser.parse_args()

    if args.command == "probe":
        raise SystemExit(probe.main())
    print("backroom-bench all: the benchmark harness lands in milestone M4.", file=sys.stderr)
    raise SystemExit(2)
