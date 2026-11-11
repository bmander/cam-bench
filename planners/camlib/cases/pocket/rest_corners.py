"""The pocket and its slot as one camlib region; the 12 mm tool clears what it can by Pocket,
then the 4 mm tool, by RestPocket, cuts only what camlib's model of the stock shows it left: the
corners and the slot."""
from camlib.operations import HelicalEntry, Pocket, RestPocket
from camlib.planar import Boundary, Component, PlanarRegion

from bench import QUARTER, cutting, tool, write


def outline():
    """The pocket's rectangle, corners rounded to 2, with the slot running out of its right
    wall and ending in a half disk of radius 2.5: anticlockwise from the bottom left."""
    return Boundary(((12, 10, 0), (68, 10, QUARTER), (70, 12, 0), (70, 27.5, 0),
                     (79.5, 27.5, 1), (79.5, 32.5, 0), (70, 32.5, 0), (70, 48, QUARTER),
                     (68, 50, 0), (12, 50, QUARTER), (10, 48, 0), (10, 12, QUARTER)))


def make(stl, out):
    t1 = tool(1, "flat", 12, flute=25, length=40, holder=35)
    t2 = tool(2, "flat", 4, flute=12, length=20, holder=25)
    region = PlanarRegion("pocket", (Component(outline()),))
    heights = dict(top_z_mm=20, floor_z_mm=10, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5)
    ops = [Pocket("rough", t1, region, stepdown_mm=2.5, stepover_mm=5, entry=HelicalEntry(),
                  **heights, **cutting(1, rpm=12000, feed=2000, plunge=500)),
           RestPocket("rest", t2, region, stepdown_mm=2.5, stepover_mm=1.8, entry=HelicalEntry(),
                      **heights, **cutting(2, rpm=20000, feed=900, plunge=200))]
    write("rest-corners", (0, 0, 0), (90, 60, 20), [t1, t2], {1: 12000, 2: 20000}, ops, out)
