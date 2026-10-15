import * as Icons from "lucide-react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, isArabic, safe } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export type IconItem = { icon: string; label?: string; value?: string; mark?: "up" | "down" | "x" | "check" };

/**
 * Animated illustration tiles (batch 3, "heavy motion graphics"): a Night tile with a Core Blue edge, the icon
 * DRAWS itself (stroke reveal), an orbit ring closes around it, then an optional value / label and a marker
 * (up/down arrow, x, check). Smooth entrances only (Coach Osama: no fast zooms): 14-frame eased rise, 5-frame stagger,
 * gentle float while on screen, 8-frame fade-lift exit. Icons: lucide-react (ISC licence).
 */
export const IconPop: React.FC<{
  items: IconItem[]; dur: number; top?: number; size?: number; align?: "center" | "left" | "right";
}> = ({ items, dur, top = 0.17, size = 190, align = "center" }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const exit = interpolate(frame, [durF - 8, durF], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const justify = align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center";
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute", top: Math.max(safe.top, height * top), left: safe.side, right: safe.side,
          display: "flex", justifyContent: justify, gap: 34, opacity: 1 - exit, transform: `translateY(${-30 * exit}px)`,
        }}
      >
        {items.map((it, i) => {
          const st = 2 + i * 5;
          const p = interpolate(frame, [st, st + 14], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
          const draw = interpolate(frame, [st + 4, st + 22], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
          const ring = interpolate(frame, [st + 6, st + 26], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
          const lab = interpolate(frame, [st + 12, st + 24], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
          const markP = interpolate(frame, [st + 18, st + 28], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.4)) });
          const float = Math.sin((frame + i * 11) / 16) * 4;
          const Ico = (Icons as unknown as Record<string, React.FC<Record<string, unknown>>>)[it.icon] ?? Icons.Circle;
          const r = size / 2 + 14;
          const circ = 2 * Math.PI * r;
          const markColor = it.mark === "x" ? color.copper : color.coreBlue;
          return (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14,
              opacity: p, transform: `translateY(${(1 - p) * 40 + float}px) scale(${0.9 + 0.1 * p})` }}>
              <div style={{ position: "relative", width: size, height: size }}>
                <svg width={size + 40} height={size + 40} style={{ position: "absolute", left: -20, top: -20 }}>
                  <circle cx={size / 2 + 20} cy={size / 2 + 20} r={r} fill="none" stroke={color.glowBlue} strokeWidth={4}
                    strokeDasharray={circ} strokeDashoffset={circ * (1 - ring)} strokeLinecap="round"
                    transform={`rotate(-90 ${size / 2 + 20} ${size / 2 + 20})`} opacity={0.85} />
                </svg>
                <div style={{
                  position: "absolute", inset: 0, borderRadius: size * 0.28,
                  background: `radial-gradient(circle at 50% 35%, #16263f 0%, ${color.night} 75%)`,
                  border: `3px solid ${color.coreBlue}`, // no glow / soft shadow around the tile (2026-10-15: no haze behind text)
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  {it.value ? (
                    <div style={{ fontFamily: font.numbers, fontWeight: 700, fontSize: size * 0.5, color: color.text, letterSpacing: "0.01em",
                      opacity: draw, transform: `translateY(${(1 - draw) * 12}px)` }}>{it.value}</div>
                  ) : (
                    <Ico size={size * 0.52} color={color.text} strokeWidth={1.9}
                      style={{ strokeDasharray: 100, strokeDashoffset: 100 * (1 - draw) }} />
                  )}
                </div>
                {it.mark ? (
                  <div style={{
                    position: "absolute", right: -16, top: -16, width: size * 0.36, height: size * 0.36, borderRadius: "50%",
                    background: markColor, display: "flex", alignItems: "center", justifyContent: "center",
                    transform: `scale(${markP})`, 
                  }}>
                    {it.mark === "up" ? <Icons.ArrowUp size={size * 0.24} color={color.night} strokeWidth={3} /> : null}
                    {it.mark === "down" ? <Icons.ArrowDown size={size * 0.24} color={color.night} strokeWidth={3} /> : null}
                    {it.mark === "x" ? <Icons.X size={size * 0.24} color={color.night} strokeWidth={3.2} /> : null}
                    {it.mark === "check" ? <Icons.Check size={size * 0.24} color={color.night} strokeWidth={3.2} /> : null}
                  </div>
                ) : null}
              </div>
              {it.label ? (
                <div dir={isArabic(it.label) ? "rtl" : "ltr"} style={{
                  padding: "8px 22px", borderRadius: 14, background: "#56A0FB", color: color.night,
                  fontFamily: isArabic(it.label) ? font.arabic : font.latin, fontWeight: 700, fontSize: Math.round(size * 0.2),
                  opacity: lab, transform: `translateY(${(1 - lab) * 14}px)`, whiteSpace: "nowrap",
                }}>{it.label}</div>
              ) : null}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
