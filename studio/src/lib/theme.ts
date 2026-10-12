import tokens from "../../../brand/tokens.json";

const c = tokens.color;
export const color = {
  night: c.night.hex,
  surface: c.surface.hex,
  surfaceRaised: c.surfaceRaised.hex,
  line: c.line.hex,
  coreBlue: c.coreBlue.hex,
  glowBlue: c.glowBlue.hex,
  cyan: c.signalCyan.hex,
  text: c.textWhite.hex,
  muted: c.muted.hex,
  copper: c.methodCopper.hex,
  steel: c.steel.hex,
} as const;

export const font = {
  latin: "OSM Inter",
  latinItalic: "OSM Inter Italic",
  numbers: "OSM Barlow Condensed",
  arabic: "OSM Plex Arabic",
} as const;

// 9:16 frame. Book rule: no text in the top/bottom 14% on Reels and Stories.
export const frame = { width: 1080, height: 1920, fps: 30 } as const;
export const safe = { top: Math.round(frame.height * 0.14), bottom: Math.round(frame.height * 0.14), side: 72 } as const;

export const isArabic = (s: string) => /[؀-ۿ]/.test(s);
