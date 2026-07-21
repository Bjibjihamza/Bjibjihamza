"""Compose one seamless whoami card: portrait + stats, identical background."""
from __future__ import annotations

from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PORTRAIT = ASSETS / "ascii-magic-2.png"
OUT = ASSETS / "whoami-card.png"

BG = (22, 27, 34)  # #161b22 — GitHub dark / SVG panel
FG = (201, 209, 217)
KEY = (255, 166, 87)
VAL = (165, 214, 255)
CC = (97, 110, 127)
ADD = (63, 185, 80)
DEL = (248, 81, 73)

H = 560
PAD = 20
PORTRAIT_MAX_W = 380
PANEL_W = 640
GAP = 28


def load_font(size: int = 15) -> ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\consola.ttf"),
        Path(r"C:\Windows\Fonts\CascadiaMono.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def svg_text(root, eid: str, default: str = "") -> str:
    el = root.find(f".//*[@id='{eid}']")
    if el is not None and el.text is not None:
        return el.text
    return default


def read_stats_from_svg() -> dict[str, str]:
    path = ROOT / "dark_mode.svg"
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
    if not path.exists():
        return defaults
    root = etree.parse(str(path)).getroot()
    return {k: svg_text(root, {
        "age": "age_data",
        "repos": "repo_data",
        "contrib": "contrib_data",
        "stars": "star_data",
        "commits": "commit_data",
        "followers": "follower_data",
        "loc": "loc_data",
        "loc_add": "loc_add",
        "loc_del": "loc_del",
    }[k], v) for k, v in defaults.items()}


def prepare_portrait(img: Image.Image, threshold: int = 16) -> Image.Image:
    """
    Keep only the colored ASCII dots.
    Transparent + near-black pixels become fully transparent so the card BG shows through.
    """
    rgba = img.convert("RGBA")
    pixels = list(rgba.getdata())
    out = []
    for r, g, b, a in pixels:
        if a < 40 or (r <= threshold and g <= threshold and b <= threshold):
            out.append((0, 0, 0, 0))
        else:
            out.append((r, g, b, 255))
    rgba.putdata(out)

    # Crop to visible content so we don't reserve a black rectangle
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    return rgba


def draw_colored_line(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    parts: list[tuple[str, tuple[int, int, int]]],
    font: ImageFont.ImageFont,
) -> None:
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        bbox = draw.textbbox((cx, y), text, font=font)
        cx = bbox[2]


def build_card() -> Path:
    stats = read_stats_from_svg()
    font = load_font(15)
    font_sm = load_font(14)

    portrait = prepare_portrait(Image.open(PORTRAIT))

    # Scale portrait to fit card height (with padding)
    max_h = H - PAD * 2
    ratio = max_h / portrait.height
    pw = int(portrait.width * ratio)
    ph = max_h
    if pw > PORTRAIT_MAX_W:
        pw = PORTRAIT_MAX_W
        ratio = pw / portrait.width
        ph = int(portrait.height * ratio)
    portrait = portrait.resize((pw, ph), Image.Resampling.LANCZOS)

    width = PAD + pw + GAP + PANEL_W + PAD
    # One flat background — no boxes, no borders, no dividers
    card = Image.new("RGBA", (width, H), (*BG, 255))

    px = PAD
    py = (H - ph) // 2
    card.alpha_composite(portrait, (px, py))

    draw = ImageDraw.Draw(card)
    x = PAD + pw + GAP
    y = 32
    lh = 21

    lines: list[list[tuple[str, tuple[int, int, int]]]] = [
        [("hamza@bjibji", VAL), (" --------------------------------", CC)],
        [(". ", CC), ("OS", KEY), (":", KEY), (" ........................ ", CC), ("Windows 11, Linux (WSL)", VAL)],
        [(". ", CC), ("Uptime", KEY), (":", KEY), (" ...................... ", CC), (stats["age"], VAL)],
        [(". ", CC), ("Host", KEY), (":", KEY), (" ............................. ", CC), ("ENSA Tetouan — Big Data & AI", VAL)],
        [(". ", CC), ("Kernel", KEY), (":", KEY), (" ......................... ", CC), ("AI & Data Engineer", VAL)],
        [(". ", CC), ("IDE", KEY), (":", KEY), (" ........................ ", CC), ("Cursor, VS Code", VAL)],
        [(". ", CC)],
        [(". ", CC), ("Languages", KEY), (".", FG), ("Programming", KEY), (":", KEY), (" ..... ", CC), ("Python, JavaScript, TypeScript, C#, SQL", VAL)],
        [(". ", CC), ("Languages", KEY), (".", FG), ("Computer", KEY), (":", KEY), (" ......... ", CC), ("HTML, CSS, JSON, YAML, Docker", VAL)],
        [(". ", CC), ("Languages", KEY), (".", FG), ("Real", KEY), (":", KEY), (" ......................... ", CC), ("Arabic, French, English", VAL)],
        [(". ", CC)],
        [(". ", CC), ("Interests", KEY), (".", FG), ("Software", KEY), (":", KEY), (" .... ", CC), ("Real-Time Pipelines, MLOps, Full-Stack", VAL)],
        [(". ", CC), ("Interests", KEY), (".", FG), ("Domains", KEY), (":", KEY), (" ............. ", CC), ("Cybersecurity, Smart Energy", VAL)],
        [("- Contact", FG), (" --------------------------------", CC)],
        [(". ", CC), ("Email", KEY), (":", KEY), (" ..................... ", CC), ("hamzabjibji@gmail.com", VAL)],
        [(". ", CC), ("GitHub", KEY), (":", KEY), (" .................... ", CC), ("Bjibjihamza", VAL)],
        [(". ", CC), ("LinkedIn", KEY), (":", KEY), (" .................................... ", CC), ("hamzabjibji", VAL)],
        [(". ", CC), ("Phone", KEY), (":", KEY), (" ..................................... ", CC), ("+212 636 376 992", VAL)],
        [("- GitHub Stats", FG), (" ---------------------------", CC)],
        [
            (". ", CC), ("Repos", KEY), (":", KEY), (" .... ", CC), (stats["repos"], VAL),
            (" {", FG), ("Contributed", KEY), (": ", FG), (stats["contrib"], VAL),
            ("} | ", FG), ("Stars", KEY), (":", KEY), (" ........... ", CC), (stats["stars"], VAL),
        ],
        [
            (". ", CC), ("Commits", KEY), (":", KEY), (" ................. ", CC), (stats["commits"], VAL),
            (" | ", FG), ("Followers", KEY), (":", KEY), (" ....... ", CC), (stats["followers"], VAL),
        ],
        [
            (". ", CC), ("Lines of Code on GitHub", KEY), (":", KEY), (". ", CC), (stats["loc"], VAL),
            (" ( ", FG), (stats["loc_add"], ADD), ("++", ADD), (", ", FG),
            (stats["loc_del"], DEL), ("--", DEL), (" )", FG),
        ],
    ]

    for i, parts in enumerate(lines):
        if i == 13:
            y += 16
        if i == 18:
            y += 20
        f = font_sm if i >= 19 else font
        draw_colored_line(draw, x, y, parts, f)
        y += lh

    card.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({width}x{H})")
    return OUT


if __name__ == "__main__":
    build_card()
