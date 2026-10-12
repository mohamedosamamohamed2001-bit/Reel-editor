import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { presence, progress } from "../lib/motion";
import { color, font, isArabic } from "../lib/theme";
import { Hairlines } from "./Hairlines";

/**
 * Wordmark end card on Night. Logo is the untouched raster file (no glow, recolour or resize distortion),
 * width 640px so clear space (½ "O" height) is respected on all sides.
 * `signature` shows "TRAIN WITH A METHOD." — pending approval in the brand book, so it is opt-in.
 */
export const EndCard: React.FC<{ dur: number; cta: string; signature?: boolean }> = ({ dur, cta, signature }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = presence(frame, Math.round(dur * fps), 12, 1);
  const ctaP = progress(frame, 14, 26);
  const rtl = isArabic(cta);
  return (
    <AbsoluteFill style={{ background: color.night, opacity: p, alignItems: "center", justifyContent: "center" }}>
      <Hairlines />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 70 }}>
        {/* The JPEG has a black box baked in. "lighten" lets the Night background replace only the box's
            near-black pixels; every logo pixel brighter than Night stays exactly as drawn (no recolour). */}
        <Img src={staticFile("brand/logo/osm-wordmark-780x264.jpg")} style={{ width: 640, height: "auto", mixBlendMode: "lighten", transform: `translateY(${20 * (1 - p)}px)` }} />
        {signature ? (
          <div style={{ fontFamily: font.latin, fontWeight: 700, fontSize: 30, letterSpacing: "0.3em", color: color.steel }}>TRAIN WITH A METHOD</div>
        ) : null}
        <div
          dir={rtl ? "rtl" : "ltr"}
          style={{
            opacity: ctaP,
            transform: `translateY(${24 * (1 - ctaP)}px)`,
            padding: "30px 64px",
            borderRadius: 999,
            background: `linear-gradient(180deg, ${color.glowBlue}, ${color.coreBlue})`,
            color: color.night, // book: text on Core Blue is Night, never white
            fontFamily: rtl ? font.arabic : font.latin,
            fontWeight: 700,
            fontSize: 48,
            boxShadow: `0 0 40px rgba(86,160,251,0.35)`, // the one glow on this frame
          }}
        >
          {cta}
        </div>
      </div>
    </AbsoluteFill>
  );
};
