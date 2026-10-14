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
  /** original SOURCE in/out when the clip was replaced by a pre-framed plate (tools/render_edit.py);
   *  caption timing always maps through these, never through the plate's own 0-based times */
  orig?: { in: number; out: number };
  /** set when src is a JPEG image-sequence plate (folder of 00001.jpg…): frame count and its fps */
  frames?: { count: number; fps: number };
  /** set by tools/render_edit.py: folder of RGBA PNG cut-outs (him only) for frames under a behind-the-head title */
  fg?: string;
  /** punch "settle": start at this scale (e.g. 1.04) and ease to 1 over 10 frames, like camera inertia */
  settle?: number;
  /** playback speed (plates only): 2 = twice as fast (frames blended = motion blur); timeline length = (out-in)/speed */
  speed?: number;
  /** hold the frame at `in` for out-in seconds, silent (plates only). (A clip with "hold": t in edit.json shows the
   *  still frame at source time t while its dialogue plays; render_edit.py bakes it into the plate.) */
  freeze?: boolean;
  /** transition INTO this clip from the previous one (the previous clip plays the matching exit) */
  tin?: Transition;
};

/**
 * whip: directional move with real motion blur and mirrored edges (outgoing accelerates out, incoming decelerates in)
 * zoom: punch through (outgoing scales up, incoming lands from over-scale), zoom blur + exposure bloom
 * flash: hard cut under a short bright flash
 * frames = frames on EACH side of the cut (default 4 whip / 5 zoom / 3 flash)
 */
export type Transition = { type: "whip" | "zoom" | "flash"; dir?: "left" | "right" | "up" | "down"; frames?: number; flash?: boolean };

/** output length of a clip in frames (speed-aware; at speed 1 identical to the original per-edge rounding) */
export const clipFrames = (c: Clip, fps: number) =>
  (c.speed ?? 1) === 1 ? Math.round(c.out * fps) - Math.round(c.in * fps) : Math.round(((c.out - c.in) / (c.speed ?? 1)) * fps);

const span = (c: Clip) => c.orig ?? { in: c.in, out: c.out };

/** One piece of a screen recording inside a ScreenCard: plays from `in` at `rate` for `dur` output seconds. */
export type ScreenSegment = { in: number; rate?: number; dur: number };

export type Word = { w: string; start: number; end: number };

export type Overlay =
  | { type: "exerciseTitle"; at: number; dur: number; title: string; eyebrow?: string }
  | { type: "visualCard"; at: number; dur: number; src: string; mode?: "card" | "full"; label?: string; sub?: string; credit?: string;
      srcW?: number; srcH?: number; width?: number; top?: number; markers?: { at: number; x: number; y: number; label?: string; r?: number }[];
      push?: [number, number]; focusY?: number }
  | { type: "iconPop"; at: number; dur: number; items: { icon: string; label?: string; value?: string; mark?: "up" | "down" | "x" | "check" }[];
      top?: number; size?: number; align?: "center" | "left" | "right" }
  | { type: "kineticTitle"; at: number; dur: number; lines: { text: string; accent?: boolean; size?: number }[]; eyebrow?: string; top?: number; tilt?: boolean; backdrop?: boolean; motion?: "slam" | "smooth"; depth?: boolean; ink?: "light" | "dark";
      /** behind-the-head: he occludes the title (person cut-out by tools/render_edit.py, MODNet matte) */ occlude?: boolean }
  | { type: "stepBadge"; at: number; dur: number; mark: string; label: string; sub?: string; top?: number; side?: "left" | "right" }
  | { type: "lowerLabel"; at: number; dur: number; title: string; sets?: string; eyebrow?: string; top?: number }
  | { type: "trackedLabel"; at: number; dur: number; text: string; sub?: string; keys: { t: number; x: number; y: number }[]; side?: "left" | "right" }
  | { type: "callout"; at: number; dur: number; text?: string; number?: string; unit?: string; earned?: boolean; position?: "top" | "center" }
  | { type: "insetCard"; at: number; dur: number; src: string; in: number; eyebrow?: string; volume?: number }
  | { type: "split"; at: number; dur: number; top: { src: string; in: number }; bottom: { src: string; in: number } }
  | { type: "endCard"; at: number; dur: number; cta: string; signature?: boolean; reveal?: "fade" | "wipe"; sub?: string; image?: string }
  | { type: "checklist"; at: number; dur: number; items: { at: number; text: string }[]; top?: number; row?: boolean }
  | {
      type: "screenCard"; at: number; dur: number; src: string; segments: ScreenSegment[];
      /** visible part of the recording, as fractions of its width/height (crop out status bar / keyboard) */
      region?: { x: number; y: number; w: number; h: number };
      width?: number; top?: number; srcW?: number; srcH?: number;
      /** Lanczos-prescale the recording to the card width (tools/render_edit.py) */
      plate?: boolean;
      /** set by tools/render_edit.py when src became an image sequence */
      frames?: { count: number; fps: number };
      /** tap ripple; at = seconds from the card's start, x/y = fractions of the visible region */
      taps?: { at: number; x: number; y: number }[];
      /** outline + dim the rest; at/dur = seconds from the card's start, box = fractions of the visible region */
      highlights?: { at: number; dur: number; box: { x: number; y: number; w: number; h: number } }[];
      /** "tilt" = 2.5D entrance/exit (rises with an X-tilt, lifts away); default flat */
      entrance?: "flat" | "tilt";
      /** draw a check mark on the active highlight */
      checks?: boolean;
      /** privacy blur over parts of the recording; at/dur = seconds from the card's start, box = fractions of the visible region */
      masks?: { at: number; dur: number; box: { x: number; y: number; w: number; h: number } }[];
    };

export type Edit = {
  title: string;
  fps: number;
  width: number;
  height: number;
  clips: Clip[];
  captions?: {
    words: Word[]; keywords?: string[]; maxWords?: number; maxChars?: number;
    /** word-synced captions: upcoming words dimmed, each lights up on its spoken start; keyword underline on its word */
    karaoke?: boolean;
    /** exact-word replacements applied when loading the transcript (spelling fixes, English terms) */
    replace?: Record<string, string>;
    /** "plate" = Night plate behind the text (use over bright or white areas); default soft shadow */
    style?: "shadow" | "plate";
    /** move captions for a stretch of the OUTPUT timeline, e.g. below a screen card. top = fraction of height */
    zones?: { at: number; dur: number; top: number }[];
    /** cover plates baked into the footage (tools/render_edit.py): captions sit centred on them, without a plate of their own */
    anchors?: { at: number; dur: number; box: number[] }[];
    /** keep the caption's own plate (tight to the text) even when anchored on a cover (batch 2: narrow blue bars) */
    anchorPlate?: boolean;
  };
  overlays: Overlay[];
  tail?: number; // seconds after the last clip (e.g. for an end card on its own)
  /** solid colour for every plate behind text (caption bar, chips, label cards), e.g. "#56A0FB". Unset = Night glass */
  textPlate?: string;
  /** camera-shake hits (output seconds): a short decaying jolt of the whole frame on big impacts */
  shakes?: { at: number; amp?: number }[];
};

export const clipsDuration = (clips: Clip[]) => clips.reduce((t, c) => t + (c.out - c.in) / (c.freeze ? 1 : c.speed ?? 1), 0);

export const editDuration = (e: Edit) => {
  const overlaysEnd = Math.max(0, ...e.overlays.map((o) => o.at + o.dur));
  // frame-exact: the clips play for their ROUNDED frame counts (clipFrames); summing float durations made the
  // composition a few frames longer than the picture on speed-ramped edits (black frames after the end card)
  const clipsSec = e.clips.reduce((n, c) => n + clipFrames(c, e.fps), 0) / e.fps;
  return Math.max(clipsSec + (e.tail ?? 0), overlaysEnd);
};

/**
 * Map a source time to output time. Returns null if that moment was cut out.
 * Only valid when every clip comes from the same source (the usual talking-head edit).
 */
export const sourceToOutput = (clips: Clip[], t: number): number | null => {
  let offset = 0;
  for (const c of clips) {
    const { in: a, out: b } = span(c);
    const silent = c.freeze || (c.speed ?? 1) !== 1; // no dialogue on frozen / speed-ramped picture
    if (!silent && t >= a && t < b) return offset + (t - a);
    offset += c.freeze ? b - a : (b - a) / (c.speed ?? 1);
  }
  return null;
};

/** times[i] = output start of words[i] (for word-synced captions) */
export type CaptionGroup = { words: string[]; start: number; end: number; times: number[] };

/**
 * Group words into short on-screen phrases (the reference reels show 1–3 words at a time).
 * Breaks on pauses, on punctuation, and at maxWords/maxChars. Times are output times.
 */
const latin = (w: string) => /^[A-Za-z0-9&][A-Za-z0-9&'’-]*$/.test(w.replace(/[.,!?،؟]+$/, ""));

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
      const clip = clips.filter((c) => !c.freeze && (c.speed ?? 1) === 1).map(span).find((c) => mid >= c.in && mid < c.out);
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
      cur = { words: [w.w], start: w.start, end: w.end, times: [w.start] };
    } else {
      cur.words.push(w.w);
      cur.times.push(w.start);
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
      p.times.push(...g.times);
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
