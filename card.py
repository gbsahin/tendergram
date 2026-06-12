"""Generate tender card images (PNG) with Pillow."""
import io
import textwrap

import config

SOURCE_NAMES = {"world_bank": "World Bank", "undp": "UNDP", "manual": "Manual"}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
W, H = 1200, 630


def _font(name: str, size: int):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(f"{FONT_DIR}/{name}.ttf", size)
    except OSError:
        try:  # windows fallback
            fallback = {"DejaVuSans-Bold": "arialbd.ttf", "DejaVuSans": "arial.ttf"}
            return ImageFont.truetype(fallback.get(name, "arial.ttf"), size)
        except OSError:
            return ImageFont.load_default()


def render(t: dict) -> bytes:
    """Return PNG bytes for a tender card, or raise ImportError if no Pillow."""
    from PIL import Image, ImageDraw

    accent = config.REGION_COLORS.get(t.get("region"), "#444444")
    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    # Top accent band
    d.rectangle([0, 0, W, 14], fill=accent)

    # Region + country chip
    chip_font = _font("DejaVuSans-Bold", 34)
    chip_text = f"{(t.get('country') or '').upper()}  ·  {(t.get('region') or '').upper()}"
    d.text((60, 56), chip_text, font=chip_font, fill=accent)

    # Notice type
    type_font = _font("DejaVuSans", 28)
    d.text((60, 112), t.get("notice_type") or "Procurement Notice",
           font=type_font, fill="#777777")

    # Title (wrapped, max 4 lines)
    title_font = _font("DejaVuSans-Bold", 52)
    lines = textwrap.wrap(t.get("title", ""), width=40)[:4]
    if len(textwrap.wrap(t.get("title", ""), width=40)) > 4:
        lines[-1] = lines[-1][:37] + "..."
    y = 180
    for line in lines:
        d.text((60, y), line, font=title_font, fill="#1A1A1A")
        y += 66

    # Footer divider
    d.line([60, 500, W - 60, 500], fill="#DDDDDD", width=2)

    # Deadline + reference
    foot_font = _font("DejaVuSans-Bold", 32)
    foot_small = _font("DejaVuSans", 26)
    if t.get("deadline"):
        d.text((60, 524), f"Deadline: {str(t['deadline'])[:10]}",
               font=foot_font, fill=accent)
    if t.get("reference_no"):
        d.text((60, 570), f"Ref: {t['reference_no']}", font=foot_small, fill="#777777")

    # Source watermark
    src = SOURCE_NAMES.get(t.get("source"), str(t.get("source") or ""))
    bbox = d.textbbox((0, 0), src, font=foot_small)
    d.text((W - 60 - (bbox[2] - bbox[0]), 570), src, font=foot_small, fill="#AAAAAA")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
