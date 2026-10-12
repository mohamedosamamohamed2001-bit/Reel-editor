/**
 * The edit file (projects/<name>/edit.json) drives a whole video. Times are in seconds.
 * - clips[].in/out are SOURCE times; clips play back to back to form the output timeline.
 * - overlays[].at/dur are OUTPUT times (what you see in the finished video).
 * - caption words come from tools/transcribe.py (source times) and are remapped through the cuts.
 */
/**
 * zoom: 1 = fill the frame (cover). A pair [from, to] animates a slow push across the clip.
 * focusX/focusY (0–1): the point of the source kept at the frame centre (clamped so no edge shows).
 * srcW/srcH are filled in by tools/render_edit.py from ffprobe.
 */
export type Clip = {
  src: string; in: number; out: number; volume?: number;
  zoom?: number | [number, number]; focusX?: number; focusY?: number; srcW?: number; srcH?: number;
};

/** One piece of a screen recording inside a ScreenCard: plays from `in` at `rate` for `dur` output seconds. */
export type ScreenSegment = { in: number; rate?: number; dur: number };

export type Word = { w: string; start: number; end: number };

export type Overlay =
  | { type: "exerciseTitle"; at: number; dur: number; title: string; eyebrow?: string }
  | { type: "callout"; at: number; dur: number; text?: string; number?: string; unit?: string; earned?: boolean; position?: "top" | "center" }
  | { type: "insetCard"; at: number; dur: number; src: string; in: number; eyebrow?: string; volume?: number }
  | { type: "split"; at: number; dur: number; top: { src: string; in: number }; bottom: { src: string; in: number } }
  | { type: "endCard"; at: number; dur: number; cta: string; signature?: boolean }
  | {
      type: "screenCard"; at: number; dur: number; src: string; segments: ScreenSegment[];
      /** visible part of the recording, as fractions of its width/height (crop out status bar / keyboard) */
      region?: { x: number; y: number; w: number; h: number };
      width?: number; top?: number; srcW?: number; srcH?: number;
    };

export type Edit = {
  title: string;
  fps: number;
  width: number;
  height: number;
  clips: Clip[];
  captions?: {
    words: Word[]; keywords?: string[]; maxWords?: number; maxChars?: number;
    /** "plate" = Night plate behind the text (use over bright or white areas); default soft shadow */
    style?: "shadow" | "plate";
    /** move captions for a stretch of the OUTPUT timeline, e.g. below a screen card. top = fraction of height */
    zones?: { at: number; dur: number; top: number }[];
  };
  overlays: Overlay[];
  tail?: number; // seconds after the last clip (e.g. for an end card on its own)
};

export const clipsDuration = (clips: Clip[]) => clips.reduce((t, c) => t + (c.out - c.in), 0);

export const editDuration = (e: Edit) => {
  const overlaysEnd = Math.max(0, ...e.overlays.map((o) => o.at + o.dur));
  return Math.max(clipsDuration(e.clips) + (e.tail ?? 0), overlaysEnd);
};

/**
 * Map a source time to output time. Returns null if that moment was cut out.
 * Only valid when every clip comes from the same source (the usual talking-head edit).
 */
export const sourceToOutput = (clips: Clip[], t: number): number | null => {
  let offset = 0;
  for (const c of clips) {
    if (t >= c.in && t < c.out) return offset + (t - c.in);
    offset += c.out - c.in;
  }
  return null;
};

export type CaptionGroup = { words: string[]; start: number; end: number };

/**
 * Group words into short on-screen phrases (the reference reels show 1–3 words at a time).
 * Breaks on pauses, on punctuation, and at maxWords/maxChars. Times are output times.
 */
const latin = (w: string) => /^[A-Za-z0-9][A-Za-z0-9'’-]*$/.test(w.replace(/[.,!?،؟]+$/, ""));

/**
 * Group words into short on-screen phrases (the reference reels show 1–3 words at a time).
 * Breaks on pauses, punctuation, maxWords/maxChars and at `breaks` (output times where the caption
 * position changes). Consecutive English words stay together ("for free"). Times are output times.
 * A word belongs to the clip that contains its MIDPOINT: transcript word edges drift a little past
 * the real silence, so start-time mapping can resurrect a word that was cut out.
 */
export const groupCaptions = (words: Word[], clips: Clip[], maxWords = 3, maxChars = 22, rawBreaks: number[] = []): CaptionGroup[] => {
  const EPS = 0.005; // seconds; zone edges are sums of floats (8.85 + 8.28 = 17.130000000000003)
  const breaks = rawBreaks.map((b) => Math.round(b * 1000) / 1000);
  const mapped = words
    .map((w) => {
      const mid = (w.start + w.end) / 2;
      const clip = clips.find((c) => mid >= c.in && mid < c.out);
      if (!clip) return null;
      const s = sourceToOutput(clips, Math.max(w.start, clip.in))!;
      const e = sourceToOutput(clips, Math.min(w.end, clip.out - 0.001)) ?? s + 0.2;
      return { w: w.w.trim(), start: s, end: e };
    })
    .filter((w): w is { w: string; start: number; end: number } => !!w && w.w.length > 0);

  const groups: CaptionGroup[] = [];
  let cur: CaptionGroup | null = null;
  for (const w of mapped) {
    const gap = cur ? w.start - cur.end : 0;
    const chars = cur ? cur.words.join(" ").length + 1 + w.w.length : w.w.length;
    const prev = cur ? cur.words[cur.words.length - 1] : "";
    const keepLatinRun = !!cur && latin(prev) && latin(w.w) && gap <= 0.35;
    const crossesBreak = !!cur && breaks.some((b) => b > cur!.start + EPS && b <= w.start + EPS);
    if (!cur || crossesBreak || gap > 0.35 || (!keepLatinRun && (cur.words.length >= maxWords || chars > maxChars))) {
      if (cur) groups.push(cur);
      cur = { words: [w.w], start: w.start, end: w.end };
    } else {
      cur.words.push(w.w);
      cur.end = w.end;
    }
    if (/[.!?،؟]$/.test(w.w)) {
      groups.push(cur);
      cur = null;
    }
  }
  if (cur) groups.push(cur);
  // A phrase shorter than 0.35 s can't be read: fold it into the previous phrase when they are the same
  // sentence (previous doesn't end in punctuation) and no position break separates them.
  for (let i = groups.length - 1; i > 0; i--) {
    const g = groups[i], p = groups[i - 1];
    const sameSentence = !/[.!?،؟]$/.test(p.words[p.words.length - 1]);
    const separated = breaks.some((b) => b > p.start + EPS && b <= g.start + EPS);
    if (g.end - g.start < 0.35 && sameSentence && !separated && g.start - p.end <= 0.35 &&
        [...p.words, ...g.words].join(" ").length <= maxChars + 6) {
      p.words.push(...g.words);
      p.end = g.end;
      groups.splice(i, 1);
    }
  }
  // Hold each phrase until the next one starts when the gap is short, so captions don't flicker,
  // but never across a break (the next phrase may sit somewhere else on screen).
  for (let i = 0; i < groups.length - 1; i++) {
    const next = groups[i + 1].start;
    const blocked = breaks.some((b) => b > groups[i].end - EPS && b <= next + EPS);
    if (next - groups[i].end < 0.3 && !blocked) groups[i].end = next;
  }
  for (const g of groups) {
    const b = breaks.find((x) => x > g.start + EPS && x < g.end - EPS);
    if (b !== undefined) g.end = b;
  }
  return groups;
};
