// Soundtrack in code (Spec 2 build 3): OfflineAudioContext, deterministic (seeded noise), rendered to WAV.
// Pieces import from "/osm/audio.js" and expose window.renderAudio = () => renderSoundtrack({...}).
// Levels are conservative (peaks ~ -6 dBFS): the studio masters final mixes itself (render_edit, -14 LUFS).

const SR = 48000;
const seeded = (seed) => () => { seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

function noiseBuffer(ctx, dur, seed) {
  const b = ctx.createBuffer(1, Math.ceil(dur * SR), SR), d = b.getChannelData(0), r = seeded(seed);
  for (let i = 0; i < d.length; i++) d[i] = r() * 2 - 1;
  return b;
}
/** kick: pitch-swept sine, short exponential decay */
export function kick(ctx, t, gain = 0.9) {
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.frequency.setValueAtTime(140, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.12);
  g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(gain, t + 0.004); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
  o.connect(g).connect(ctx.destination); o.start(t); o.stop(t + 0.4);
}
/** hit on a scene change: filtered noise burst + low thump */
export function hit(ctx, t, gain = 0.5, seed = 7) {
  const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, 0.5, seed);
  const f = ctx.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = 1800; f.Q.value = 0.8;
  const g = ctx.createGain(); g.gain.setValueAtTime(gain, t); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.28);
  n.connect(f).connect(g).connect(ctx.destination); n.start(t); n.stop(t + 0.5);
  kick(ctx, t, gain * 0.8);
}
/** riser into time t1: noise through a rising band-pass + rising tone, starts at t0 */
export function riser(ctx, t0, t1, gain = 0.25, seed = 11) {
  const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, t1 - t0 + 0.05, seed);
  const f = ctx.createBiquadFilter(); f.type = "bandpass"; f.Q.value = 2.5;
  f.frequency.setValueAtTime(300, t0); f.frequency.exponentialRampToValueAtTime(6000, t1);
  const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(gain, t1 - 0.02); g.gain.linearRampToValueAtTime(0, t1);
  n.connect(f).connect(g).connect(ctx.destination); n.start(t0); n.stop(t1 + 0.05);
  const o = ctx.createOscillator(), og = ctx.createGain(); o.type = "sawtooth";
  o.frequency.setValueAtTime(110, t0); o.frequency.exponentialRampToValueAtTime(880, t1);
  og.gain.setValueAtTime(0.0001, t0); og.gain.exponentialRampToValueAtTime(gain * 0.25, t1 - 0.02); og.gain.linearRampToValueAtTime(0, t1);
  const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 2400;
  o.connect(lp).connect(og).connect(ctx.destination); o.start(t0); o.stop(t1 + 0.05);
}
/** {dur, bpm, kicks: true, riser: [t0, t1], hits: [t...]} -> base64 WAV (16-bit stereo 48 kHz) */
export async function renderSoundtrack({ dur, bpm, kicks = true, riser: rz = null, hits = [] }) {
  const ctx = new OfflineAudioContext(2, Math.ceil(dur * SR), SR);
  if (kicks) for (let t = 0; t < dur - 1e-6; t += 60 / bpm) kick(ctx, t, 0.75);
  if (rz) riser(ctx, rz[0], rz[1]);
  hits.forEach((t, i) => hit(ctx, t, 0.45, 13 + i));
  return toWavBase64(await ctx.startRendering());
}
export function toWavBase64(buf) {
  const ch = buf.numberOfChannels, len = buf.length, bytes = 44 + len * ch * 2, dv = new DataView(new ArrayBuffer(bytes));
  const w = (o, s) => [...s].forEach((c, i) => dv.setUint8(o + i, c.charCodeAt(0)));
  w(0, "RIFF"); dv.setUint32(4, bytes - 8, true); w(8, "WAVE"); w(12, "fmt "); dv.setUint32(16, 16, true); dv.setUint16(20, 1, true);
  dv.setUint16(22, ch, true); dv.setUint32(24, buf.sampleRate, true); dv.setUint32(28, buf.sampleRate * ch * 2, true); dv.setUint16(32, ch * 2, true);
  dv.setUint16(34, 16, true); w(36, "data"); dv.setUint32(40, len * ch * 2, true);
  const data = [...Array(ch)].map((_, c) => buf.getChannelData(c)); let o = 44;
  for (let i = 0; i < len; i++) for (let c = 0; c < ch; c++) { const s = Math.max(-1, Math.min(1, data[c][i])); dv.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true); o += 2; }
  let bin = ""; const u8 = new Uint8Array(dv.buffer);
  for (let i = 0; i < u8.length; i += 0x8000) bin += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  return btoa(bin);
}
