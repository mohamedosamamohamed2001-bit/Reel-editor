import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, isArabic } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Motion-tracked label: a ring + leader line pinned to an object, following tracked keyframes (tools/track.py),
 * with the text card at the end of the leader. keys: t = seconds from the overlay start, x/y = output-frame fractions.
 */
export const TrackedLabel: React.FC<{ text: string; sub?: string; keys: { t: number; x: number; y: number }[]; dur: number; side?: "left" | "right"; plate?: string }> = ({
  text, sub, keys, dur, side = "right", plate,
}) => {
  const frame = useCurrentFrame();
  const { fps, width: W, height: H } = useVideoConfig();
  const t = frame / fps;
  const durF = Math.round(dur * fps);
  const ts = keys.map((k) => k.t);
  const x = interpolate(t, ts, keys.map((k) => k.x), clamp) * W;
  const y = interpolate(t, ts, keys.map((k) => k.y), clamp) * H;
  const ring = interpolate(frame, [0, 8], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) });
  const line = interpolate(frame, [5, 13], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const card = interpolate(frame, [10, 18], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const exit = interpolate(frame, [durF - 6, durF], [1, 0], clamp);
  const s = side === "right" ? 1 : -1;
  const L = 170; // leader length
  const ex = x + s * L * 0.7 * line;
  const ey = y - L * 0.7 * line;
  const rtl = isArabic(text);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: exit }}>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        <circle cx={x} cy={y} r={30 * ring} fill="none" stroke={color.coreBlue} strokeWidth={5} />
        <circle cx={x} cy={y} r={7 * ring} fill={color.text} />
        <line x1={x + s * 30 * 0.7} y1={y - 30 * 0.7} x2={ex} y2={ey} stroke={color.text} strokeWidth={4} strokeLinecap="round" opacity={line > 0 ? 1 : 0} />
      </svg>
      <div
        dir={rtl ? "rtl" : "ltr"}
        style={{
          position: "absolute", top: ey - 60, [side === "right" ? "left" : "right"]: side === "right" ? ex + 14 : W - ex + 14,
          opacity: card, transform: `translateX(${s * 20 * (1 - card)}px)`,
          background: plate ?? "rgba(10,15,22,0.86)", border: `1px solid ${plate ?? "rgba(38,50,68,0.9)"}`, borderRadius: 18, padding: "10px 22px",
        }}
      >
        <div style={{ fontFamily: rtl ? font.arabic : font.numbers, fontWeight: 700, fontSize: rtl ? 50 : 60, lineHeight: rtl ? 1.4 : 1, color: color.text, textTransform: rtl ? undefined : "uppercase", whiteSpace: "nowrap" }}>
          {text}
        </div>
        {sub ? <div style={{ fontFamily: isArabic(sub) ? font.arabic : font.latin, fontWeight: 700, fontSize: 26, color: plate ? color.night : color.cyan, letterSpacing: isArabic(sub) ? 0 : "0.16em", whiteSpace: "nowrap" }}>{sub}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
