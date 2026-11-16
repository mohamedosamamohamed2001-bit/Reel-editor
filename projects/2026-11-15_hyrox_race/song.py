"""The reference song (from Vedio1.mov, his explicit request) fitted to the edit's 105 bpm grid: work/song.wav.

Song tempo measured 105.25 bpm (spectral-flux autocorrelation), beat phase refined on its onsets. Steps: time-stretch by
105/105.25 (atempo, pitch kept) so song beats land on the edit's frame-snapped beat grid; part A = song beats 2-42 placed at edit
beat 0 (the song's drop, song beat 10, lands on the edit's first drop, beat 8 = SkiErg); part B = song beats 8-33 placed at edit
beat 40 (its drop lands on the edit's second drop, beat 42 = sandbag lunges); 20 ms crossfade at the join; fade-out under the iris.
"""
import subprocess, sys
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent
SR = 48000
BPM_SONG, BPM_EDIT = 105.25, 105.0


def onset_phase(x, sr, bpm):
    hop = 256; win = np.hanning(1024); prev = None; env = []
    for i in range(0, len(x) - 1024, hop):
        s = np.abs(np.fft.rfft(x[i:i + 1024] * win))
        if prev is not None:
            env.append(np.maximum(s - prev, 0).sum())
        prev = s
    env = np.array(env); fps = sr / hop; per = 60 / bpm * fps
    best = max(np.arange(0, per, 0.1), key=lambda o: np.interp(np.arange(o, len(env) - 1, per), np.arange(len(env)), env).sum())
    return (best + 1) / fps            # +1: env[i] is the flux between frames i and i+1


def main(total_s, fade_at):
    w = P / "work"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(P / "ref" / "Vedio1.mov"), "-vn", "-ac", "1", "-ar", "22050", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    ph = onset_phase(np.frombuffer(raw, np.float32), 22050, BPM_SONG)
    k = BPM_EDIT / BPM_SONG
    st = w / "song_stretched.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(P / "ref" / "Vedio1.mov"), "-vn", "-af", f"aresample={SR},atempo={k:.6f}",
                    "-c:a", "pcm_s24le", str(st)], check=True)
    beat_e = 60 / BPM_EDIT
    ts = lambda b: (ph + b * 60 / BPM_SONG) / k        # song beat -> time in the stretched song
    te = lambda b: b * beat_e                           # edit beat -> output time (cuts are frame-snapped to this grid)
    SYNC = 0.028                                        # measured: song kicks sat 28 ms ahead of the cut grid -> play it 28 ms later
    a0, a1, b0 = ts(2) - SYNC, ts(42) - SYNC, ts(8) - SYNC
    lenA, lenB = te(40), total_s - te(40)
    xf = 0.02
    pa, pb = w / "song_A.wav", w / "song_B.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(st), "-af", f"atrim=start={a0:.4f}:end={a0 + lenA + xf:.4f},asetpts=PTS-STARTPTS",
                    "-c:a", "pcm_s24le", str(pa)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(st), "-af", f"atrim=start={b0:.4f}:end={b0 + lenB + 0.05:.4f},asetpts=PTS-STARTPTS",
                    "-c:a", "pcm_s24le", str(pb)], check=True)
    g = (f"[0:a][1:a]acrossfade=d={xf}:c1=tri:c2=tri,atrim=end={total_s:.4f},"
         f"afade=t=out:st={fade_at:.3f}:d={max(0.1, total_s - fade_at):.3f}[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pa), "-i", str(pb), "-filter_complex", g, "-map", "[o]", "-c:a", "pcm_s24le",
                    str(w / "song.wav")], check=True)
    print(f"song phase {ph:.3f}s; A {a0:.3f}-{a0 + lenA:.3f}s, B from {b0:.3f}s; song.wav {total_s:.2f}s")
    return w / "song.wav"


if __name__ == "__main__":
    main(float(sys.argv[1]), float(sys.argv[2]))
