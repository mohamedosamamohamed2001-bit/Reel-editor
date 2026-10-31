// Unit tests for studio/src/lib/motionCore.ts (transpiled in memory, the same way seek_render serves it).
//   node tools/motion_selftest.js
const fs = require("fs"), path = require("path"), vm = require("vm");
const ROOT = path.resolve(__dirname, "..");
const ts = require(path.join(ROOT, "studio/node_modules/typescript"));
const js = ts.transpileModule(fs.readFileSync(path.join(ROOT, "studio/src/lib/motionCore.ts"), "utf8"),
  { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS } }).outputText;
const M = {}; vm.runInNewContext(js, { exports: M, Math });
let pass = 0, fail = 0;
const ok = (name, cond) => { cond ? pass++ : fail++; console.log(`${cond ? "PASS" : "FAIL"} ${name}`); };
const near = (a, b, e = 1e-6) => Math.abs(a - b) <= e;

ok("spring starts at 0 and settles at 1", M.spring(0) === 0 && M.spring(-1) === 0 && near(M.spring(5), 1, 1e-6));
const crit = Array.from({ length: 400 }, (_, i) => M.spring(i / 100));
ok("critically damped spring never overshoots (no bounce)", crit.every((v) => v <= 1 + 1e-9) && crit.every((v, i) => i === 0 || v >= crit[i - 1] - 1e-12));
ok("underdamped spring overshoots once (weighted settle)", Math.max(...Array.from({ length: 400 }, (_, i) => M.spring(i / 100, { damping: 0.75 }))) > 1.01);
ok("overdamped spring is monotonic and settles", near(M.spring(8, { damping: 1.5 }), 1, 1e-4));
ok("spring is a pure function of time (same t, same value)", M.spring(0.3721) === M.spring(0.3721));
ok("expo easings hit 0 and 1 exactly", M.expoOut(0) === 0 && M.expoOut(1) === 1 && M.expoIn(0) === 0 && M.expoIn(1) === 1 && M.expoInOut(0.5) === 0.5);
ok("impact ease starts fast (expoOut reaches 50% by 10% of the time)", M.expoOut(0.1) >= 0.5);
ok("beat grid at 120 BPM", M.beatLen(120) === 0.5 && M.beatOf(1.49, 120) === 2 && M.beatOf(1.5, 120) === 3 && M.barOf(2.1, 120) === 1);
ok("beatPulse is 1 on the beat and decays", near(M.beatPulse(1.0, 120), 1, 1e-3) && M.beatPulse(1.2, 120) < 0.3);
const r = Array.from({ length: 2000 }, (_, i) => M.rand(7, i));
ok("seeded rand: deterministic, in [0,1), spread", M.rand(7, 3) === M.rand(7, 3) && r.every((v) => v >= 0 && v < 1) && Math.abs(r.reduce((a, b) => a + b) / r.length - 0.5) < 0.03 && M.rand(7, 3) !== M.rand(8, 3));
const start = { x: 0, y: 0, z: 0, rx: 0, ry: 0, rz: 0, fov: 40, focus: 0 };
const shots = [{ kind: "dolly", t0: 1, t1: 2, to: { z: 100 } }, { kind: "crane", t0: 2, t1: 3, to: { y: -50, rx: 20 } }];
ok("camera holds before the first shot and lands exactly", M.cameraAt(0.5, start, shots).z === 0 && M.cameraAt(2, start, shots).z === 100 && M.cameraAt(3, start, shots).rx === 20);
ok("camera eases in and out (slow at both ends)", M.cameraAt(1.05, start, shots).z < 1 && M.cameraAt(1.95, start, shots).z > 99);
let threw = false; try { M.cameraAt(1.5, start, [{ kind: "dolly", t0: 1, t1: 2, to: { ry: 30 } }]); } catch (e) { threw = true; }
ok("a named move cannot change other channels (dolly cannot orbit)", threw);
ok("default camera renders the z=0 plane 1:1", M.cssWorld(start) === "translateZ(0px) rotateZ(0deg) rotateX(0deg) rotateY(0deg) translate3d(0px, 0px, 0px)");
const a = M.resample(M.rectPoly(0, 0, 100, 50), 64), b = M.circlePoly(0, 0, 40, 64);
ok("morph endpoints equal the source and target shapes", a.length === 64 && M.morph(a, b, 0).every((p, i) => p[0] === a[i][0]) && M.morph(a, b, 1).every((p, i) => near(p[0], b[i][0])));
ok("motionBlur: none when slow, along the move when fast", M.motionBlur(() => [0, 0], 1).sx === 0 && M.motionBlur((t) => [t * 3000, 0], 1).sx > 5 && M.motionBlur((t) => [t * 3000, 0], 1).sy === 0);
ok("frameTime quantises subframes to their frame", M.frameTime(1 / 60 + 1 / 180) === 1 / 60 && M.frameTime(0.999) === Math.floor(0.999 * 60) / 60);
ok("countUp lands on the target", M.countUp(2, 0, 1, 0, 75) === 75 && M.countUp(0, 0, 1, 0, 75) === 0);
console.log(`\n${pass} passed, ${fail} failed`); process.exit(fail ? 1 : 0);
