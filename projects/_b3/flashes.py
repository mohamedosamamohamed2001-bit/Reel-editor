"""Find the old edit's flash / light-leak / glitch spans: frames whose picture jumps (mean abs diff > thr) and
cluster them within 0.4 s. Prints 'a-b' spans (source s). Single hard cuts give 1-frame spans."""
import subprocess, sys, numpy as np
f = sys.argv[1]; thr = float(sys.argv[2]) if len(sys.argv) > 2 else 10
raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-vf","fps=30,scale=36:64","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(raw,np.uint8).reshape(-1,64,36,3).astype(np.int16)
d = np.abs(np.diff(fr, axis=0)).mean(axis=(1,2,3))
ev = [(i+1)/30 for i,x in enumerate(d) if x > thr]
spans = []
for t in ev:
    if spans and t - spans[-1][1] < 0.4: spans[-1][1] = t
    else: spans.append([t, t])
print(" ".join(f"{a:.2f}-{b:.2f}" for a,b in spans))
