"""Grade a program for a case: read it, cut the stock with it, and compare what is left with the
part and with what the case's tools can reach (SPEC.md, "Grading").

    python3 harness/grade.py CASE PROGRAM.nc     # grade one program by hand
    python3 harness/grade.py CASE PROGRAM.json   # or one toolpath (SPEC.md, "The toolpath")

The case's part heights and its reference are kept in results/reference/ (not committed), keyed
by everything they depend on, since the reference of a large case takes a while."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gcode  # noqa: E402
import sim  # noqa: E402
import toolpath  # noqa: E402
from suite import ROOT, case as read_case  # noqa: E402

CACHE = os.path.join(ROOT, "results", "reference")
# where the tool starts: this far above the middle of the stock's top
START_ABOVE = 50.0
# how a program is written: its reader, and the extension it is kept with
FORMATS = {"gcode": (gcode.read, ".nc"), "toolpath": (toolpath.read, ".json")}


def start_of(case):
    lo, hi = case["stock"]["min"], case["stock"]["max"]
    return ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] + START_ABOVE)


def prepared(case):
    """The case's grid, its part's heights, the heights below which a tool gouges, and the
    reference (the lowest any of its tools can cut), from the cache where they are there."""
    lo, hi, h = case["stock"]["min"], case["stock"]["max"], case["resolution"]
    grid = sim.Grid(lo, hi, h)
    key = sim.cache_key(case)
    path = os.path.join(CACHE, case["id"].replace("/", "__") + ".npz")
    if os.path.exists(path):
        z = np.load(path)
        if str(z["key"]) == key:
            return grid, z["part"], z["gouge"], z["ref"]
    tris = sim.read_stl(case["part"] + ".stl")
    part = sim.heights(tris, grid, lo[2])
    # outside the part a tool may go into the spoilboard, as far as the case allows
    bare = sim.heights(tris, grid, -np.inf)
    gouge = np.where(np.isfinite(bare), part, lo[2] - case["spoilboard"])
    ref, _ = sim.reference(case, part)
    os.makedirs(CACHE, exist_ok=True)
    np.savez_compressed(path, key=key, part=part, gouge=gouge, ref=ref)
    return grid, part, gouge, ref


def describe(kind, p):
    """One problem in words, for a result's `why`."""
    lines = ", ".join(str(l) for l in p["lines"])
    more = f" ({p['count']} moves)" if p["count"] > 1 else ""
    amount = ""
    if kind in ("gouge", "rapid", "shank", "holder"):
        x, y = p["where"]
        amount = f" by {p['worst']:.3g} at ({x:.1f}, {y:.1f})"
    elif kind in ("feed", "plunge"):
        amount = f" by {p['worst']:.4g} mm/min"
    return f"{sim.UNSAFE[kind]}{amount}{more}, line {lines}"


def grade(case, text, keep=None, form="gcode"):
    """The outcome of a program (pass, incomplete, unsafe or invalid), why, and what it measures.
    `form` is how it is written, "gcode" or "toolpath". With `keep`, a path, the stock it leaves
    is saved there (npz), and its path beside it, for the board's drawings."""
    hi = case["stock"]["max"]
    try:
        moves = FORMATS[form][0](text, start_of(case))
    except gcode.Invalid as e:
        return "invalid", str(e), None
    known = {t["number"] for t in case["tools"]}
    for mv in moves:
        if mv.tool is not None and mv.tool not in known:
            return "invalid", f"line {mv.line}: tool {mv.tool} is not one of the case's", None
    grid, part, gouge, ref = prepared(case)
    grid, stock, probs, m = sim.simulate(case, moves, part, gouge)
    excess = sim.leftover(case, stock, ref)
    cell = grid.h * grid.h
    m["leftover_max"] = float(excess.max())
    m["leftover_volume"] = float(excess.sum() * cell)
    m["reachable"] = float((hi[2] - np.minimum(ref, hi[2])).sum() * cell)
    m["gouge_max"] = probs.kinds.get("gouge", {}).get("worst", 0.0)
    m["problems"] = probs.kinds
    for k in ("feed_length", "rapid_length", "air_length", "time", "removed", "reachable"):
        m[k] = round(m[k], 3)
    if keep:
        os.makedirs(os.path.dirname(keep), exist_ok=True)
        np.savez_compressed(keep, stock=stock.astype(np.float32), excess=excess.astype(np.float32))
        with open(keep[:-len(".npz")] + ".path.json", "w") as f:
            json.dump(thin(moves), f)
    if probs.kinds:
        order = [k for k in sim.UNSAFE if k in probs.kinds]
        return "unsafe", "; ".join(describe(k, probs.kinds[k]) for k in order), m
    if m["leftover_max"] > 0:
        at = np.unravel_index(int(np.argmax(excess)), excess.shape)
        x, y = grid.x[at[1]], grid.y[at[0]]
        return ("incomplete", f"leaves {m['leftover_max']:.3g} more than the tools can reach at "
                f"({x:.1f}, {y:.1f}), {m['leftover_volume']:.4g} mm³ in all", m)
    return "pass", "", m


# the most points a drawn path keeps
DRAWN = 60000


def thin(moves):
    """The program's path for drawing, as polylines of one kind and tool: [{"rapid", "tool",
    "points": [x, y, z, ...]}], with points closer than the cells dropped while there are too
    many."""
    runs, cur = [], None
    for mv in moves:
        if cur is None or cur["rapid"] != (mv.kind == "rapid") or cur["tool"] != mv.tool \
                or cur["end"] != mv.a:
            cur = {"rapid": mv.kind == "rapid", "tool": mv.tool, "pts": [mv.a], "end": mv.a}
            runs.append(cur)
        cur["pts"].append(mv.b)
        cur["end"] = mv.b
    total = sum(len(r["pts"]) for r in runs)
    step = 1
    while total / step > DRAWN:
        step *= 2
    out = []
    for r in runs:
        pts = r["pts"][::step] + ([r["pts"][-1]] if (len(r["pts"]) - 1) % step else [])
        out.append({"rapid": r["rapid"], "tool": r["tool"],
                    "points": [round(c, 3) for p in pts for c in p]})
    return out


def main():
    cid, program = sys.argv[1], sys.argv[2]
    with open(program) as f:
        text = f.read()
    form = "toolpath" if program.endswith(".json") else "gcode"
    outcome, why, m = grade(read_case(cid), text, form=form)
    print(outcome, why)
    if m:
        print(json.dumps({k: v for k, v in m.items() if k != "problems"}, indent=1))


if __name__ == "__main__":
    main()
