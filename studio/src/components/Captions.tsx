import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { CaptionGroup } from "../lib/edit";
import { presence } from "../lib/motion";
import { color, font, isArabic } from "../lib/theme";

/**
 * Short-phrase captions (1–3 words) in the lower-middle of the frame, as in the reference reels.
 * Exact transcript words only. Keywords switch to Core Blue (one blue word per phrase, max).
 */
export const Captions: React.FC<{ groups: CaptionGroup[]; keywords?: string[] }> = ({ groups, keywords = [] }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;
  const g = groups.find((x) => t >= x.start && t < x.end);
  if (!g) return null;

  const local = Math.round((t - g.start) * fps);
  const dur = Math.max(1, Math.round((g.end - g.start) * fps));
  const p = presence(local, dur, 4, 3);
  const rtl = isArabic(g.words.join(" "));
  const kw = new Set(keywords.map((k) => k.toLowerCase()));
  let blueUsed = false;

  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none" }}>
      <div
        dir={rtl ? "rtl" : "ltr"}
        style={{
          position: "absolute",
          top: height * 0.6, // sits above the exercise-title zone (bottom 14% safe area + title block)
          maxWidth: "84%",
          textAlign: "center",
          fontFamily: rtl ? font.arabic : font.latin,
          fontWeight: 700,
          // Book: Arabic 1–2px larger than Latin, line-height 1.7, never italic, never letter-spaced.
          fontSize: rtl ? 66 : 62,
          lineHeight: rtl ? 1.7 : 1.25,
          color: color.text,
          opacity: p,
          transform: `scale(${0.94 + 0.06 * p})`,
          textShadow: "0 4px 22px rgba(10,15,22,0.9), 0 1px 3px rgba(10,15,22,0.9)",
        }}
      >
        {g.words.map((w, i) => {
          const isKw = !blueUsed && kw.has(w.replace(/[.,!?،؟]/g, "").toLowerCase());
          if (isKw) blueUsed = true;
          return (
            <span key={i} style={{ color: isKw ? color.coreBlue : undefined }}>
              {w}
              {i < g.words.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
