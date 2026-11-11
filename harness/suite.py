"""What the harness reads: the cases (cases/**/*.md), the planners (planners.json), and where a
planner's implementation of a case lives. Standard library only (tomllib: Python 3.11 or later)."""
import json
import os
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# what a case says when it leaves a field out
DEFAULTS = {"resolution": 0.1, "tolerance": 0.01, "leftover": 0.02, "spoilboard": 0.0}
TOOL_SHAPES = ("flat", "ball")


def read_case(path):
    """A case file: its TOML header (between `+++` lines) and the description after it."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("+++"):
        raise ValueError(f"{path}: no +++ header")
    _, header, body = text.split("+++", 2)
    meta = tomllib.loads(header)
    cid = os.path.relpath(path, os.path.join(ROOT, "cases"))[:-len(".md")].replace(os.sep, "/")
    tools = []
    for t in meta["tools"]:
        if t["shape"] not in TOOL_SHAPES:
            raise ValueError(f"{cid}: tool {t['number']} has shape {t['shape']!r}")
        tools.append({**t, "shank": t.get("shank", t["diameter"])})
    removed = meta.get("removed")
    return {
        "id": cid,
        "title": meta.get("title", cid),
        "tags": meta.get("tags", []),
        **{k: float(meta.get(k, v)) for k, v in DEFAULTS.items()},
        "stock": {"min": [float(v) for v in meta["stock"]["min"]],
                  "max": [float(v) for v in meta["stock"]["max"]]},
        "tools": tools,
        # the volume the case's tools can reach, as a closed form, where there is one: a check
        # of the harness's own reference (harness/parts.py), not of any planner
        "removed": ({"value": float(removed["value"]), "exact": removed["exact"],
                     "tex": removed.get("tex")} if removed else None),
        "description": body.strip(),
        "path": path,
        "part": path[:-len(".md")],  # + .py (how it is built), .step, .stl
    }


def cases(prefix=""):
    """Every case whose id starts with `prefix`, in id order."""
    out = []
    for dirpath, _, files in os.walk(os.path.join(ROOT, "cases")):
        for f in files:
            if f.endswith(".md"):
                c = read_case(os.path.join(dirpath, f))
                if c["id"].startswith(prefix):
                    out.append(c)
    return sorted(out, key=lambda c: c["id"])


def case(cid):
    return read_case(os.path.join(ROOT, "cases", cid + ".md"))


def planners():
    with open(os.path.join(ROOT, "planners.json")) as f:
        return json.load(f)["planners"]


def source(planner, cid):
    """Where `planner`'s implementation of case `cid` is, from its `source` pattern, or None."""
    pattern = planner.get("source")
    if not pattern:
        return None
    category, _, name = cid.rpartition("/")
    return os.path.join(ROOT, pattern.format(case=cid, category=category, name=name,
                                             name_snake=name.replace("-", "_")))


def implements(planner, cid):
    """Whether `planner` has an implementation of case `cid` (or keeps none apart from its
    runner)."""
    src = source(planner, cid)
    return not src or os.path.exists(src)
