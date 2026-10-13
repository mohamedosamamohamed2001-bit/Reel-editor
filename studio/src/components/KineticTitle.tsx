import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, isArabic, safe } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/**
 * Hook / chapter title: words SLAM in one after another (scale 1.7 → 1 with motion blur, 5 frames, 3-frame stagger),
 * the accent line in Core Blue gets the brand title bar (drawn at 112°, the book's slash angle), and the block exits
 * by snapping up with blur. Latin = Barlow Condensed caps; Arabic = IBM Plex Sans Arabic Bold (book: no italic/tracking).
 * tilt: the block enters with a 2.5D X-tilt (depth) and settles flat.
 */
export const KineticTitle: React.FC<{
  lines: { text: string; accent?: boolean; size?: number }[]; eyebrow?: string; dur: number; top?: number; tilt?: boolean;
  /** full-frame title card: Night backdrop (hard cut in/out) - used to replace an old light leak mid-sentence */
  backdrop?: boolean;
}> = ({ lines, eyebrow, dur, top = 0.2, tilt = false, backdrop = false }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const exitStart = durF - 6;
  const exit = interpolate(frame, [exitStart, durF], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const tiltP = tilt ? interpolate(frame, [0, 12], [1, 0], { ...clamp, easing: Easing.out(Easing.cubic) }) : 0;

  let wordIdx = 0;
  const slam = (k: number) => {
    const start = 2 + k * 3;
    const p = interpolate(frame, [start, start + 5], [0, 1], { ...clamp, easing: Easing.out(Easing.exp) });
    return p;
  };

  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none", perspective: 1400 }}>
      {backdrop ? (
        <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 42%, #13243d 0%, ${color.night} 62%)` }}>
          {/* 112° hairlines: the brand's slash motif, drifting slowly so the card isn't a dead frame */}
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ position: "absolute", top: -200, bottom: -200, left: `${18 + i * 30 + frame * 0.25}%`, width: 2, background: "rgba(86,160,251,0.14)", transform: "skewX(-22deg)" }} />
          ))}
        </AbsoluteFill>
      ) : null}
      <div
        style={{
          position: "absolute",
          top: Math.max(safe.top, height * top),
          width: "86%",
          textAlign: "center",
          transform: `translateY(${-140 * exit}px) rotateX(${22 * tiltP}deg)`,
          transformOrigin: "50% 100%",
          filter: exit > 0.01 ? `blur(${14 * exit}px)` : undefined,
          opacity: backdrop ? 1 : 1 - exit,
        }}
      >
        {eyebrow ? (
          <div
            style={{
              fontFamily: isArabic(eyebrow) ? font.arabic : font.latin, fontWeight: 700, fontSize: 30,
              letterSpacing: isArabic(eyebrow) ? 0 : "0.24em", color: color.cyan, textTransform: "uppercase",
              opacity: interpolate(frame, [0, 6], [0, 1], clamp), marginBottom: 6,
            }}
          >
            {eyebrow}
          </div>
        ) : null}
        {lines.map((ln, li) => {
          const rtl = isArabic(ln.text);
          const words = ln.text.split(/\s+/);
          const size = ln.size ?? (rtl ? 112 : 150);
          const lineStart = 2 + wordIdx * 3;
          const bar = interpolate(frame, [lineStart + words.length * 3 + 2, lineStart + words.length * 3 + 10], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
          const row = (
            <div key={li} dir={rtl ? "rtl" : "ltr"} style={{ position: "relative", lineHeight: rtl ? 1.45 : 0.98, marginTop: li ? (rtl ? -4 : 6) : 0 }}>
              {words.map((w, wi) => {
                const p = slam(wordIdx++);
                return (
                  <span
                    key={wi}
                    style={{
                      display: "inline-block",
                      margin: rtl ? "0 0.14em" : "0 0.09em",
                      fontFamily: rtl ? font.arabic : font.numbers,
                      fontWeight: 700,
                      fontSize: size,
                      textTransform: rtl ? undefined : "uppercase",
                      letterSpacing: rtl ? 0 : "0.01em",
                      color: ln.accent ? color.coreBlue : color.text,
                      opacity: p,
                      transform: `scale(${1.7 - 0.7 * p})`,
                      filter: p < 0.98 ? `blur(${(1 - p) * 10}px)` : undefined,
                      textShadow: "0 8px 40px rgba(10,15,22,0.85), 0 2px 6px rgba(10,15,22,0.7)",
                    }}
                  >
                    {w}
                  </span>
                );
              })}
              {ln.accent ? (
                <div
                  style={{
                    margin: "6px auto 0", height: 10, width: `${46 * bar}%`, borderRadius: 2,
                    background: color.coreBlue, transform: "skewX(-22deg)", boxShadow: `0 0 22px ${color.glowBlue}`,
                  }}
                />
              ) : null}
            </div>
          );
          return row;
        })}
      </div>
    </AbsoluteFill>
  );
};
