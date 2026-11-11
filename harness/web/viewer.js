// A case page's 3D view: the stock a planner's program leaves (or the part, as the tools can leave
// it), as a height map coloured as the maps are, with the program's path over it. The page holds
// what to draw in <script id=view>: each entry's height map (float32 heights then uint8 kinds,
// written by harness/site.py) and its path (polylines, harness/grade.py's `thin`).
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const view = JSON.parse(document.getElementById("view").textContent);
const holder = document.getElementById("viewer");
const pick = document.getElementById("pick");
const KINDS = [[176, 181, 190], [122, 170, 226], [240, 160, 48], [227, 73, 72]];
const UNTOUCHED = [214, 200, 172];
const TOOL_COLORS = [0x2a78d6, 0x8e44ad, 0x1baf7a, 0xd35400];

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
holder.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 5000);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x666670, 1.6));
const sun = new THREE.DirectionalLight(0xffffff, 1.8);
sun.position.set(-1, 1.5, 2.5);
scene.add(sun);

const lo = view.stock.min, hi = view.stock.max;
const center = new THREE.Vector3((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2);
const size = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]);
camera.position.set(center.x - 0.5 * size, center.y - 0.95 * size, center.z + 0.8 * size);
controls.target.copy(center);

let shown = [];
let pathShown = true;
const cache = new Map();

function background() {
  const css = getComputedStyle(document.body);
  scene.background = new THREE.Color(css.getPropertyValue("--card").trim() || "#f6f6f4");
}

function resize() {
  const w = holder.clientWidth, h = holder.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

async function fetchEntry(name) {
  if (cache.has(name)) return cache.get(name);
  const en = view.entries[name];
  const buf = await (await fetch(en.data)).arrayBuffer();
  const count = en.nx * en.ny;
  const out = { z: new Float32Array(buf, 0, count), k: new Uint8Array(buf, 4 * count, count) };
  if (en.path) out.path = await (await fetch(en.path)).json();
  cache.set(name, out);
  return out;
}

function surface(en, data) {
  // a vertex at each cell's center, and a skirt down to the stock's floor round the edge
  const { nx, ny, name } = en, step = view.h * en.n;
  const pos = [], col = [], idx = [];
  const top = hi[2];
  for (let j = 0; j < ny; j++) {
    for (let i = 0; i < nx; i++) {
      const z = data.z[j * nx + i];
      pos.push(lo[0] + (i + 0.5) * step, lo[1] + (j + 0.5) * step, z);
      const c = name !== "the part" && z >= top - 1e-6 ? UNTOUCHED : KINDS[data.k[j * nx + i]];
      col.push(c[0] / 255, c[1] / 255, c[2] / 255);
    }
  }
  for (let j = 0; j < ny - 1; j++) {
    for (let i = 0; i < nx - 1; i++) {
      const a = j * nx + i, b = a + 1, c = a + nx, d = c + 1;
      idx.push(a, b, d, a, d, c);
    }
  }
  const ring = [];
  for (let i = 0; i < nx; i++) ring.push(i);
  for (let j = 1; j < ny; j++) ring.push(j * nx + nx - 1);
  for (let i = nx - 2; i >= 0; i--) ring.push((ny - 1) * nx + i);
  for (let j = ny - 2; j > 0; j--) ring.push(j * nx);
  const base = pos.length / 3;
  ring.forEach((v) => {
    pos.push(pos[3 * v], pos[3 * v + 1], lo[2]);
    col.push(0.55, 0.55, 0.58);
  });
  for (let r = 0; r < ring.length; r++) {
    const a = ring[r], b = ring[(r + 1) % ring.length];
    const a2 = base + r, b2 = base + ((r + 1) % ring.length);
    idx.push(a, a2, b2, a, b2, b);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return new THREE.Mesh(g, new THREE.MeshLambertMaterial({ vertexColors: true,
                                                           side: THREE.DoubleSide }));
}

function paths(runs) {
  const group = new THREE.Group();
  const tools = [...new Set(runs.map((r) => r.tool))];
  for (const r of runs) {
    const pts = [];
    for (let i = 0; i < r.points.length; i += 3) {
      pts.push(new THREE.Vector3(r.points[i], r.points[i + 1], r.points[i + 2]));
    }
    const g = new THREE.BufferGeometry().setFromPoints(pts);
    const material = r.rapid
      ? new THREE.LineDashedMaterial({ color: 0xe34948, dashSize: 1.5, gapSize: 1.2 })
      : new THREE.LineBasicMaterial({ color: TOOL_COLORS[tools.indexOf(r.tool) % 4] });
    const line = new THREE.Line(g, material);
    if (r.rapid) line.computeLineDistances();
    group.add(line);
  }
  return group;
}

async function show(name) {
  for (const b of pick.querySelectorAll("button[data-k]")) {
    b.setAttribute("aria-current", b.dataset.k === name ? "true" : "false");
  }
  const en = { ...view.entries[name], name };
  const data = await fetchEntry(name);
  shown.forEach((o) => scene.remove(o));
  shown = [surface(en, data)];
  if (data.path) {
    const p = paths(data.path);
    p.visible = pathShown;
    shown.push(p);
  }
  shown.forEach((o) => scene.add(o));
}

for (const name of Object.keys(view.entries)) {
  const b = document.createElement("button");
  b.textContent = name;
  b.dataset.k = name;
  b.addEventListener("click", () => {
    show(name);
    if (name !== "the part") history.replaceState(null, "", "#k-" + name);
  });
  pick.appendChild(b);
}
const toggle = document.createElement("button");
toggle.className = "chip";
toggle.textContent = "path";
toggle.setAttribute("aria-pressed", "true");
toggle.addEventListener("click", () => {
  pathShown = !pathShown;
  toggle.setAttribute("aria-pressed", String(pathShown));
  shown.slice(1).forEach((o) => (o.visible = pathShown));
});
pick.appendChild(toggle);

background();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", background);
new ResizeObserver(resize).observe(holder);
resize();
renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});
const wanted = decodeURIComponent(location.hash.replace(/^#k-/, ""));
const names = Object.keys(view.entries);
show(names.includes(wanted) ? wanted : names[1] || names[0]);
