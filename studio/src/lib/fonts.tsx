import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";
import { font } from "./theme";

const f = (p: string) => staticFile(`brand/fonts/${p}`);

const faces: [string, string, FontFaceDescriptors][] = [
  [font.latin, "Inter[opsz,wght].ttf", { weight: "100 900", style: "normal" }],
  [font.latinItalic, "Inter-Italic[opsz,wght].ttf", { weight: "100 900", style: "italic" }],
  [font.numbers, "BarlowCondensed-SemiBold.ttf", { weight: "600" }],
  [font.numbers, "BarlowCondensed-Bold.ttf", { weight: "700" }],
  [font.arabic, "IBMPlexSansArabic-Regular.ttf", { weight: "400" }],
  [font.arabic, "IBMPlexSansArabic-Medium.ttf", { weight: "500" }],
  [font.arabic, "IBMPlexSansArabic-SemiBold.ttf", { weight: "600" }],
  [font.arabic, "IBMPlexSansArabic-Bold.ttf", { weight: "700" }],
];

let loading: Promise<void> | null = null;
const loadAll = () =>
  (loading ??= Promise.all(
    faces.map(([family, file, desc]) =>
      new FontFace(family, `url("${f(file)}")`, desc).load().then((ff) => {
        document.fonts.add(ff);
      }),
    ),
  ).then(() => undefined));

/** Blocks rendering until every brand font (OFL) is loaded, so no frame renders in a fallback font. */
export const useBrandFonts = () => {
  const [handle] = useState(() => delayRender("Loading OSM brand fonts"));
  useEffect(() => {
    loadAll()
      .then(() => continueRender(handle))
      .catch((e) => {
        throw new Error(`Brand font failed to load: ${e}`);
      });
  }, [handle]);
};
