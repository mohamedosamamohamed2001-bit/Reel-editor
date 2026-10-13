import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { presence } from "../lib/motion";
import { color, font, isArabic } from "../lib/theme";

/**
 * Items tick in as they are spoken (e.g. "نظام التمرين", "نظام التغذية"). Text must be the speaker's own words.
 * Night chips with a Core Blue check that draws on; at = seconds from the overlay start.
 */
export const Checklist: React.FC<{ dur: number; items: { at: number; text: string }[]; top?: number }> = ({ dur, items, top = 0.42 }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;
  const out = presence(frame, Math.round(dur * fps), 1, 8);
  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: height * top, display: "flex", flexDirection: "column", gap: 18, alignItems: "center", opacity: out }}>
        {items.map((it, i) => {
          const p = interpolate(t, [it.at, it.at + 9 / fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
          const draw = interpolate(t, [it.at + 4 / fps, it.at + 12 / fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
          const rtl = isArabic(it.text);
          return (
            <div
              key={i}
              dir={rtl ? "rtl" : "ltr"}
              style={{
                display: "flex", alignItems: "center", gap: 20, padding: "16px 34px 18px",
                background: "rgba(10,15,22,0.86)", border: `1px solid ${color.line}`, borderRadius: 22,
                boxShadow: "0 14px 34px rgba(10,15,22,0.35)",
                opacity: p, transform: `translateY(${24 * (1 - p)}px) scale(${0.96 + 0.04 * p})`,
              }}
            >
              <svg width={44} height={44} viewBox="0 0 44 44">
                <circle cx="22" cy="22" r="20" fill={color.coreBlue} />
                <path d="M13 22.5 L19.5 29 L31 16" fill="none" stroke={color.night} strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round"
                  strokeDasharray={28} strokeDashoffset={28 * (1 - draw)} />
              </svg>
              <span style={{ fontFamily: rtl ? font.arabic : font.latin, fontWeight: 700, fontSize: 52, lineHeight: 1.5, color: color.text }}>{it.text}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
