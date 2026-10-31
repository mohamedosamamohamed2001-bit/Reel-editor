/**
 * OSM motion core: pure functions of TIME (seconds), no imports, no state, no clock.
 * Shared by Remotion components (import from "./motionCore") and by HTML motion pieces (tools/seek_render.js serves this
 * file transpiled as /osm/motion-core.js). Principles from docs/motion/ (Spec 1 + Spec 2), adapted in docs/motion/MOTION_SYSTEM.md:
 * springs and exponential easing as functions of time (never linear tweens, never bouncy), seeded randomness, blur that
 * follows speed and direction, one named camera move per shot, eased in and out.
 */

export const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
/** progress of t through [t0, t1], 0..1, optional easing */
export const seg = (t: number, t0: number, t1: number, ease: (x: number) => number = (x) => x) =>
  ease(clamp01((t - t0) / Math.max(1e-9, t1 - t0)));

// ---------- easing (exponential, no overshoot) ----------
export const expoOut = (x: number) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * clamp01(x)));
export const expoIn = (x: number) => (x <= 0 ? 0 : Math.pow(2, 10 * (clamp01(x) - 1)));
export const expoInOut = (x: number) => {
  x = clamp01(x);
  if (x === 0 || x === 1) return x;
  return x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2;
};

// ---------- springs (closed form: same value for the same t, any frame order) ----------
export type SpringOpts = { freq?: number; damping?: number };
/** step response 0 -> 1 of a damped spring, t = seconds since release (t <= 0 -> 0).
 *  freq = natural frequency in Hz (higher = snappier). damping = zeta: 1 = critical (default, no overshoot);
 *  0.7..0.9 = a physical "weighted" settle with one small overshoot (for objects with mass, not for UI/type). */
export const spring = (t: number, { freq = 2.2, damping = 1 }: SpringOpts = {}) => {
  if (t <= 0) return 0;
  const w = 2 * Math.PI * freq, z = damping;
  if (z >= 1) {
    if (z === 1) return 1 - Math.exp(-w * t) * (1 + w * t);
    const s = Math.sqrt(z * z - 1), r1 = -w * (z - s), r2 = -w * (z + s);
    return 1 + (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r1 - r2);
  }
  const wd = w * Math.sqrt(1 - z * z);
  return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
};
/** spring between two values, released at t0 */
export const springTo = (t: number, t0: number, from: number, to: number, o?: SpringOpts) => lerp(from, to, spring(t - t0, o));
/** numeric derivative of any time function (units per second) */
export const velocity = (f: (t: number) => number, t: number, dt = 1 / 240) => (f(t + dt) - f(t - dt)) / (2 * dt);

// ---------- beat grid ----------
export const beatLen = (bpm: number) => 60 / bpm;
export const beatOf = (t: number, bpm: number) => Math.floor(t / beatLen(bpm) + 1e-9);
export const barOf = (t: number, bpm: number, perBar = 4) => Math.floor(beatOf(t, bpm) / perBar);
/** 1 on each beat, decaying exponentially (tau seconds) until the next one: an "accent" envelope */
export const beatPulse = (t: number, bpm: number, tau = 0.12) => Math.exp(-((t % beatLen(bpm)) + 1e-9) / tau);
/** time of beat n */
export const beatT = (n: number, bpm: number) => n * beatLen(bpm);

// ---------- seeded randomness (stateless: rand(seed, i) is the same in every frame) ----------
export const rand = (seed: number, i = 0) => {
  let h = (Math.imul(seed | 0, 0x9e3779b1) ^ Math.imul((i | 0) + 0x632be5ab, 0x85ebca6b)) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x7feb352d) >>> 0;
  h = Math.imul(h ^ (h >>> 15), 0x846ca68b) >>> 0;
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
};
export const randRange = (seed: number, i: number, a: number, b: number) => lerp(a, b, rand(seed, i));

// ---------- blur that follows speed and direction ----------
/** directional blur from a position function (px), for fast moves only: below `minSpeed` px/s there is no blur.
 *  Returns sx, sy (Gaussian std-dev in px along x and y) for an SVG feGaussianBlur or a CSS blur fallback. */
export const motionBlur = (pos: (t: number) => [number, number], t: number, fps = 60, minSpeed = 900, k = 0.35) => {
  const dt = 1 / 240, a = pos(t - dt), b = pos(t + dt);
  const vx = (b[0] - a[0]) / (2 * dt), vy = (b[1] - a[1]) / (2 * dt);
  const sp = Math.hypot(vx, vy);
  if (sp < minSpeed) return { sx: 0, sy: 0, speed: sp };
  const len = (sp / fps) * k; // ~a third of the distance moved during one frame
  return { sx: (Math.abs(vx) / sp) * len, sy: (Math.abs(vy) / sp) * len, speed: sp };
};

// ---------- camera language: one named move per shot, eased in and out ----------
export type Cam = { x: number; y: number; z: number; rx: number; ry: number; rz: number; fov: number; focus: number };
export type MoveKind = "dolly" | "crane" | "orbit" | "pushIn" | "rackFocus" | "hold";
/** which camera channels each named move may change (everything else is held) */
export const MOVE_KEYS: Record<MoveKind, (keyof Cam)[]> = {
  dolly: ["x", "z"], crane: ["y", "z", "rx"], orbit: ["x", "z", "ry"], pushIn: ["z", "fov", "focus"], rackFocus: ["focus"], hold: [],
};
export type Shot = { kind: MoveKind; t0: number; t1: number; to: Partial<Cam> };
/** camera at time t from a starting camera and a list of shots (sorted by t0). Each shot moves only its own channels,
 *  eased in and out (expoInOut); values carry over between shots, so there are no jumps. Unknown keys throw. */
export const cameraAt = (t: number, start: Cam, shots: Shot[]): Cam => {
  let cam = { ...start };
  for (const s of shots) {
    if (t < s.t0) break;
    const p = seg(t, s.t0, s.t1, expoInOut);
    const next = { ...cam };
    for (const k of Object.keys(s.to) as (keyof Cam)[]) {
      if (!MOVE_KEYS[s.kind].includes(k)) throw new Error(`camera move "${s.kind}" cannot change "${k}"`);
      next[k] = lerp(cam[k], s.to[k] as number, p);
    }
    cam = next;
  }
  return cam;
};
/** CSS 3D: perspective (px) for a vertical field of view, and the transform for the "world" element.
 *  Camera model = a film camera aimed at a target: x, y = where it looks (px, screen axes; crane up = negative y),
 *  z = push-in toward the target (px; 0 = natural scale), rx = pitch (crane tilt, + looks down onto the floor),
 *  ry = yaw (orbit around the target, + = camera moves right), rz = roll, fov = lens. At the default camera every element
 *  on the z = 0 plane renders at exactly 1:1, so 2D layouts and their 3D continuation are the same pixels. */
export const cssPerspective = (fovDeg: number, height: number) => height / 2 / Math.tan((fovDeg * Math.PI) / 360);
export const cssWorld = (c: Cam, _height?: number) =>
  `translateZ(${c.z}px) rotateZ(${-c.rz}deg) rotateX(${-c.rx}deg) rotateY(${-c.ry}deg) translate3d(${-c.x}px, ${-c.y}px, 0px)`;
/** depth of field: blur (px) of a layer at depth z for a camera focused at `focus` (same units) */
export const dofBlur = (z: number, focus: number, aperture = 0.004, max = 14) => Math.min(max, Math.abs(z - focus) * aperture);

// ---------- shape morphing ----------
export type Pt = [number, number];
/** resample a closed polygon to n points evenly spaced along its perimeter (so any two shapes can morph) */
export const resample = (poly: Pt[], n: number): Pt[] => {
  const segs = poly.map((p, i) => { const q = poly[(i + 1) % poly.length]; return Math.hypot(q[0] - p[0], q[1] - p[1]); });
  const total = segs.reduce((a, b) => a + b, 0), out: Pt[] = [];
  let si = 0, acc = 0;
  for (let k = 0; k < n; k++) {
    const d = (k / n) * total;
    while (acc + segs[si] < d && si < segs.length - 1) acc += segs[si++];
    const p = poly[si], q = poly[(si + 1) % poly.length], f = segs[si] ? (d - acc) / segs[si] : 0;
    out.push([lerp(p[0], q[0], f), lerp(p[1], q[1], f)]);
  }
  return out;
};
export const morph = (a: Pt[], b: Pt[], p: number): Pt[] => a.map((pa, i) => [lerp(pa[0], b[i][0], p), lerp(pa[1], b[i][1], p)]);
export const polyPath = (pts: Pt[]) => "M" + pts.map((p) => `${p[0].toFixed(2)},${p[1].toFixed(2)}`).join("L") + "Z";
/** rounded rectangle / circle outlines as polygons (cx, cy = centre) */
export const rectPoly = (cx: number, cy: number, w: number, h: number): Pt[] => [[cx - w / 2, cy - h / 2], [cx + w / 2, cy - h / 2], [cx + w / 2, cy + h / 2], [cx - w / 2, cy + h / 2]];
export const circlePoly = (cx: number, cy: number, r: number, n = 96): Pt[] =>
  Array.from({ length: n }, (_, i) => [cx + r * Math.cos(-Math.PI / 2 + (2 * Math.PI * i) / n), cy + r * Math.sin(-Math.PI / 2 + (2 * Math.PI * i) / n)] as Pt);

// ---------- data / UI ----------
/** a number counting up with an exponential settle (data moments): returns the value at t */
export const countUp = (t: number, t0: number, t1: number, from: number, to: number) => lerp(from, to, seg(t, t0, t1, expoOut));
/** discrete content (counter digits, swapped text) must change once per FRAME, not per motion-blur subframe, or the
 *  subframe blend ghosts two values on top of each other: evaluate it at the frame's own time */
export const frameTime = (t: number, fps = 60) => Math.floor(t * fps + 1e-6) / fps;
