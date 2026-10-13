#!/usr/bin/env python3
"""OSM music engine: original, energetic sports tracks synthesised here (numpy + scipy). No samples, no licences.

    .venv/bin/python tools/music.py SPEC.json OUT.wav          # also writes OUT.grid.json (beat/bar/section times)

SPEC = {
  "bpm": 120,                 # 120 bpm = a beat every 15 frames at 30 fps, so cuts can sit exactly on beats
  "key": "D", "mode": "minor",
  "progression": [0, -4, 3, -2],   # chord roots in semitones from the key (i, VI, III, VII by default)
  "style": "trap" | "drive",  # trap = syncopated kick + 808, hats in 16ths/rolls; drive = four-on-the-floor
  "seed": 1,
  "sections": [ {"type": "intro"|"groove"|"build"|"drop"|"break"|"outro", "bars": 2, "stop": true}, ... ],
  "duration": 31.5            # seconds; the track is cut there with a short fade (the outro rings out)
}

Sections:
  intro  - filtered pad, hats, half-time kick: under a first line of dialogue without fighting it
  groove - kick, clap on 2 & 4, hats, 808, light stabs: the bed under most dialogue
  build  - toms + accelerating snare roll + noise riser + opening filter; "stop": true mutes the last beat (the gap before a drop)
  drop   - everything: kick, clap, 16th hats, 808 + reese, supersaw stabs, arp; starts with an impact
  break  - pad + arp only (a reflective line / a breath)
  outro  - final impact on beat 1, ringing pad, nothing after
Phone speakers can't play the sub, so the bass is saturated (harmonics) and doubled by a mid-range reese.
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter, sosfilt

SR = 48000
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


# ---------------- DSP ----------------
def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos"), x, axis=0)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos"), x, axis=0)


def sweep_lp(x, fc, block=256):
    """Low-pass with a time-varying cutoff (fc = array per sample), block-wise with carried state."""
    out = np.zeros_like(x)
    zi = None
    for s in range(0, len(x), block):
        f = float(np.clip(fc[min(s, len(fc) - 1)], 40, SR * 0.45))
        b, a = butter(2, f, "low", fs=SR)
        if zi is None:
            zi = np.zeros((2, x.shape[1])) if x.ndim == 2 else np.zeros(2)
        seg = x[s:s + block]
        y, zi = lfilter(b, a, seg, axis=0, zi=zi)
        out[s:s + block] = y
    return out


def sweep_bp(x, fc, q_oct=1.0, block=256):
    out = np.zeros_like(x)
    zi = np.zeros((4,) + x.shape[1:])
    for s in range(0, len(x), block):
        f = float(np.clip(fc[min(s, len(fc) - 1)], 60, SR * 0.4))
        lo, hi = f / 2 ** (q_oct / 2), min(f * 2 ** (q_oct / 2), SR * 0.45)
        b, a = butter(2, [lo, hi], "band", fs=SR)
        y, zi = lfilter(b, a, x[s:s + block], axis=0, zi=zi)
        out[s:s + block] = y
    return out


def env(n, a, d, curve=1.0):
    e = np.ones(n)
    na = int(a * SR)
    if na:
        e[:min(na, n)] = np.linspace(0, 1, na)[:n]
    if n > na:
        e[na:] = np.exp(-np.arange(n - na) / max(d * SR, 1)) ** curve
    return e


def saw(freq, n, phase0=0.0):
    """Band-limited (polyBLEP) saw. freq: scalar or per-sample array."""
    f = np.broadcast_to(np.asarray(freq, float), (n,))
    dt = f / SR
    ph = (phase0 + np.cumsum(dt)) % 1.0
    y = 2 * ph - 1
    t1 = ph < dt
    t = ph[t1] / dt[t1]
    y[t1] -= t + t - t * t - 1
    t2 = ph > 1 - dt
    t = (ph[t2] - 1) / dt[t2]
    y[t2] -= t * t + t + t + 1
    return y


def sine(freq, n, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, float), (n,))
    return np.sin(2 * np.pi * (phase0 + np.cumsum(f / SR)))


def stereo(x, width=0.0, rng=None):
    if x.ndim == 2:
        return x
    if width <= 0:
        return np.stack([x, x], 1)
    d = int(0.011 * SR * width)  # Haas-style decorrelation for pads/stabs only (never on kick/bass)
    r = np.concatenate([np.zeros(d), x[:-d]]) if d else x
    return np.stack([x * (1 - width * 0.15) + r * width * 0.15, r * (1 - width * 0.15) + x * width * 0.15], 1)


def reverb(x, seconds=1.4, wet=0.2, seed=3):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], 1) * np.exp(-t * 6.9 / seconds)[:, None]
    ir = lp(ir, 6000)
    ir /= np.sqrt((ir ** 2).sum(0))
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    X = np.fft.rfft(x, nfft, axis=0)
    y = np.fft.irfft(X * np.fft.rfft(ir, nfft, axis=0), nfft, axis=0)[:len(x)]
    return x * (1 - wet) + y * wet * 2.2


# ---------------- instruments (mono float arrays) ----------------
class Kit:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)

    def noise(self, n):
        return self.rng.standard_normal(n)

    def kick(self, punch=1.0):
        n = int(0.55 * SR)
        t = np.arange(n) / SR
        f = 46 + 130 * np.exp(-t / 0.035)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.28)
        click = hp(self.noise(int(0.004 * SR)), 2500) * 0.5
        body[:len(click)] += click
        return np.tanh(body * (1.6 + punch)) * 0.9

    def clap(self):
        n = int(0.35 * SR)
        x = np.zeros(n)
        for k, off in enumerate((0, 0.011, 0.023)):
            s = int(off * SR)
            b = self.noise(int(0.012 * SR)) * env(int(0.012 * SR), 0.0005, 0.004)
            x[s:s + len(b)] += b * (0.8 if k < 2 else 1.0)
        tail = self.noise(n) * env(n, 0.0, 0.12)
        tail[:int(0.023 * SR)] = 0
        x += tail * 0.8
        x = bp(x, 800, 4200)
        return reverb(np.stack([x, x], 1), 0.6, 0.18)[:, 0] * 1.6

    def snare(self, vel=1.0):
        n = int(0.28 * SR)
        t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * 190 * t) * env(n, 0.0005, 0.06)
        nz = bp(self.noise(n), 1500, 9000) * env(n, 0.0005, 0.11)
        return np.tanh((tone * 0.6 + nz) * 1.4) * 0.8 * vel

    def hat(self, open_=False, vel=1.0):
        n = int((0.32 if open_ else 0.06) * SR)
        x = lp(hp(self.noise(n), 7000, 4), 11000, 2) * env(n, 0.0005, 0.12 if open_ else 0.018)
        return x * 0.35 * vel

    def tom(self, pitch=110, vel=1.0):
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        f = pitch * (1 + 0.6 * np.exp(-t / 0.03))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.22)
        x += bp(self.noise(n), 300, 2500) * env(n, 0.0005, 0.04) * 0.3
        return np.tanh(x * 2) * 0.8 * vel

    def impact(self):
        n = int(2.4 * SR)
        t = np.arange(n) / SR
        f = 38 + 70 * np.exp(-t / 0.08)
        boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.9)
        crack = bp(self.noise(n), 400, 7000) * env(n, 0.0005, 0.09)
        x = np.tanh((boom * 1.4 + crack * 0.7) * 1.5)
        return reverb(np.stack([x, x], 1), 2.2, 0.28)

    def crash(self):
        n = int(2.0 * SR)
        x = hp(self.noise(n), 4500, 2) * env(n, 0.001, 0.7)
        return stereo(x * 0.35, 0.8)


def supersaw(midi_notes, n, cutoff, voices=5, detune=0.12, rng=None):
    rng = rng or np.random.default_rng(1)
    out = np.zeros((n, 2))
    for m in midi_notes:
        for v in range(voices):
            d = (v - (voices - 1) / 2) / ((voices - 1) / 2 or 1) * detune
            s = saw(hz(m + d), n, rng.random())
            pan = 0.5 + 0.45 * (v - (voices - 1) / 2) / ((voices - 1) / 2 or 1)
            out[:, 0] += s * (1 - pan)
            out[:, 1] += s * pan
    out /= voices * max(1, len(midi_notes)) ** 0.7
    return lp(out, cutoff, 2)


# ---------------- arrangement ----------------
def render(spec):
    bpm = spec.get("bpm", 120)
    beat = 60 / bpm
    bar = beat * 4
    key = NOTE[spec.get("key", "D")]
    minor = spec.get("mode", "minor") == "minor"
    prog = spec.get("progression", [0, -4, 3, -2])
    style = spec.get("style", "trap")
    kit = Kit(spec.get("seed", 1))
    rng = np.random.default_rng(spec.get("seed", 1) + 11)
    sections = spec["sections"]
    # sections may end at an exact time ("until", output seconds): the beat flexes a few % inside that section so
    # its first downbeat lands exactly on the cut it belongs to; otherwise "bars" at the nominal tempo
    t_acc = 0.0
    for sec in sections:
        if "until" in sec:
            d = sec["until"] - t_acc
            sec["_beats"] = max(1, round(d / beat))
            sec["_beat"] = d / sec["_beats"]
        else:
            sec["_beats"] = sec["bars"] * 4
            sec["_beat"] = beat
        t_acc += sec["_beats"] * sec["_beat"]
    dur = spec.get("duration", t_acc)
    N = int((t_acc + 3.0) * SR)
    drums, bass, synth, fx = (np.zeros((N, 2)) for _ in range(4))
    kicks = []  # kick times for the sidechain pump
    grid = {"bpm": bpm, "beat": beat, "bar": bar, "sections": [], "drops": [], "stops": []}

    def put(bus, x, t, gain=1.0, pan=0.0):
        s = int(round(t * SR))
        if s >= N:
            return
        if x.ndim == 1:
            x = np.stack([x * (1 - max(0, pan)), x * (1 + min(0, pan))], 1)
        e = min(N, s + len(x))
        bus[s:e] += x[:e - s] * gain

    def chord_tones(root_off, minor_chord=True):
        r = key + root_off
        third = 3 if minor_chord else 4
        return [r, r + third, r + 7]

    # chord quality for i, VI, III, VII in a minor key: min, maj, maj, maj
    def quality(off):
        return (off % 12) == 0 if minor else (off % 12) in (2, 4, 9)

    t0 = 0.0
    bar_idx = 0
    for si, sec in enumerate(sections):
        typ = sec["type"]
        beat = sec["_beat"]
        bar = beat * 4
        nbeats = sec["_beats"]
        nb = -(-nbeats // 4)
        grid["sections"].append({"type": typ, "start": round(t0, 4), "beats": nbeats, "beat": round(beat, 5)})
        if typ == "drop":
            grid["drops"].append(round(t0, 4))
        for b in range(nb):
            tb = t0 + b * bar
            off = prog[(bar_idx) % len(prog)]
            tones = chord_tones(off, quality(off))
            root = key + off
            last_bar = b == nb - 1
            in_bar = min(4, nbeats - 4 * b)
            stop_beat = sec.get("stop") and last_bar
            if stop_beat:
                grid["stops"].append(round(tb + (in_bar - 1) * beat, 4))
            beats_active = in_bar - 1 if stop_beat else in_bar

            # ---- drums ----
            if typ in ("groove", "drop", "intro", "build"):
                if typ == "intro":
                    kpos = [0, 2]
                elif style == "drive" or typ == "build":
                    kpos = [0, 1, 2, 3]
                else:  # trap: syncopated
                    kpos = [0, 1.75, 2.5] if b % 2 == 0 else [0, 0.75, 2.5, 3.25]
                if typ == "build":
                    kpos = [0, 1, 2, 3] if b < nb - 1 else [0, 0.5, 1, 1.5, 2, 2.5]
                for k in kpos:
                    if k < beats_active:
                        put(drums, kit.kick(1.0 if typ == "drop" else 0.6), tb + k * beat, 0.9 if typ != "intro" else 0.6)
                        kicks.append(tb + k * beat)
            if typ in ("groove", "drop"):
                for k in (1, 3):
                    if k < beats_active:
                        put(drums, kit.clap(), tb + k * beat, 0.55 if typ == "groove" else 0.7)
                        put(drums, kit.snare(0.6), tb + k * beat, 0.25)
            # hats
            if typ in ("intro", "groove", "drop", "build"):
                step = 0.25 if typ == "drop" or (style == "trap" and typ == "groove") else 0.5
                k = 0.0
                while k < beats_active:
                    vel = 1.0 if (k * 4) % 2 == 0 else 0.55
                    if typ == "intro":
                        vel *= 0.6
                    put(drums, kit.hat(False, vel), tb + k * beat, 0.45, pan=0.15)
                    k += step
                if style == "trap" and typ in ("groove", "drop") and b % 2 == 1 and beats_active == 4:
                    for r in range(6):  # 32nd-triplet hat roll on the last beat (trap signature)
                        put(drums, kit.hat(False, 0.5 + r * 0.08), tb + 3 * beat + r * beat / 6, 0.4, pan=0.15)
                if typ == "drive" or style == "drive":
                    for k2 in (0.5, 1.5, 2.5, 3.5):
                        if k2 < beats_active and typ in ("groove", "drop"):
                            put(drums, kit.hat(True, 0.7), tb + k2 * beat, 0.3, pan=-0.1)
            if typ == "build":
                # accelerating snare roll + toms: 8ths, then 16ths, then 32nds in the last bar's second half
                frac = (b + 1) / nb
                div = 2 if frac <= 0.5 else 4
                k = 0.0
                while k < beats_active:
                    if last_bar and k >= 2:
                        div = 8
                    v = 0.35 + 0.65 * ((b * 4 + k) / (nb * 4))
                    put(drums, kit.snare(v), tb + k * beat, 0.5)
                    k += 1 / div
                for i, p in enumerate((150, 120, 95, 80)):
                    if last_bar and i < beats_active:
                        put(drums, kit.tom(p, 0.9), tb + i * beat, 0.6)

            # ---- bass ----
            if typ in ("groove", "drop", "build"):
                bpos = kpos if typ != "build" else [0, 2]
                for i, k in enumerate(bpos):
                    if k >= beats_active:
                        continue
                    nxt = bpos[i + 1] if i + 1 < len(bpos) else 4
                    ln = max(0.12, min(nxt, beats_active) - k) * beat
                    n = int(ln * SR)
                    m0 = root + 24
                    while m0 < 31:
                        m0 += 12
                    f0 = hz(m0)  # fundamental 49-93 Hz: the energy peak of the reference beds is the 63 Hz octave
                    ff = np.full(n, f0)
                    if style == "trap" and typ == "drop" and i == len(bpos) - 1 and b % 2 == 1:
                        ff = f0 * 2 ** (np.linspace(0, 12, n) * (np.arange(n) > n * 0.5) / 12)  # 808 glide up
                    sub = sine(ff, n)
                    e = env(n, 0.003, ln * 0.9 + 0.05) * np.minimum(1, (n - np.arange(n)) / (0.01 * SR))
                    x = np.tanh(sub * e * 2.2) * 0.75
                    put(bass, x, tb + k * beat, 1.0 if typ == "drop" else 0.8)
                if typ == "drop":
                    n = int(beats_active * beat * SR)
                    reese = (saw(hz(root + 36) * 1.003, n) + saw(hz(root + 36) * 0.997, n, 0.5)) * 0.5
                    reese = lp(np.tanh(reese * 1.5), 650) * env(n, 0.01, 4.0)
                    put(bass, stereo(reese * 0.35, 0.3), tb)

            # ---- synths ----
            if typ in ("intro", "break", "groove", "drop", "outro", "build"):
                n = int((beats_active * beat + (0.6 if typ in ("break", "outro") else 0.05)) * SR)
                pad_cut = {"intro": 700, "break": 1600, "groove": 1100, "drop": 2600, "outro": 1800, "build": 900}[typ]
                if typ == "build":
                    pad_cut = 600 + 3200 * (b + 1) / nb
                pad = supersaw([t + 48 for t in tones] + [root + 36], n, pad_cut, voices=5, detune=0.14, rng=rng)
                pad *= env(n, 0.25 if typ in ("intro", "break") else 0.02, 6.0)[:, None]
                put(synth, pad * (0.32 if typ in ("drop", "groove") else 0.42), tb)
            if typ in ("drop", "groove"):
                # off-beat stabs (drop) / sparse stabs (groove)
                pos = [0.5, 1.5, 2.5, 3.0, 3.5] if typ == "drop" else [0.5, 2.5]
                for k in pos:
                    if k >= beats_active:
                        continue
                    n = int(0.22 * SR)
                    st = supersaw([t + 60 for t in tones], n, 3800 if typ == "drop" else 2000, voices=7, detune=0.18, rng=rng)
                    st *= env(n, 0.002, 0.08)[:, None]
                    put(synth, st * (0.55 if typ == "drop" else 0.3), tb + k * beat)
            if typ in ("drop", "break"):
                arp = [tones[0] + 72, tones[1] + 72, tones[2] + 72, tones[1] + 72]
                k = 0.0
                i = 0
                while k < beats_active:
                    n = int(beat / 4 * SR * 0.9)
                    m = arp[i % 4] + (12 if i % 8 == 7 else 0)
                    s = saw(hz(m), n) * 0.6 + saw(hz(m) * 1.005, n, 0.3) * 0.3
                    s = lp(s * env(n, 0.001, 0.05), 3200)
                    put(synth, stereo(s, 0.6), tb + k * beat, 0.16 if typ == "drop" else 0.2, pan=0.2 * (1 if i % 2 else -1))
                    k += 0.25
                    i += 1

            # ---- fx ----
            if typ == "build" and b == 0:
                ln = nbeats * beat - (beat if sec.get("stop") else 0)
                n = int(ln * SR)
                prog_ = np.linspace(0, 1, n) ** 2
                nz = sweep_bp(kit.noise(n), 300 + 9000 * prog_, 1.2) * (0.15 + 0.85 * prog_)
                rise = saw(hz(root + 48) * 2 ** (prog_ * 12 / 12), n) * 0.12 * prog_
                put(fx, stereo(nz * 0.55 + lp(rise, 4000), 0.7), tb)
            if typ == "drop" and b == 0:
                put(fx, kit.impact(), tb, 0.8)
                put(fx, kit.crash(), tb, 0.8)
            if typ == "outro" and b == 0:
                put(fx, kit.impact(), tb, 0.9)
                put(fx, kit.crash(), tb, 0.6)
            bar_idx += 1
        t0 += nbeats * beat

    # sidechain pump on synths + bass reese (classic energy), from the kick times
    pump = np.ones(N)
    for k in kicks:
        s = int(k * SR)
        n = int(0.22 * SR)
        e = 1 - 0.55 * np.exp(-np.arange(n) / (0.07 * SR))
        seg = pump[s:s + n]
        pump[s:s + n] = np.minimum(seg, e[:len(seg)])
    synth *= pump[:, None]
    # intro / build filter on the whole bed is applied per section via pad cutoffs; master chain:
    mix = drums * 1.0 + bass * 0.95 + synth * 0.9 + fx * 0.8
    mix = hp(mix, 28, 2)
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)  # glue saturation
    end = int(dur * SR)
    mix = mix[:end]
    fade = int(0.25 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    mix /= max(1e-9, np.abs(mix).max()) / 0.89  # -1 dBFS peak; final level is set by the edit's mix
    grid["duration"] = round(dur, 4)
    return mix.astype(np.float32), grid


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    spec = json.load(open(sys.argv[1]))
    out = Path(sys.argv[2])
    mix, grid = render(spec)
    write_wav(out, mix)
    json.dump(grid, open(out.with_suffix(".grid.json"), "w"), indent=1)
    print(out, f"{len(mix) / SR:.2f}s", "drops", grid["drops"])


if __name__ == "__main__":
    main()
