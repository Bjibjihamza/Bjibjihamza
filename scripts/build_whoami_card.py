"""Compose whoami card: portrait + Andrew-style RIGHT-aligned panel (cube edge)."""
from __future__ import annotations

from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PORTRAIT = ASSETS / "ascii-magic-3.png"
OUT = ASSETS / "whoami-card.png"

BG = (22, 27, 34)
FG = (201, 209, 217)
KEY = (255, 166, 87)
VAL = (165, 214, 255)
CC = (97, 110, 127)
ADD = (63, 185, 80)
DEL = (248, 81, 73)

PAD = 20
PORTRAIT_MAX_W = 360
GAP = 28
TOP = 30
LINE = 20
BOTTOM_PAD = 24
# Fixed content width in characters → every line ends on the same vertical edge
PANEL_WIDTH_CHARS = 62

# header + OS block + gaps + languages + interests + contact + stats
_CONTENT_LINES = 1 + 4 + 1 + 1 + 1 + 2 + 1 + 1 + 4 + 1 + 1 + 3
H = TOP + _CONTENT_LINES * LINE + BOTTOM_PAD


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


def draw_rule(draw, x: int, y: int, prefix: str, font, right_x: int, prefix_color=VAL) -> None:
    """Draw 'prefix ———…' filling exactly to right_x (cube right edge)."""
    draw.text((x, y), prefix, fill=prefix_color, font=font)
    cx = x + font.getlength(prefix)
    dash = "—"
    dash_w = font.getlength(dash)
    # trailing "-—-" like Andrew
    tail = "-—-"
    tail_w = font.getlength(tail)
    while cx + dash_w + tail_w <= right_x:
        draw.text((cx, y), dash, fill=CC, font=font)
        cx += dash_w
    draw.text((right_x - tail_w, y), tail, fill=CC, font=font)


def draw_kv_row(draw, x: int, y: int, label: str, value: str, font, right_x: int) -> None:
    """
    Andrew cube style:
      . Label: .............. value
    Values are RIGHT-aligned to right_x so every line ends on the same edge.
    """
    # Left: ". Label:"
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

    # Right-aligned value
    val_w = font.getlength(value)
    value_x = right_x - val_w

    # Dots between label and value
    dot_w = font.getlength(".")
    gap = font.getlength(" ")
    cx += gap
    while cx + dot_w + gap <= value_x:
        draw.text((cx, y), ".", fill=CC, font=font)
        cx += dot_w

    draw.text((value_x, y), value, fill=VAL, font=font)


def draw_stats_line(draw, x: int, y: int, parts: list[tuple[str, tuple]], font, right_x: int) -> None:
    """Draw a stats line, then pad trailing dots/spaces conceptually by ensuring end == right_x.
    For multi-segment stats we left-draw then fill remaining with nothing (line naturally ends early)
    OR we right-pad with spaces visually by pushing last segment — Andrew's LOC line defines the edge.
    """
    cx = x
    for text, color in parts:
        draw.text((cx, y), text, fill=color, font=font)
        cx += font.getlength(text)
    # If short, fill remaining with dim dots to the cube edge (keeps rectangular block)
    if cx < right_x - font.getlength(" "):
        dot_w = font.getlength(".")
        cx += font.getlength(" ")
        while cx + dot_w <= right_x:
            draw.text((cx, y), ".", fill=CC, font=font)
            cx += dot_w


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

    panel_w = int(PANEL_WIDTH_CHARS * cw)
    width = PAD + pw + GAP + panel_w + PAD
    card = Image.new("RGBA", (width, H), (*BG, 255))
    card.alpha_composite(portrait, (PAD, (H - ph) // 2))
    draw = ImageDraw.Draw(card)

    x = PAD + pw + GAP
    right_x = x + panel_w  # ← every line ends here (the cube edge)
    y = TOP
    lh = LINE

    # Header rule — full width to right_x
    draw_rule(draw, x, y, "hamza@bjibji ", font, right_x, prefix_color=VAL)
    y += lh

    for label, value in [
        ("Signal", "Online · Building"),
        ("Uptime", stats["age"]),
        ("Host", "ENSA Tetouan — Big Data & AI"),
        ("Kernel", "AI & Data Engineer"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, right_x)
        y += lh

    y += lh
    for label, value in [
        ("Languages.Real", "Arabic, French, English"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, right_x)
        y += lh

    y += lh
    for label, value in [
        ("Interests.Software", "Pipelines, MLOps, Real-time"),
        ("Interests.Domains", "AI, Big Data, Smart Energy"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, right_x)
        y += lh

    y += lh
    draw_rule(draw, x, y, "- Contact ", font, right_x, prefix_color=FG)
    y += lh
    for label, value in [
        ("Email", "hamzabjibji@gmail.com"),
        ("GitHub", "Bjibjihamza"),
        ("LinkedIn", "hamzabjibji"),
        ("Phone", "+212 636 376 992"),
    ]:
        draw_kv_row(draw, x, y, label, value, font, right_x)
        y += lh

    y += lh
    draw_rule(draw, x, y, "- GitHub Stats ", font, right_x, prefix_color=FG)
    y += lh

    # Stats: compose as one string-width line ending at right_x
    # Line 1: Repos + Stars
    draw_kv_row(
        draw,
        x,
        y,
        "Repos",
        f"{stats['repos']} {{Contributed: {stats['contrib']}}} | Stars: {stats['stars']}",
        font,
        right_x,
    )
    y += lh
    draw_kv_row(
        draw,
        x,
        y,
        "Commits",
        f"{stats['commits']} | Followers: {stats['followers']}",
        font,
        right_x,
    )
    y += lh

    # LOC with colored ++/-- — draw manually, right-aligned block
    label = "Lines of Code on GitHub"
    draw.text((x, y), ". ", fill=CC, font=font)
    cx = x + font.getlength(". ")
    draw.text((cx, y), label, fill=KEY, font=font)
    cx += font.getlength(label)
    draw.text((cx, y), ":", fill=KEY, font=font)
    cx += font.getlength(":")

    loc_tail = f"{stats['loc']} ( {stats['loc_add']}++, {stats['loc_del']}-- )"
    # Measure colored segments for right align
    # We draw: loc VAL, " ( " FG, add ADD, "++" ADD, ", " FG, del DEL, "--" DEL, " )" FG
    segments = [
        (stats["loc"], VAL),
        (" ( ", FG),
        (stats["loc_add"], ADD),
        ("++", ADD),
        (", ", FG),
        (stats["loc_del"], DEL),
        ("--", DEL),
        (" )", FG),
    ]
    tail_w = sum(font.getlength(t) for t, _ in segments)
    value_x = right_x - tail_w

    dot_w = font.getlength(".")
    gap = font.getlength(" ")
    cx += gap
    while cx + dot_w + gap <= value_x:
        draw.text((cx, y), ".", fill=CC, font=font)
        cx += dot_w

    cx = value_x
    for text, color in segments:
        draw.text((cx, y), text, fill=color, font=font)
        cx += font.getlength(text)

    card.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT} ({width}x{H}) right_x={right_x}")
    return OUT


if __name__ == "__main__":
    build_card()
