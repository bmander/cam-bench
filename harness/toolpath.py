"""Read a program in the bench's toolpath format (SPEC.md, "The toolpath") into straight moves.

A toolpath is what a CAM kernel plans, before any post-processor writes it for a controller: a
JSON object whose `moves` are rapids, lines and arcs, in order, each from where the last ended,
with the tool, the feed and the spindle speed holding until a move changes them:

    {"toolpath": 1,
     "moves": [
       {"tool": 1, "rpm": 18000},
       {"rapid": [10, 10, 25]},
       {"line": [10, 10, 18], "feed": 300},
       {"line": [[40, 10, 18], [40, 30, 18]], "feed": 1200},
       {"arc": [40, 30, 16], "center": [35, 30], "sweep": 6.283185307179586}
     ]}

`read(text, start)` returns the same `gcode.Move`s as `gcode.read`, so a toolpath is graded
exactly as a G-code program is; anything the format does not allow raises `gcode.Invalid`.
Standard library only."""
import json
import math

from gcode import SAG, Invalid, Move

VERSION = 1
STATE = ("tool", "rpm", "feed")
MOTIONS = ("rapid", "line", "arc")


def point(v, where):
    if (not isinstance(v, list) or len(v) != 3
            or not all(isinstance(c, (int, float)) and not isinstance(c, bool)
                       and math.isfinite(c) for c in v)):
        raise Invalid(f"{where}: a point is three finite numbers, not {json.dumps(v)[:60]}")
    return tuple(float(c) for c in v)


def arc(a, b, center, sweep, where):
    """Points along the arc from a about center (x, y) through `sweep` radians (anticlockwise
    positive, seen from above), its z varying linearly to b's; b itself is last."""
    cx, cy = center
    r0 = math.hypot(a[0] - cx, a[1] - cy)
    if r0 < 1e-9:
        raise Invalid(f"{where}: an arc of radius 0")
    t0 = math.atan2(a[1] - cy, a[0] - cx)
    ex, ey = cx + r0 * math.cos(t0 + sweep), cy + r0 * math.sin(t0 + sweep)
    if math.hypot(ex - b[0], ey - b[1]) > max(2e-3, 1e-4 * r0):
        raise Invalid(f"{where}: the arc ends at ({ex:.4f}, {ey:.4f}), not at its end point")
    step = 2 * math.acos(max(-1.0, 1 - SAG / r0)) if SAG < r0 else math.pi / 2
    n = max(1, math.ceil(abs(sweep) / step))
    pts = [(cx + r0 * math.cos(t0 + sweep * i / n), cy + r0 * math.sin(t0 + sweep * i / n),
            a[2] + (b[2] - a[2]) * i / n) for i in range(1, n)]
    return pts + [b]


def read(text, start):
    try:
        doc = json.loads(text)
    except ValueError as e:
        raise Invalid(f"not JSON: {e}")
    if not isinstance(doc, dict) or doc.get("toolpath") != VERSION:
        raise Invalid(f'not a toolpath: its object must say "toolpath": {VERSION}')
    if not isinstance(doc.get("moves"), list):
        raise Invalid('a toolpath\'s "moves" is a list')
    pos = tuple(start)
    tool, rpm, feed = None, 0.0, None
    moves = []
    for no, m in enumerate(doc["moves"], 1):
        where = f"move {no}"
        if not isinstance(m, dict):
            raise Invalid(f"{where}: a move is an object")
        extra = set(m) - set(STATE) - set(MOTIONS) - {"center", "sweep"}
        if extra:
            raise Invalid(f"{where}: {', '.join(sorted(extra))} is not in the toolpath format")
        if "tool" in m:
            if not isinstance(m["tool"], int) or isinstance(m["tool"], bool):
                raise Invalid(f"{where}: a tool is its case's number")
            tool = m["tool"]
        if "rpm" in m:
            if not isinstance(m["rpm"], (int, float)) or m["rpm"] < 0:
                raise Invalid(f"{where}: rpm is 0 (stopped) or more")
            rpm = float(m["rpm"])
        if "feed" in m:
            if not isinstance(m["feed"], (int, float)) or not m["feed"] > 0:
                raise Invalid(f"{where}: a feed is more than 0")
            feed = float(m["feed"])
        kinds = [k for k in MOTIONS if k in m]
        if len(kinds) > 1:
            raise Invalid(f"{where}: one motion a move")
        if not kinds:
            if "center" in m or "sweep" in m:
                raise Invalid(f"{where}: center and sweep belong to an arc")
            continue
        kind = kinds[0]

        def emit(a, b, k):
            if k == "feed":
                if feed is None:
                    raise Invalid(f"{where}: a cut with no feed")
                if tool is None:
                    raise Invalid(f"{where}: a cut with no tool")
            moves.append(Move(a, b, k, tool, feed, rpm > 0, no))

        if kind == "arc":
            b = point(m["arc"], where)
            c = m.get("center")
            if (not isinstance(c, list) or len(c) != 2
                    or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in c)):
                raise Invalid(f"{where}: an arc's center is [x, y]")
            s = m.get("sweep")
            if not isinstance(s, (int, float)) or not math.isfinite(s) or s == 0:
                raise Invalid(f"{where}: an arc's sweep is a turn in radians, not 0")
            a = pos
            for p in arc(pos, b, c, float(s), where):
                emit(a, p, "feed")
                a = p
            pos = b
            continue
        if "center" in m or "sweep" in m:
            raise Invalid(f"{where}: center and sweep belong to an arc")
        v = m[kind]
        pts = [point(p, where) for p in v] if v and isinstance(v[0], list) else [point(v, where)]
        for p in pts:
            emit(pos, p, "rapid" if kind == "rapid" else "feed")
            pos = p
    return moves
