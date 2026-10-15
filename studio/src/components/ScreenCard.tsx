import { AbsoluteFill, Easing, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ScreenSegment } from "../lib/edit";
import { presence } from "../lib/motion";
import { color } from "../lib/theme";
import { Hairlines } from "./Hairlines";

type Box = { x: number; y: number; w: number; h: number };
type Props = {
  src: string; dur: number; segments: ScreenSegment[];
  region?: Box; width?: number; top?: number; srcW?: number; srcH?: number; backdrop?: "blur" | "none";
  taps?: { at: number; x: number; y: number }[];
  highlights?: { at: number; dur: number; box: Box }[];
  frames?: { count: number; fps: number };
  entrance?: "flat" | "tilt";
  checks?: boolean;
  masks?: { at: number; dur: number; box: Box }[];
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Real app screen recording shown as a card over the blurred, darkened talking head (which keeps playing below).
 * `region` crops away the status bar / keyboard; `segments` re-time the recording (e.g. speed up typing).
 * `taps` show where the user taps; `highlights` outline one element and dim the rest, synced to the speech.
 */
export const ScreenCard: React.FC<Props> = ({
  src, dur, segments, region = { x: 0, y: 0, w: 1, h: 1 }, width = 920, top = 300, srcW = 1080, srcH = 1920,
  taps = [], highlights = [], frames, entrance = "flat", checks = false, masks = [], backdrop = "blur",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const p = presence(frame, durF, 12, 8);
  const enter = interpolate(frame, [0, 14], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const tilt = entrance === "tilt";
  // 2.5D: the card rises with a 10° X-tilt and a controlled 1.5% overshoot in scale, then lifts away on exit
  const enterScale = tilt ? interpolate(frame, [0, 16], [0, 1], { ...clamp, easing: Easing.bezier(0.2, 1.18, 0.35, 1) }) : enter;
  const exitP = tilt ? interpolate(frame, [durF - 9, durF], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) }) : 0;
  const blurK = enter * (1 - exitP);
  const cardOpacity = Math.min(
    interpolate(frame, [0, 5], [0, 1], { ...clamp, easing: Easing.out(Easing.quad) }),
    interpolate(frame, [durF - 6, durF], [1, 0], { ...clamp, easing: Easing.in(Easing.quad) }),
  );
  const cardH = Math.round((width * (region.h * srcH)) / (region.w * srcW));
  const scale = width / (region.w * srcW);
  const url = staticFile(src);

  const imgStyle = { position: "absolute" as const, left: -region.x * srcW * scale, top: -region.y * srcH * scale, width: srcW * scale, height: srcH * scale, maxWidth: "none" };
  let cursor = 0;
  const seqs = segments.map((sg, i) => {
    const from = cursor;
    const len = Math.round(sg.dur * fps);
    cursor += len;
    if (frames) {
      // image-sequence plate: pick the recording frame for this moment (re-timed by `rate`)
      if (frame < from || frame >= from + len) return null;
      const tRec = sg.in + ((frame - from) / fps) * (sg.rate ?? 1);
      const idx = Math.min(frames.count, Math.max(1, Math.floor(tRec * frames.fps) + 1));
      return <Img key={i} src={staticFile(`${src}/${String(idx).padStart(5, "0")}.jpg`)} style={imgStyle} />;
    }
    return (
      <Sequence key={i} from={from} durationInFrames={len} layout="none">
        <OffthreadVideo
          src={url}
          muted
          startFrom={Math.round(sg.in * fps)}
          playbackRate={sg.rate ?? 1}
          style={{ position: "absolute", left: -region.x * srcW * scale, top: -region.y * srcH * scale, width: srcW * scale, height: srcH * scale, maxWidth: "none" }}
        />
      </Sequence>
    );
  });

  const t = frame / fps;
  const active = highlights.find((h) => t >= h.at && t < h.at + h.dur);
  // highlight geometry eases between targets so the outline glides from card to card
  const hlP = active ? interpolate(t, [active.at, active.at + 0.18], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) }) : 0;
  const prevIdx = active ? highlights.indexOf(active) - 1 : -1;
  const prev = prevIdx >= 0 && highlights[prevIdx].at + highlights[prevIdx].dur >= active!.at - 0.05 ? highlights[prevIdx] : null;
  const box = active
    ? prev
      ? {
          x: interpolate(hlP, [0, 1], [prev.box.x, active.box.x]), y: interpolate(hlP, [0, 1], [prev.box.y, active.box.y]),
          w: interpolate(hlP, [0, 1], [prev.box.w, active.box.w]), h: interpolate(hlP, [0, 1], [prev.box.h, active.box.h]),
        }
      : active.box
    : null;
  const hlOpacity = active ? (prev ? 1 : hlP) * interpolate(t, [active.at + active.dur - 0.15, active.at + active.dur], [1, 0], clamp) : 0;
  const lastHl = highlights.length ? highlights[highlights.length - 1] : null;
  const dimIn = highlights.length ? interpolate(t, [highlights[0].at, highlights[0].at + 0.2], [0, 1], clamp) : 0;
  const dimOut = lastHl ? interpolate(t, [lastHl.at + lastHl.dur - 0.2, lastHl.at + lastHl.dur], [1, 0], clamp) : 0;
  const dim = Math.min(dimIn, dimOut);

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ opacity: p }}>
      {/* blurs whatever is underneath (the speaker keeps talking behind the card); blur deepens as the card arrives.
          backdrop "none": nothing behind the card (Coach Osama 2026-10-15: no blur / haze; promos put it on a Night plate) */}
      {backdrop === "none" ? null : <AbsoluteFill
        style={{
          backdropFilter: `blur(${34 * blurK}px) brightness(${1 - 0.62 * blurK}) saturate(0.85)`,
          WebkitBackdropFilter: `blur(${34 * blurK}px) brightness(${1 - 0.62 * blurK}) saturate(0.85)`,
          background: `rgba(10,15,22,${0.35 * blurK})`,
        }}
      />}
      <Hairlines />
      </AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, opacity: tilt ? cardOpacity : p, perspective: tilt ? 1800 : undefined, perspectiveOrigin: "50% 30%" }}>
      <div
        style={{
          position: "absolute", left: (1080 - width) / 2, top, width, height: cardH,
          borderRadius: 52, overflow: "hidden", border: `2px solid ${color.line}`,
          // shadow deepens as the card arrives (reads as distance from the backdrop)
          boxShadow: `0 ${20 + 30 * enter}px ${50 + 50 * enter}px rgba(0,0,0,${0.35 + 0.25 * enter})`,
          // slow 2% push across the card's life keeps held frames (e.g. a frozen result screen) alive
          transform: tilt
            ? `translateY(${80 * (1 - enter) - 60 * exitP}px) rotateX(${10 * (1 - enter) - 7 * exitP}deg) scale(${(0.94 + 0.06 * enterScale - 0.03 * exitP) * (1 + 0.02 * (frame / durF))})`
            : `translateY(${70 * (1 - enter)}px) scale(${(0.94 + 0.06 * enter) * (1 + 0.02 * (frame / durF))})`,
          transformOrigin: "50% 100%",
        }}
      >
        {seqs}
        {/* privacy masks (account numbers, emails): heavy blur + Night tint over exactly that area */}
        {masks.filter((m) => t >= m.at && t < m.at + m.dur).map((m, i) => (
          <div key={`m${i}`} style={{
            position: "absolute", left: m.box.x * width, top: m.box.y * cardH, width: m.box.w * width, height: m.box.h * cardH,
            backdropFilter: "blur(14px)", WebkitBackdropFilter: "blur(14px)", background: "rgba(20,27,38,0.55)", borderRadius: 8,
          }} />
        ))}
        {/* dim everything except the highlighted element */}
        {box && dim > 0 ? (
          <div
            style={{
              position: "absolute", left: box.x * width, top: box.y * cardH, width: box.w * width, height: box.h * cardH,
              borderRadius: 26, boxShadow: `0 0 0 4000px rgba(10,15,22,${0.42 * dim})`, opacity: 1,
            }}
          />
        ) : null}
        {box ? (
          <div
            style={{
              position: "absolute", left: box.x * width - 6, top: box.y * cardH - 6, width: box.w * width + 12, height: box.h * cardH + 12,
              borderRadius: 30, border: `4px solid ${color.coreBlue}`, opacity: hlOpacity,
              boxShadow: `0 0 26px rgba(86,160,251,0.45)`, // the one glow on this frame
            }}
          />
        ) : null}
        {taps.map((tp, i) => {
          const k = interpolate(t, [tp.at, tp.at + 0.55], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
          if (t < tp.at || k >= 1) return null;
          return (
            <div key={i} style={{ position: "absolute", left: tp.x * width, top: tp.y * cardH }}>
              <div style={{ position: "absolute", width: 120, height: 120, left: -60, top: -60, borderRadius: "50%", border: `5px solid ${color.coreBlue}`, transform: `scale(${0.35 + 0.65 * k})`, opacity: 1 - k }} />
              <div style={{ position: "absolute", width: 44, height: 44, left: -22, top: -22, borderRadius: "50%", background: "rgba(86,160,251,0.55)", transform: `scale(${1 - 0.3 * k})`, opacity: 1 - k }} />
            </div>
          );
        })}
        {checks && active ? <Check box={active.box} width={width} cardH={cardH} t={t} at={active.at} fps={fps} /> : null}
      </div>
      </div>
    </AbsoluteFill>
  );
};

/** Check mark drawn on the active highlight's right side: Core Blue disc pops, white stroke draws. */
const Check: React.FC<{ box: Box; width: number; cardH: number; t: number; at: number; fps: number }> = ({ box, width, cardH, t, at, fps }) => {
  const pop = interpolate(t, [at + 2 / fps, at + 8 / fps], [0, 1], { ...clamp, easing: Easing.bezier(0.2, 1.4, 0.4, 1) });
  const draw = interpolate(t, [at + 5 / fps, at + 12 / fps], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const size = 64;
  const len = 40; // path length of the check stroke below
  return (
    <svg
      width={size} height={size} viewBox="0 0 64 64"
      style={{ position: "absolute", left: (box.x + box.w) * width - size - 34, top: (box.y + box.h / 2) * cardH - size / 2, transform: `scale(${pop})`, opacity: pop > 0 ? 1 : 0 }}
    >
      <circle cx="32" cy="32" r="30" fill={color.coreBlue} />
      <path d="M19 33 L28 42 L46 23" fill="none" stroke={color.night} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round"
        strokeDasharray={len} strokeDashoffset={len * (1 - draw)} />
    </svg>
  );
};
