/**
 * The edit file (projects/<name>/edit.json) drives a whole video. Times are in seconds.
 * - clips[].in/out are SOURCE times; clips play back to back to form the output timeline.
 * - overlays[].at/dur are OUTPUT times (what you see in the finished video).
 * - caption words come from tools/transcribe.py (source times) and are remapped through the cuts.
 */
export type Clip = { src: string; in: number; out: number; volume?: number };

export type Word = { w: string; start: number; end: number };

export type Overlay =
  | { type: "exerciseTitle"; at: number; dur: number; title: string; eyebrow?: string }
  | { type: "callout"; at: number; dur: number; text?: string; number?: string; unit?: string; earned?: boolean; position?: "top" | "center" }
  | { type: "insetCard"; at: number; dur: number; src: string; in: number; eyebrow?: string; volume?: number }
  | { type: "split"; at: number; dur: number; top: { src: string; in: number }; bottom: { src: string; in: number } }
  | { type: "endCard"; at: number; dur: number; cta: string; signature?: boolean };

export type Edit = {
  title: string;
  fps: number;
  width: number;
  height: number;
  clips: Clip[];
  captions?: { words: Word[]; keywords?: string[]; maxWords?: number; maxChars?: number };
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
export const groupCaptions = (words: Word[], clips: Clip[], maxWords = 3, maxChars = 22): CaptionGroup[] => {
  const mapped = words
    .map((w) => {
      const s = sourceToOutput(clips, w.start);
      const e = sourceToOutput(clips, Math.max(w.start, w.end - 0.001));
      return s === null ? null : { w: w.w.trim(), start: s, end: e ?? s + 0.2 };
    })
    .filter((w): w is { w: string; start: number; end: number } => !!w && w.w.length > 0);

  const groups: CaptionGroup[] = [];
  let cur: CaptionGroup | null = null;
  for (const w of mapped) {
    const gap = cur ? w.start - cur.end : 0;
    const chars = cur ? cur.words.join(" ").length + 1 + w.w.length : w.w.length;
    if (!cur || gap > 0.35 || cur.words.length >= maxWords || chars > maxChars) {
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
  // Hold each phrase until the next one starts when the gap is short, so captions don't flicker.
  for (let i = 0; i < groups.length - 1; i++) {
    if (groups[i + 1].start - groups[i].end < 0.3) groups[i].end = groups[i + 1].start;
  }
  return groups;
};
