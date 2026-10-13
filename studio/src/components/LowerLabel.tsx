import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, isArabic, safe } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Exercise label for training footage: a Core Blue 112° bar shoots in from the left, the exercise name is revealed
 * behind it (mask wipe, never over the logo), and the prescription ("3 × 15") counts up digit by digit.
 * Lives just above the bottom safe line. Exit: slides out left with blur.
 */
export const LowerLabel: React.FC<{ title: string; sets?: string; eyebrow?: string; dur: number; top?: number }> = ({
  title, sets, eyebrow, dur, top,
}) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const bar = interpolate(frame, [0, 6], [0, 1], { ...clamp, easing: Easing.out(Easing.exp) });
  const wipe = interpolate(frame, [3, 12], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const setsP = interpolate(frame, [10, 18], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const exit = interpolate(frame, [durF - 6, durF], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const rtl = isArabic(title);
  // "3 × 15": count the trailing number up as it lands
  const m = sets?.match(/^(.*?)(\d+)(\D*)$/);
  const shown = m ? `${m[1]}${Math.max(1, Math.round(Number(m[2]) * setsP))}${m[3]}` : sets;
  const y = top !== undefined ? height * top : height - safe.bottom - 250;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute", left: safe.side, top: y,
          transform: `translateX(${-300 * exit}px)`, filter: exit > 0.01 ? `blur(${10 * exit}px)` : undefined, opacity: 1 - exit,
        }}
      >
        {eyebrow ? (
          <div style={{ fontFamily: font.latin, fontWeight: 700, fontSize: 28, letterSpacing: "0.24em", color: color.cyan, marginBottom: 8, opacity: wipe }}>
            {eyebrow}
          </div>
        ) : null}
        <div style={{ display: "flex", alignItems: "stretch", gap: 22 }}>
          <div style={{ width: 14, borderRadius: 2, background: color.coreBlue, transform: `skewX(-22deg) scaleY(${bar})`, transformOrigin: "50% 100%", boxShadow: `0 0 22px ${color.glowBlue}` }} />
          <div dir={rtl ? "rtl" : "ltr"} style={{ clipPath: `inset(0 ${100 - wipe * 100}% 0 0)` }}>
            <div
              style={{
                fontFamily: rtl ? font.arabic : font.numbers, fontWeight: 700, fontSize: rtl ? 84 : 112, lineHeight: rtl ? 1.3 : 0.95,
                textTransform: rtl ? undefined : "uppercase", color: color.text,
                textShadow: "0 6px 30px rgba(10,15,22,0.85), 0 2px 6px rgba(10,15,22,0.7)",
              }}
            >
              {title}
            </div>
            {sets ? (
              <div
                style={{
                  fontFamily: font.numbers, fontWeight: 700, fontSize: 64, lineHeight: 1.1, color: color.coreBlue,
                  opacity: setsP, transform: `translateY(${16 * (1 - setsP)}px)`, textShadow: "0 4px 20px rgba(10,15,22,0.8)",
                }}
              >
                {shown}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
