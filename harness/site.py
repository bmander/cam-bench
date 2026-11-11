#!/usr/bin/env python3
"""Render the results as a static site (site/):

- index.html: what the bench is, each planner's outcomes, and every case's outcome for every
  planner, each with a map of the stock its program leaves;
- a page for each case (cases/<case>.html): its description, its stock and tools, the volume its
  tools can reach (with the closed form, where there is one, beside the harness's own), a map of
  its part, and each planner's entry: its outcome and why, what its program measures, a map of
  the stock it leaves, the stock and the path in 3D (viewer.js), its program and its code;
- board.json: every outcome and measure, in one file.

Planners are listed in planners.json's order, everywhere: the board ranks nothing. Reads
results/<planner>.json, and the height maps harness/run.py keeps in results/runs/. Needs numpy."""
import html
import json
import math
import os
import shutil
import struct
import sys
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade  # noqa: E402
from highlight import highlight, loc  # noqa: E402
from suite import ROOT, cases, planners, source  # noqa: E402

SITE = os.path.join(ROOT, "site")
WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
REPO = "https://github.com/bmander/cam-bench"
# the most cells along a side of a map or of the 3D view
MAP_SIDE = 400
VIEW_SIDE = 320
# the largest program the site carries, in bytes
PROGRAM_KEPT = 5_000_000
OUTCOMES = ["pass", "refused", "incomplete", "unsafe", "invalid", "crashed", "timeout", "missing"]
# what a cell of a map is: finished (at the part), left where no tool reaches, left where a tool
# reaches (an incomplete program's), cut into the part
FINISHED, UNREACHED, EXCESS, GOUGED = 0, 1, 2, 3
COLORS = {FINISHED: (176, 181, 190), UNREACHED: (122, 170, 226), EXCESS: (240, 160, 48),
          GOUGED: (227, 73, 72)}
STOCK = (214, 200, 172)  # stock the program never touched


def e(s):
    return html.escape(str(s), quote=True)


def head(title, description, depth):
    up = "../" * depth
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8>\n"
            f"<meta name=viewport content='width=device-width, initial-scale=1'>\n"
            f"<title>{e(title)}</title>\n<meta name=description content='{e(description)}'>\n"
            f"<link rel=stylesheet href='{up}style.css'>\n"
            f"<link rel=icon href='{up}favicon.svg' type='image/svg+xml'>\n</head>")


def nav(depth, current=None):
    up = "../" * depth
    here = " aria-current=page" if current == "index" else ""
    return (f"<nav class=top><a href='{up}index.html'{here}>cam-bench</a>"
            f"<a href='{REPO}/blob/main/SPEC.md'>Rules</a><a href='{REPO}'>Source</a></nav>")


# ------------------------------------------------------------------------------------------- maps

def png(path, rgb):
    """Write an RGB image (h, w, 3) of uint8 as PNG."""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[j].tobytes() for j in range(h - 1, -1, -1))  # +y up

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def coarse(a, n, op):
    """`a` in blocks of n by n cells, each block reduced by op (np.min, np.max)."""
    ny, nx = a.shape
    ny2, nx2 = -(-ny // n), -(-nx // n)
    pad = np.pad(a, ((0, ny2 * n - ny), (0, nx2 * n - nx)), mode="edge")
    return op(pad.reshape(ny2, n, nx2, n), axis=(1, 3))


def shade(z, h):
    """Light on a height map from the upper left, 0.35 to 1."""
    gy, gx = np.gradient(z, h)
    n = np.stack([-gx, -gy, np.ones_like(z)])
    n /= np.linalg.norm(n, axis=0)
    light = np.array([-0.5, 0.5, 0.75])
    light /= np.linalg.norm(light)
    return 0.35 + 0.65 * np.clip(np.tensordot(light, n, axes=1), 0, 1)


def kinds(case, stock, part, ref, excess):
    k = np.full(stock.shape, FINISHED, dtype=np.uint8)
    k[stock > part + case["leftover"]] = UNREACHED
    k[excess > 0] = EXCESS
    k[stock < part - case["tolerance"]] = GOUGED
    return k


def draw(path, case, z, kind, h, untouched=None):
    n = max(1, math.ceil(max(z.shape) / MAP_SIDE))
    zc, kc = coarse(z, n, np.min), coarse(kind, n, np.max)
    base = np.array([COLORS[i] for i in range(4)], dtype=np.float64)[kc]
    if untouched is not None:
        base[coarse(untouched, n, np.min)] = STOCK
    # lower is darker, so that a floor reads apart from the top it is cut from
    # (over at least a millimetre, so that a flat part's rounding is not drawn as relief)
    span = max(float(zc.max() - zc.min()), 1.0)
    depth = 0.72 + 0.28 * (zc - zc.min()) / span
    rgb = base * (shade(zc, h * n) * depth)[..., None]
    png(path, np.clip(rgb, 0, 255).astype(np.uint8))


def view_data(path, z, kind):
    """The stock left, for the 3D viewer: heights (float32) then kinds (uint8), on a grid of at
    most VIEW_SIDE a side; returns the grid's size and its cells' coarsening."""
    n = max(1, math.ceil(max(z.shape) / VIEW_SIDE))
    zc = coarse(z, n, np.min).astype(np.float32)
    kc = coarse(kind, n, np.max).astype(np.uint8)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(zc.tobytes() + kc.tobytes())
    return {"nx": zc.shape[1], "ny": zc.shape[0], "n": n}


# ------------------------------------------------------------------------------------------- text

def seconds(x):
    if x is None:
        return "–"
    if x < 1:
        return f"{x * 1000:.0f} ms"
    if x < 120:
        return f"{x:.1f} s"
    return f"{x / 60:.1f} min"


def clock(x):
    """A program's time, minutes and seconds."""
    if x is None:
        return "–"
    m, s = divmod(round(x), 60)
    return f"{m}:{s:02d}"


def length(x):
    return "–" if x is None else (f"{x / 1000:.2f} m" if x >= 1000 else f"{x:.0f} mm")


def paragraphs(text):
    """A description's Markdown, as far as cases use it: paragraphs, and lists of `- ` items."""
    out = []
    for block in text.split("\n\n"):
        lines = block.strip().splitlines()
        if lines and lines[0].startswith("- "):
            items = []
            for l in lines:
                if l.startswith("- "):
                    items.append(l[2:].strip())
                else:
                    items[-1] += " " + l.strip()
            out.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>")
        elif lines:
            out.append(f"<p>{e(' '.join(l.strip() for l in lines))}</p>")
    return "\n".join(out)


def tool_text(t):
    return (f"T{t['number']}: {t['shape']} end mill ⌀{t['diameter']:g}, flutes {t['flute']:g}, "
            f"{t['length']:g} out of a ⌀{t.get('holder', t['shank']):g} holder; feed to "
            f"{t['feed']:g} mm/min, plunge to {t['plunge']:g}, {t['rpm']:g} rpm")


# ------------------------------------------------------------------------------------------ pages

def load():
    results = {}
    for p in planners():
        path = os.path.join(ROOT, "results", p["name"] + ".json")
        if os.path.exists(path):
            with open(path) as f:
                results[p["name"]] = {r["case"]: r for r in json.load(f)["cases"]}
    return results


def entry_html(c, p, row, depth, maps):
    name = p["name"]
    out = [f"<section class=entry id='k-{e(name)}'><h3>{e(name)} "
           f"<span class='badge {row['outcome']}'>{row['outcome']}</span></h3>"]
    if row.get("why"):
        out.append(f"<p class=why>{e(row['why'])}</p>")
    m = row.get("program")
    if m:
        removed_pct = 100 * m["removed"] / m["reachable"] if m.get("reachable") else None
        facts = [
            ("its time, at its feeds", clock(m["time"])),
            ("cutting", length(m["feed_length"] - m["air_length"])),
            ("fed through air", length(m["air_length"])),
            ("rapids", length(m["rapid_length"])),
            ("removed", f"{m['removed']:.1f} mm³" + (f" ({removed_pct:.2f}% of what the tools "
                                                     f"can reach)" if removed_pct else "")),
            ("most left above what the tools reach", f"{m['leftover_max']:.3f}"),
            ("deepest cut in one move", ", ".join(f"T{k} {v:.2f}" for k, v in
                                                  sorted(m["max_depth"].items()))),
            ("tools", ", ".join(f"T{t}" for t in m["tools"])),
            ("program", (f"{m['lines']:,} lines, " if m.get("lines") else "")
             + f"{m['moves']:,} moves"),
        ]
        out.append("<table class=facts>" + "".join(f"<tr><th>{a}</th><td>{b}</td></tr>"
                                                    for a, b in facts) + "</table>")
    cost = [("planning", seconds(row.get("seconds"))),
            ("its CPU", seconds(row.get("cpu_seconds"))),
            ("peak memory", f"{row['peak_mb']:.0f} MB" if row.get("peak_mb") else "–")]
    out.append("<p class=muted>" + " · ".join(f"{a} {b}" for a, b in cost) + "</p>")
    if name in maps:
        out.append(f"<figure class=map><img src='{maps[name]}' alt='the stock {e(name)}'s "
                   f"program leaves, from above' loading=lazy></figure>")
    links = []
    progs = [os.path.join(ROOT, "results", "runs", name, c["id"] + ext) for ext in (".nc", ".json")]
    prog = next((p for p in progs if os.path.exists(p)), None)
    if prog and os.path.getsize(prog) <= PROGRAM_KEPT:
        rel = f"programs/{name}/{c['id']}{os.path.splitext(prog)[1]}"
        dst = os.path.join(SITE, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(prog, dst)
        what = "the toolpath" if rel.endswith(".json") else "the program"
        links.append(f"<a href='{'../' * depth}{rel}' download>{what}</a>")
    if links:
        out.append("<p>" + " · ".join(links) + "</p>")
    src = source(p, c["id"])
    if src and os.path.exists(src):
        with open(src) as f:
            code = f.read()
        rel = os.path.relpath(src, ROOT)
        out.append(f"<details><summary>its code, <a href='{REPO}/blob/main/{e(rel)}'>{e(rel)}"
                   f"</a> ({loc(code, src)} lines)</summary><pre class=code>"
                   f"{highlight(code, src)}</pre></details>")
    out.append("</section>")
    return "\n".join(out)


def case_page(c, registry, results, cells):
    depth = c["id"].count("/") + 1
    up = "../" * depth
    grid, part, gouge, ref = grade.prepared(c)
    h = c["resolution"]
    top = c["stock"]["max"][2]
    reach = float((top - np.minimum(ref, top)).sum() * h * h)
    # the part, with what no tool reaches over it
    pk = np.where(np.minimum(ref, top) > part + c["leftover"], UNREACHED, FINISHED).astype(np.uint8)
    part_img = f"img/part/{c['id']}.png"
    draw(os.path.join(SITE, part_img), c, np.minimum(ref, top), pk, h)
    view = {"case": c["id"], "x0": c["stock"]["min"][0], "y0": c["stock"]["min"][1], "h": h,
            "stock": c["stock"], "tools": c["tools"], "entries": {}}
    meta = view_data(os.path.join(SITE, "data", "part", c["id"] + ".bin"),
                     np.minimum(ref, top), pk)
    view["entries"]["the part"] = {"data": f"{up}data/part/{c['id']}.bin", **meta}
    maps = {}
    for p in registry:
        row = results.get(p["name"], {}).get(c["id"])
        keep = os.path.join(ROOT, "results", "runs", p["name"], c["id"])
        if not row or not os.path.exists(keep + ".npz"):
            continue
        z = np.load(keep + ".npz")
        stock, excess = z["stock"].astype(np.float64), z["excess"].astype(np.float64)
        kind = kinds(c, stock, part, ref, excess)
        untouched = stock >= top - 1e-9
        img = f"img/{p['name']}/{c['id']}.png"
        draw(os.path.join(SITE, img), c, stock, kind, h, untouched)
        maps[p["name"]] = up + img
        cells[(p["name"], c["id"])] = img
        meta = view_data(os.path.join(SITE, "data", p["name"], c["id"] + ".bin"), stock, kind)
        entry = {"data": f"{up}data/{p['name']}/{c['id']}.bin", **meta}
        if os.path.exists(keep + ".path.json"):
            dst = os.path.join(SITE, "data", p["name"], c["id"] + ".path.json")
            shutil.copyfile(keep + ".path.json", dst)
            entry["path"] = f"{up}data/{p['name']}/{c['id']}.path.json"
        view["entries"][p["name"]] = entry

    rows = []
    for p in registry:
        row = results.get(p["name"], {}).get(c["id"])
        if row is None:
            continue
        m = row.get("program") or {}
        rows.append(f"<tr><th><a href='#k-{e(p['name'])}'>{e(p['name'])}</a></th>"
                    f"<td class='cell {row['outcome']}'>{row['outcome']}</td>"
                    f"<td class=num>{clock(m.get('time'))}</td>"
                    f"<td class=num>{length(m.get('feed_length'))}</td>"
                    f"<td class=num>{length(m.get('air_length'))}</td>"
                    f"<td class=num>{seconds(row.get('seconds'))}</td></tr>")
    removed = c["removed"]
    closed = ""
    if removed:
        rel = reach / removed["value"] - 1
        closed = (f"<p>The volume the tools can reach is <b>{removed['value']:.6g}</b> mm³, "
                  f"<span class=formula>{e(removed['exact'])}</span>. The harness's reference, "
                  f"on its grid of {h:g}, makes it {reach:.6g} ({rel:+.1e}).</p>")
    else:
        closed = (f"<p>The volume the tools can reach, by the harness's reference on its grid "
                  f"of {h:g}, is {reach:.6g} mm³; it has no closed form.</p>")
    lo, hi = c["stock"]["min"], c["stock"]["max"]
    setup = [
        ("stock", f"({lo[0]:g}, {lo[1]:g}, {lo[2]:g}) to ({hi[0]:g}, {hi[1]:g}, {hi[2]:g})"),
        *(("tool", tool_text(t)) for t in c["tools"]),
        ("may cut into the part", f"{c['tolerance']:g}"),
        ("may leave above what the tools reach", f"{c['leftover']:g}"),
    ]
    if c["spoilboard"]:
        setup.append(("may cut into the spoilboard", f"{c['spoilboard']:g}"))
    page = [head(f"{c['title']} · cam-bench", c["description"][:150], depth),
            "<body>", nav(depth),
            f"<h1>{e(c['title'])}</h1><p class=muted>{e(c['id'])} · "
            + " ".join(f"<span class=tag>{e(t)}</span>" for t in c["tags"]) + "</p>",
            f"<div class=description>{paragraphs(c['description'])}</div>",
            "<table class=facts>" + "".join(f"<tr><th>{a}</th><td class=wrap>{e(b)}</td></tr>"
                                            for a, b in setup) + "</table>",
            closed,
            f"<p>The part's files: <a href='{REPO}/blob/main/cases/{c['id']}.step'>STEP</a>, "
            f"<a href='{REPO}/blob/main/cases/{c['id']}.stl'>STL</a>, and how it is built, "
            f"<a href='{REPO}/blob/main/cases/{c['id']}.py'>{e(c['id'])}.py</a>.</p>",
            "<div class=maps><figure class=map><img src='" + up + part_img + "' alt='the part "
            "from above'><figcaption>The part from above, as the tools can leave it: blue where "
            "no tool reaches.</figcaption></figure></div>",
            "<h2>The planners</h2>",
            "<table class=entries><thead><tr><th>planner</th><th>outcome</th>"
            "<th class=num>time</th><th class=num>fed</th><th class=num>through air</th>"
            "<th class=num>planning</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>",
            "<div class=mapkey><span><i class=sw style='background:rgb(176,181,190)'></i>at the part"
            "</span><span><i class=sw style='background:rgb(122,170,226)'></i>left where no tool "
            "reaches</span><span><i class=sw style='background:rgb(240,160,48)'></i>left where a "
            "tool reaches</span><span><i class=sw style='background:rgb(227,73,72)'></i>cut into "
            "the part</span><span><i class=sw style='background:rgb(214,200,172)'></i>stock never "
            "touched</span></div>",
            "<div class=pick id=pick></div><div id=viewer></div>"
            "<p class=muted id=viewer-note>Drag to turn, scroll to zoom. The path's rapids are "
            "dashed.</p>",
            *(entry_html(c, p, results[p["name"]][c["id"]], depth, maps)
              for p in registry if c["id"] in results.get(p["name"], {})),
            f"<script type=application/json id=view>{json.dumps(view)}</script>",
            "<script type=importmap>{\"imports\": {\"three\": "
            "\"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js\", "
            "\"three/addons/\": \"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/\"}}"
            "</script>",
            f"<script type=module src='{up}viewer.js'></script>",
            "</body></html>"]
    path = os.path.join(SITE, "cases", c["id"] + ".html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(page))
    return reach


def index(registry, results, all_cases, cells):
    tallies = []
    for p in registry:
        rows = results.get(p["name"], {})
        t = {o: sum(1 for c in all_cases if rows.get(c["id"], {"outcome": "missing"})["outcome"]
                    == o) for o in OUTCOMES}
        bar = "".join(f"<span class={o} style='flex:{t[o]}' title='{o}: {t[o]}'></span>"
                      for o in OUTCOMES if t[o])
        tallies.append(f"<tr><th><a href='{e(p['planner'])}'>{e(p['name'])}</a>"
                       f"<small class=muted>{'a CAM kernel, ' if p.get('kernel') else ''}"
                       f"{e(p.get('frontend', ''))} on {e(p.get('backend', ''))}"
                       f", {e(p.get('license', ''))}</small></th>"
                       + "".join(f"<td class='num {o if t[o] else ''}'>{t[o] or ''}</td>"
                                 for o in OUTCOMES)
                       + f"<td><div class=bar>{bar}</div></td></tr>")
    grid_rows = []
    for c in all_cases:
        cellsh = []
        for p in registry:
            row = results.get(p["name"], {}).get(c["id"])
            outcome = row["outcome"] if row else "missing"
            img = cells.get((p["name"], c["id"]))
            pic = f"<img class=thumb src='{img}' alt='' loading=lazy>" if img else ""
            m = (row or {}).get("program") or {}
            sub = f"<small>{clock(m['time'])}</small>" if m.get("time") else ""
            cellsh.append(f"<td class='cell {outcome}'><a href='cases/{c['id']}.html#k-"
                          f"{e(p['name'])}' title='{e((row or {}).get('why', ''))}'>{pic}"
                          f"{outcome}{sub}</a></td>")
        grid_rows.append(f"<tr><td class=case><a href='cases/{c['id']}.html'>{e(c['title'])}</a>"
                         f"<small>{e(c['id'])}</small></td>"
                         f"<td><img class=thumb src='img/part/{c['id']}.png' alt=''></td>"
                         + "".join(cellsh) + "</tr>")
    page = [head("cam-bench", "A neutral benchmark for CAM toolpath planners: the same parts, "
                 "stock and tools for every planner, every program cut and graded the same way.", 0),
            "<body class=wide>", nav(0, "index"),
            "<h1>cam-bench</h1>",
            "<p class=lede>Rosetta Code for CAM toolpath planners. Each case gives a part, the "
            "stock it is cut from and the tools to cut it with. Each planner writes a program for "
            "it in its own idioms, and the harness cuts the stock with every program on the same "
            "height map and grades it the same way: a program passes when it removes everything "
            "the tools can reach, within the case's tolerance, and never cuts into the part or "
            "meets material with anything but its flutes. A refusal ranks above a wrong program, "
            "and no planner ranks above another.</p>",
            "<h2>What is a toolpath planner?</h2>",
            "<p class=definition>A toolpath planner, the CAM in CAD/CAM, turns a part's geometry "
            "and a choice of tools into the moves a milling machine makes: here, G-code for three "
            "axes. It decides how to clear material in levels, how close to pass to the part, how "
            "far apart to step, how to enter and leave the cut, and how fast to feed. The bench "
            "grades whether its programs are right and safe, and measures how long they take to "
            "run and to plan.</p>",
            "<h2>Planners</h2>",
            "<div class=scroll><table class=tally><thead><tr><th>planner</th>"
            + "".join(f"<th class=num>{o}</th>" for o in OUTCOMES) + "<th></th></tr></thead>"
            + "<tbody>" + "".join(tallies) + "</tbody></table></div>",
            "<h2>Cases</h2>",
            "<p class=muted>Each cell shows the stock the planner's program leaves, from above: "
            "grey at the part, blue where no tool can reach, orange where a tool could have "
            "reached but did not, red cut into the part, tan never touched. Under it, the "
            "program's time at its own feeds.</p>",
            "<div class=scroll><table class=grid><thead><tr><th>case</th><th>part</th>"
            + "".join(f"<th>{e(p['name'])}</th>" for p in registry) + "</tr></thead><tbody>"
            + "".join(grid_rows) + "</tbody></table></div>",
            "</body></html>"]
    with open(os.path.join(SITE, "index.html"), "w") as f:
        f.write("\n".join(page))


def main():
    registry = [p for p in planners()]
    results = load()
    all_cases = cases()
    os.makedirs(SITE, exist_ok=True)
    for name in ("style.css", "viewer.js", "favicon.svg"):
        shutil.copyfile(os.path.join(WEB, name), os.path.join(SITE, name))
    cells, board = {}, {"planners": registry, "cases": []}
    for c in all_cases:
        reach = case_page(c, registry, results, cells)
        board["cases"].append({
            "id": c["id"], "title": c["title"], "tags": c["tags"], "reachable": reach,
            "removed": c["removed"],
            "results": {p["name"]: results.get(p["name"], {}).get(c["id"]) for p in registry}})
        print(f"{c['id']}", flush=True)
    index(registry, results, all_cases, cells)
    with open(os.path.join(SITE, "board.json"), "w") as f:
        json.dump(board, f)


if __name__ == "__main__":
    main()
