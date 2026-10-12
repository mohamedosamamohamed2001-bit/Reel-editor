import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { presence } from "../lib/motion";
import { color } from "../lib/theme";

/** Two angles stacked (reference: front + side view of the same movement). */
export const SplitStack: React.FC<{ top: { src: string; in: number }; bottom: { src: string; in: number }; dur: number }> = ({ top, bottom, dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = presence(frame, Math.round(dur * fps), 6, 6);
  const half = (c: { src: string; in: number }) => (
    <div style={{ flex: 1, overflow: "hidden" }}>
      <OffthreadVideo src={staticFile(c.src)} startFrom={Math.round(c.in * fps)} muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </div>
  );
  return (
    <AbsoluteFill style={{ background: color.night, opacity: p, display: "flex", flexDirection: "column", gap: 6 }}>
      {half(top)}
      {half(bottom)}
    </AbsoluteFill>
  );
};
