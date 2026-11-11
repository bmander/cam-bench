"""What the camlib implementations share: the case's tools as camlib tool assemblies, its part as
a camlib surface mesh, outlines as camlib planar boundaries, and the plan written out as the
bench's toolpath (SPEC.md, "The toolpath").

camlib plans each operation's cuts and the moves between them, and streams its plan as typed
motion (lines, arcs and helices, each with its operation, tool, feed and whether it is a rapid);
`write` keeps that motion as it is. An arc in a plane other than XY, which the toolpath format
does not carry, becomes chords within 0.0005 of it."""
import json
import math
import struct

from camlib.jobs import Job, Setup
from camlib.planar import Boundary
from camlib.simulation import OperationUpdate, StockSpec
from camlib.surface import SurfaceMesh
from camlib.tools import BallEndMill, EndMill, HolderSection, ToolAssembly

# above the stock's top: where camlib travels between operations
CLEARANCE = 3.0
# how far the tool starts above the stock's top (SPEC.md, "The program")
START_ABOVE = 50.0
# how long a holder is, above the tool's length out of it
HOLDER_LENGTH = 40.0
# how much of a tool is inside its holder
GRIP = 15.0
SAG = 0.0005


def tool(number, shape, diameter, flute, length, holder, shank=None):
    """A case's tool as a camlib assembly: the cutter, `length` out of a holder of diameter
    `holder`."""
    make = EndMill if shape == "flat" else BallEndMill
    cutter = make(f"T{number}", diameter=diameter, flute_length=flute,
                  overall_length=length + GRIP, shank_diameter=shank)
    return ToolAssembly(f"T{number}", cutter, stickout_mm=length,
                        gauge_length_mm=length + HOLDER_LENGTH,
                        holders=(HolderSection(z_min_mm=length, z_max_mm=length + HOLDER_LENGTH,
                                               radius_min_mm=holder / 2,
                                               radius_max_mm=holder / 2),))


def cutting(number, rpm, feed, plunge):
    """An operation's cutting data, for tool `number`."""
    return dict(feed_mm_min=feed, plunge_mm_min=plunge, spindle_rpm=rpm, coolant="off",
                tool_number=number, length_register=number)


def part(stl, error=0.002):
    """The part's STL as a camlib surface mesh; the bench meshes its parts to within 0.002. A
    triangle of no area, which a mesher leaves now and then and camlib refuses, is left out: it
    bounds nothing."""
    with open(stl, "rb") as f:
        data = f.read()
    n = struct.unpack_from("<I", data, 80)[0]
    tris = []
    for i in range(n):
        v = struct.unpack_from("<9f", data, 84 + 50 * i + 12)
        a, b, c = (v[0], v[1], v[2]), (v[3], v[4], v[5]), (v[6], v[7], v[8])
        u = [b[k] - a[k] for k in range(3)]
        w = [c[k] - a[k] for k in range(3)]
        n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
        if math.sqrt(sum(x * x for x in n)) > 1e-9:
            tris.append((a, b, c))
    return SurfaceMesh(tris, surface_error_mm=error)


QUARTER = math.tan(math.pi / 8)  # a quarter turn's bulge, tan(sweep / 4)


def rounded_rectangle(x0, y0, x1, y1, r):
    """A rectangle from (x0, y0) to (x1, y1), anticlockwise, its corners rounded to radius r."""
    if r == 0:
        return Boundary.polygon(((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
    return Boundary(((x0 + r, y0, 0), (x1 - r, y0, QUARTER), (x1, y0 + r, 0),
                     (x1, y1 - r, QUARTER), (x1 - r, y1, 0), (x0 + r, y1, QUARTER),
                     (x0, y1 - r, 0), (x0, y0 + r, QUARTER)))


def stadium(x0, x1, y, r):
    """The points within r of the segment from (x0, y) to (x1, y): a slot with round ends."""
    return Boundary(((x0, y - r, 0), (x1, y - r, 1), (x1, y + r, 0), (x0, y + r, 1)))


def setup(stock_min, stock_max, tools, operations, cell=0.25):
    """One setup: the stock box, the tools, the operations in order, and the tool starting where
    the bench's tool starts."""
    start = ((stock_min[0] + stock_max[0]) / 2, (stock_min[1] + stock_max[1]) / 2,
             stock_max[2] + START_ABOVE)
    return Setup("top", stock=StockSpec(min_mm=tuple(stock_min), max_mm=tuple(stock_max),
                                        cell_size_mm=cell),
                 tools=tuple(tools), operations=tuple(operations), initial_position_mm=start)


def _chords(curve):
    """An arc or helix outside the XY plane as points along it, its end last."""
    start, end, center = curve["start"], curve["end"], curve["center"]
    sweep, plane = curve["sweep_rad"], curve["plane"]
    u, v = {"xz": (2, 0), "yz": (1, 2)}[plane]  # camlib's oriented axes: Z,X about +Y; Y,Z
    w = 3 - u - v
    r = math.hypot(start[u] - center[u], start[v] - center[v])
    t0 = math.atan2(start[v] - center[v], start[u] - center[u])
    step = 2 * math.acos(max(-1.0, 1 - SAG / r)) if r > SAG else math.pi / 2
    n = max(1, math.ceil(abs(sweep) / step))
    pts = []
    for i in range(1, n):
        p = list(start)
        p[u] = center[u] + r * math.cos(t0 + sweep * i / n)
        p[v] = center[v] + r * math.sin(t0 + sweep * i / n)
        p[w] = start[w] + (end[w] - start[w]) * i / n
        pts.append(p)
    return pts + [list(end)]


def write(name, stock_min, stock_max, tools, rpm, operations, out):
    """Plan the operations and write their motion to `out` as a toolpath. `tools` are the
    assemblies, `rpm` each tool's spindle speed by its case number."""
    numbers = {t.id: int(t.id[1:]) for t in tools}
    job = Job(name, "1", (setup(stock_min, stock_max, tools, operations),))
    moves, state = [], {}
    with job.regenerate() as run:
        for item in run:
            update = item.update
            if isinstance(update, OperationUpdate) or not isinstance(
                    getattr(update, "motion", None), dict):
                continue
            m = update.motion
            number = numbers[m["tool"]]
            move = {}
            if state.get("tool") != number:
                move.update(tool=number, rpm=rpm[number])
            c = m["curve"]
            if m["kind"] == "rapid" and not m.get("feed_mm_min"):
                move["rapid"] = list(c["end"])
            else:
                if state.get("feed") != m["feed_mm_min"]:
                    move["feed"] = m["feed_mm_min"]
                if c["kind"] == "line":
                    move["line"] = list(c["end"])
                elif c.get("plane", "xy") == "xy":
                    move.update(arc=list(c["end"]), center=list(c["center"][:2]),
                                sweep=c["sweep_rad"])
                else:
                    move["line"] = _chords(c)
            state.update({k: move[k] for k in ("tool", "feed") if k in move})
            moves.append(move)
    with open(out, "w") as f:
        json.dump({"toolpath": 1, "moves": moves}, f, separators=(",", ":"))
