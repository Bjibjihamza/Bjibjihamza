"""Compose one seamless whoami card: ascii-me-3.png + stats panel, same background."""
from __future__ import annotations

from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PORTRAIT = ASSETS / "ascii-me-3.png"
OUT = ASSETS / "whoami-card.png"

BG = (22, 27, 34)  # #161b22
FG = (201, 209, 217)
KEY = (255, 166, 87)
VAL = (165, 214, 255)
CC = (97, 110, 127)
ADD = (63, 185, 80)
DEL = (248, 81, 73)

H = 530
PAD = 16
PORTRAIT_W = 420
PANEL_W = 640
GAP = 12  # same BG color → no visible split


def match_bg(img: Image.Image, bg: tuple[int, int, int] = BG, threshold: int = 22) -> Image.Image:
    """Map near-black portrait pixels to card background so there is no seam."""
    rgba = img.convert("RGBA")
    pixels = list(rgba.getdata())
    br, bg_, bb = bg
    out = []
    for r, g, b, a in pixels:
        if a < 10 or (r <= threshold and g <= threshold and b <= threshold):
            out.append((br, bg_, bb, 255))
        else:
            out.append((r, g, b, a))
    rgba.putdata(out)
    return rgba


def load_font(size: int = 15) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
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
    if not path.exists():
        return {
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
    root = etree.parse(str(path)).getroot()
    return {
        "age": svg_text(root, "age_data", "22 years, 9 months, 23 days"),
        "repos": svg_text(root, "repo_data", "23"),
        "contrib": svg_text(root, "contrib_data", "24"),
        "stars": svg_text(root, "star_data", "9"),
        "commits": svg_text(root, "commit_data", "20"),
        "followers": svg_text(root, "follower_data", "12"),
        "loc": svg_text(root, "loc_data", "68,915"),
        "loc_add": svg_text(root, "loc_add", "92,404"),
        "loc_del": svg_text(root, "loc_del", "23,489"),
    }


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


def match_bg(img: Image.Image, bg: tuple[int, int, int] = BG, threshold: int = 18) -> Image.Image:
    """Map near-black portrait pixels to card background so there is no seam."""
    rgba = img.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size
    br, bg_, bb = bg
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 10 or (r <= threshold and g <= threshold and b <= threshold):
                pixels[x, y] = (br, bg_, bb, 255)
    return rgba


def build_card() -> Path:
    stats = read_stats_from_svg()
    font = load_font(15)
    font_sm = load_font(14)

    portrait = match_bg(Image.open(PORTRAIT))
    # Fit portrait into left column, cover height
    target_h = H - PAD * 2
    ratio = target_h / portrait.height
    pw = int(portrait.width * ratio)
    if pw > PORTRAIT_W:
        pw = PORTRAIT_W
        ratio = pw / portrait.width
        target_h = int(portrait.height * ratio)
    portrait = portrait.resize((pw, target_h), Image.Resampling.LANCZOS)

    width = PAD + pw + GAP + PANEL_W + PAD
    card = Image.new("RGB", (width, H), BG)

    # Portrait flush on left, vertically centered — same BG, no divider
    px = PAD
    py = (H - portrait.height) // 2
    card.paste(portrait.convert("RGB"), (px, py))
    draw = ImageDraw.Draw(card)

    x = PAD + pw + GAP
    y0 = 28
    lh = 22

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
            (". ", CC),
            ("Repos", KEY),
            (":", KEY),
            (" .... ", CC),
            (stats["repos"], VAL),
            (" {", FG),
            ("Contributed", KEY),
            (": ", FG),
            (stats["contrib"], VAL),
            ("} | ", FG),
            ("Stars", KEY),
            (":", KEY),
            (" ........... ", CC),
            (stats["stars"], VAL),
        ],
        [
            (". ", CC),
            ("Commits", KEY),
            (":", KEY),
            (" ................. ", CC),
            (stats["commits"], VAL),
            (" | ", FG),
            ("Followers", KEY),
            (":", KEY),
            (" ....... ", CC),
            (stats["followers"], VAL),
        ],
        [
            (". ", CC),
            ("Lines of Code on GitHub", KEY),
            (":", KEY),
            (". ", CC),
            (stats["loc"], VAL),
            (" ( ", FG),
            (stats["loc_add"], ADD),
            ("++", ADD),
            (", ", FG),
            (stats["loc_del"], DEL),
            ("--", DEL),
            (" )", FG),
        ],
    ]

    # Spacing map similar to SVG y positions
    y = y0
    for i, parts in enumerate(lines):
        # Extra space before Contact / Stats headers (indices 13, 18)
        if i == 13:
            y += 16
        if i == 18:
            y += 20
        f = font_sm if i >= 19 else font
        draw_colored_line(draw, x, y, parts, f)
        y += lh

    # Soft rounded look: optional border matching card
    # (no internal divider)
    card.save(OUT, optimize=True)
    print(f"Wrote {OUT} ({card.size[0]}x{card.size[1]})")
    return OUT


if __name__ == "__main__":
    build_card()
