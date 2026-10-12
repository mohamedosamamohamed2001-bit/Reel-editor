import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ScreenSegment } from "../lib/edit";
import { presence } from "../lib/motion";
import { color } from "../lib/theme";
import { Hairlines } from "./Hairlines";

type Props = {
  src: string; dur: number; segments: ScreenSegment[];
  region?: { x: number; y: number; w: number; h: number };
  width?: number; top?: number; srcW?: number; srcH?: number;
};

/**
 * Real app screen recording shown as a card over the blurred, darkened talking head (which keeps playing below).
 * `region` crops away the status bar / keyboard; `segments` re-time the recording (e.g. speed up typing).
 */
export const ScreenCard: React.FC<Props> = ({ src, dur, segments, region = { x: 0, y: 0, w: 1, h: 1 }, width = 920, top = 300, srcW = 1080, srcH = 1920 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = presence(frame, Math.round(dur * fps), 9, 7);
  const cardH = Math.round((width * (region.h * srcH)) / (region.w * srcW));
  const scale = width / (region.w * srcW);
  const url = staticFile(src);

  let cursor = 0;
  const seqs = segments.map((sg, i) => {
    const from = cursor;
    const len = Math.round(sg.dur * fps);
    cursor += len;
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

  return (
    <AbsoluteFill style={{ opacity: p }}>
      {/* blurs whatever is underneath (the speaker keeps talking behind the card) */}
      <AbsoluteFill style={{ backdropFilter: "blur(34px) brightness(0.38) saturate(0.85)", WebkitBackdropFilter: "blur(34px) brightness(0.38) saturate(0.85)", background: "rgba(10,15,22,0.35)" }} />
      <Hairlines />
      <div
        style={{
          position: "absolute", left: (1080 - width) / 2, top, width, height: cardH,
          borderRadius: 52, overflow: "hidden", border: `2px solid ${color.line}`,
          boxShadow: "0 40px 90px rgba(0,0,0,0.55)",
          transform: `translateY(${30 * (1 - p)}px) scale(${0.96 + 0.04 * p})`,
        }}
      >
        {seqs}
      </div>
    </AbsoluteFill>
  );
};
