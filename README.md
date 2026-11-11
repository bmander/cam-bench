# cam-bench

Rosetta Code for CAM toolpath planners. Each case gives a part, the stock it is cut from and the
tools to cut it with. Each planner writes the case's program in its own language and idioms, and
the harness cuts the stock with every program the same way, so reading one case across the
planners shows how each is used and where each falls short.

It is [brep-bench](https://brepbench.org)'s sibling: there kernels build solids from words, here
planners cut them. Results: **[bmander.github.io/cam-bench](https://bmander.github.io/cam-bench/)**.

## Why

Toolpath planners are hard to compare. Each is judged by its own simulator, on its own parts,
often by eye. cam-bench is a shared yardstick: parts whose answers no planner chose, one
simulator and one set of rules for every program, and every planner in one table.

## Cases and grading

Twenty-four cases so far, three axes, flat and ball end mills: facing; pockets (round and
square corners, a round pocket, an island, a pocket in a pocket, slots, one exactly as wide as the
tool, a thin wall, a narrow gap, a field of pins, corners left for a smaller tool, a pocket deeper
than the flutes, a pocket open to the stock's side); profiles (a part cut out of a plate, a boss);
and surfaces (a dome, a half cylinder, a pocket with a rounded floor edge, a bowl, a drafted
pocket, a round groove, a fillet tighter than the ball). Each
part is a STEP and an STL beside its case, built with Open CASCADE from a short script, and each
case states its reachable volume in closed form where it has one.

A runner writes the case's program, in G-code or, for a CAM kernel, as a toolpath in the
bench's JSON format: rapids, lines and arcs, with the tool, feed and spindle speed. The harness
cuts the stock with it on a height map, each move's tool swept in closed form, and works out from
the part alone what the case's tools can reach. The program **passes** when it is valid and safe and leaves nowhere more than the
case's `leftover` above what the tools can reach. It is **unsafe** when it cuts into the part by
more than the case's `tolerance`, rapids through material, meets material with the shank or the
holder, or cuts faster than the tool's feeds; **incomplete** when it is safe but leaves material
the tools could have reached. **Refused** ranks above both. Its time on the machine, its length
through air, and the time and memory it took to plan are measured, not graded. The full rules are
in [SPEC.md](SPEC.md).

## Running it

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt   # numpy
.venv/bin/python harness/build.py     # set up every planner's runner
.venv/bin/python harness/run.py       # run every case: results/*.json
.venv/bin/python harness/site.py      # render the board: site/
python3 -m http.server -d site        # serve it
```

`harness/run.py --planner NAME --case pocket/` runs part of the suite, `harness/grade.py CASE
PROGRAM.nc` (or `TOOLPATH.json`) grades one program by hand, and `harness/run.py --regrade`
grades the last run's programs again after a change to the grading. `harness/parts.py` writes the
cases' STEP and STL from their scripts (it needs `cadquery-ocp`; grading needs only numpy). Each runner needs its
planner's own toolchain: opencamlib's Python wheels need Python 3.11 or earlier, so its runner
keeps a venv of its own.

A push to `main` runs the whole suite on GitHub Actions and publishes the board
(`.github/workflows/bench.yml`).

## Planners

Two CAM kernels so far: opencamlib, a library of tool placements (drop-cutter, waterline) that a
small helper of its implementations links into G-code; and camlib, a Rust engine with a Python
API whose own planned motion is written as the bench's toolpath (SPEC.md, "The toolpath").
Wanted: the CAM crates of vcad and next.BREP, the toolpath generators inside camcraft and
CamCraft, raygeo's adaptive clearing, and FreeCAD's CAM, Kiri:Moto and the commercial planners'
scripting interfaces.

## Contributing

- **A planner:** add `planners/<planner>/` with a runner (see [SPEC.md](SPEC.md#a-runner)) and as
  many implementations as you like, following [the rules](SPEC.md#an-implementation); add it to
  `planners.json`; and open a pull request. Where your planner can't do a case, add the file
  anyway and have it refuse, saying why.
- **A case:** add `cases/<category>/<name>.md`, its part's script `<name>.py`, and the `.step`
  and `.stl` that `harness/parts.py` writes from it. Hard cases are the most valuable, especially
  ones your own planner gets wrong.

## License

The harness, the cases and the implementations here are MIT OR Apache-2.0, at your option. Each
planner keeps its own license; an implementation only calls its planner and does not include it.
