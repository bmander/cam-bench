"""What the opencamlib implementations share: opencamlib computes where a tool may be (drop-cutter
along a path, waterline around a part at a height); this writes those places as G-code, and
links them the way a user of the library would: rasters at falling levels to clear material, a
waterline at each level to finish the walls, and rasters of a ball tool to finish a surface."""
import math

import opencamlib as ocl

# above the stock, where the tool moves between passes
CLEAR = 3.0


def load(stl):
    surf = ocl.STLSurf()
    ocl.STLReader(stl, surf)
    return surf


def levels(top, bottom, step):
    """Heights from just under `top` down to `bottom`, no more than `step` apart."""
    n = max(1, math.ceil((top - bottom) / step - 1e-9))
    return [top - (top - bottom) * (i + 1) / n for i in range(n)]


def straight(points, tol=1e-5):
    """The points without those that lie on the line between their neighbours."""
    out = [points[0]]
    for i in range(1, len(points) - 1):
        a, b, c = out[-1], points[i], points[i + 1]
        ab = [b[k] - a[k] for k in range(3)]
        ac = [c[k] - a[k] for k in range(3)]
        n = math.sqrt(sum(v * v for v in ac))
        if n == 0:
            continue
        t = sum(ab[k] * ac[k] for k in range(3)) / (n * n)
        off = math.sqrt(sum((ab[k] - t * ac[k]) ** 2 for k in range(3)))
        if not (0 <= t <= 1 and off <= tol):
            out.append(b)
    out.append(points[-1])
    return out


class Job:
    """A program being written: one stock, tools loaded by number, moves fed no faster than the
    tool allows (and, going down, no faster than its plunge)."""

    def __init__(self, stock_min, stock_max):
        self.lo, self.hi = stock_min, stock_max
        self.safe = stock_max[2] + CLEAR
        self.lines = ["(opencamlib)", "G21 G90 G17", "G0 Z%.4f" % (self.safe + 20)]
        self.pos = None
        self.cutter = None

    def tool(self, number, cutter, rpm, feed, plunge):
        self.cutter, self.feed, self.plunge = cutter, feed, plunge
        self.radius = cutter.getDiameter() / 2
        self.lines += ["T%d M6" % number, "S%d M3" % rpm, "G0 Z%.4f" % self.safe]
        self.pos = None

    def _to(self, p, rapid=False):
        # the place as written, to 4 places, from which the feed is worked out
        x, y, z = (float("%.4f" % v) for v in p)
        if rapid:
            self.lines.append("G0 X%.4f Y%.4f Z%.4f" % (x, y, z))
        else:
            a = self.pos
            d = math.dist(a, (x, y, z)) if a else 0
            f = self.feed
            if a and d > 0 and z < a[2]:
                f = min(f, self.plunge * d / (a[2] - z))
            # written to 0.1, rounded down
            self.lines.append("G1 X%.4f Y%.4f Z%.4f F%.1f" % (x, y, z, math.floor(f * 10) / 10))
        self.pos = (x, y, z)

    def follow(self, points):
        """Cut along the points: from above the stock to the first, and back above it after."""
        points = straight(points)
        x, y, z = points[0]
        self._to((x, y, self.safe), rapid=True)
        for p in points:
            self._to(p)
        self._to((self.pos[0], self.pos[1], self.safe), rapid=True)

    def drop(self, surf, path, z, sampling=0.1):
        """The places along a polyline (x, y pairs) where the tool, dropped, first meets the
        part, but no lower than z."""
        p = ocl.Path()
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            p.append(ocl.Line(ocl.Point(x0, y0, z), ocl.Point(x1, y1, z)))
        dc = ocl.AdaptivePathDropCutter()
        dc.setSTL(surf)
        dc.setCutter(self.cutter)
        dc.setPath(p)
        dc.setZ(z)
        dc.setSampling(sampling)
        dc.setMinSampling(sampling / 20)
        dc.run()
        return [(q.x, q.y, q.z) for q in dc.getCLPoints()]

    def raster(self, surf, z, stepover, region=None, along="x", sampling=0.1):
        """A zigzag over the region (x0, y0, x1, y1) of tool centers, by default the stock and
        a tool's radius past it, its lines along x (or y) `stepover` apart, dropped onto the
        part and no lower than z."""
        if region is None:
            m = self.radius + 0.5
            region = (self.lo[0] - m, self.lo[1] - m, self.hi[0] + m, self.hi[1] + m)
        x0, y0, x1, y1 = region
        if along == "y":
            x0, y0, x1, y1 = y0, x0, y1, x1
        n = max(1, math.ceil((y1 - y0) / stepover - 1e-9))
        path = []
        for i in range(n + 1):
            y = y0 + (y1 - y0) * i / n
            ends = [(x0, y), (x1, y)] if i % 2 == 0 else [(x1, y), (x0, y)]
            path += ends
        if along == "y":
            path = [(b, a) for a, b in path]
        self.follow(self.drop(surf, path, z, sampling))

    def waterline(self, surf, z, sampling=0.1):
        """Around the part at height z, every loop the tool can follow touching it, but the loop
        around the outside of the whole stock, which cuts nothing."""
        w = ocl.Waterline()
        w.setSTL(surf)
        w.setCutter(self.cutter)
        w.setZ(z)
        w.setSampling(sampling)
        w.run()
        for loop in w.getLoops():
            pts = [(q.x, q.y, q.z) for q in loop]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if not (min(xs) <= self.lo[0] and max(xs) >= self.hi[0]
                    and min(ys) <= self.lo[1] and max(ys) >= self.hi[1]):
                self.follow(pts + pts[:1])

    def clear(self, surf, top, bottom, stepdown, stepover, region=None, floor=None):
        """Clear down to `bottom` (or to the part, where it is higher) in levels: at each, a
        raster, then a waterline to finish the walls just above it (or above `floor`, if
        the level is under the part's lowest face)."""
        for z in levels(top, bottom, stepdown):
            self.raster(surf, z, stepover, region)
            self.waterline(surf, max(z, floor if floor is not None else z) + 0.001)

    def write(self, out):
        self.lines += ["G0 Z%.4f" % (self.safe + 20), "M5", "M30"]
        with open(out, "w") as f:
            f.write("\n".join(self.lines) + "\n")
