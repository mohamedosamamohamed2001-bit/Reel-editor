import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { presence } from "../lib/motion";
import { color, font, isArabic, safe } from "../lib/theme";

/**
 * Big kinetic number or keyword that restates what is being said
 * (reference: "12 عدة", "8 عدات", "العدة السلبية"). Numbers in Barlow Condensed.
 * Copper only when the number is earned (points, PR, streak) — book: copper means earned.
 */
export const Callout: React.FC<{ dur: number; text?: string; number?: string; unit?: string; earned?: boolean; position?: "top" | "center" }> = ({
  dur, text, number, unit, earned, position = "top",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = presence(frame, Math.round(dur * fps));
  const unitRtl = unit ? isArabic(unit) : false;
  const textRtl = text ? isArabic(text) : false;

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: position === "center" ? "center" : "flex-start", pointerEvents: "none" }}>
      <div
        style={{
          marginTop: position === "top" ? safe.top + 40 : 0,
          opacity: p,
          transform: `translateY(${36 * (1 - p)}px)`,
          display: "flex",
          flexDirection: unitRtl ? "row-reverse" : "row",
          alignItems: "baseline",
          gap: 22,
          textShadow: "0 6px 30px rgba(10,15,22,0.8)",
        }}
      >
        {number ? (
          <span style={{ fontFamily: font.numbers, fontWeight: 700, fontSize: 250, lineHeight: 1, color: earned ? color.copper : color.text, fontVariantNumeric: "tabular-nums" }}>
            {number}
          </span>
        ) : null}
        {unit ? (
          <span dir={unitRtl ? "rtl" : "ltr"} style={{ fontFamily: unitRtl ? font.arabic : font.numbers, fontWeight: unitRtl ? 700 : 600, fontSize: unitRtl ? 96 : 110, color: earned ? color.copper : color.coreBlue }}>
            {unit}
          </span>
        ) : null}
        {text && !number ? (
          <span
            dir={textRtl ? "rtl" : "ltr"}
            style={{
              fontFamily: textRtl ? font.arabic : font.latinItalic,
              fontStyle: textRtl ? "normal" : "italic",
              fontWeight: textRtl ? 700 : 900,
              fontSize: textRtl ? 128 : 120,
              lineHeight: textRtl ? 1.4 : 0.95,
              letterSpacing: textRtl ? 0 : "-0.02em",
              textTransform: "uppercase",
              color: color.text,
              textAlign: "center",
              maxWidth: 920,
            }}
          >
            {text}
          </span>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
