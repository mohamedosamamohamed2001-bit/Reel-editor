import { useMemo } from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Callout } from "./components/Callout";
import { Captions } from "./components/Captions";
import { Checklist } from "./components/Checklist";
import { EndCard } from "./components/EndCard";
import { ExerciseTitle } from "./components/ExerciseTitle";
import { FramedVideo } from "./components/FramedVideo";
import { InsetCard } from "./components/InsetCard";
import { KineticTitle } from "./components/KineticTitle";
import { LowerLabel } from "./components/LowerLabel";
import { ScreenCard } from "./components/ScreenCard";
import { SplitStack } from "./components/SplitStack";
import { IconPop } from "./components/IconPop";
import { StepBadge } from "./components/StepBadge";
import { TrackedLabel } from "./components/TrackedLabel";
import { VisualCard } from "./components/VisualCard";
import { Edit, Overlay, clipFrames, groupCaptions } from "./lib/edit";
import { useBrandFonts } from "./lib/fonts";
import { color } from "./lib/theme";

const layer: Record<Overlay["type"], number> = {
  split: 1, insetCard: 1, screenCard: 1, exerciseTitle: 3, callout: 3, checklist: 3, endCard: 4,
  kineticTitle: 3, iconPop: 3, stepBadge: 3, lowerLabel: 3, trackedLabel: 3, visualCard: 1,
};

const renderOverlay = (o: Overlay, plate?: string) => {
  switch (o.type) {
    case "exerciseTitle":
      return <ExerciseTitle title={o.title} eyebrow={o.eyebrow} dur={o.dur} />;
    case "callout":
      return <Callout {...o} />;
    case "insetCard":
      return <InsetCard src={o.src} inSec={o.in} dur={o.dur} eyebrow={o.eyebrow} volume={o.volume} />;
    case "split":
      return <SplitStack top={o.top} bottom={o.bottom} dur={o.dur} />;
    case "endCard":
      return <EndCard dur={o.dur} cta={o.cta} signature={o.signature} reveal={o.reveal} sub={o.sub} image={o.image} />;
    case "checklist":
      return <Checklist dur={o.dur} items={o.items} top={o.top} row={o.row} plate={plate} />;
    case "kineticTitle":
      return <KineticTitle lines={o.lines} eyebrow={o.eyebrow} dur={o.dur} top={o.top} tilt={o.tilt} backdrop={o.backdrop} motion={o.motion} depth={o.depth} ink={o.ink} />;
    case "iconPop":
      return <IconPop items={o.items} dur={o.dur} top={o.top} size={o.size} align={o.align} />;
    case "stepBadge":
      return <StepBadge mark={o.mark} label={o.label} sub={o.sub} dur={o.dur} top={o.top} side={o.side} />;
    case "lowerLabel":
      return <LowerLabel title={o.title} sets={o.sets} eyebrow={o.eyebrow} dur={o.dur} top={o.top} />;
    case "visualCard":
      return <VisualCard src={o.src} dur={o.dur} mode={o.mode} label={o.label} sub={o.sub} credit={o.credit} srcW={o.srcW} srcH={o.srcH}
        width={o.width} top={o.top} markers={o.markers} push={o.push} focusY={o.focusY} />;
    case "trackedLabel":
      return <TrackedLabel text={o.text} sub={o.sub} keys={o.keys} dur={o.dur} side={o.side} plate={plate} />;
    case "screenCard":
      return <ScreenCard src={o.src} dur={o.dur} segments={o.segments} region={o.region} width={o.width} top={o.top} srcW={o.srcW} srcH={o.srcH} taps={o.taps} highlights={o.highlights} frames={o.frames} entrance={o.entrance} checks={o.checks} masks={o.masks} />;
  }
};

/** Bright flash over a cut: 1 frame of pre-glow, peak on the cut frame, decays over `n` frames. */
const Flashes: React.FC<{ at: number[]; n?: number }> = ({ at, n = 4 }) => {
  const frame = useCurrentFrame();
  const a = at.reduce((m, c) => {
    const d = frame - c;
    if (d < -1 || d > n) return m;
    const v = d < 0 ? 0.35 : interpolate(d, [0, n], [0.9, 0], { extrapolateRight: "clamp" });
    return Math.max(m, v);
  }, 0);
  if (a <= 0) return null;
  // white core with a Core Blue rim: the brand's one glow for that frame
  return <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 45%, rgba(255,255,255,${a}) 0%, rgba(214,232,255,${a * 0.9}) 55%, rgba(86,160,251,${a * 0.75}) 100%)`, mixBlendMode: "screen" }} />;
};

/** Short decaying camera jolt on impact frames (sum of damped sines, deterministic). */
const useShake = (shakes: { f: number; amp: number }[]) => {
  const frame = useCurrentFrame();
  let x = 0, y = 0, r = 0;
  for (const s of shakes) {
    const d = frame - s.f;
    if (d < 0 || d > 8) continue;
    const k = Math.exp(-d / 2.2) * s.amp;
    x += Math.sin(d * 2.9 + 1) * 14 * k;
    y += Math.cos(d * 3.7) * 10 * k;
    r += Math.sin(d * 2.3) * 0.35 * k;
  }
  return x || y ? `translate(${x}px, ${y}px) rotate(${r}deg) scale(${1 + 0.02 * Math.min(1, Math.abs(x) / 14)})` : undefined;
};

export const ReelEdit: React.FC<{ edit: Edit }> = ({ edit }) => {
  useBrandFonts();
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);

  const groups = useMemo(
    () => {
      if (!edit.captions) return [];
      // caption position changes at zone edges, and captions must not straddle a card's entrance
      const breaks = (edit.captions.zones ?? []).flatMap((z) => [z.at, z.at + z.dur]);
      return groupCaptions(edit.captions.words, edit.clips, edit.captions.maxWords, edit.captions.maxChars, breaks);
    },
    [edit],
  );

  let cursor = 0;
  const cuts: { f: number; n: number }[] = []; // transition cuts: captions step aside while the picture moves
  const flashes: number[] = [];
  const clipSeqs = edit.clips.map((c, i) => {
    const from = cursor;
    const len = clipFrames(c, fps);
    cursor += len;
    const next = edit.clips[i + 1];
    if (c.tin) {
      cuts.push({ f: from, n: c.tin.frames ?? (c.tin.type === "whip" ? 4 : c.tin.type === "zoom" ? 5 : 2) });
      if (c.tin.type === "flash" || c.tin.flash) flashes.push(from);
    }
    return (
      <Sequence key={`clip${i}`} from={from} durationInFrames={len} name={`clip ${i + 1}${c.tin ? ` (${c.tin.type})` : ""}`}>
        <FramedVideo clip={c} durationInFrames={len} startFrom={Math.round(c.in * fps)} tout={next?.tin} />
      </Sequence>
    );
  });
  const shake = useShake((edit.shakes ?? []).map((s) => ({ f: f(s.at), amp: s.amp ?? 1 })));

  const seq = (o: Overlay, i: number) => (
    <Sequence key={`ov${i}`} from={f(o.at)} durationInFrames={Math.max(1, f(o.dur))} name={`${o.type} @${o.at}s`}>
      {renderOverlay(o, edit.textPlate)}
    </Sequence>
  );
  // a full-frame title card sits under the captions (his words stay readable while it covers the picture)
  const occluded = (o: Overlay) => o.type === "kineticTitle" && !!o.occlude;
  const layerOf = (o: Overlay) => (o.type === "kineticTitle" && o.backdrop ? 1 : occluded(o) ? 2 : layer[o.type]);
  // behind-the-head titles: the title (layer 2) sits under a cut-out copy of the footage (him), under the captions
  const fgSeqs: React.ReactNode[] = [];
  edit.overlays.forEach((o, oi) => {
    if (!occluded(o)) return;
    const a = f(o.at), b = a + Math.max(1, f(o.dur));
    let start = 0;
    edit.clips.forEach((c, ci) => {
      const len = clipFrames(c, fps);
      const lo = Math.max(a, start), hi = Math.min(b, start + len);
      if (c.fg && hi > lo) {
        fgSeqs.push(
          <Sequence key={`fg${oi}_${ci}`} from={start} durationInFrames={len} name={`cut-out ${ci + 1}`}>
            <FramedVideo clip={c} durationInFrames={len} startFrom={Math.round(c.in * fps)} tout={edit.clips[ci + 1]?.tin} fgWindow={[lo - start, hi - start]} />
          </Sequence>,
        );
      }
      start += len;
    });
  });
  const byLayer = (n: number) => edit.overlays.map((o, i) => (layerOf(o) === n ? seq(o, i) : null));

  return (
    <AbsoluteFill style={{ background: color.night }}>
      <AbsoluteFill style={{ transform: shake }}>
        {clipSeqs}
        {byLayer(1)}
        {byLayer(2)}
        {fgSeqs}
        {edit.captions ? (
          <Captions groups={groups} keywords={edit.captions.keywords} style={edit.captions.style} zones={edit.captions.zones}
            karaoke={edit.captions.karaoke} anchors={edit.captions.anchors} cuts={cuts} plateColor={edit.textPlate} anchorPlate={edit.captions.anchorPlate} />
        ) : null}
        {byLayer(3)}
      </AbsoluteFill>
      <Flashes at={flashes} />
      {byLayer(4)}
    </AbsoluteFill>
  );
};
