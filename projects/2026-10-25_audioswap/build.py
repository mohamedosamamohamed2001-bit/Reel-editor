"""Video 2 (main, HLG HDR) + the exact audio of Video 1 + the OSM caption for the first 7 s.

- Picture: Video 2's own frames, 1080x1920, 30 fps, 687 frames, untouched except the caption overlay (0-7 s).
  Kept 10-bit HLG/BT.2020 (no grade, no tone-mapping); libx265 CRF 10 slow, same tags.
- Caption: caption.png (rendered by caption.js, sRGB #56A0FB bar + #FFFFFF text) converted to HLG with BT.2408
  placement (SDR white = 75 % HLG), shown from frame 0, 0.2 s fade-out ending at 7.0 s.
- Audio: Video 1's track, decoded and placed sample-exact: its sound (22.883 s, from sample 17625) starts 8 ms in.
  Only the digital silence before/after was trimmed; no gain, EQ or limiting. Encoded AAC 320k 44.1 kHz.

    python3 build.py
"""
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
V1, V2 = P / "source" / "video1.mp4", P / "source" / "video2.mov"
CAP = P / "work" / "caption.png"
OUT = P / "renders" / "OSM_Video2_with_Video1_audio.mov"
SR, FIRST_SOUND, LEAD = 44100, 17625, 353          # samples
DUR = 22.9                                          # Video 2 length (687 frames @ 30 fps)
CAP_END, CAP_FADE = 7.0, 0.2


def run(c):
    subprocess.run(c, check=True)


OUT.parent.mkdir(exist_ok=True)
start = (FIRST_SOUND - LEAD) / SR
aud = P / "work" / "audio.m4a"
run(["ffmpeg", "-v", "error", "-y", "-i", str(V1), "-map", "0:a", "-af",
     f"aresample={SR},atrim=start_sample={FIRST_SOUND - LEAD},asetpts=PTS-STARTPTS,apad,atrim=duration={DUR}",
     "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), str(aud)])

x265 = ("crf=10:preset=slow:keyint=30:min-keyint=30:no-scenecut=1:colorprim=bt2020:transfer=arib-std-b67:"
        "colormatrix=bt2020nc:range=limited:repeat-headers=1:aud=1:log-level=error")
fc = (f"[1:v]format=gbrap,zscale=tin=iec61966-2-1:pin=bt709:min=gbr:t=arib-std-b67:p=bt2020:m=bt2020nc:r=limited:npl=203,"
      f"format=yuva444p10le,fade=t=out:st={CAP_END - CAP_FADE}:d={CAP_FADE}:alpha=1[cap];"
      f"[0:v][cap]overlay=0:0:format=yuv420p10:enable='lt(t,{CAP_END})',format=yuv420p10le[v]")
vid = P / "work" / "video.mov"
run(["ffmpeg", "-v", "error", "-y", "-i", str(V2), "-loop", "1", "-framerate", "30", "-t", str(CAP_END), "-i", str(CAP),
     "-filter_complex", fc, "-map", "[v]", "-c:v", "libx265", "-preset", "slow", "-x265-params", x265,
     "-pix_fmt", "yuv420p10le", "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc",
     "-color_range", "tv", "-tag:v", "hvc1", "-an", str(vid)])
run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(aud), "-map", "0:v", "-map", "1:a", "-c", "copy",
     "-tag:v", "hvc1", "-movflags", "+faststart", str(OUT)])
print(OUT, f"audio from Video 1 starts at {start:.4f} s of its track")
