"""Compose one seamless whoami card: portrait + Andrew-style aligned panel."""
from __future__ import annotations

from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PORTRAIT = ASSETS / "ascii-magic-2.png"
OUT = ASSETS / "whoami-card.png"

BG = (22, 27, 34)  # #161b22
FG = (201, 209, 217)
KEY = (255, 166, 87)  # #ffa657
VAL = (165, 214, 255)  # #a5d6ff
CC = (97, 110, 127)  # #616e7f
ADD = (63, 185, 80)
DEL = (248, 81, 73)

H = 530
PAD = 20
PORTRAIT_MAX_W = 360
# Panel wide enough for full Andrew-style lines
PANEL_CHARS = 78
GAP = 28

# Character column where VALUES start (Andrew-style justified layout)
VALUE_COL = 34


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
    pixels = list(rgba.getdata())
    out = []
    for r, g, b, a in pixels:
        if a < 40 or (r <= threshold and g <= threshold and b <= threshold):
            out.append((0, 0, 0, 0))
        else:
            out.append((r, g, b, 255))
    rgba.putdata(out)
    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    return rgba


def char_w(font: ImageFont.ImageFont) -> float:
    """Average monospace advance."""
    bbox = font.getbbox("M")
    return float(bbox[2] - bbox[0])


def draw_parts(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    parts: list[tuple[str, tuple[int, int, int]]],
    font: ImageFont.ImageFont,
) -> None:
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        cx += font.getlength(text)


def dots_to(label_plain: str, value_col: int = VALUE_COL) -> str:
    """Andrew-style: ' ...... ' padding so values share one vertical column."""
    # prefix is ". {label}:"
    prefix_len = 2 + len(label_plain) + 1  # ". " + label + ":"
    pad = max(1, value_col - prefix_len)
    return " " + ("." * pad) + " "


def row_kv(label: str, value: str) -> list[tuple[str, tuple[int, int, int]]]:
    """Single label (may contain dots like Languages.Programming)."""
    # Color dotted labels: Languages.Programming → Languages orange, . gray, Programming orange
    parts: list[tuple[str, tuple[int, int, int]]] = [(". ", CC)]
    if "." in label:
        left, right = label.split(".", 1)
        parts += [(left, KEY), (".", FG), (right, KEY), (":", KEY)]
    else:
        parts += [(label, KEY), (":", KEY)]
    parts += [(dots_to(label), CC), (value, VAL)]
    return parts


def header_line(title: str, total_chars: int = 58) -> list[tuple[str, tuple[int, int, int]]]:
    # "- Contact ———————————"
    dash = "—" * max(4, total_chars - len(title) - 3)
    return [(title, FG), (f" {dash}-—-", CC)]


def build_card() -> Path:
    stats = read_stats_from_svg()
    font = load_font(15)

    portrait = prepare_portrait(Image.open(PORTRAIT))
    max_h = H - PAD * 2
    ratio = max_h / portrait.height
    pw = int(portrait.width * ratio)
    ph = max_h
    if pw > PORTRAIT_MAX_W:
        pw = PORTRAIT_MAX_W
        ratio = pw / portrait.width
        ph = int(portrait.height * ratio)
    portrait = portrait.resize((pw, ph), Image.Resampling.LANCZOS)

    cw = char_w(font)
    panel_px = int(PANEL_CHARS * cw) + 8
    width = PAD + pw + GAP + panel_px + PAD

    card = Image.new("RGBA", (width, H), (*BG, 255))
    card.alpha_composite(portrait, (PAD, (H - ph) // 2))
    draw = ImageDraw.Draw(card)

    x = PAD + pw + GAP
    y = 30
    lh = 20

    # Exact Andrew structure, Hamza content, justified VALUE_COL
    rows: list[list[tuple[str, tuple[int, int, int]]] | None] = [
        [("hamza@bjibji", VAL), (" -———————————————————————————————————————————-—-", CC)],
        row_kv("OS", "Windows 11, Linux (WSL)"),
        row_kv("Uptime", stats["age"]),
        row_kv("Host", "ENSA Tetouan — Big Data & AI"),
        row_kv("Kernel", "AI & Data Engineer"),
        row_kv("IDE", "Cursor, VS Code"),
        None,  # blank
        row_kv("Languages.Programming", "Python, JS, TypeScript, C#, SQL"),
        row_kv("Languages.Computer", "HTML, CSS, JSON, YAML, Docker"),
        row_kv("Languages.Real", "Arabic, French, English"),
        None,
        row_kv("Interests.Software", "Pipelines, MLOps, Full-Stack"),
        row_kv("Interests.Domains", "Cybersecurity, Smart Energy"),
        None,
        header_line("- Contact"),
        row_kv("Email", "hamzabjibji@gmail.com"),
        row_kv("GitHub", "Bjibjihamza"),
        row_kv("LinkedIn", "hamzabjibji"),
        row_kv("Phone", "+212 636 376 992"),
        None,
        header_line("- GitHub Stats"),
        # Stats: keep Andrew's multi-column feel but still readable
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

    for row in rows:
        if row is None:
            y += lh
            continue
        draw_parts(draw, x, y, row, font)
        y += lh

    card.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({width}x{H})")
    return OUT


if __name__ == "__main__":
    build_card()
