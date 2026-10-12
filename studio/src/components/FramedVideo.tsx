import { Easing, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Clip } from "../lib/edit";

/**
 * Smart vertical framing for one clip: cover-scale, punch-in (zoom), and a focus point kept at centre.
 * Edges are clamped so the frame never shows outside the source. Without srcW/srcH it falls back to centre cover.
 */
export const FramedVideo: React.FC<{ clip: Clip; durationInFrames: number; startFrom: number }> = ({ clip, durationInFrames, startFrom }) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  const url = staticFile(clip.src);
  const volume = clip.volume ?? 1;

  if (!clip.srcW || !clip.srcH) {
    return <OffthreadVideo src={url} startFrom={startFrom} volume={volume} style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
  }
  const z = Array.isArray(clip.zoom)
    ? interpolate(frame, [0, Math.max(1, durationInFrames - 1)], clip.zoom, { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : clip.zoom ?? 1;
  const s = Math.max(W / clip.srcW, H / clip.srcH) * z;
  const dw = clip.srcW * s;
  const dh = clip.srcH * s;
  const left = Math.min(0, Math.max(W - dw, W / 2 - (clip.focusX ?? 0.5) * dw));
  const top = Math.min(0, Math.max(H - dh, H / 2 - (clip.focusY ?? 0.5) * dh));
  // punch "settle": the cut lands slightly over-scaled and eases to rest, like a camera finding its frame
  const settle = clip.settle
    ? interpolate(frame, [0, 10], [clip.settle, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })
    : 1;
  if (clip.frames) {
    // image-sequence plate: shown 1:1 (OffthreadVideo extraction measured ~7x softer)
    const idx = Math.min(clip.frames.count, Math.max(1, startFrom + frame + 1));
    return (
      <div style={{ position: "absolute", inset: 0, overflow: "hidden", transform: settle !== 1 ? `scale(${settle})` : undefined }}>
        <Img src={staticFile(`${clip.src}/${String(idx).padStart(5, "0")}.jpg`)} style={{ position: "absolute", left, top, width: dw, height: dh, maxWidth: "none" }} />
      </div>
    );
  }
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <OffthreadVideo src={url} startFrom={startFrom} volume={volume} style={{ position: "absolute", left, top, width: dw, height: dh, maxWidth: "none" }} />
    </div>
  );
};
