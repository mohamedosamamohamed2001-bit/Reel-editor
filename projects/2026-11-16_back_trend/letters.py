"""LO_E letters of the trend (reference Trent1.mp4): bold serif, white, stacked down his spine; the V slot is left empty so his
back's V-taper reads as the V of LOVE. Sizes measured on the reference (screen 1320x2868, reel fitted to width = x1.2222):
cap heights L 187, O 174 (overshoot incl.), E 187; widths L 146, O 159, E 132 (reel px). Placed by his anatomy on the freeze
frame (src 22.95 s): O over the back of his head, L above it with the reference's L-O gap, E on his waistband.
Font: Liberation Serif Bold (SIL OFL, system font), each glyph scaled to the reference box (the reference face is narrower)."""
import sys
from PIL import Image, ImageDraw, ImageFont
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
REF = {"L": (146, 187), "O": (159, 174), "E": (132, 187)}       # w, h in reel px (reference)


def glyph(ch, w, h, grow=0.025):
    """Glyph scaled to the reference box, strokes grown evenly (round kernel) to the reference's heavier, softer weight;
    the outer box stays w x h."""
    import cv2, numpy as np
    f = ImageFont.truetype(FONT, 800)
    im = Image.new("L", (900, 900), 0); d = ImageDraw.Draw(im)
    d.text((50, 0), ch, font=f, fill=255)
    im = im.crop(im.getbbox())
    r = max(1, round(grow * h))                      # stroke growth in output px
    S = 4                                            # work at 4x for clean edges
    a = np.asarray(im.resize((round((w - 2 * r) * S), round((h - 2 * r) * S)), Image.LANCZOS))
    a = cv2.copyMakeBorder(a, r * S, r * S, r * S, r * S, cv2.BORDER_CONSTANT, value=0)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r * S + 1, 2 * r * S + 1))
    a = cv2.dilate(a, k)
    return Image.fromarray(a).resize((round(w), round(h)), Image.LANCZOS)


def render(out, k=1.15, cx=540, o_mid=530, e_top=1344, gap_lo=86):
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    wL, hL = REF["L"]; wO, hO = REF["O"]; wE, hE = REF["E"]
    O = glyph("O", wO * k, hO * k); L = glyph("L", wL * k, hL * k); E = glyph("E", wE * k, hE * k)
    o_top = round(o_mid - O.height / 2)
    l_top = o_top - round(gap_lo * k) - L.height
    for g, top, ox in ((L, l_top, 4), (O, o_top, 0), (E, e_top, 0)):     # optical centring: L's stem sits left of its box centre
        white = Image.new("RGBA", g.size, (255, 255, 255, 255)); white.putalpha(g)
        img.alpha_composite(white, (round(cx - g.width / 2 + ox), top))
    img.save(out)
    return {"L": l_top, "O": o_top, "E": e_top}


if __name__ == "__main__":
    print(render(sys.argv[1] if len(sys.argv) > 1 else "work/letters.png"))
