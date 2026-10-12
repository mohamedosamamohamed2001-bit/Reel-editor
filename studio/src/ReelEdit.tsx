import { useMemo } from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { Callout } from "./components/Callout";
import { Captions } from "./components/Captions";
import { EndCard } from "./components/EndCard";
import { ExerciseTitle } from "./components/ExerciseTitle";
import { FramedVideo } from "./components/FramedVideo";
import { InsetCard } from "./components/InsetCard";
import { ScreenCard } from "./components/ScreenCard";
import { SplitStack } from "./components/SplitStack";
import { Edit, Overlay, groupCaptions } from "./lib/edit";
import { useBrandFonts } from "./lib/fonts";
import { color } from "./lib/theme";

const layer: Record<Overlay["type"], number> = { split: 1, insetCard: 1, screenCard: 1, exerciseTitle: 3, callout: 3, endCard: 4 };

const renderOverlay = (o: Overlay) => {
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
      return <EndCard dur={o.dur} cta={o.cta} signature={o.signature} />;
    case "screenCard":
      return <ScreenCard src={o.src} dur={o.dur} segments={o.segments} region={o.region} width={o.width} top={o.top} srcW={o.srcW} srcH={o.srcH} taps={o.taps} highlights={o.highlights} frames={o.frames} />;
  }
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
  const clipSeqs = edit.clips.map((c, i) => {
    const from = cursor;
    const len = f(c.out) - f(c.in);
    cursor += len;
    return (
      <Sequence key={`clip${i}`} from={from} durationInFrames={len} name={`clip ${i + 1}`}>
        <FramedVideo clip={c} durationInFrames={len} startFrom={f(c.in)} />
      </Sequence>
    );
  });

  const seq = (o: Overlay, i: number) => (
    <Sequence key={`ov${i}`} from={f(o.at)} durationInFrames={Math.max(1, f(o.dur))} name={`${o.type} @${o.at}s`}>
      {renderOverlay(o)}
    </Sequence>
  );
  const byLayer = (n: number) => edit.overlays.map((o, i) => (layer[o.type] === n ? seq(o, i) : null));

  return (
    <AbsoluteFill style={{ background: color.night }}>
      {clipSeqs}
      {byLayer(1)}
      {edit.captions ? <Captions groups={groups} keywords={edit.captions.keywords} style={edit.captions.style} zones={edit.captions.zones} /> : null}
      {byLayer(3)}
      {byLayer(4)}
    </AbsoluteFill>
  );
};
