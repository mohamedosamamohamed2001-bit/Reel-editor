import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, isArabic, safe } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export type Marker = { at: number; x: number; y: number; label?: string; r?: number };

/**
 * Supporting visual (batch 2): an external image that explains what he is saying, at the moment he says it.
 * mode "card": picture-in-picture card (brand-blue frame) over the dimmed footage; "full": full-screen cutaway.
 * Entrance: slams in (scale 1.18 -> 1, motion blur, 6 frames). Exit: lifts away with blur. A slow push keeps it alive.
 * markers: pulsing Core Blue rings (+ optional label pill) on the image, at = seconds from the card's start,
 * x/y = fractions of the image. credit: small attribution line (required by CC BY / BY-SA images).
 */
export const VisualCard: React.FC<{
  src: string; dur: number; mode?: "card" | "full"; label?: string; sub?: string; credit?: string;
  srcW?: number; srcH?: number; width?: number; top?: number; markers?: Marker[]; push?: [number, number]; focusY?: number;
}> = ({ src, dur, mode = "card", label, sub, credit, srcW = 1000, srcH = 1000, width = 860, top, markers = [], push = [1.0, 1.06], focusY = 0.5 }) => {
  const frame = useCurrentFrame();
  const { fps, width: W, height: H } = useVideoConfig();
  const durF = Math.round(dur * fps);
  const t = frame / fps;
  const inP = interpolate(frame, [0, 6], [0, 1], { ...clamp, easing: Easing.out(Easing.exp) });
  const outP = interpolate(frame, [durF - 6, durF], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const scale = 1.18 - 0.18 * inP;
  const blur = (1 - inP) * 14 + outP * 16;
  const kb = interpolate(frame, [0, durF], push, clamp);
  const url = staticFile(src);

  const labelEl = label ? (
    <div
      dir={isArabic(label) ? "rtl" : "ltr"}
      style={{
        display: "inline-block", marginTop: 22, padding: isArabic(label) ? "4px 26px 10px" : "10px 26px",
        background: color.coreBlue, borderRadius: 18, color: color.text,
        fontFamily: isArabic(label) ? font.arabic : font.numbers, fontWeight: 700, fontSize: isArabic(label) ? 52 : 60,
        lineHeight: isArabic(label) ? 1.5 : 1.05, textTransform: isArabic(label) ? undefined : "uppercase",
        opacity: interpolate(frame, [4, 10], [0, 1], clamp), transform: `translateY(${18 * (1 - interpolate(frame, [4, 10], [0, 1], clamp))}px)`,
      }}
    >
      {label}
      {sub ? <div style={{ fontFamily: isArabic(sub) ? font.arabic : font.latin, fontSize: 28, letterSpacing: isArabic(sub) ? 0 : "0.14em", color: color.night, lineHeight: 1.3 }}>{sub}</div> : null}
    </div>
  ) : null;

  const markerEls = (boxW: number, boxH: number) =>
    markers.map((m, i) => {
      const lt = t - m.at;
      if (lt < 0) return null;
      const p = interpolate(lt, [0, 0.25], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.8)) });
      const pulse = 1 + 0.12 * Math.sin(lt * 7);
      const r = (m.r ?? 0.07) * boxW;
      return (
        <div key={i} style={{ position: "absolute", left: m.x * boxW, top: m.y * boxH, width: 0, height: 0 }}>
          <div style={{ position: "absolute", left: -r, top: -r, width: 2 * r, height: 2 * r, borderRadius: "50%", border: `7px solid ${color.coreBlue}`,
            boxShadow: `0 0 24px ${color.glowBlue}`, transform: `scale(${p * pulse})` }} />
          {m.label ? (
            <div dir={isArabic(m.label) ? "rtl" : "ltr"} style={{ position: "absolute", left: r * 0.75, top: -r - 46, whiteSpace: "nowrap", opacity: p,
              background: color.coreBlue, color: color.text, borderRadius: 14, padding: isArabic(m.label) ? "0 16px 6px" : "6px 16px",
              fontFamily: isArabic(m.label) ? font.arabic : font.numbers, fontWeight: 700, fontSize: isArabic(m.label) ? 36 : 40, lineHeight: 1.4,
              textTransform: isArabic(m.label) ? undefined : "uppercase" }}>
              {m.label}
            </div>
          ) : null}
        </div>
      );
    });

  const creditEl = credit ? (
    <div style={{ position: "absolute", right: safe.side, bottom: safe.bottom - 40, fontFamily: font.latin, fontSize: 20, color: "rgba(244,246,250,0.75)",
      textShadow: "0 1px 4px rgba(10,15,22,0.9)", opacity: inP * (1 - outP) }}>
      {credit}
    </div>
  ) : null;

  if (mode === "full") {
    const s = Math.max(W / srcW, H / srcH) * kb;
    const dw = srcW * s, dh = srcH * s;
    return (
      <AbsoluteFill style={{ background: color.night, opacity: 1 - outP, filter: blur > 0.3 ? `blur(${blur}px)` : undefined, transform: `scale(${scale})` }}>
        <div style={{ position: "absolute", left: (W - dw) / 2, top: Math.min(0, Math.max(H - dh, H / 2 - focusY * dh)), width: dw, height: dh }}>
          <Img src={url} style={{ width: "100%", height: "100%" }} />
          {markerEls(dw, dh)}
        </div>
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(10,15,22,0) 55%, rgba(10,15,22,0.75) 100%)" }} />
        <div style={{ position: "absolute", left: 0, right: 0, bottom: safe.bottom + 40, textAlign: "center" }}>{labelEl}</div>
        {creditEl}
      </AbsoluteFill>
    );
  }
  const cw = width;
  const ch = Math.min(H * 0.36, (cw * srcH) / srcW);
  const iw = (ch * srcW) / srcH;
  const y0 = top !== undefined ? H * top : safe.top + 10;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: `rgba(10,15,22,${0.45 * inP * (1 - outP)})` }} />
      <div style={{ position: "absolute", top: y0, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center",
        transform: `translateY(${-90 * outP}px) scale(${scale})`, opacity: inP * (1 - outP), filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        <div style={{ position: "relative", width: Math.min(cw, iw), height: ch, borderRadius: 30, overflow: "hidden", border: `6px solid ${color.coreBlue}`,
          boxShadow: `0 24px 60px rgba(10,15,22,0.55), 0 0 30px rgba(86,160,251,0.35)`, background: color.night }}>
          <div style={{ position: "absolute", inset: 0, transform: `scale(${kb})`, transformOrigin: "50% 50%" }}>
            <Img src={url} style={{ position: "absolute", left: (Math.min(cw, iw) - iw) / 2, top: 0, width: iw, height: ch, maxWidth: "none" }} />
            <div style={{ position: "absolute", left: (Math.min(cw, iw) - iw) / 2, top: 0, width: iw, height: ch }}>{markerEls(iw, ch)}</div>
          </div>
        </div>
        {labelEl}
      </div>
      {creditEl}
    </AbsoluteFill>
  );
};
