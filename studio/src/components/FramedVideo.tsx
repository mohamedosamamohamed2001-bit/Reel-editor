import { Easing, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Clip, Transition } from "../lib/edit";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Default frames on each side of the cut. */
const sideFrames = (t: Transition) => t.frames ?? (t.type === "whip" ? 4 : t.type === "zoom" ? 5 : 0);

type Pose = { dx: number; dy: number; s: number; bright: number };
const REST: Pose = { dx: 0, dy: 0, s: 1, bright: 0 };

/**
 * Where the picture is on local frame `fr` of a clip `len` frames long, given its entrance and exit transitions.
 * Whip: displacement grows with the cube of the distance to the cut (accelerating out, decelerating in), so most
 * of the travel happens in the frame or two next to the cut, where motion blur hides the join.
 */
const pose = (fr: number, len: number, W: number, H: number, tin?: Transition, tout?: Transition): Pose => {
  const p = { ...REST };
  const apply = (t: Transition, k: number, entering: boolean) => {
    // k: 0 = the frame touching the cut, N-1 = the first frame of the move
    const N = sideFrames(t);
    if (!N || k >= N) return;
    const e = Math.pow((N - k) / (N + 1), 3); // 0 → ~1 towards the cut
    if (t.type === "whip") {
      const dir = t.dir ?? "left";
      const D = (dir === "left" || dir === "right" ? W : H) * 0.9;
      const sign = dir === "left" || dir === "up" ? -1 : 1; // direction of travel
      // outgoing leaves in the travel direction; incoming arrives from the opposite side, moving the same way
      const d = (entering ? -1 : 1) * sign * D * e;
      if (dir === "left" || dir === "right") p.dx += d;
      else p.dy += d;
      p.s *= 1 + 0.08 * e;
    } else if (t.type === "zoom") {
      p.s *= entering ? 1 + 0.45 * e : 1 + 0.6 * e;
      p.bright += 0.55 * e;
    }
  };
  if (tin) apply(tin, fr, true);
  if (tout) apply(tout, len - 1 - fr, false);
  return p;
};

/**
 * Smart vertical framing for one clip: cover-scale, punch-in (zoom), and a focus point kept at centre.
 * Edges are clamped so the frame never shows outside the source. Without srcW/srcH it falls back to centre cover.
 * tin/tout: the transition into this clip and out of it (motion-blurred whip / zoom punch).
 */
export const FramedVideo: React.FC<{ clip: Clip; durationInFrames: number; startFrom: number; tout?: Transition;
  /** foreground pass (behind-the-head titles): only local frames [a, b), drawn from clip.fg (RGBA PNG cut-outs of the
   * same plate frames), with the exact same geometry, settle and transitions as the picture under it */
  fgWindow?: [number, number];
}> = ({
  clip, durationInFrames, startFrom, tout, fgWindow,
}) => {
  const frame = useCurrentFrame();
  const { width: W, height: H } = useVideoConfig();
  if (fgWindow && (frame < fgWindow[0] || frame >= fgWindow[1] || !clip.fg)) return null;
  const url = staticFile(clip.src);
  const volume = clip.volume ?? 1;

  if (!clip.srcW || !clip.srcH) {
    return <OffthreadVideo src={url} startFrom={startFrom} volume={volume} style={{ width: "100%", height: "100%", objectFit: "cover" }} />;
  }
  const zoomAt = (fr: number) =>
    Array.isArray(clip.zoom)
      ? interpolate(fr, [0, Math.max(1, durationInFrames - 1)], clip.zoom, clamp)
      : clip.zoom ?? 1;
  const geom = (fr: number) => {
    const s = Math.max(W / clip.srcW!, H / clip.srcH!) * zoomAt(fr);
    const dw = clip.srcW! * s;
    const dh = clip.srcH! * s;
    const left = Math.min(0, Math.max(W - dw, W / 2 - (clip.focusX ?? 0.5) * dw));
    const top = Math.min(0, Math.max(H - dh, H / 2 - (clip.focusY ?? 0.5) * dh));
    return { dw, dh, left, top };
  };
  const { dw, dh, left, top } = geom(frame);
  // punch "settle": the cut lands slightly over-scaled and eases to rest, like a camera finding its frame
  const settle = clip.settle ? interpolate(frame, [0, 10], [clip.settle, 1], { ...clamp, easing: Easing.out(Easing.cubic) }) : 1;

  if (!clip.frames) {
    return (
      <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
        <OffthreadVideo src={url} startFrom={startFrom} volume={volume} style={{ position: "absolute", left, top, width: dw, height: dh, maxWidth: "none" }} />
      </div>
    );
  }
  // image-sequence plate: shown 1:1 (OffthreadVideo extraction measured ~7x softer)
  const idx = Math.min(clip.frames.count, Math.max(1, startFrom + frame + 1));
  const src = fgWindow ? staticFile(`${clip.fg}/${String(idx).padStart(5, "0")}.png`) : staticFile(`${clip.src}/${String(idx).padStart(5, "0")}.jpg`);
  const now = pose(frame, durationInFrames, W, H, clip.tin, tout);
  const moving = now.dx !== 0 || now.dy !== 0 || now.s !== 1;

  if (!moving) {
    return (
      <div style={{ position: "absolute", inset: 0, overflow: "hidden", transform: settle !== 1 ? `scale(${settle})` : undefined }}>
        <Img src={src} style={{ position: "absolute", left, top, width: dw, height: dh, maxWidth: "none" }} />
      </div>
    );
  }

  // Motion blur: average K sub-frame poses between the previous frame and this one (shutter 360°). Layer i drawn
  // with opacity 1/(i+1) over the ones below makes every layer count equally.
  const prev = pose(frame - 1, durationInFrames, W, H, clip.tin, tout);
  // enough sub-frames that neighbouring copies are <= ~10 px apart (fewer show as stripes on fast whips)
  const travel = Math.hypot(now.dx - prev.dx, now.dy - prev.dy) + Math.abs(now.s - prev.s) * Math.max(W, H);
  const K = Math.max(8, Math.min(28, Math.ceil(travel / 10)));
  const horizontal = clip.tin?.type === "whip" && (clip.tin.dir === "left" || clip.tin.dir === "right" || !clip.tin.dir)
    ? true
    : tout?.type === "whip" && (tout.dir === "left" || tout.dir === "right" || !tout.dir);
  const vertical = (clip.tin?.type === "whip" && !horizontal) || (tout?.type === "whip" && !horizontal);
  // mirrored neighbours so a travelling frame never reveals an empty edge (standard whip-pan practice)
  const tiles: { x: number; y: number; fx: number; fy: number }[] = [{ x: 0, y: 0, fx: 1, fy: 1 }];
  if (horizontal) tiles.push({ x: -W, y: 0, fx: -1, fy: 1 }, { x: W, y: 0, fx: -1, fy: 1 });
  if (vertical) tiles.push({ x: 0, y: -H, fx: 1, fy: -1 }, { x: 0, y: H, fx: 1, fy: -1 });
  const layers = [];
  for (let i = 0; i < K; i++) {
    const u = i / (K - 1);
    const dx = prev.dx + (now.dx - prev.dx) * u;
    const dy = prev.dy + (now.dy - prev.dy) * u;
    const s = prev.s + (now.s - prev.s) * u;
    layers.push(
      <div key={i} style={{ position: "absolute", inset: 0, opacity: 1 / (i + 1), transform: `translate(${dx}px, ${dy}px) scale(${s})` }}>
        {tiles.map((t, j) => (
          <div key={j} style={{ position: "absolute", left: t.x, top: t.y, width: W, height: H, overflow: "hidden", transform: `scale(${t.fx}, ${t.fy})` }}>
            <Img src={src} style={{ position: "absolute", left, top, width: dw, height: dh, maxWidth: "none" }} />
          </div>
        ))}
      </div>,
    );
  }
  return (
    <div
      style={{
        position: "absolute", inset: 0, overflow: "hidden",
        transform: settle !== 1 ? `scale(${settle})` : undefined,
        filter: now.bright > 0.01 ? `brightness(${1 + now.bright}) contrast(${1 + now.bright * 0.25})` : undefined,
      }}
    >
      {layers}
    </div>
  );
};
