"""HEIC -> sRGB PNG (work/<stem>.png). pillow-heif decode, EXIF orientation applied, the photo's own ICC profile
(iPhone Display P3) converted to sRGB with ImageCms (relative colorimetric). No other colour, tone or detail change."""
import io
from pathlib import Path
from PIL import Image, ImageCms, ImageOps
import pillow_heif

P = Path(__file__).resolve().parent
pillow_heif.register_heif_opener()
(P / "work").mkdir(exist_ok=True)
srgb = ImageCms.createProfile("sRGB")
for f in sorted((P / "source").glob("*.HEIC")):
    im = ImageOps.exif_transpose(Image.open(f))
    icc = im.info.get("icc_profile")
    if icc:
        im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb,
                                       renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, outputMode="RGB")
    else:
        im = im.convert("RGB")
    im.save(P / "work" / f"{f.stem}.png")
    print(f.stem, im.size, "icc" if icc else "no-icc")
