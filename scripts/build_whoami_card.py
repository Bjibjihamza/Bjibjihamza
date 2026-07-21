"""Compose one seamless whoami card: portrait + Andrew-style pixel-aligned panel."""
from __future__ import annotations

from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PORTRAIT = ASSETS / "ascii-magic-2.png"
OUT = ASSETS / "whoami-card.png"

BG = (22, 27, 34)
FG = (201, 209, 217)
KEY = (255, 166, 87)
VAL = (165, 214, 255)
CC = (97, 110, 127)
ADD = (63, 185, 80)
DEL = (248, 81, 73)

H = 530
PAD = 20
PORTRAIT_MAX_W = 360
PANEL_CHARS = 78
GAP = 28
VALUE_COL = 34  # char column → converted to pixels for perfect alignment


def load_font(size: int = 15) -> ImageFont.ImageFont:
    for p in (
        Path(r"C:\Windows\Fonts\consola.ttf"),
        Path(r"C:\Windows\Fonts\CascadiaMono.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"),
    ):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def svg_text(root, eid: str, default: str = "") -> str:
    el = root.find(f".//*[@id='{eid}']")
    if el is not None and el.text is not None:
        return el.text
    return default


def read_stats_from_svg() -> dict[str, str]:
    defaults = {
        "age": "22 years, 9 months, 23 days",
        "repos": "23",
        "contrib": "24",
        "stars": "9",
        "commits": "20",
        "followers": "12",
        "loc": "68,915",
        "loc_add": "92,404",
        "loc_del": "23,489",
    }
    path = ROOT / "dark_mode.svg"
    if not path.exists():
        return defaults
    root = etree.parse(str(path)).getroot()
    ids = {
        "age": "age_data",
        "repos": "repo_data",
        "contrib": "contrib_data",
        "stars": "star_data",
        "commits": "commit_data",
        "followers": "follower_data",
        "loc": "loc_data",
        "loc_add": "loc_add",
        "loc_del": "loc_del",
    }
    return {k: svg_text(root, ids[k], v) for k, v in defaults.items()}


def prepare_portrait(img: Image.Image, threshold: int = 16) -> Image.Image:
    rgba = img.convert("RGBA")
    out = []
    for r, g, b, a in rgba.getdata():
        if a < 40 or (r <= threshold and g <= threshold and b <= threshold):
            out.append((0, 0, 0, 0))
        else:
            out.append((r, g, b, 255))
    rgba.putdata(out)
    bbox = rgba.getbbox()
    return rgba.crop(bbox) if bbox else rgba


def draw_parts(draw, x, y, parts, font) -> None:
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        cx += font.getlength(text)


def draw_kv_row(draw, x, y, label, value, font, value_x) -> None:
    """Andrew-style row with value locked to a fixed pixel X."""
    draw.text((x, y), ". ", fill=CC, font=font)
    cx = x + font.getlength(". ")

    if "." in label:
        left, right = label.split(".", 1)
        draw.text((cx, y), left, fill=KEY, font=font)
        cx += font.getlength(left)
        draw.text((cx, y), ".", fill=FG, font=font)
        cx += font.getlength(".")
        draw.text((cx, y), right, fill=KEY, font=font)
        cx += font.getlength(right)
    else:
        draw.text((cx, y), label, fill=KEY, font=font)
        cx += font.getlength(label)

    draw.text((cx, y), ":", fill=KEY, font=font)
    cx += font.getlength(":")

    dot_w = font.getlength(".")
    gap = font.getlength(" ")
    cx += gap
    while cx + dot_w + gap <= value_x:
        draw.text((cx, y), ".", fill=CC, font=font)
        cx += dot_w

    draw.text((value_x, y), value, fill=VAL, font=font)


def header_line(title: str) -> list[tuple[str, tuple[int, int, int]]]:
    dash = "—" * 40
    return [(title, FG), (f" {dash}-—-", CC)]


def build_card() -> Path:
    stats = read_stats_from_svg()
    font = load_font(15)
    cw = float(font.getbbox("M")[2] - font.getbbox("M")[0])

    portrait = prepare_portrait(Image.open(PORTRAIT))
    max_h = H - PAD * 2
    ratio = max_h / portrait.height
    pw, ph = int(portrait.width * ratio), max_h
    if pw > PORTRAIT_MAX_W:
        pw = PORTRAIT_MAX_W
        ratio = pw / portrait.width
        ph = int(portrait.height * ratio)
    portrait = portrait.resize((pw, ph), Image.Resampling.LANCZOS)

    panel_px = int(PANEL_CHARS * cw) + 16
    width = PAD + pw + GAP + panel_px + PAD
    card = Image.new("RGBA", (width, H), (*BG, 255))
    card.alpha_composite(portrait, (PAD, (H - ph) // 2))
    draw = ImageDraw.Draw(card)

    x = PAD + pw + GAP
    value_x = int(x + VALUE_COL * cw)
    y = 30
    lh = 20

    draw_parts(
        draw,
        x,
        y,
        [("hamza@bjibji", VAL), (" -———————————————————————————————————————————-—-", CC)],
        font,
    )
    y += lh

    for label, value in [
        ("OS", "Windows 11, Linux (WSL)"),
        ("Uptime", stats["age"]),
        ("Host", "ENSA Tetouan — Big Data & AI"),
        ("Kernel", "AI & Data Engineer"),
        ("IDE", "Cursor, VS Code"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, value_x)
        y += lh

    y += lh
    for label, value in [
        ("Languages.Programming", "Python, JS, TypeScript, C#, SQL"),
        ("Languages.Computer", "HTML, CSS, JSON, YAML, Docker"),
        ("Languages.Real", "Arabic, French, English"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, value_x)
        y += lh

    y += lh
    for label, value in [
        ("Interests.Software", "Pipelines, MLOps, Full-Stack"),
        ("Interests.Domains", "Cybersecurity, Smart Energy"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, value_x)
        y += lh

    y += lh
    draw_parts(draw, x, y, header_line("- Contact"), font)
    y += lh
    for label, value in [
        ("Email", "hamzabjibji@gmail.com"),
        ("GitHub", "Bjibjihamza"),
        ("LinkedIn", "hamzabjibji"),
        ("Phone", "+212 636 376 992"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, value_x)
        y += lh

    y += lh
    draw_parts(draw, x, y, header_line("- GitHub Stats"), font)
    y += lh
    draw_parts(
        draw,
        x,
        y,
        [
            (". ", CC), ("Repos", KEY), (":", KEY), (" .... ", CC), (stats["repos"], VAL),
            (" {", FG), ("Contributed", KEY), (": ", FG), (stats["contrib"], VAL),
            ("} | ", FG), ("Stars", KEY), (":", KEY), (" ........... ", CC), (stats["stars"], VAL),
        ],
        font,
    )
    y += lh
    draw_parts(
        draw,
        x,
        y,
        [
            (". ", CC), ("Commits", KEY), (":", KEY), (" ................. ", CC), (stats["commits"], VAL),
            (" | ", FG), ("Followers", KEY), (":", KEY), (" ....... ", CC), (stats["followers"], VAL),
        ],
        font,
    )
    y += lh
    draw_parts(
        draw,
        x,
        y,
        [
            (". ", CC), ("Lines of Code on GitHub", KEY), (":", KEY), (". ", CC), (stats["loc"], VAL),
            (" ( ", FG), (stats["loc_add"], ADD), ("++", ADD), (", ", FG),
            (stats["loc_del"], DEL), ("--", DEL), (" )", FG),
        ],
        font,
    )

    card.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({width}x{H}) value_x={value_x}")
    return OUT


if __name__ == "__main__":
    build_card()
