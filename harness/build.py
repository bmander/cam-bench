#!/usr/bin/env python3
"""Set up every planner's runner, or those named: `python3 harness/build.py [NAME ...]` runs each
planner's `build` command from planners.json. Standard library only."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from suite import ROOT, planners  # noqa: E402


def main():
    wanted = sys.argv[1:]
    failed = []
    for p in planners():
        if not p.get("build") or (wanted and p["name"] not in wanted):
            continue
        print(f"building {p['name']}: {' '.join(p['build'])}", flush=True)
        if subprocess.run(p["build"], cwd=ROOT).returncode != 0:
            failed.append(p["name"])
    if failed:
        sys.exit(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
