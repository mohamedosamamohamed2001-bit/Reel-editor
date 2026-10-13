import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, isArabic, safe } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Numbered point / chapter marker ("01", "02", "+", "−"): a big outlined Barlow numeral wipes in behind a 112° slash
 * that sweeps across, then fills with Core Blue; the label (Arabic or English) slides out from under the slash.
 * Exit: everything snaps sideways with blur. Sits in the upper third so it never fights the captions.
 */
export const StepBadge: React.FC<{ mark: string; label: string; sub?: string; dur: number; top?: number; side?: "left" | "right" }> = ({
  mark, label, sub, dur, top = 0.17, side = "right",
}) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const slash = interpolate(frame, [0, 7], [0, 1], { ...clamp, easing: Easing.out(Easing.exp) });
  const num = interpolate(frame, [2, 9], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const fill = interpolate(frame, [8, 14], [0, 1], clamp);
  const lab = interpolate(frame, [6, 14], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const exit = interpolate(frame, [durF - 6, durF], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const rtlLabel = isArabic(label);
  const dirSign = side === "right" ? 1 : -1;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: Math.max(safe.top, height * top),
          [side]: safe.side,
          display: "flex",
          flexDirection: side === "right" ? "row-reverse" : "row",
          alignItems: "center",
          gap: 26,
          transform: `translateX(${dirSign * 260 * exit}px)`,
          filter: exit > 0.01 ? `blur(${12 * exit}px)` : undefined,
          opacity: 1 - exit,
        }}
      >
        <div style={{ position: "relative", width: 230, height: 210 }}>
          {/* the slash */}
          <div
            style={{
              position: "absolute", left: 92, top: -10, width: 16, height: 230, borderRadius: 3,
              background: color.coreBlue, transform: `skewX(-22deg) scaleY(${slash})`, transformOrigin: "50% 100%",
              boxShadow: `0 0 26px ${color.glowBlue}`,
            }}
          />
          <div
            style={{
              position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: font.numbers, fontWeight: 700, fontSize: 210, lineHeight: 1,
              color: fill > 0 ? `rgba(86,160,251,${fill})` : "transparent",
              WebkitTextStroke: `4px ${color.text}`,
              clipPath: `inset(${100 - num * 100}% 0 0 0)`,
              transform: `translateY(${30 * (1 - num)}px)`,
              textShadow: "0 10px 40px rgba(10,15,22,0.6)",
            }}
          >
            {mark}
          </div>
        </div>
        <div
          dir={rtlLabel ? "rtl" : "ltr"}
          style={{
            clipPath: side === "right" ? `inset(0 0 0 ${100 - lab * 100}%)` : `inset(0 ${100 - lab * 100}% 0 0)`,
            transform: `translateX(${dirSign * 40 * (1 - lab)}px)`,
            textAlign: side === "right" ? "right" : "left",
            maxWidth: 560,
          }}
        >
          <div
            style={{
              fontFamily: rtlLabel ? font.arabic : font.numbers, fontWeight: 700, fontSize: rtlLabel ? 74 : 92,
              lineHeight: rtlLabel ? 1.35 : 1, color: color.text, textTransform: rtlLabel ? undefined : "uppercase",
              textShadow: "0 6px 30px rgba(10,15,22,0.85), 0 2px 6px rgba(10,15,22,0.7)",
            }}
          >
            {label}
          </div>
          {sub ? (
            <div style={{ fontFamily: isArabic(sub) ? font.arabic : font.latin, fontWeight: 700, fontSize: 36, color: color.cyan, letterSpacing: isArabic(sub) ? 0 : "0.18em", textTransform: "uppercase", marginTop: 4 }}>
              {sub}
            </div>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};
