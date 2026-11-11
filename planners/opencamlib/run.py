"""cam-bench's runner for opencamlib: `run.py CASE OUT` writes the program of case CASE (its
implementation, cases/<category>/<name>.py, whose `make(stl, out)` writes it) and answers one
line of JSON (SPEC.md, "A runner")."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)


def main():
    if sys.argv[1:] == ["--version"]:
        import opencamlib
        print("opencamlib", opencamlib.version())
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
    # opencamlib writes to standard output as its objects are freed: send that to standard error,
    # so that the reply is the last line
    sys.stdout.flush()
    reply = os.dup(1)
    os.dup2(2, 1)
    mod.make(os.path.join(ROOT, "cases", cid + ".stl"), out)
    sys.stdout.flush()
    os.dup2(reply, 1)
    print(json.dumps({"status": "ok"}), flush=True)
    # and leave before the interpreter frees the rest, which opencamlib would announce
    os._exit(0)


if __name__ == "__main__":
    main()
