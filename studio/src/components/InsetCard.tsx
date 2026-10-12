import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { presence } from "../lib/motion";
import { color, font } from "../lib/theme";
import { Hairlines } from "./Hairlines";

/**
 * B-roll shown in a rounded card over a blurred, darkened copy of itself
 * (reference: demo clips framed as a card while the coach keeps talking).
 * OSM version: Surface card radius, 1px Line border, Night backdrop + hairlines.
 */
export const InsetCard: React.FC<{ src: string; inSec: number; dur: number; eyebrow?: string; volume?: number }> = ({ src, inSec, dur, eyebrow, volume = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = presence(frame, Math.round(dur * fps), 8, 6);
  const startFrom = Math.round(inSec * fps);
  const url = staticFile(src);

  return (
    <AbsoluteFill style={{ opacity: p }}>
      <AbsoluteFill style={{ background: color.night }}>
        <OffthreadVideo src={url} startFrom={startFrom} muted style={{ width: "100%", height: "100%", objectFit: "cover", filter: "blur(36px) brightness(0.4) saturate(0.8)", transform: "scale(1.15)" }} />
      </AbsoluteFill>
      <Hairlines />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 860, height: 1380, borderRadius: 48, overflow: "hidden", border: `2px solid ${color.line}`, boxShadow: "0 30px 80px rgba(0,0,0,0.55)", transform: `scale(${0.95 + 0.05 * p})`, position: "relative" }}>
          <OffthreadVideo src={url} startFrom={startFrom} volume={volume} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          {eyebrow ? (
            <div style={{ position: "absolute", top: 36, left: 40, fontFamily: font.latin, fontWeight: 700, fontSize: 28, letterSpacing: "0.22em", color: color.cyan, textTransform: "uppercase", textShadow: "0 2px 10px rgba(10,15,22,0.9)" }}>
              {eyebrow}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
