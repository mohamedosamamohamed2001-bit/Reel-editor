import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CaptionGroup } from "../lib/edit";
import { presence } from "../lib/motion";
import { color, font, isArabic } from "../lib/theme";

type Zone = { at: number; dur: number; top: number };

const isLatin = (w: string) => /^[A-Za-z0-9&]/.test(w);

/** Split a phrase into runs of consecutive English / Arabic words (keeping each word's index in the phrase). */
const runs = (words: string[]) =>
  words.reduce<{ latin: boolean; words: string[]; idx: number[] }[]>((acc, w, i) => {
    const latin = isLatin(w);
    const last = acc[acc.length - 1];
    if (last && last.latin === latin) {
      last.words.push(w);
      last.idx.push(i);
    } else acc.push({ latin, words: [w], idx: [i] });
    return acc;
  }, []);

/**
 * Short-phrase captions (1–3 words) in the lower-middle of the frame, as in the reference reels.
 * Exact transcript words only. A keyword turns Core Blue and gets the brand's title-bar underline,
 * drawn as it appears (one keyword per phrase, max). English words inside Arabic phrases are set in
 * Inter (the brand Latin face) instead of the Arabic font's Latin glyphs.
 */
export const Captions: React.FC<{
  groups: CaptionGroup[]; keywords?: string[]; style?: "shadow" | "plate"; zones?: Zone[]; karaoke?: boolean;
  anchors?: { at: number; dur: number; box: number[] }[]; cuts?: { f: number; n: number }[];
  /** solid plate colour (brand blue): keywords switch to Night so they don't vanish into the plate */
  plateColor?: string;
  /** light caption bar (Coach Osama 2026-10-16: white bars): Night text, the keyword stays Core Blue */
  light?: boolean;
  anchorPlate?: boolean;
}> = ({ groups, keywords = [], style = "shadow", zones = [], karaoke = false, anchors = [], cuts = [], plateColor, anchorPlate = false, light = false }) => {
  const frame = useCurrentFrame();
  const { fps, height, width } = useVideoConfig();
  const t = frame / fps;
  const g = groups.find((x) => t >= x.start && t < x.end);
  if (!g) return null;
  // while the picture whips/zooms through a cut, the caption steps aside (it would otherwise float over a moving frame)
  const cutFade = cuts.reduce((m, c) => {
    const d = frame - c.f;
    if (d < -c.n - 1 || d > c.n + 1) return m;
    return Math.min(m, Math.min(1, Math.abs(d + 0.5) / (c.n + 1)) ** 2);
  }, 1);
  // a baked cover plate (old burned-in text hidden in the footage) under this moment: sit centred on it, no own plate
  const anchor = anchors.find((a) => t >= a.at && t < a.at + a.dur);

  const local = Math.round((t - g.start) * fps);
  const dur = Math.max(1, Math.round((g.end - g.start) * fps));
  const p = presence(local, dur, 4, 3);
  const bar = interpolate(local, [3, 11], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const rtl = isArabic(g.words.join(" "));
  // 5 ms tolerance: zone edges are float sums (8.85 + 8.28 = 17.130000000000003)
  const zone = zones.find((z) => g.start >= z.at - 0.005 && g.start < z.at + z.dur - 0.005);
  const plate = style === "plate" && (!anchor || anchorPlate);
  // on a brand-blue plate the blue keyword would disappear: Night keyword + underline instead
  const kwColor = light ? color.coreBlue : plateColor && (plate || anchor) ? color.night : color.coreBlue;
  const kw = new Set(keywords.map((k) => k.toLowerCase()));
  let blueUsed = false;

  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none" }}>
      <div
        dir={rtl ? "rtl" : "ltr"}
        style={{
          position: "absolute",
          // default sits above the exercise-title zone (bottom 14% safe area + title block)
          // anchored on an old caption's place, but never in the bottom safe zone (Reels UI)
          top: anchor ? height * Math.min(0.8, (anchor.box[1] + anchor.box[3]) / 2) : height * (zone ? zone.top : 0.6),
          left: anchor ? width * ((anchor.box[0] + anchor.box[2]) / 2) : undefined,
          maxWidth: "80%",
          whiteSpace: anchor ? "nowrap" : undefined,
          textAlign: "center",
          fontFamily: rtl ? font.arabic : font.latin,
          fontWeight: 700,
          // Book: Arabic 1–2px larger than Latin, line-height 1.7, never italic, never letter-spaced.
          fontSize: rtl ? 66 : 62,
          lineHeight: rtl ? 1.7 : 1.25,
          color: light && plate ? color.night : color.text,
          opacity: p * cutFade,
          transform: `${anchor ? "translate(-50%, -50%) " : ""}translateY(${10 * (1 - p)}px) scale(${0.95 + 0.05 * p})`,
          textShadow: plate ? "none" : anchor ? "0 2px 8px rgba(10,15,22,0.6)" : "0 4px 22px rgba(10,15,22,0.9), 0 1px 3px rgba(10,15,22,0.9)",
          boxSizing: "border-box",
          // Book: Night plate ~80% opacity, card radius, for legibility over bright areas (e.g. a white shirt)
          background: plate ? plateColor ?? "rgba(10,15,22,0.82)" : undefined,
          border: plate ? `1px solid ${plateColor ?? "rgba(38,50,68,0.9)"}` : undefined,
          // Coach Osama 2026-10-15: no soft shadow / haze around the bar (it moved and faded with the text)
          boxShadow: undefined,
          padding: plate ? (rtl ? "6px 30px 10px" : "14px 30px") : undefined,
          borderRadius: plate ? 20 : undefined,
        }}
      >
        {runs(g.words).map((run, ri, all) => {
          const words = run.words.map((w, wi) => {
            const clean = w.replace(/[.,!?،؟]/g, "");
            const isKw = !blueUsed && kw.has(clean.toLowerCase());
            if (isKw) blueUsed = true;
            // word-synced: each word eases from 45% to full on its own spoken start (3 frames)
            const wStart = g.times?.[run.idx[wi]] ?? g.start;
            const lit = karaoke ? interpolate(t, [wStart - 1 / fps, wStart + 2 / fps], [0.45, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
            const wBar = karaoke
              ? interpolate(t, [wStart, wStart + 8 / fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) })
              : bar;
            return (
              <span key={w + wi} style={{ position: "relative", display: "inline-block", color: isKw ? kwColor : undefined, opacity: lit }}>
                {run.latin && rtl ? w.replace(/[.،,؟]+$/, "") : w.replace(/[.،,]+$/, "")}
                {isKw ? (
                  <span
                    style={{
                      position: "absolute", left: 0, right: 0, bottom: rtl && !run.latin ? 8 : -2, height: 6, borderRadius: 3,
                      background: kwColor, transformOrigin: rtl ? "right" : "left", transform: `scaleX(${wBar})`,
                    }}
                  />
                ) : null}
              </span>
            );
          });
          return (
            <span key={ri}>
              {run.latin ? (
                // one isolated LTR run per English phrase, so "Calories Calculator" never flips inside RTL text;
                // an Arabic "؟" ending the run is moved outside it so it sits at the RTL sentence end
                <>
                  <span dir="ltr" style={{ unicodeBidi: "isolate", fontFamily: font.latin, fontSize: rtl ? "0.92em" : undefined }}>
                    {words.flatMap((el, i) => (i ? [" ", el] : [el]))}
                  </span>
                  {rtl && /؟$/.test(run.words[run.words.length - 1]) ? "؟" : null}
                </>
              ) : (
                words.flatMap((el, i) => (i ? [" ", el] : [el]))
              )}
              {ri < all.length - 1 ? " " : ""}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
