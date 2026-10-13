#!/usr/bin/env python3
"""Split a finished mix into dialogue and music-bed stems, locally (no paid service).

    .venv/bin/python tools/separate.py VIDEO_OR_AUDIO --out DIR

Writes DIR/<stem>.vocals.wav and DIR/<stem>.rest.wav (44.1 kHz stereo float).
rest = mix - vocals, so the two stems always sum back to the original exactly.

Model: UVR-MDX-NET-Voc_FT (ONNX, from github.com/TRvlvr/model_repo, the Ultimate Vocal Remover project, MIT).
It is cached in ~/.cache/osm-models. Inference follows the reference MDX-Net recipe: STFT n_fft 7680, hop 1024,
3072 bins x 256 frames per chunk, overlapping chunks trimmed by n_fft/2, the "denoise" pass (average of f(x) and
-f(-x)), and the model's compensation factor 1.021.
"""
import argparse
import pathlib
import subprocess
import sys

import numpy as np

MODEL_URL = "https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/UVR-MDX-NET-Voc_FT.onnx"
MODEL = pathlib.Path.home() / ".cache/osm-models/UVR-MDX-NET-Voc_FT.onnx"
SR, N_FFT, HOP, DIM_F, DIM_T, COMP = 44100, 7680, 1024, 3072, 256, 1.021
CHUNK = HOP * (DIM_T - 1)
TRIM = N_FFT // 2
GEN = CHUNK - 2 * TRIM
WIN = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N_FFT) / N_FFT)).astype(np.float32)  # periodic Hann (torch)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def write(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_f32le", str(path)],
                   input=np.ascontiguousarray(x.T, np.float32).tobytes(), check=True)


def stft(x):  # x [n, L] -> [n, F, T] complex, torch.stft(center=True, pad_mode="reflect")
    xp = np.pad(x, ((0, 0), (N_FFT // 2, N_FFT // 2)), mode="reflect")
    idx = np.arange(DIM_T)[:, None] * HOP + np.arange(N_FFT)[None]
    return np.fft.rfft(xp[:, idx] * WIN, axis=-1).transpose(0, 2, 1)


def istft(X, length):  # X [n, F, T] -> [n, length]
    frames = np.fft.irfft(X.transpose(0, 2, 1), n=N_FFT, axis=-1) * WIN
    out = np.zeros((X.shape[0], N_FFT + HOP * (X.shape[2] - 1)), np.float64)
    norm = np.zeros(out.shape[1])
    for t in range(X.shape[2]):
        out[:, t * HOP:t * HOP + N_FFT] += frames[:, t]
        norm[t * HOP:t * HOP + N_FFT] += WIN ** 2
    out /= np.maximum(norm, 1e-8)
    return out[:, N_FFT // 2:N_FFT // 2 + length]


def to_spec(chunk):  # [2, CHUNK] -> [1, 4, DIM_F, DIM_T]  (L re, L im, R re, R im)
    X = stft(chunk)[:, :DIM_F]
    return np.stack([X[0].real, X[0].imag, X[1].real, X[1].imag])[None].astype(np.float32)


def from_spec(S):
    S = S[0]
    X = np.zeros((2, N_FFT // 2 + 1, DIM_T), np.complex64)
    X[0, :DIM_F] = S[0] + 1j * S[1]
    X[1, :DIM_F] = S[2] + 1j * S[3]
    return istft(X, CHUNK)


def separate(mix):
    import onnxruntime as ort
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sSL", "--fail", "-o", str(MODEL), MODEL_URL], check=True)
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    n = mix.shape[1]
    pad = GEN - n % GEN
    mp = np.concatenate([np.zeros((2, TRIM)), mix, np.zeros((2, pad)), np.zeros((2, TRIM))], axis=1)
    out = []
    for i in range(0, mp.shape[1] - CHUNK + 1, GEN):
        spec = to_spec(mp[:, i:i + CHUNK])
        pos = sess.run(None, {"input": spec})[0]
        neg = sess.run(None, {"input": -spec})[0]
        wav = from_spec((pos - neg) * 0.5)
        out.append(wav[:, TRIM:-TRIM])
        print(f"  chunk {len(out)}", file=sys.stderr, end="\r")
    voc = np.concatenate(out, axis=1)[:, :n] * COMP
    return voc.astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    mix = load(a.src)
    voc = separate(mix)
    stem = pathlib.Path(a.src).stem
    write(out / f"{stem}.vocals.wav", voc)
    write(out / f"{stem}.rest.wav", mix - voc)
    print(out / f"{stem}.vocals.wav")


if __name__ == "__main__":
    main()
