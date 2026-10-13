#!/usr/bin/env python3
"""OSM sound-design kit: every effect is synthesised here (numpy only), so there are no third-party samples or licences.

Each sound returns (stereo float32 array [n, 2] at 48 kHz, hit_index). `hit_index` is the sample that must land on the
visual event (a whoosh's peak, an impact's transient), so cues are placed by their hit, not by the file start.

Design rules (see projects/*/analysis/upgrade_plan_v3.md): layered = transient + tone/texture + sub (major only) + tail;
nothing occupies the speech presence band for long; peaks are normalised per sound and levelled by the cue gain.

    python3 tools/sfx.py OUT_DIR      # writes every sound as a WAV for auditioning
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
RNG = np.random.default_rng(7)  # deterministic: the same edit always renders the same sounds


# ---------- DSP helpers ----------
def _t(n):
    return np.arange(n) / SR


def _stft_filter(x, gain_fn, n_fft=1024, hop=256):
    """Time-varying spectral filter. gain_fn(frame_time_s, freqs) -> gains for that frame."""
    win = np.hanning(n_fft).astype(np.float64)
    pad = np.concatenate([np.zeros(n_fft), x, np.zeros(n_fft)])
    out = np.zeros_like(pad)
    norm = np.zeros_like(pad)
    freqs = np.fft.rfftfreq(n_fft, 1 / SR)
    for start in range(0, len(pad) - n_fft, hop):
        seg = pad[start:start + n_fft] * win
        spec = np.fft.rfft(seg) * gain_fn((start - n_fft + n_fft / 2) / SR, freqs)
        out[start:start + n_fft] += np.fft.irfft(spec, n_fft) * win
        norm[start:start + n_fft] += win ** 2
    out /= np.maximum(norm, 1e-6)
    return out[n_fft:n_fft + len(x)]


def _band(freqs, centre, width_oct):
    """Smooth band-pass gain around `centre` Hz, `width_oct` octaves wide."""
    with np.errstate(divide="ignore"):
        d = np.log2(np.maximum(freqs, 1) / centre) / (width_oct / 2)
    return np.exp(-0.5 * d * d)


def _lowpass(freqs, fc, order=2):
    return 1 / np.sqrt(1 + (freqs / max(fc, 1)) ** (2 * order))


def _highpass(freqs, fc, order=2):
    with np.errstate(divide="ignore"):
        return 1 / np.sqrt(1 + (max(fc, 1) / np.maximum(freqs, 1e-3)) ** (2 * order))


def _env(n, attack, release, curve=3.0):
    """Attack/release envelope (seconds) with exponential-ish shape."""
    a = int(attack * SR)
    e = np.ones(n)
    if a > 0:
        e[:a] = (np.arange(a) / a) ** curve
    r = n - a
    if r > 0:
        e[a:] = np.exp(-np.arange(r) / (release * SR))
    return e


def _fade_end(x, ms=12):
    """Fade the last `ms` to zero: a layer cut while still audible clicks (seen as vertical lines in a spectrogram)."""
    k = min(len(x), int(ms / 1000 * SR))
    x = np.array(x, dtype=np.float64, copy=True)
    x[len(x) - k:] *= np.linspace(1, 0, k)[:, None] if x.ndim == 2 else np.linspace(1, 0, k)
    return x


def _reverb(x, seconds=0.9, damp=4000, wet=0.25):
    """Short stereo room tail: decorrelated decaying-noise IRs, FFT-convolved."""
    x = _fade_end(x)
    n_ir = int(seconds * SR)
    out = []
    for ch in range(2):
        ir = RNG.standard_normal(n_ir) * np.exp(-np.arange(n_ir) / (seconds * SR / 6.9))
        ir = np.fft.irfft(np.fft.rfft(ir) * _lowpass(np.fft.rfftfreq(n_ir, 1 / SR), damp), n_ir)
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        n = len(x) + n_ir
        y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)
        out.append(y)
    dry = np.pad(x, (0, n_ir))
    return np.stack([dry * (1 - wet) + out[0] * wet, dry * (1 - wet) + out[1] * wet], axis=1)


def _stereo(x, width_ms=0.0, pan=0.0):
    """Mono -> stereo with optional Haas width and constant-power pan (-1..1)."""
    d = int(width_ms / 1000 * SR)
    l, r = x, np.concatenate([np.zeros(d), x])[:len(x)] if d else x
    a = (pan + 1) * np.pi / 4
    return np.stack([l * np.cos(a), r * np.sin(a)], axis=1)


def _norm(s, peak_db=-1.0):
    s = _fade_end(s, 8)
    p = np.max(np.abs(s)) + 1e-9
    return (s / p * 10 ** (peak_db / 20)).astype(np.float32)


# ---------- sounds ----------
def air(dur=0.42, lo=500, hi=2600):
    """Soft air movement (minor transitions). Peak at ~60% of the duration."""
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    pk = 0.6 * dur
    y = _stft_filter(x, lambda t, f: _band(f, lo * (hi / lo) ** np.clip(t / dur, 0, 1), 1.4) * _highpass(f, 180))
    e = np.exp(-0.5 * ((_t(n) - pk) / (dur * 0.22)) ** 2)
    return _norm(_stereo(y * e, width_ms=0.4)), int(pk * SR)


def whoosh_in(dur=0.62):
    """Cinematic whoosh building into a landing (major transition). Peak (hit) at 85%."""
    n = int(dur * SR)
    x = RNG.standard_normal(n)
    pk = 0.85 * dur
    body = _stft_filter(x, lambda t, f: _lowpass(f, 300 * (7000 / 300) ** np.clip(t / pk, 0, 1), 2) * _highpass(f, 120))
    e = np.where(_t(n) < pk, (_t(n) / pk) ** 2.6, np.exp(-(_t(n) - pk) / 0.05))
    sub = np.sin(2 * np.pi * (70 - 25 * np.clip(_t(n) / dur, 0, 1)) * _t(n)) * e * 0.35
    l = body * e
    r = np.concatenate([np.zeros(18), body])[:n] * e  # tiny Haas for width
    return _norm(np.stack([l + sub, r + sub], axis=1)), int(pk * SR)


def whoosh_out(dur=0.36):
    """Quick air pull-away (card exit). Hit at 25%."""
    s, _ = air(dur, lo=2200, hi=600)
    return s, int(0.25 * dur * SR)


def swell(dur=0.55, root=196.0):
    """Reverse-swell pad rising into a moment (anticipation). Hit = last sample."""
    n = int(dur * SR)
    t = _t(n)
    chord = [root, root * 1.5, root * 2, root * 2.52]  # root, fifth, octave, major-ish tenth (soft, consonant)
    pad = sum(np.sin(2 * np.pi * f * t * (1 + 0.003 * np.sin(2 * np.pi * 0.7 * t))) / (i + 1) for i, f in enumerate(chord))
    noise = _stft_filter(RNG.standard_normal(n), lambda tt, f: _band(f, 900 + 2500 * tt / dur, 1.6))
    e = (t / dur) ** 3.2
    y = (pad * 0.6 + noise * 0.4) * e
    y[-int(0.004 * SR):] *= np.linspace(1, 0, int(0.004 * SR))  # clean cut on the hit
    return _norm(_stereo(y, width_ms=0.6)), n - 1


def thump(freq=58, dur=0.5):
    """Soft low thump (weight under a landing). Hit at 0."""
    n = int(dur * SR)
    t = _t(n)
    f = freq + 40 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    y[:96] *= np.linspace(0, 1, 96)
    return _norm(_stereo(y)), 0


def impact(dur=1.6):
    """Layered cinematic impact for the end card: transient + 55 Hz body + textured tail. Hit at 0."""
    n = int(1.4 * SR)  # body decays by exp(-1.4/0.28) ≈ -43 dB before the end fade
    t = _t(n)
    trans = _stft_filter(RNG.standard_normal(n), lambda tt, f: _lowpass(f, 4500) * _highpass(f, 400)) * np.exp(-t / 0.012)
    f = 55 + 70 * np.exp(-t / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    tex = _stft_filter(RNG.standard_normal(n), lambda tt, f: _band(f, 1200, 2.0)) * np.exp(-t / 0.09)
    dry = trans * 0.55 + body * 1.0 + tex * 0.25
    dry[:48] *= np.linspace(0, 1, 48)
    y = _reverb(dry, seconds=max(0.4, dur - 0.6), damp=3500, wet=0.22)
    return _norm(y), 0


def click(freq=2400, dur=0.06):
    """Refined UI click (tap / CTA). Hit at 0."""
    n = int(dur * SR)
    t = _t(n)
    tick = _stft_filter(RNG.standard_normal(n), lambda tt, f: _highpass(f, 2500)) * np.exp(-t / 0.0025)
    tone = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.012)
    body = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.02) * 0.4
    return _norm(_stereo(tick * 0.5 + tone * 0.6 + body)), 0


def key_tick():
    """Micro keystroke tick (very quiet in the mix). Hit at 0."""
    n = int(0.035 * SR)
    t = _t(n)
    x = _stft_filter(RNG.standard_normal(n), lambda tt, f: _band(f, 3800, 1.2)) * np.exp(-t / 0.004)
    x += np.sin(2 * np.pi * 1300 * t) * np.exp(-t / 0.006) * 0.3
    return _norm(_stereo(x)), 0


def blip(freq=880.0, dur=0.22):
    """Soft select blip (highlights): sine + octave partial, quick decay, tiny tail. Hit at 0."""
    n = int(max(dur, 0.32) * SR)  # 0.045 s decay needs ~0.3 s to reach -60 dB
    t = _t(n)
    y = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t)) * np.exp(-t / 0.045)
    y[:72] *= np.linspace(0, 1, 72)
    return _norm(_reverb(y, seconds=0.35, damp=6000, wet=0.15)), 0


def chime(f1=659.25, f2=987.77):
    """Two-note confirm (results ready): E5 then B5, 70 ms apart. Hit at 0."""
    a, _ = blip(f1, 0.3)
    b, _ = blip(f2, 0.4)
    d = int(0.07 * SR)
    out = np.zeros((max(len(a), d + len(b)), 2), np.float32)
    out[:len(a)] += a * 0.8
    out[d:d + len(b)] += b
    return _norm(out), 0


def accent(freq=523.25):
    """Tonal accent for a key word (Method): bell-like partials + a light sub tap. Hit at 0."""
    n = int(2.4 * SR)  # longest partial (0.5 s) decays ~-42 dB by the end fade
    t = _t(n)
    partials = [(1, 1.0, 0.5), (2.01, 0.45, 0.3), (3.0, 0.2, 0.18), (4.2, 0.1, 0.1)]
    y = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t / d) for m, a, d in partials)
    y[:96] *= np.linspace(0, 1, 96)
    sub = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.07) * 0.5
    return _norm(_reverb(y * 0.8 + sub, seconds=0.6, damp=5000, wet=0.2)), 0



# ---------- v4: power transitions (the collection upgrade: "transitions must sound powerful") ----------
def whip(dur=0.3, dir=1.0, bright=6500):
    """Punchy whip-pan whoosh: fast band sweep up then down, peak at 55 %, panned across with the motion (dir = +1
    left->right, -1 right->left), a low thwump on the peak so it has weight on phones too. Hit = the peak."""
    n = int(dur * SR)
    t = _t(n)
    pk = 0.55 * dur
    u = np.clip(t / pk, 0, 1)
    v = np.clip((t - pk) / (dur - pk), 0, 1)
    centre = lambda tt: 500 * (bright / 500) ** min(1, tt / pk) if tt < pk else bright * (1400 / bright) ** min(1, (tt - pk) / (dur - pk))
    body = _stft_filter(RNG.standard_normal(n), lambda tt, f: _band(f, centre(tt), 1.8) * _highpass(f, 150), n_fft=512, hop=128)
    e = np.where(t < pk, u ** 3.0, np.exp(-(t - pk) / (0.18 * (dur - pk) + 1e-3)))
    thw = np.sin(2 * np.pi * np.cumsum(90 + 60 * np.exp(-np.abs(t - pk) / 0.02)) / SR) * np.exp(-np.abs(t - pk) / 0.035) * 0.45
    y = body * e + thw
    pan = np.clip(-dir + 2 * dir * t / dur, -1, 1)  # sweeps across the stereo field
    a = (pan + 1) * np.pi / 4
    return _norm(np.stack([y * np.cos(a), y * np.sin(a)], axis=1)), int(pk * SR)


def boom(dur=2.4, freq=42.0, drive=3.5):
    """Deep cinematic impact: pitch-dropping sub (120 -> 42 Hz) saturated for audible harmonics on small speakers,
    a sharp crack, a noise burst and a long dark tail. The biggest sound in the kit (hooks, drops, end card). Hit at 0."""
    n = int(dur * SR)
    t = _t(n)
    f = freq + 80 * np.exp(-t / 0.05)
    sub = np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.55) * drive) / np.tanh(drive)
    crack = _stft_filter(RNG.standard_normal(n), lambda tt, fr: _lowpass(fr, 7000) * _highpass(fr, 700), n_fft=512, hop=128) * np.exp(-t / 0.008)
    burst = _stft_filter(RNG.standard_normal(n), lambda tt, fr: _lowpass(fr, 2500 * np.exp(-tt / 0.25) + 200)) * np.exp(-t / 0.16)
    # knock: the 120-250 Hz body that a phone speaker actually reproduces (the sub alone vanishes on phones)
    knock = np.tanh(np.sin(2 * np.pi * np.cumsum(150 + 90 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.09) * 2.5)
    dry = sub * 1.0 + knock * 0.55 + crack * 0.8 + burst * 0.35
    dry[:24] *= np.linspace(0, 1, 24)
    y = _reverb(dry, seconds=1.8, damp=2500, wet=0.3)
    return _norm(y), 0


def riser(dur=1.0, lo=400, hi=9000):
    """Short tension riser into a hit: noise band sweeping up, two rising tones a fifth apart, tremolo speeding up.
    Hit = the last sample (stops dead on the cut/drop)."""
    n = int(dur * SR)
    t = _t(n)
    u = t / dur
    nz = _stft_filter(RNG.standard_normal(n), lambda tt, fr: _band(fr, lo * (hi / lo) ** min(1, tt / dur), 1.2))
    f1 = 220 * 2 ** (u * 1.5)
    tone = np.sin(2 * np.pi * np.cumsum(f1) / SR) + 0.6 * np.sin(2 * np.pi * np.cumsum(f1 * 1.5) / SR)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(4 + 26 * u ** 2) / SR)
    y = (nz * 0.8 + tone * 0.18) * u ** 2.2 * trem
    y[-int(0.003 * SR):] *= np.linspace(1, 0, int(0.003 * SR))
    return _norm(_stereo(y, width_ms=0.8)), n - 1


def slam(dur=0.5, freq=120.0):
    """Text slam: a hard transient, a mid punch (120 Hz falling), a snare-ish noise snap and a tight room. Hit at 0."""
    n = int(dur * SR)
    t = _t(n)
    punch = np.tanh(np.sin(2 * np.pi * np.cumsum(freq * (1 + 0.8 * np.exp(-t / 0.015))) / SR) * np.exp(-t / 0.09) * 2.0)
    snap = _stft_filter(RNG.standard_normal(n), lambda tt, fr: _band(fr, 2500, 2.2)) * np.exp(-t / 0.035)
    tick = _stft_filter(RNG.standard_normal(n), lambda tt, fr: _highpass(fr, 3000)) * np.exp(-t / 0.003)
    dry = punch * 0.9 + snap * 0.45 + tick * 0.4
    dry[:16] *= np.linspace(0, 1, 16)
    return _norm(_reverb(dry, seconds=0.5, damp=5000, wet=0.15)), 0


def mech(dur=0.42):
    """Futuristic mechanical lock: three servo clicks 45 ms apart over a short rising filtered whir. Hit at 0."""
    n = int(dur * SR)
    t = _t(n)
    y = np.zeros(n)
    for k, off in enumerate((0.0, 0.045, 0.09)):
        s = int(off * SR)
        m = int(0.012 * SR)
        c = _stft_filter(RNG.standard_normal(m), lambda tt, fr: _band(fr, 3200 + 900 * k, 1.0), n_fft=256, hop=64) * np.exp(-_t(m) / 0.0025)
        y[s:s + m] += c * (1.0 - 0.15 * k)
    ph = np.cumsum(300 + 700 * np.clip(t / 0.25, 0, 1)) / SR
    saw = 2 * (ph % 1) - 1
    whir = _stft_filter(saw, lambda tt, fr: _band(fr, 1200, 1.5), n_fft=512, hop=128) * np.exp(-((t - 0.12) / 0.08) ** 2) * 0.35
    return _norm(_stereo(y + whir, width_ms=0.5)), 0


def bass_drop(dur=1.3, f0=95.0, f1=38.0):
    """808 drop: sine gliding f0 -> f1, saturated (harmonics reach phone speakers), long decay. Hit at 0."""
    n = int(dur * SR)
    t = _t(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.18)
    y = np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 2.5) * np.exp(-t / 0.5)
    y[:48] *= np.linspace(0, 1, 48)
    return _norm(_stereo(y)), 0


def reverse_hit(dur=0.7):
    """Reversed impact tail sucking into the cut (pre-drop). Hit = the last sample."""
    s, _ = impact(dur=1.6)
    k = int(dur * SR)
    y = s[:k][::-1].copy()
    y *= (np.linspace(0, 1, k) ** 1.5)[:, None]
    y[-int(0.003 * SR):] *= np.linspace(1, 0, int(0.003 * SR))[:, None]
    return _norm(y), k - 1


SOUNDS = {
    "air": air, "whoosh_in": whoosh_in, "whoosh_out": whoosh_out, "swell": swell, "thump": thump, "impact": impact,
    "click": click, "key": key_tick, "blip": blip, "chime": chime, "accent": accent,
    "whip": whip, "boom": boom, "riser": riser, "slam": slam, "mech": mech, "bass_drop": bass_drop, "reverse_hit": reverse_hit,
}


def make(name, **kw):
    if name not in SOUNDS:
        raise SystemExit(f"unknown sound '{name}' (have: {', '.join(SOUNDS)})")
    return SOUNDS[name](**kw)


def write_wav(path, stereo):
    data = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def render_cues(cues, total, fps):
    """Mix cues into one stereo bus. cue: {"at": seconds, "sound": name, "gain_db": -18, ...sound kwargs}.

    Cue times are snapped to the frame grid (round(at * fps) / fps) so a sound can't drift off its visual frame.
    The sound's hit sample lands exactly on that frame time.
    """
    bus = np.zeros((int(total * SR) + SR, 2), np.float32)
    placed = []
    for c in cues:
        kw = {k: v for k, v in c.items() if k not in ("at", "sound", "gain_db", "note")}
        s, hit = make(c["sound"], **kw)
        frame_t = round(c["at"] * fps) / fps
        start = int(round(frame_t * SR)) - hit
        g = 10 ** (c.get("gain_db", -18) / 20)
        a, b = max(0, start), min(len(bus), start + len(s))
        if b > a:
            bus[a:b] += s[a - start:b - start] * g
        placed.append((c["sound"], round(frame_t, 3)))
    return bus[:int(total * SR)], placed


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "sfx_audition")
    out.mkdir(parents=True, exist_ok=True)
    for name in SOUNDS:
        s, hit = make(name)
        write_wav(out / f"{name}.wav", s)
        print(f"{name:10s} {len(s) / SR:5.2f}s hit@{hit / SR:.3f}s peak {20 * np.log10(np.max(np.abs(s)) + 1e-9):.1f} dBFS")
