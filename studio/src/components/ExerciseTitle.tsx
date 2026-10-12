import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { presence, progress } from "../lib/motion";
import { color, font, isArabic, safe } from "../lib/theme";

/**
 * Exercise name as the hero title (reference: "LEG EXTENSION", "HACK SQUAT" over the set).
 * OSM version: Inter Black Italic caps, last word in Core Blue, cyan eyebrow, blue bar draws after the title lands.
 * Arabic titles become bold upright (book rule).
 */
export const ExerciseTitle: React.FC<{ title: string; eyebrow?: string; dur: number }> = ({ title, eyebrow, dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const p = presence(frame, durF, 12, 8);
  const wipe = progress(frame, 0, 12);
  const bar = progress(frame, 10, 20);
  const rtl = isArabic(title);
  const words = title.trim().split(/\s+/);
  const last = words.pop()!;

  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: rtl ? "flex-end" : "flex-start", pointerEvents: "none" }}>
      <div
        dir={rtl ? "rtl" : "ltr"}
        style={{
          margin: `0 ${safe.side}px ${safe.bottom + 60}px`,
          opacity: p,
          transform: `translateX(${(rtl ? 1 : -1) * 40 * (1 - wipe)}px)`,
        }}
      >
        {eyebrow ? (
          <div style={{ fontFamily: rtl ? font.arabic : font.latin, fontWeight: 700, fontSize: 30, letterSpacing: rtl ? 0 : "0.22em", color: color.cyan, textTransform: "uppercase", marginBottom: 14 }}>
            {eyebrow}
          </div>
        ) : null}
        <div
          style={{
            fontFamily: rtl ? font.arabic : font.latinItalic,
            fontStyle: rtl ? "normal" : "italic",
            fontWeight: rtl ? 700 : 900,
            fontSize: rtl ? 118 : 124,
            lineHeight: rtl ? 1.3 : 0.95,
            letterSpacing: rtl ? 0 : "-0.02em",
            textTransform: "uppercase",
            color: color.text,
            clipPath: rtl ? `inset(0 0 0 ${100 - wipe * 100}%)` : `inset(0 ${100 - wipe * 100}% 0 0)`,
            textShadow: "0 6px 30px rgba(10,15,22,0.75)",
            paddingRight: 12, // room for the italic overhang so the clip doesn't cut the last letter
          }}
        >
          {words.length ? <>{words.join(" ")} </> : null}
          <span style={{ color: color.coreBlue }}>{last}</span>
        </div>
        <div style={{ height: 8, width: 150 * bar, marginTop: 20, borderRadius: 4, background: color.coreBlue, boxShadow: `0 0 18px ${color.glowBlue}` }} />
      </div>
    </AbsoluteFill>
  );
};
