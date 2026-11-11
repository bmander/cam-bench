"""Cut a case's stock with a program, on a height map, and grade what is left.

The stock, the part and every tool are seen from above, as heights over a square grid of cells
(the case's `resolution` apart), which is exact for three axes and tools that cut from below: a
cell's height is the top of the material over its center. The tools are a flat end mill (a
cylinder) and a ball end mill (a cylinder ending in a half ball). Each straight move sweeps its
tool from one end to the other; the lowest point of that sweep over each cell's center is found
in closed form (a disk swept along a line for the flat tool, a capsule for the ball), so a move
cuts exactly at the cells it passes over, however long it is.

What the case's tools can reach is found the same way, for comparison: for each tool, the lowest
its tip can go at every place without entering the part (dropped onto the part), and then the
lowest any of those placements can cut each cell (the part, opened by the tool). The case's
reference is the lowest over its tools. Needs numpy."""
import math
import os
import struct

import numpy as np

# how fast a rapid moves (mm/min), for a program's time; the bench's machine has no acceleration
RAPID = 5000.0
# how many cells' sweeps are found at once
CHUNK = 32
# the most material a move may touch and still count as touching none (mm)
EPS = 1e-6
# the most moves a problem lists by line
LISTED = 5


class Grid:
    """Square cells of side h over the stock's footprint, a cell's center at (x[i], y[j])."""

    def __init__(self, lo, hi, h):
        self.x0, self.y0 = lo[0], lo[1]
        self.nx = int(round((hi[0] - lo[0]) / h))
        self.ny = int(round((hi[1] - lo[1]) / h))
        if abs(self.nx * h - (hi[0] - lo[0])) > 1e-9 or abs(self.ny * h - (hi[1] - lo[1])) > 1e-9:
            raise ValueError(f"the stock is not a whole number of {h} cells")
        self.h = h
        self.x = lo[0] + (np.arange(self.nx) + 0.5) * h
        self.y = lo[1] + (np.arange(self.ny) + 0.5) * h

    def span(self, xlo, xhi, ylo, yhi):
        """The cells whose centers lie in the box: (i0, i1, j0, j1), half-open, or None."""
        i0 = max(0, int(math.ceil((xlo - self.x0) / self.h - 0.5)))
        i1 = min(self.nx, int(math.floor((xhi - self.x0) / self.h - 0.5)) + 1)
        j0 = max(0, int(math.ceil((ylo - self.y0) / self.h - 0.5)))
        j1 = min(self.ny, int(math.floor((yhi - self.y0) / self.h - 0.5)) + 1)
        return (i0, i1, j0, j1) if i0 < i1 and j0 < j1 else None


# ---------------------------------------------------------------------------------------- the part

def read_stl(path):
    """An STL file's triangles, an array (n, 3, 3)."""
    with open(path, "rb") as f:
        data = f.read()
    if len(data) >= 84:
        n = struct.unpack_from("<I", data, 80)[0]
        if 84 + 50 * n == len(data):
            rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)),
                                                      ("a", "<u2")]), count=n, offset=84)
            return rec["v"].astype(np.float64)
    vs = [tuple(map(float, l.split()[1:4])) for l in data.decode("ascii", "replace").splitlines()
          if l.strip().startswith("vertex")]
    return np.array(vs, dtype=np.float64).reshape(-1, 3, 3)


def heights(tris, grid, floor):
    """The part's top over each cell's center: the highest triangle over it, else `floor`."""
    top = np.full((grid.ny, grid.nx), -np.inf)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    area = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])
    for t in np.nonzero(np.abs(area) > 1e-12)[0]:
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tris[t]
        s = grid.span(min(ax, bx, cx), max(ax, bx, cx), min(ay, by, cy), max(ay, by, cy))
        if s is None:
            continue
        i0, i1, j0, j1 = s
        X, Y = np.meshgrid(grid.x[i0:i1], grid.y[j0:j1])
        d = area[t]
        u = ((bx - X) * (cy - Y) - (cx - X) * (by - Y)) / d
        v = ((cx - X) * (ay - Y) - (ax - X) * (cy - Y)) / d
        w = 1 - u - v
        inside = (u >= -1e-9) & (v >= -1e-9) & (w >= -1e-9)
        if inside.any():
            z = u * az + v * bz + w * cz
            block = top[j0:j1, i0:i1]
            np.maximum(block, np.where(inside, z, -np.inf), out=block)
    return np.where(np.isfinite(top), top, floor)


# ------------------------------------------------------------------------------------ the reference

def profile(tool, d):
    """How far above the tip the tool's surface is at distance d from its axis."""
    r = tool["diameter"] / 2
    if tool["shape"] == "flat":
        return np.zeros_like(d)
    return r - np.sqrt(np.maximum(r * r - d * d, 0.0))


def _window(a, w, axis, op):
    """op (np.maximum or np.minimum) over a window of 2w + 1 along `axis`, centered: the result is
    2w shorter along it."""
    n = 2 * w + 1
    a = np.moveaxis(a, axis, -1)
    out, length = a, 1
    while length * 2 <= n:
        out = op(out[..., :-length], out[..., length:])
        length *= 2
    # out[i] covers [i, i + length); two of them cover any window of n <= 2 * length
    out = op(out[..., :out.shape[-1] - (n - length)], out[..., n - length:])
    return np.moveaxis(out, -1, axis)


def opened(part, tool, h, floor):
    """The lowest the tool can cut each cell without entering the part: the part opened by the
    tool, on the grid. Tool placements range over the cells' centers, and past the stock's edges
    by the tool's radius, where there is no part."""
    r = tool["diameter"] / 2
    n = int(math.floor(r / h + 1e-9))
    ny, nx = part.shape
    big = np.pad(part, 2 * n, constant_values=floor)  # (ny + 4n, nx + 4n)
    rows = range(-n, n + 1)
    if tool["shape"] == "flat":
        # a disk's max is each row's window max, over the rows
        top = np.full((ny + 2 * n, nx + 2 * n), -np.inf)
        for dj in rows:
            w = int(math.floor(math.sqrt(max(r * r - (dj * h) ** 2, 0.0)) / h + 1e-9))
            band = big[n + dj:n + dj + ny + 2 * n, n - w:n - w + nx + 2 * n + 2 * w]
            np.maximum(top, _window(band, w, 1, np.maximum), out=top)
        low = np.full((ny, nx), np.inf)
        for dj in rows:
            w = int(math.floor(math.sqrt(max(r * r - (dj * h) ** 2, 0.0)) / h + 1e-9))
            band = top[n - dj:n - dj + ny, n - w:n - w + nx + 2 * w]
            np.minimum(low, _window(band, w, 1, np.minimum), out=low)
        return low
    offsets = [(dj, di) for dj in rows for di in rows if (dj * dj + di * di) * h * h <= r * r + 1e-9]
    f = {o: float(profile(tool, np.array(h * math.hypot(*o)))) for o in offsets}
    top = np.full((ny + 2 * n, nx + 2 * n), -np.inf)
    for (dj, di) in offsets:
        np.maximum(top, big[n + dj:n + dj + ny + 2 * n, n + di:n + di + nx + 2 * n] - f[(dj, di)],
                   out=top)
    low = np.full((ny, nx), np.inf)
    for (dj, di) in offsets:
        np.minimum(low, top[n - dj:n - dj + ny, n - di:n - di + nx] + f[(dj, di)], out=low)
    return low


def reference(case, part):
    """The lowest any of the case's tools can cut each cell, and each tool's own."""
    floor = case["stock"]["min"][2]
    each = {t["number"]: opened(part, t, case["resolution"], floor) for t in case["tools"]}
    return np.minimum.reduce(list(each.values())), each


# -------------------------------------------------------------------------------------- the sweeps

def sweep_flat(a, b, r, X, Y, entry=False):
    """The lowest point of a flat tool of radius r, its tip moved from each a to each b (k, 3),
    over each point (X, Y) (m): an array (k, m), inf where it does not pass over. With `entry`,
    instead the height of the tip when the tool first comes over the point."""
    ax, ay, az = a[:, 0:1], a[:, 1:2], a[:, 2:3]
    vx, vy, dz = b[:, 0:1] - ax, b[:, 1:2] - ay, b[:, 2:3] - az
    dx, dy = X[None, :] - ax, Y[None, :] - ay
    qa = vx * vx + vy * vy
    qb = dx * vx + dy * vy
    qc = dx * dx + dy * dy - r * r
    moving = qa > 1e-18
    sa = np.where(moving, qa, 1.0)
    disc = qb * qb - sa * qc
    root = np.sqrt(np.maximum(disc, 0.0))
    t1 = np.clip((qb - root) / sa, 0.0, 1.0)
    t2 = np.clip((qb + root) / sa, 0.0, 1.0)
    over = (disc >= 0) & ((qb + root) / sa >= 0) & ((qb - root) / sa <= 1)
    low = az + t1 * dz if entry else np.minimum(az + t1 * dz, az + t2 * dz)
    still = (az if entry else np.minimum(az, az + dz)) + np.zeros_like(qc)
    return np.where(moving, np.where(over, low, np.inf), np.where(qc <= 0, still, np.inf))


def sweep_ball(a, b, r, X, Y):
    """As sweep_flat, for a ball tool of radius r: the lowest point of the capsule its ball's
    center sweeps, less r."""
    out = np.full((a.shape[0], X.shape[0]), np.inf)
    for c in (a, b):
        d2 = (X[None, :] - c[:, 0:1]) ** 2 + (Y[None, :] - c[:, 1:2]) ** 2
        s = c[:, 2:3] + r - np.sqrt(np.maximum(r * r - d2, 0.0))
        np.minimum(out, np.where(d2 <= r * r, s, np.inf), out=out)
    vx, vy, dz = b[:, 0:1] - a[:, 0:1], b[:, 1:2] - a[:, 1:2], b[:, 2:3] - a[:, 2:3]
    m = vx * vx + vy * vy + dz * dz
    alpha = (vx * vx + vy * vy) / np.where(m > 0, m, 1.0)
    ok = alpha > 1e-12
    if ok.any():
        sm = np.where(ok, m, 1.0)
        sal = np.where(ok, alpha, 1.0)
        dx, dy = X[None, :] - a[:, 0:1], Y[None, :] - a[:, 1:2]
        k = dx * vx + dy * vy
        beta = -k * dz / sm
        gamma = dx * dx + dy * dy - k * k / sm - r * r
        disc = beta * beta - sal * gamma
        e = (-beta - np.sqrt(np.maximum(disc, 0.0))) / sal
        t = (k + e * dz) / sm
        valid = ok & (disc >= 0) & (t >= 0) & (t <= 1)
        np.minimum(out, np.where(valid, a[:, 2:3] + r + e, np.inf), out=out)
    return out


def sweep(tool, a, b, X, Y, shrink=0.0):
    """The lowest point of `tool` swept from a to b over (X, Y); with `shrink`, of the tool less
    every point within `shrink` of its surface (how a gouge is told from a touch)."""
    r = tool["diameter"] / 2 - shrink
    lift = np.array([0.0, 0.0, shrink])
    fn = sweep_flat if tool["shape"] == "flat" else sweep_ball
    return fn(a + lift, b + lift, r, X, Y)


# ---------------------------------------------------------------------------------------- the cut

class Problems:
    """What a program did wrong, by kind: how often, the worst amount, and the first lines."""

    def __init__(self):
        self.kinds = {}

    def add(self, kind, line, amount=0.0, where=None):
        k = self.kinds.setdefault(kind, {"count": 0, "worst": 0.0, "lines": [], "where": None})
        k["count"] += 1
        if amount > k["worst"] or k["where"] is None:
            k["worst"], k["where"] = max(k["worst"], amount), where
        if len(k["lines"]) < LISTED and line not in k["lines"]:
            k["lines"].append(line)


UNSAFE = {
    "gouge": "cuts into the part",
    "rapid": "rapids through material",
    "shank": "the tool's shank meets material above its flutes",
    "holder": "the holder meets material",
    "spindle": "cuts with the spindle stopped",
    "feed": "cuts faster than the tool's feed",
    "plunge": "goes down into material faster than the tool's plunge",
}


def plunges(move, took, X, Y, tool, h):
    """Whether a move that goes down cuts deep under the tool's axis: deeper than a quarter of the
    tool's diameter at the cells within a quarter of its radius of the axis's path (or the
    nearest cell, for a narrow tool). That is a plunge, a ramp or a helix into solid material,
    which its plunge feed limits; a light cut down a surface, finishing, is fed as any cut."""
    r = tool["diameter"] / 2
    core = max(r / 4, h * 0.71)
    (ax, ay, _), (bx, by, _) = move.a, move.b
    vx, vy = bx - ax, by - ay
    n = vx * vx + vy * vy
    t = np.clip(((X - ax) * vx + (Y - ay) * vy) / n, 0, 1) if n > 0 else 0.0
    near = np.hypot(X - (ax + t * vx), Y - (ay + t * vy)) <= core
    return bool(near.any()) and float(took[near].max()) > tool["diameter"] / 4


def simulate(case, moves, part, gouge_floor):
    """Cut the stock with the moves. Returns the stock left (heights), the problems, and what the
    program measures (lengths, time, volume, tools)."""
    lo, hi, h = case["stock"]["min"], case["stock"]["max"], case["resolution"]
    grid = Grid(lo, hi, h)
    stock = np.full((grid.ny, grid.nx), hi[2])
    tools = {t["number"]: t for t in case["tools"]}
    tol = case["tolerance"]
    probs = Problems()
    m = {"moves": len(moves), "feed_length": 0.0, "rapid_length": 0.0, "air_length": 0.0,
         "time": 0.0, "tool_changes": 0, "removed": 0.0, "max_depth": {}, "tools": []}
    cell = h * h

    last_tool = None
    i = 0
    while i < len(moves):
        mv = moves[i]
        if mv.tool != last_tool and mv.tool is not None:
            m["tool_changes"] += 1
            last_tool = mv.tool
            if mv.tool not in m["tools"]:
                m["tools"].append(mv.tool)
        # a chunk: consecutive moves of one kind and tool
        j = i + 1
        while (j < len(moves) and j - i < CHUNK and moves[j].kind == mv.kind
               and moves[j].tool == mv.tool):
            j += 1
        chunk = moves[i:j]
        i = j
        a = np.array([c.a for c in chunk])
        b = np.array([c.b for c in chunk])
        lengths = np.linalg.norm(b - a, axis=1)
        for c, length in zip(chunk, lengths):
            if c.kind == "rapid":
                m["rapid_length"] += length
                m["time"] += length / RAPID * 60
            else:
                m["feed_length"] += length
                m["time"] += length / c.feed * 60
        tool = tools.get(mv.tool)
        if tool is None:
            continue  # nothing loaded: a rapid before the first tool change moves no tool
        r = tool["diameter"] / 2
        tip_low = min(a[:, 2].min(), b[:, 2].min())
        xlo, xhi = min(a[:, 0].min(), b[:, 0].min()), max(a[:, 0].max(), b[:, 0].max())
        ylo, yhi = min(a[:, 1].min(), b[:, 1].min()), max(a[:, 1].max(), b[:, 1].max())

        def around(rad):
            return grid.span(xlo - rad, xhi + rad, ylo - rad, yhi + rad)

        # the parts of the tool that cut nothing, which may meet material only where it stands
        # higher than their bottom within their reach: the shank above the flutes, the holder
        # above the tool's length
        bodies = []
        for kind, rad, height in (("shank", tool["shank"] / 2, tool["flute"]),
                                  ("holder", tool.get("holder", tool["shank"]) / 2,
                                   tool["length"])):
            sp = around(rad)
            if sp and tip_low + height < stock[sp[2]:sp[3], sp[0]:sp[1]].max() - tol:
                bodies.append((kind, rad, height))
        span = around(max([r] + [rad for _, rad, _ in bodies]))
        if span is None:
            if mv.kind == "feed":
                m["air_length"] += float(lengths.sum())
            continue
        i0, i1, j0, j1 = span
        block = stock[j0:j1, i0:i1]
        s = block.ravel().copy()
        cutting = tip_low < s.max()
        if not cutting and not bodies:
            if mv.kind == "feed":
                m["air_length"] += float(lengths.sum())
            continue  # the whole chunk passes above the material
        X, Y = np.meshgrid(grid.x[i0:i1], grid.y[j0:j1])
        X, Y = X.ravel(), Y.ravel()
        cuts = None
        if cutting:
            cuts = sweep(tool, a, b, X, Y)
            pg = gouge_floor[j0:j1, i0:i1].ravel()
            if (cuts < pg).any():
                worse = sweep(tool, a, b, X, Y, shrink=tol)
                for k in np.nonzero((worse < pg[None, :]).any(axis=1))[0]:
                    deep = pg - worse[k] + tol
                    at = int(np.argmax(deep))
                    probs.add("gouge", chunk[k].line, float(deep[at]),
                              (float(X[at]), float(Y[at])))
        # a body meets material where it stands above the body's bottom when the tool first
        # comes over it: what the flutes reach as the tool goes on, they cut first
        lows = [(kind, sweep_flat(a, b, rad, X, Y, entry=True) + height)
                for kind, rad, height in bodies]
        for k, c in enumerate(chunk):
            # against the material as it stands before this move
            for kind, low in lows:
                over = s - low[k]
                if (over > tol).any():
                    at = int(np.argmax(over))
                    probs.add(kind, c.line, float(over[at]), (float(X[at]), float(Y[at])))
            took = s - cuts[k] if cuts is not None else None
            if took is None or not (took > EPS).any():
                if c.kind == "feed":
                    m["air_length"] += lengths[k]
                continue
            hit = took > EPS
            if c.kind == "rapid":
                if took.max() > tol:
                    at = int(np.argmax(took))
                    probs.add("rapid", c.line, float(took[at]), (float(X[at]), float(Y[at])))
            else:
                if not c.spindle:
                    probs.add("spindle", c.line)
                if c.feed > tool["feed"] * (1 + 1e-9):
                    probs.add("feed", c.line, c.feed - tool["feed"])
                down = (c.a[2] - c.b[2]) / lengths[k] * c.feed if lengths[k] > 0 else 0
                if down > tool["plunge"] * (1 + 1e-9) and plunges(c, took, X, Y, tool, h):
                    probs.add("plunge", c.line, down - tool["plunge"])
            key = str(mv.tool)
            m["max_depth"][key] = max(m["max_depth"].get(key, 0.0), float(took.max()))
            m["removed"] += float(took[hit].sum()) * cell
            np.minimum(s, cuts[k], out=s)
        block[...] = s.reshape(block.shape)
    return grid, stock, probs, m


def dilated(a):
    """Each cell's highest neighbour, itself included (3 by 3)."""
    p = np.pad(a, 1, mode="edge")
    ny, nx = a.shape
    return np.maximum.reduce([p[dj:dj + ny, di:di + nx] for dj in range(3) for di in range(3)])


def leftover(case, stock, ref):
    """Material standing above what the tools can reach by more than the case's `leftover`: a
    cell's allowance is the highest reference among its neighbours, so that a wall does not count
    against a cut that stops a fraction of a cell short of it. Returns the excess at each cell."""
    allowed = dilated(np.minimum(ref, case["stock"]["max"][2])) + case["leftover"]
    return np.maximum(stock - allowed, 0.0)


def cache_key(case):
    """What the reference depends on, for its cache."""
    with open(case["part"] + ".stl", "rb") as f:
        stl = f.read()
    import hashlib
    sig = repr((case["stock"], case["tools"], case["resolution"])).encode()
    with open(os.path.abspath(__file__), "rb") as f:
        code = f.read()
    return hashlib.sha256(stl + sig + code).hexdigest()[:20]
