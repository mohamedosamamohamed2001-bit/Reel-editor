import { AbsoluteFill } from "remotion";

/** Brand texture: diagonal hairlines at 112°, 3–5% white. Quiet background texture only. */
export const Hairlines: React.FC<{ opacity?: number }> = ({ opacity = 0.04 }) => (
  <AbsoluteFill
    style={{
      backgroundImage: `repeating-linear-gradient(112deg, rgba(255,255,255,${opacity}) 0 2px, transparent 2px 120px)`,
      pointerEvents: "none",
    }}
  />
);
