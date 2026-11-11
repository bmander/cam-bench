# cam-bench specification, version 0.3

cam-bench works like Rosetta Code, as [brep-bench](https://brepbench.org) does for B-rep kernels.
Each **case** gives a part, the stock it is cut from and the tools to cut it with. Each
**planner** has its own **implementation** of each case, written the way that planner's users
write: in its own language, with its own operations and idioms. A planner is a CAM kernel (a
library that takes geometry and tools and plans the tool's path) or a whole CAM program. A
**runner** has the planner write the case's **program**: in G-code, or, for a kernel, in the
bench's **toolpath** format, the path itself before any post-processor writes it for a
controller. The **harness** cuts the stock with every program the same way and grades what is
left.

## Principles

- **No canonical program.** A case is a part and a setup, not a sequence of operations. No
  strategy is privileged: a planner may clear in levels or adaptively, finish by waterline or by
  raster, and enter by ramp, helix or plunge. Reading one case's implementations side by side
  shows how each planner is used.
- **Neutral answers.** Every program is graded by the harness alone, against the part, never
  against another planner's program. What a case's tools can reach is found by the harness from
  the part and the tools (below), and, where it has one, checked against a closed form written in
  the case: the closed forms check the harness, not the planners.
- **Right before fast.** A program is graded on whether it is right and safe. What it costs (its
  time on the machine, its length, the material it cuts through air, the time and memory it took
  to plan) is measured and shown, never graded.
- **A refusal ranks above a wrong program.** A planner that says "I cannot" is more useful than
  one that writes a program that cuts into the part. A case with no implementation yet is
  *missing*, which is neither.
- **The same rules for every planner.** The rules change only by a versioned edit to this file,
  made before any results under the new rules are published.

## A case

A case is a Markdown file, `cases/<category>/<name>.md`, beside its part. Its id is the path
without the extension, for example `pocket/island`. A TOML header between `+++` lines holds the
setup; the text after it describes the part in words.

```
+++
title = "A pocket around a round island"
tags = ["2.5d", "pocket", "island"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [80, 60, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 6
flute = 15
length = 25
holder = 30
feed = 1200
plunge = 300
rpm = 18000

[removed]
value = 17419.823092079983
exact = "(60·40 − (4 − π)·5² − π·8²)·8 = 18400 − 312π"
tex = '\left(60\cdot 40 - (4 - \pi)\cdot 5^2 - \pi\cdot 8^2\right)\cdot 8 = 18400 - 312\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a pocket in its
top, …
```

The header's fields:

| field | meaning |
|---|---|
| `stock` | the stock, a box from `min` to `max`, sitting on the table (or a spoilboard) at its `min` z |
| `tools` | the tools a program may use, by `number`: `shape` (`flat` or `ball`), `diameter`, `flute` (the length of its cutting edges, from the tip), `length` (how far it stands out of its holder), `shank` (its diameter above the flutes; the diameter if not given), `holder` (the holder's diameter), and the most it may be fed when cutting, `feed`, and moving down into material, `plunge`, both in mm/min, and its `rpm` |
| `tolerance` | how far a tool may enter the part (default 0.01) |
| `leftover` | how much material may stand above what the tools can reach (default 0.02) |
| `spoilboard` | how far below the stock's bottom a tool may cut outside the part (default 0) |
| `resolution` | the side of the harness's cells (default 0.1) |
| `removed` | the volume the tools can reach, as a closed form, where there is one (`exact`, and in LaTeX, `tex`) |
| `material` | what the stock is, for feeds and speeds; not graded |

Lengths are in millimetres. Coordinates are right-handed x, y, z, with z up; the machine has three
axes, and its tools point down.

The part is `cases/<category>/<name>.step` and `.stl`, written by `harness/parts.py` from
`<name>.py`, which builds it with Open CASCADE; the STL is meshed to within 0.002 of the solid.
The part lies inside the stock. A planner reads either file. The description says what the part
is, in words, so that a reader knows what is being cut, and says where a tool cannot reach.

A case is a part whose material **every tool can reach from above**: what one of its tools cannot
reach is left, and the reference allows for it, but no case asks for an undercut. Its tools'
flutes and holders are long enough for its depths, so that the reference (which knows nothing of
flutes and holders) is what a careful program can do.

## An implementation

Each planner lives in `planners/<planner>/`, listed in `planners.json`. The directory holds a
runner and one source file per case, at the planner's `source` pattern, for example
`planners/opencamlib/cases/{category}/{name_snake}.py` (`{case}`, `{category}`, `{name}` and
`{name_snake}` as in brep-bench).

An implementation sets up the case and has the planner write its program the way a user of the
planner would: it chooses the operations, their order and their parameters (stepdown, stepover,
entries, links, feeds within the tools' limits).

- **It may** use anything in the planner's public API or the operations of its user interface,
  as a script; read the part from its STEP or STL file; and state the stock and tools as a user
  types them in. A small helper module shared by one planner's implementations is fine. Each case
  file should still read as an example of the planner's use.
- **It may give the part in the planner's own terms,** where the planner takes those rather than
  a solid: a pocket as the outline and the depth a 2.5D operation clears, a wall as the contour
  it follows. Such geometry is stated from the case's description, as a user draws it, and may
  approximate the part no more than the case's `tolerance`. The program is still graded against
  the part's own files, so a region drawn wrong is a program that gouges or leaves material.
- **The moves between operations are the program's.** Where a kernel plans each operation's
  cuts but not the moves that join them (retracts, rapids, entries), the implementation's helper
  joins them in the plainest way (straight up to a safe height, across, and down at the plunge
  feed), and the helper says so. Those moves are graded like any other: a rapid that crosses
  material is unsafe whoever planned it.
- **It may not:**
  - compute tool placements outside the planner (no hand-made toolpaths);
  - read the harness's reference, or grade itself against it;
  - patch the planner;
  - catch a crash and report it as a refusal;
  - work around the grading.
- **A post-processor is part of the planner.** The program is written by the planner's own
  output, to G-code or to the toolpath format, or by a post-processor for either written in the
  planner's own way of writing one. It may translate, not plan: it may not add, move or drop
  moves beyond what the format requires (an arc in a plane other than XY, which neither format
  carries, becomes chords within 0.0005 of it).
- **A case the planner cannot do** still has a file, which refuses, saying precisely why.
- **A case with no file is missing.**

## A runner

The harness runs a planner's `command` from `planners.json` once per case:

```
<command> CASE OUT
```

`CASE` is the case's id. The runner writes the case's program to the file `OUT` and prints one
line of JSON as the last line of its standard output:

```json
{"status": "ok"}
```

for a program in G-code, or, for one in the toolpath format,

```json
{"status": "ok", "format": "toolpath"}
```

or, when the implementation refuses or the planner declines:

```json
{"status": "refused", "reason": "…"}
```

A runner must also answer `--version` with one line naming the planner and its version, and,
given a case id it has no implementation of, exit without planning anything (the harness times
that, as what starting the runner costs).

## The program

A program is G-code (RS-274) for a three-axis mill, in the case's frame and in millimetres. The
tool starts 50 above the middle of the stock's top. The harness reads:

- **motion:** `G0` (rapid), `G1` (feed), `G2` and `G3` (arcs in the XY plane, by `I J` from the
  start, or by `R`; with a Z, a helix), and the drilling cycles `G81`, `G82`, `G83` and `G73` (to
  the hole, to `R`, down to `Z`, and back to the start's height after `G98` or to `R` after
  `G99`, and to the higher of that and `R`), their `R` and `Z` holding from hole to hole until
  `G80` cancels them;
- **modes:** `G90` and `G91` (absolute and incremental), `G90.1` and `G91.1` (arc centers
  absolute or from the start, the default), `G21` and `G20` (millimetres, the default, or
  inches), `G17`, `G94`; `G40`, `G49`, `G43`, `G54`–`G59`, `G61`, `G64` and `G4` are read and do
  nothing: every position is the tool's tip, in the case's frame;
- **the rest:** `F` (feed, per minute), `S`, `T` and `M6` (choose and load a tool), `M3`, `M4`
  and `M5` (the spindle), `M7`, `M8`, `M9`, `M0`, `M1`, and `M2` or `M30` (the end), `N` line
  numbers, `H` (with `G43`), and comments in `( )` or after `;`.

Anything else (any other letter, cutter compensation `G41`/`G42`, machine coordinates
`G28`/`G30`/`G53`, arcs in another plane) makes the program *invalid*: the planner must give the
tool's path itself.

## The toolpath

A toolpath is the same program as data: what a CAM kernel plans, before a post-processor writes
it for a controller. It is a JSON object:

```json
{"toolpath": 1,
 "moves": [
   {"tool": 1, "rpm": 18000},
   {"rapid": [10, 10, 25]},
   {"line": [10, 10, 18], "feed": 300},
   {"line": [[40, 10, 18], [40, 30, 18], [10, 30, 18]], "feed": 1200},
   {"arc": [15, 30, 16], "center": [10, 30], "sweep": 6.283185307179586},
   {"rapid": [15, 30, 25]}
 ]}
```

`"toolpath": 1` names the format's version. Its `moves` are done in order, each from where the
last ended; the tool starts where a G-code program's does, 50 above the middle of the stock's
top. A move is an object with at most one motion:

- **`rapid`**: a point `[x, y, z]`, or a list of them, reached in straight lines at the machine's
  rapid rate;
- **`line`**: a point or a list of points, reached in straight lines at the feed;
- **`arc`**: the end point, about `center` (`[x, y]`) in the XY plane through `sweep` radians,
  anticlockwise seen from above where positive; z changes evenly along it, a helix where the
  end's z differs from the start's. A full turn is a sweep of 2π back to the start, and several
  turns a larger one. The end must lie on the circle, within 0.002 of where the sweep ends.

And the state the moves cut with, which holds until a move changes it:

- **`tool`**: the case's number of the tool in the spindle (a change of tool is a change of this);
- **`rpm`**: the spindle's speed, 0 when it is stopped (the start);
- **`feed`**: the feed of lines and arcs, in mm/min.

A move with no motion only changes the state. Points are the tool's tip, in the case's frame, in
millimetres. Any other key, a cut with no tool or feed, or an arc whose end is not on its circle
makes the toolpath *invalid*. A toolpath is graded exactly as a G-code program is.

## Grading

The harness cuts the stock with the program on a height map: a square grid of cells, the case's
`resolution` apart, each holding the top of the material over its center. That is exact for three
axes and tools that cut from below. Each straight move sweeps its tool, a cylinder (flat) or a
cylinder ending in a half ball (ball), from one end to the other; the lowest point of the sweep
over each cell's center is found in closed form, so a move cuts exactly at every cell it passes
over, however long it is. Arcs are cut into chords that stray no more than 0.0005 from them.

**What the tools can reach** is found the same way: for each tool, the lowest its tip can go at
every place without entering the part, and then the lowest any of those placements cuts each cell
(the part *opened* by the tool), the lowest over the case's tools. Where the case has a closed
form for the volume this removes, `harness/parts.py` and the board show the harness's own beside
it.

Each program gets one outcome. The outcomes, best first:

| outcome | when |
|---|---|
| **pass** | the program is valid and safe, and nowhere leaves more than `leftover` above what the tools can reach |
| **refused** | the runner answered `refused` |
| **incomplete** | the program is valid and safe, but leaves more than `leftover` above what the tools can reach somewhere |
| **unsafe** | some move cuts into the part by more than `tolerance`; or rapids through material; or meets material with the tool's shank, above its flutes, or with its holder; or cuts with the spindle stopped; or cuts faster than its tool's `feed`, or moves down through material faster than its `plunge` |
| **invalid** | the harness cannot read the program, or it uses a tool the case does not have |
| **crashed** | the runner exited non-zero, or printed no JSON |
| **timeout** | it ran past the time limit (600 s by default) |
| **missing** | the planner has no implementation of the case; not ranked |

Each is decided as follows:

- **Cutting into the part.** A move gouges where the tool, less every point within `tolerance`
  of its surface, passes below the part's top at a cell's center (or, outside the part, below
  the spoilboard's allowance). A cut that touches the part, or skims it within the tolerance, is
  not a gouge, on a wall as on a floor.
- **Leftover.** At each cell, the material left may stand no higher than `leftover` above the
  highest reach among the cell and its eight neighbours, so that a wall does not count against a
  cut that stops a fraction of a cell short of it.
- **The shank and the holder.** A tool's shank is a cylinder of its `shank` diameter from its
  flutes' end up; its holder a cylinder of the holder's diameter from `length` above its tip up.
  Either meets material where, during any move, material stands higher than it within its radius
  by more than `tolerance` when the tool first comes over it (what the flutes reach as the tool
  goes on, they cut first, so a plunge as deep as the flutes and the shank's length may go in one
  move).
- **Feeds.** Only moves that cut are checked: a move's feed may not exceed its tool's `feed`. A
  move that goes down deep into material under the tool's axis (a plunge, or a ramp or helix
  into solid stock) may not go down faster than `plunge`: its rate down (its feed times the share
  of its length that is down) is limited where it cuts deeper than a quarter of the tool's
  diameter at the cells within a quarter of the tool's radius of the path of its axis (or at the
  nearest cell, for a narrow tool). A light cut down a surface, as in finishing, is fed as any
  cut. A tool may plunge straight down: the bench's end mills cut at their center.

**What a program measures**, none of it graded: its time on the bench's machine, at the
program's own feeds and rapids at 5000 mm/min, with no acceleration; its length fed and its length
rapid; its length fed through air (moves that cut nothing); the volume it removed against what
the tools can reach; the most it leaves above what the tools reach; the deepest cut any of its
moves takes, by tool; its lines and moves. And, for the planner: its time, CPU time and peak
memory to write the program, measured as brep-bench measures a kernel's run.

## `planners.json`

One entry per planner:

| field | meaning |
|---|---|
| `name` | the planner's name on the board |
| `planner` | its home page |
| `license` | shown on the board |
| `backend`, `frontend` | the language the planner is written in, and the language its implementations are written in |
| `build` | the command that sets up the runner (`harness/build.py` runs it) |
| `command` | the runner; `null` lists the planner as awaiting an implementation |
| `version` | the command that prints the planner's version |
| `source` | the pattern of an implementation's path |
| `kernel` | `true` for a CAM kernel (a library), as opposed to a whole CAM program; shown on the board |
| `note` | shown beside the planner on the board |

## Versions

- **0.3:** the plunge feed limits only a move that goes down deep into material under the tool's
  axis (deeper than a quarter of its diameter): a plunge, or a ramp or helix into solid stock.
  A light cut down a surface, as a ball end mill finishing a slope makes, is fed as any cut, as
  CAM programs feed it. Grading is otherwise as in 0.2.
- **0.2:** a planner may be a CAM kernel, whose program is a toolpath (JSON: rapids, lines and
  arcs, with the tool, feed and spindle speed) rather than G-code; the runner's reply names the
  format. An implementation may give the part in the planner's own terms (a pocket's outline and
  depth) where the planner takes those, and the moves a kernel does not plan between its
  operations are joined by the implementation's helper, plainly, and graded like any other.
  Grading is as in 0.1.
- **0.1:** three axes, flat and ball end mills, a height map; cases in words with their parts as
  STEP and STL; programs in G-code; pass, refused, incomplete, unsafe, invalid, crashed, timeout.

## Changing the suite

- **A new case** is a pull request adding its Markdown file, its part's `.py`, and the `.step`
  and `.stl` that `harness/parts.py` writes from it, with the reachable volume's closed form
  where there is one. Hard cases are the most valuable, especially ones your own planner gets
  wrong.
- **A new planner** is a pull request adding `planners/<planner>/` and its entry in
  `planners.json`. A planner's own authors write its best implementations; implementations by
  anyone else are welcome too.
- **A better implementation** of a case is welcome when it is more idiomatic, or when it does what
  the case asks where the old one refused.
