"""Read a program in the bench's G-code (SPEC.md, "The program") into straight moves.

`read(text, start)` returns a list of `Move`s: each a straight line from `a` to `b` (x, y, z), its
`kind` ("rapid" or "feed"), the tool loaded, the feed, whether the spindle turns, and the line of
the program it came from. Arcs are cut into chords that stray no more than `SAG` from the arc,
and canned drilling cycles into their rapids and feeds. A program the bench does not accept raises
`Invalid`, saying which line and why. Standard library only."""
import math
import re

SAG = 0.0005  # the most a chord of an arc strays from it
INCH = 25.4

# the letters the bench reads: any other makes a program invalid
LETTERS = set("GMNOXYZIJKRFSTPQH")
WORD = re.compile(r"([A-Z])\s*([-+]?(?:\d+\.?\d*|\.\d+))")


class Invalid(Exception):
    pass


class Move:
    __slots__ = ("a", "b", "kind", "tool", "feed", "spindle", "line")

    def __init__(self, a, b, kind, tool, feed, spindle, line):
        self.a, self.b, self.kind, self.tool = a, b, kind, tool
        self.feed, self.spindle, self.line = feed, spindle, line


def words(line):
    """The words of one line, comments removed: [(letter, value)]."""
    line = re.sub(r"\([^)]*\)", " ", line.upper()).split(";")[0]
    if "(" in line:
        raise ValueError("unclosed comment")
    out = [(m.group(1), float(m.group(2))) for m in WORD.finditer(line)]
    for k, _ in out:
        if k not in LETTERS:
            raise ValueError(f"{k} is not in the bench's G-code")
    rest = WORD.sub(" ", line)
    if rest.strip(" \t\r%"):
        raise ValueError(f"cannot read {rest.strip()!r}")
    return out


def arc_points(a, b, center, cw):
    """Points along the arc in the XY plane from a to b about center (z varying linearly: a helix),
    a full turn where a and b coincide; b itself is last."""
    cx, cy = center
    r0 = math.hypot(a[0] - cx, a[1] - cy)
    r1 = math.hypot(b[0] - cx, b[1] - cy)
    if r0 < 1e-9:
        raise ValueError("arc of radius 0")
    if abs(r0 - r1) > max(2e-3, 1e-4 * r0):
        raise ValueError(f"arc ends at radius {r1:.6g}, starts at {r0:.6g}")
    t0 = math.atan2(a[1] - cy, a[0] - cx)
    t1 = math.atan2(b[1] - cy, b[0] - cx)
    sweep = t1 - t0
    if cw:
        while sweep >= -1e-12:
            sweep -= 2 * math.pi
    else:
        while sweep <= 1e-12:
            sweep += 2 * math.pi
    if math.hypot(a[0] - b[0], a[1] - b[1]) > 1e-9 and abs(abs(sweep) - 2 * math.pi) < 1e-9:
        sweep = 0.0
    r = max(r0, r1)
    step = 2 * math.acos(max(-1.0, 1 - SAG / r)) if SAG < r else math.pi / 2
    n = max(1, math.ceil(abs(sweep) / step))
    pts = []
    for i in range(1, n):
        f = i / n
        t, rr = t0 + sweep * f, r0 + (r1 - r0) * f
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t), a[2] + (b[2] - a[2]) * f))
    pts.append(tuple(b))
    return pts


def read(text, start):
    """The program's moves, from the tool's position `start`."""
    pos = list(start)
    moves = []
    motion = None  # 0, 1, 2, 3 or a canned cycle (81, 82, 83, 73)
    absolute, arcs_absolute, scale = True, False, 1.0
    feed, tool, loaded, spindle = None, None, None, False
    retract_initial, cycle_z0, r_plane, cycle_bottom = True, None, None, None
    ended = False

    for no, raw in enumerate(text.splitlines(), 1):
        try:
            ws = words(raw)
        except ValueError as e:
            raise Invalid(f"line {no}: {e}")
        if not ws or ended:
            continue
        gs = [v for k, v in ws if k == "G"]
        ms = [v for k, v in ws if k == "M"]
        args = {k: v for k, v in ws if k not in "GMNO"}

        def bad(why):
            raise Invalid(f"line {no}: {why}: {raw.strip()}")

        for g in gs:
            if g in (0, 1, 2, 3):
                motion = int(g)
            elif g in (81, 82, 83, 73):
                if motion not in (81, 82, 83, 73):
                    cycle_z0, cycle_bottom = pos[2], None
                motion = int(g)
            elif g == 80:
                motion = None if motion in (81, 82, 83, 73) else motion
            elif g == 90:
                absolute = True
            elif g == 91:
                absolute = False
            elif g == 90.1:
                arcs_absolute = True
            elif g == 91.1:
                arcs_absolute = False
            elif g == 21:
                scale = 1.0
            elif g == 20:
                scale = INCH
            elif g == 98:
                retract_initial = True
            elif g == 99:
                retract_initial = False
            elif g in (17, 40, 49, 43, 54, 55, 56, 57, 58, 59, 61, 61.1, 64, 94, 4):
                pass  # the XY plane; no compensation; one frame; how corners are blended; dwell
            elif g in (18, 19):
                bad("arcs only in the XY plane (G17)")
            elif g in (41, 42):
                bad("no cutter compensation: give the tool's path")
            elif g in (28, 30, 53):
                bad("no machine coordinates: give every point in the case's frame")
            else:
                bad(f"G{g:g} is not in the bench's G-code")
        if "T" in args:
            tool = int(args["T"])  # chosen; loaded by M6
        for m in ms:
            if m in (3, 4):
                spindle = True
            elif m == 5:
                spindle = False
            elif m == 6:
                if tool is None:
                    bad("M6 with no tool named (T)")
                loaded = tool
            elif m in (2, 30):
                ended = True
            elif m in (0, 1, 7, 8, 9):
                pass
            else:
                bad(f"M{m:g} is not in the bench's G-code")
        if "F" in args:
            if args["F"] <= 0:
                bad("feed of 0")
            feed = args["F"] * scale
        if 4 in gs:
            continue  # a dwell's P is not a position

        axes = {k: args[k] * scale for k in "XYZ" if k in args}
        if not axes and not (motion in (2, 3) and any(k in args for k in "IJR")):
            continue
        if motion is None:
            if axes:
                bad("a position with no motion mode")
            continue

        target = list(pos)
        for i, k in enumerate("XYZ"):
            if k in axes:
                target[i] = axes[k] if absolute else pos[i] + axes[k]

        def emit(a, b, kind):
            if kind == "feed":
                if feed is None:
                    bad("a cut with no feed (F)")
                if loaded is None:
                    bad("a cut with no tool loaded (T… M6)")
            moves.append(Move(tuple(a), tuple(b), kind, loaded, feed, spindle, no))

        if motion == 0:
            emit(pos, target, "rapid")
            pos = target
        elif motion == 1:
            emit(pos, target, "feed")
            pos = target
        elif motion in (2, 3):
            if "R" in args:
                r = args["R"] * scale
                dx, dy = target[0] - pos[0], target[1] - pos[1]
                d = math.hypot(dx, dy)
                if d < 1e-9 or d > 2 * abs(r) + 1e-6:
                    bad("an arc's R does not fit its ends")
                h = math.sqrt(max(0.0, r * r - d * d / 4))
                # the shorter arc for R > 0, the longer for R < 0
                s = (1 if (motion == 3) == (r > 0) else -1)
                center = (pos[0] + dx / 2 - s * h * dy / d, pos[1] + dy / 2 + s * h * dx / d)
            else:
                if "K" in args:
                    bad("arcs only in the XY plane (G17)")
                i, j = args.get("I", 0.0) * scale, args.get("J", 0.0) * scale
                center = (i, j) if arcs_absolute else (pos[0] + i, pos[1] + j)
            try:
                pts = arc_points(pos, target, center, motion == 2)
            except ValueError as e:
                bad(str(e))
            a = pos
            for p in pts:
                emit(a, p, "feed")
                a = p
            pos = target
        else:  # a canned drilling cycle: to the hole's xy, to R, down to Z, back
            # R and Z hold from hole to hole until the cycle is cancelled
            if "R" in args:
                r_plane = args["R"] * scale if absolute else cycle_z0 + args["R"] * scale
            if "Z" in args:
                cycle_bottom = args["Z"] * scale if absolute else r_plane + args["Z"] * scale
            if r_plane is None or cycle_bottom is None:
                bad("a drilling cycle needs Z and R")
            if "L" in args:
                bad("no repeated holes (L)")
            # as a control does: up to R first if below it, across, down to R, down to Z, and
            # back to R, or after G98 to the higher of R and where the cycle began
            here = list(pos)
            if here[2] < r_plane:
                emit(here, (here[0], here[1], r_plane), "rapid")
                here[2] = r_plane
            hole = [target[0], target[1], here[2]]
            emit(here, hole, "rapid")
            emit(hole, (hole[0], hole[1], r_plane), "rapid")
            emit((hole[0], hole[1], r_plane), (hole[0], hole[1], cycle_bottom), "feed")
            back = max(cycle_z0, r_plane) if retract_initial else r_plane
            emit((hole[0], hole[1], cycle_bottom), (hole[0], hole[1], back), "rapid")
            pos = [hole[0], hole[1], back]
    return moves
