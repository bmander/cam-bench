"""cam-bench's runner for camlib: `run.py CASE OUT` plans case CASE with its implementation
(cases/<category>/<name>.py, whose `make(stl, out)` writes the toolpath) and answers one line of
JSON (SPEC.md, "A runner"). A refusal camlib makes itself, typed (a tool that cannot reach the
depth an operation needs), is the planner declining, and is answered as a refusal."""
import importlib.metadata
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)


def main():
    if sys.argv[1:] == ["--version"]:
        print("camlib", importlib.metadata.version("camlib"))
        return
    cid, out = sys.argv[1], sys.argv[2]
    category, _, name = cid.rpartition("/")
    src = os.path.join(HERE, "cases", category, name.replace("-", "_") + ".py")
    if not os.path.exists(src):
        sys.exit(f"no implementation of {cid}")
    spec = importlib.util.spec_from_file_location("case", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    reason = getattr(mod, "REFUSED", None)
    if reason:
        print(json.dumps({"status": "refused", "reason": reason}))
        return
    from camlib.simulation import ReachRefused
    try:
        mod.make(os.path.join(ROOT, "cases", cid + ".stl"), out)
    except ReachRefused as e:
        print(json.dumps({"status": "refused", "reason": str(e)}))
        return
    print(json.dumps({"status": "ok", "format": "toolpath"}))


if __name__ == "__main__":
    main()
