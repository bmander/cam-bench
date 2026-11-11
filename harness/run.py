#!/usr/bin/env python3
"""Run every case against every planner and grade the programs.

    python3 harness/run.py                          # every planner in planners.json, every case
    python3 harness/run.py --planner opencamlib --case pocket/
    python3 harness/run.py --timeout 600

A planner's runner is asked for each case it has an implementation of (SPEC.md); a case it has
none of is missing. Each program is graded by harness/grade.py. Writes results/<planner>.json
after a run of the whole suite (a run of part of it, `--case`, folds its rows into the last
one), and keeps each program, the stock it leaves and its path as results/runs/<planner>/<case>.*
for the board's drawings (not committed).

Each run is measured too, though nothing measured is graded: its wall-clock time, its CPU time
(user and system, over every thread) and its peak memory, from the operating system's account of
the runner's process (wait4), which harness/measure.py starts and waits for; and what starting the
runner costs, alone, given a case id no case has (`harness/start`)."""
import argparse
import functools
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade  # noqa: E402
from suite import ROOT, cases, implements, planners  # noqa: E402

TIME_PLACES = 6
NO_CASE = "harness/start"
STARTS = 5


class Ran:
    def __init__(self, code, stdout, stderr, seconds, cpu=None, peak_mb=None):
        self.code, self.stdout, self.stderr = code, stdout, stderr
        self.seconds, self.cpu, self.peak_mb = seconds, cpu, peak_mb


MEASURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "measure.py")
MEASURED = all(hasattr(os, f) for f in ("posix_spawnp", "wait4"))
measurer = None


def measured(request):
    global measurer
    if measurer is None or measurer.poll() is not None:
        measurer = subprocess.Popen([sys.executable, "-I", "-S", MEASURE], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, text=True, cwd=ROOT)
    measurer.stdin.write(json.dumps(request) + "\n")
    measurer.stdin.flush()
    line = measurer.stdout.readline()
    if not line:
        raise RuntimeError("harness/measure.py stopped")
    answer = json.loads(line)
    if "error" in answer:
        raise OSError(answer["error"])
    return answer


def execute(argv, timeout):
    """Run `argv` until it exits or `timeout` seconds pass, and say how it ran (`Ran`)."""
    with tempfile.TemporaryDirectory() as tmp:
        out, err = os.path.join(tmp, "stdout"), os.path.join(tmp, "stderr")
        if MEASURED:
            a = measured({"argv": argv, "cwd": ROOT, "env": dict(os.environ), "stdout": out,
                          "stderr": err, "timeout": timeout, "core": None})
            code, seconds, cpu, peak = a["code"], a["seconds"], a["cpu"], a["peak_bytes"] / 1e6
        else:
            with open(out, "wb") as o, open(err, "wb") as e:
                start = time.monotonic()
                p = subprocess.Popen(argv, stdout=o, stderr=e, stdin=subprocess.DEVNULL, cwd=ROOT)
                try:
                    code = p.wait(timeout)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
                    code = None
                seconds = time.monotonic() - start
            cpu = peak = None
        with open(out, encoding="utf-8", errors="replace") as o, \
                open(err, encoding="utf-8", errors="replace") as e:
            return Ran(code, o.read(), e.read(), seconds, cpu, peak)


def why_crashed(stderr, code):
    lines = [l for l in stderr.strip().splitlines() if l.strip()]
    return (lines[-1] if lines else f"exit {code}")[:300]


def run_one(command, case, timeout, keep):
    """Run and grade one case: (outcome, why, reply, measures, how it ran)."""
    with tempfile.TemporaryDirectory() as tmp:
        program = os.path.join(tmp, "program")
        ran = execute(command + [case["id"], program], timeout)
        if ran.code is None:
            return "timeout", f"over {timeout:g} s", None, None, ran
        if ran.code != 0:
            return "crashed", why_crashed(ran.stderr, ran.code), None, None, ran
        try:
            reply = json.loads(ran.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return "crashed", "no JSON reply", None, None, ran
        if reply.get("status") == "refused":
            return "refused", reply.get("reason", ""), reply, None, ran
        if reply.get("status") != "ok":
            return "crashed", f"status {reply.get('status')!r}", reply, None, ran
        form = reply.get("format", "gcode")
        if form not in grade.FORMATS:
            return "invalid", f"no format {form!r}", reply, None, ran
        if not os.path.exists(program):
            return "invalid", "no program written", reply, None, ran
        with open(program, encoding="utf-8", errors="replace") as f:
            text = f.read()
        os.makedirs(os.path.dirname(keep), exist_ok=True)
        shutil.copyfile(program, keep + grade.FORMATS[form][1])
    outcome, why, m = grade.grade(case, text, keep + ".npz", form)
    if m is not None:
        if form == "gcode":
            m["lines"] = text.count("\n")
        m["bytes"] = len(text.encode())
    return outcome, why, reply, m, ran


def rounded(x, places):
    return None if x is None else round(x, places)


def startup(p, timeout):
    """What starting planner `p`'s runner costs, building nothing: the median of STARTS runs."""
    def median(xs):
        xs = sorted(x for x in xs if x is not None)
        return xs[len(xs) // 2] if xs else None

    with tempfile.TemporaryDirectory() as tmp:
        argv = p["command"] + [NO_CASE, os.path.join(tmp, "none")]
        if execute(argv, min(timeout, 60)).code is None:
            return None
        runs = [execute(argv, min(timeout, 60)) for _ in range(STARTS)]
    return {"seconds": round(median(r.seconds for r in runs), TIME_PLACES),
            "cpu_seconds": rounded(median(r.cpu for r in runs), TIME_PLACES),
            "peak_mb": rounded(median(r.peak_mb for r in runs), 1)}


def version(p):
    if p.get("version"):
        try:
            return subprocess.run(p["version"], capture_output=True, text=True, cwd=ROOT,
                                  timeout=60).stdout.strip() or None
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None


@functools.cache
def host():
    cpu = platform.processor() or platform.machine()
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    if sys.platform == "darwin":
        try:
            cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True,
                                 text=True).stdout.strip() or cpu
        except OSError:
            pass
    cores = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
    return {"cpu": cpu, "cores": cores, "system": platform.platform(terse=True)}


def tally(rows):
    out = {}
    for row in rows:
        out[row["outcome"]] = out.get(row["outcome"], 0) + 1
    return out


def run_planner(p, chosen, timeout):
    rows = []
    for c in chosen:
        keep = os.path.join(ROOT, "results", "runs", p["name"], c["id"])
        for ext in (".nc", ".json", ".npz", ".path.json"):
            if os.path.exists(keep + ext):
                os.remove(keep + ext)
        if not implements(p, c["id"]):
            outcome, why, reply, m, ran = "missing", "no implementation", None, None, None
        else:
            outcome, why, reply, m, ran = run_one(p["command"], c, timeout, keep)
        rows.append({
            "case": c["id"], "outcome": outcome, "why": why,
            "seconds": rounded(ran and ran.seconds, TIME_PLACES),
            "cpu_seconds": rounded(ran and ran.cpu, TIME_PLACES),
            "peak_mb": rounded(ran and ran.peak_mb, 1),
            "program": m,
        })
        cost = (f"{ran.seconds:8.2f} s {ran.peak_mb or 0:7.1f} MB" if ran else " " * 20)
        print(f"{p['name']:<12} {outcome:<10} {c['id']:<28} {cost} {why[:90]}", flush=True)
    return rows


def record(p, rows, start):
    path = os.path.join(ROOT, "results", p["name"] + ".json")
    result = {"planner": p["name"], "version": version(p),
              "run": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": host(),
              "startup": start, "tally": tally(rows), "cases": rows}
    with open(path, "w") as f:
        json.dump(result, f, indent=1)
        f.write("\n")


def regrade(p, chosen):
    """Grade again the programs a planner's last run kept, as the harness grades now, keeping
    what the runs cost: for a change to how programs are graded."""
    path = os.path.join(ROOT, "results", p["name"] + ".json")
    with open(path) as f:
        last = json.load(f)
    wanted = {c["id"]: c for c in chosen}
    for row in last["cases"]:
        c = wanted.get(row["case"])
        keep = os.path.join(ROOT, "results", "runs", p["name"], row["case"])
        kept = [(f, ext) for f, (_, ext) in grade.FORMATS.items() if os.path.exists(keep + ext)]
        if c is None or not kept:
            continue
        form, ext = kept[0]
        with open(keep + ext, encoding="utf-8", errors="replace") as f:
            text = f.read()
        outcome, why, m = grade.grade(c, text, keep + ".npz", form)
        if m is not None:
            if form == "gcode":
                m["lines"] = text.count("\n")
            m["bytes"] = len(text.encode())
        row.update(outcome=outcome, why=why, program=m)
        print(f"{p['name']:<12} {outcome:<10} {c['id']:<28} {why[:90]}", flush=True)
    last["tally"] = tally(last["cases"])
    with open(path, "w") as f:
        json.dump(last, f, indent=1)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner", action="append", help="planner name (repeatable)")
    ap.add_argument("--case", default="", help="run the cases whose id starts with this")
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--regrade", action="store_true",
                    help="grade the last run's programs again, without running the planners")
    args = ap.parse_args()
    chosen = cases(args.case)
    if args.regrade:
        for p in planners():
            if p.get("command") and (not args.planner or p["name"] in args.planner):
                regrade(p, chosen)
        return
    for p in planners():
        if not p.get("command") or (args.planner and p["name"] not in args.planner):
            continue
        path = os.path.join(ROOT, "results", p["name"] + ".json")
        last = None
        if os.path.exists(path):
            with open(path) as f:
                last = json.load(f)
        start = startup(p, args.timeout) if not args.case or not last else last.get("startup")
        rows = run_planner(p, chosen, args.timeout)
        if args.case and last:
            # a part of the suite: its rows folded into the last run's
            done = {r["case"]: r for r in rows}
            ids = [c["id"] for c in cases()]
            old = {r["case"]: r for r in last["cases"]}
            rows = [done.get(cid) or old.get(cid) for cid in ids if done.get(cid) or old.get(cid)]
        record(p, rows, start)
        print(f"{p['name']}: {tally(rows)}")


if __name__ == "__main__":
    main()
