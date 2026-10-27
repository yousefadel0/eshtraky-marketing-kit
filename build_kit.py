"""Turns the raw tablet screenshots into clean, branded marketing images.

raw (screens/) -> clean (clean/: status bar and nav bar removed, private strings painted over)
              -> framed (framed/: on a lime or black card with rounded corners and a soft shadow)
              -> contact-sheet.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).parent
RAW, CLEAN, FRAMED = ROOT / "screens", ROOT / "clean", ROOT / "framed"
CLEAN.mkdir(exist_ok=True)
FRAMED.mkdir(exist_ok=True)

LIME = (214, 255, 0)
INK = (17, 17, 17)
TOP, BOTTOM = 36, 72  # Android status bar and navigation bar

# name -> (title for the brief, who it speaks to, rectangles to paint over (x0, y0, x1, y1, colour))
SCREENS = {
    "home": ("الرئيسية", "عضو", []),
    "offers-list": ("كل العروض", "عضو", []),
    "offer-details": ("تفاصيل العرض والمواعيد", "عضو", []),
    "booking-coupon": ("الدفع وكوبون الخصم", "عضو", [(40, 1000, 260, 1070, (255, 255, 255))]),
    "clubs": ("الأندية القريبة", "عضو", []),
    "notifications": ("الإشعارات", "عضو", []),
    "support-chat": ("الدعم داخل التطبيق", "عضو", []),
    "club-home": ("لوحة النادي: الإيراد والمشتركين", "نادي", [(170, 245, 880, 285, (24, 26, 22))]),
    "club-home-2": ("أداء العروض والاشتراكات الجاية", "نادي", []),
    "club-subscribers": ("كل مشتركين النادي", "نادي", []),
    "club-scanner": ("تسجيل الحضور بالـ QR", "نادي", []),
    "club-announce": ("إعلان لمشتركين النادي", "نادي", [(170, 245, 880, 285, (24, 26, 22))]),
}


def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def clean(name: str, patches: list) -> Image.Image:
    img = Image.open(RAW / f"{name}.png").convert("RGB")
    draw = ImageDraw.Draw(img)
    for x0, y0, x1, y1, colour in patches:
        draw.rectangle((x0, y0, x1, y1), fill=colour)
    img = img.crop((0, TOP, img.width, img.height - BOTTOM))
    img.save(CLEAN / f"{name}.png")
    return img


def frame(name: str, img: Image.Image, dark: bool) -> None:
    pad = 90
    shot = rounded(img.resize((720, int(img.height * 720 / img.width))), 48)
    w, h = shot.width + pad * 2, shot.height + pad * 2
    bg = Image.new("RGB", (w, h), INK if dark else LIME)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((pad, pad + 24, pad + shot.width, pad + shot.height + 24), 48, fill=(0, 0, 0, 120 if not dark else 200))
    shadow = shadow.filter(ImageFilter.GaussianBlur(36))
    bg.paste(shadow, (0, 0), shadow)
    bg.paste(shot, (pad, pad), shot)
    bg.save(FRAMED / f"{name}{'-dark' if dark else '-lime'}.png")


def contact_sheet(images: dict) -> None:
    cell_w, cell_h, gap = 300, 520, 24
    cols = 6
    rows = -(-len(images) // cols)
    sheet = Image.new("RGB", (cols * (cell_w + gap) + gap, rows * (cell_h + gap) + gap), INK)
    for i, (name, img) in enumerate(images.items()):
        thumb = img.copy()
        thumb.thumbnail((cell_w, cell_h))
        x, y = gap + (i % cols) * (cell_w + gap), gap + (i // cols) * (cell_h + gap)
        sheet.paste(thumb, (x, y))
    sheet.save(ROOT / "contact-sheet.png")


def main() -> None:
    cleaned = {}
    for name, (_title, _who, patches) in SCREENS.items():
        if not (RAW / f"{name}.png").exists():
            print("missing", name)
            continue
        img = clean(name, patches)
        cleaned[name] = img
        frame(name, img, dark=False)
        frame(name, img, dark=True)
    contact_sheet(cleaned)
    print(len(cleaned), "screens processed")


if __name__ == "__main__":
    main()
