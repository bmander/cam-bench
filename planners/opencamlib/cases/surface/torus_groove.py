"""Roughed with the flat tool's waterlines at 19 and 18, where it fits in the groove: two loops at
each, one on either wall, that between them clear the groove's width. Finished with the ball tool
dropped along circles round the groove's center line, 0.1 apart across it, from where the ball
touches the inner wall to where it touches the outer.

The raster that drops the tool on a grid over the whole ring is far slower here: the groove's
mesh is fine, and most of a raster's length runs over the flat top."""
import math

import opencamlib as ocl
from cam import Job, load

CENTER, RADIUS = (40, 40), 15


def circle(r, n=720):
    cx, cy = CENTER
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n + 1)]


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 80, 20))
    job.tool(1, ocl.CylCutter(6, 25), rpm=18000, feed=1200, plunge=300)
    for z in (19, 18):
        job.waterline(part, z + 0.001)
    job.tool(2, ocl.BallCutter(6, 35), rpm=18000, feed=1500, plunge=400)
    for i in range(21):
        job.follow(job.drop(part, circle(RADIUS - 1 + 0.1 * i), 16, sampling=0.25))
    job.write(out)
