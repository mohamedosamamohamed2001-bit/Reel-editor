import { Easing, interpolate } from "remotion";

// Book: calm, premium, not flashy. Short eased moves, no bounce.
export const ENTER = 10; // frames
export const EXIT = 8;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** 0→1 over the entrance, 1→0 over the exit. `frame` is local to the overlay. */
export const presence = (frame: number, duration: number, enter = ENTER, exit = EXIT) => {
  const inP = interpolate(frame, [0, enter], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const outP = interpolate(frame, [duration - exit, duration], [1, 0], { ...clamp, easing: Easing.in(Easing.cubic) });
  return Math.min(inP, outP);
};

export const progress = (frame: number, from: number, to: number) =>
  interpolate(frame, [from, to], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
