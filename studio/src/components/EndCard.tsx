import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { presence, progress } from "../lib/motion";
import { color, font, isArabic } from "../lib/theme";
import { Hairlines } from "./Hairlines";

/**
 * Wordmark end card on Night. Logo is the untouched raster file (no glow, recolour or resize distortion),
 * width 640px so clear space (½ "O" height) is respected on all sides.
 * `signature` shows "TRAIN WITH A METHOD." — pending approval in the brand book, so it is opt-in.
 */
export const EndCard: React.FC<{ dur: number; cta: string; signature?: boolean; reveal?: "fade" | "wipe"; sub?: string; image?: string }> = ({ dur, cta, signature, reveal = "fade", sub, image }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const wipe = reveal === "wipe";
  const p = presence(frame, Math.round(dur * fps), wipe ? 6 : 12, 1);
  // "wipe" reveal = fast fade + 4% scale settle. No mask: a mask reveal crops the letters for a few frames,
  // which the brand book forbids. Logo pixels, colours and proportions untouched (uniform scale only).
  const arrive = wipe ? interpolate(frame, [0, 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) }) : 1;
  const settleK = wipe ? interpolate(frame, [0, 14], [1.04, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : 1;
  const ctaP = progress(frame, 14, 26);
  const rtl = isArabic(cta);
  return (
    <AbsoluteFill style={{ background: color.night, opacity: p, alignItems: "center", justifyContent: "center" }}>
      <Hairlines />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 70 }}>
        {/* The JPEG has a black box baked in. "lighten" lets the Night background replace only the box's
            near-black pixels; every logo pixel brighter than Night stays exactly as drawn (no recolour). */}
        {/* `image`: Coach Osama's end artwork (brand/end/), shown whole and unaltered, full width. It already carries
            the OSM wordmark, so it replaces the wordmark file. Its near-black background is darker than Night, so
            "lighten" blends its edges into the card without touching the artwork. */}
        <Img src={staticFile(image ?? "brand/logo/osm-wordmark-780x264.jpg")} style={{ width: image ? 1080 : 640, height: "auto", mixBlendMode: "lighten", transform: wipe ? `scale(${settleK})` : `translateY(${20 * (1 - p)}px)`, opacity: arrive, marginBottom: image ? -110 : 0 }} />
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
        {sub ? (
          <div style={{ opacity: ctaP, fontFamily: font.latin, fontWeight: 600, fontSize: 38, letterSpacing: "0.02em", color: color.text, marginTop: -30 }}>{sub}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
