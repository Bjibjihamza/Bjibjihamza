"""Build Andrew-style ASCII portrait SVG (no photo embed)."""
from __future__ import annotations

import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Prefer face photo with visible features (not solid black cutout)
SRC = next(
    p
    for p in (
        ASSETS / "me_face2.png",
        ASSETS / "me_portrait.png",
        ASSETS / "me_face.png",
        ASSETS / "me.png",
    )
    if p.exists()
)

# Dark pixels -> dense glyphs (Andrew-like mix of symbols)
RAMP = "@%#*+=-:. "


def make_ascii(cols: int = 44, rows: int = 25) -> list[str]:
    img = Image.open(SRC).convert("RGBA")
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    bg.paste(img, mask=img.split()[-1])
    rgb = bg.convert("RGB")

    w, h = rgb.size
    # Tighter face crop (less empty margin, more facial detail)
    side = int(min(w, h) * 0.92)
    left = (w - side) // 2
    top = max(0, (h - side) // 2 - side // 16)
    rgb = rgb.crop((left, top, left + side, min(h, top + side)))

    g = ImageOps.grayscale(rgb)
    g = ImageOps.equalize(g)
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.65)
    g = ImageEnhance.Brightness(g).enhance(1.12)
    g = ImageEnhance.Sharpness(g).enhance(2.0)
    g = g.filter(ImageFilter.UnsharpMask(radius=1.4, percent=110, threshold=2))

    # Soft gamma: lift midtones (skin) so hair/glasses stay dense
    lut = [min(255, int(((i / 255.0) ** 0.75) * 255)) for i in range(256)]
    g = g.point(lut)

    g = g.resize((cols, rows), Image.Resampling.LANCZOS)
    px = list(g.getdata())
    n = len(RAMP) - 1
    lines: list[str] = []
    for y in range(rows):
        chars = [RAMP[(px[y * cols + x] * n) // 255] for x in range(cols)]
        lines.append("".join(chars))
    return lines


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(ascii_lines: list[str], *, dark: bool, stats: dict) -> str:
    if dark:
        bg, fg, cc = "#161b22", "#c9d1d9", "#616e7f"
        key, val = "#ffa657", "#a5d6ff"
        add, delete = "#3fb950", "#f85149"
    else:
        bg, fg, cc = "#ffffff", "#24292f", "#6e7781"
        key, val = "#953800", "#0550ae"
        add, delete = "#1a7f37", "#cf222e"

    W, H = 985, 530
    ax, px = 15, 390

    ascii_block = "\n".join(
        f'<tspan x="{ax}" y="{30 + i * 20}">{esc(line)}</tspan>'
        for i, line in enumerate(ascii_lines)
    )

    age = esc(stats["age"])
    repos = esc(stats["repos"])
    contrib = esc(stats["contrib"])
    stars = esc(stats["stars"])
    commits = esc(stats["commits"])
    followers = esc(stats["followers"])
    loc = esc(stats["loc"])
    loc_add = esc(stats["loc_add"])
    loc_del = esc(stats["loc_del"])

    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{W}px" height="{H}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {key};}}
.value {{fill: {val};}}
.addColor {{fill: {add};}}
.delColor {{fill: {delete};}}
.cc {{fill: {cc};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{W}px" height="{H}px" fill="{bg}" rx="15"/>
<text x="{ax}" y="30" fill="{fg}" class="ascii">
{ascii_block}
</text>
<text x="{px}" y="30" fill="{fg}">
<tspan x="{px}" y="30">hamza@bjibji</tspan> -———————————————————————————————————————————-—-
<tspan x="{px}" y="50" class="cc">. </tspan><tspan class="key">OS</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">Windows 11, Linux (WSL)</tspan>
<tspan x="{px}" y="70" class="cc">. </tspan><tspan class="key">Uptime</tspan>:<tspan class="cc" id="age_data_dots"> ...................... </tspan><tspan class="value" id="age_data">{age}</tspan>
<tspan x="{px}" y="90" class="cc">. </tspan><tspan class="key">Host</tspan>:<tspan class="cc"> ............................. </tspan><tspan class="value">ENSA Tetouan — Big Data &amp; AI</tspan>
<tspan x="{px}" y="110" class="cc">. </tspan><tspan class="key">Kernel</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">AI &amp; Data Engineer</tspan>
<tspan x="{px}" y="130" class="cc">. </tspan><tspan class="key">IDE</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">Cursor, VS Code</tspan>
<tspan x="{px}" y="150" class="cc">. </tspan>
<tspan x="{px}" y="170" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Programming</tspan>:<tspan class="cc"> ..... </tspan><tspan class="value">Python, JavaScript, TypeScript, C#, SQL</tspan>
<tspan x="{px}" y="190" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Computer</tspan>:<tspan class="cc"> ......... </tspan><tspan class="value">HTML, CSS, JSON, YAML, Docker</tspan>
<tspan x="{px}" y="210" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Real</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">Arabic, French, English</tspan>
<tspan x="{px}" y="230" class="cc">. </tspan>
<tspan x="{px}" y="250" class="cc">. </tspan><tspan class="key">Interests</tspan>.<tspan class="key">Software</tspan>:<tspan class="cc"> .... </tspan><tspan class="value">Real-Time Pipelines, MLOps, Full-Stack</tspan>
<tspan x="{px}" y="270" class="cc">. </tspan><tspan class="key">Interests</tspan>.<tspan class="key">Domains</tspan>:<tspan class="cc"> ............. </tspan><tspan class="value">Cybersecurity, Smart Energy</tspan>
<tspan x="{px}" y="310">- Contact</tspan> -——————————————————————————————————————————————-—-
<tspan x="{px}" y="330" class="cc">. </tspan><tspan class="key">Email</tspan>:<tspan class="cc"> ..................... </tspan><tspan class="value">hamzabjibji@gmail.com</tspan>
<tspan x="{px}" y="350" class="cc">. </tspan><tspan class="key">GitHub</tspan>:<tspan class="cc"> .................... </tspan><tspan class="value">Bjibjihamza</tspan>
<tspan x="{px}" y="370" class="cc">. </tspan><tspan class="key">LinkedIn</tspan>:<tspan class="cc"> .................................... </tspan><tspan class="value">hamzabjibji</tspan>
<tspan x="{px}" y="390" class="cc">. </tspan><tspan class="key">Phone</tspan>:<tspan class="cc"> ..................................... </tspan><tspan class="value">+212 636 376 992</tspan>
<tspan x="{px}" y="450">- GitHub Stats</tspan> -—————————————————————————————————————————-—-
<tspan x="{px}" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .... </tspan><tspan class="value" id="repo_data">{repos}</tspan> {{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">{contrib}</tspan>}} | <tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> ........... </tspan><tspan class="value" id="star_data">{stars}</tspan>
<tspan x="{px}" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> ................. </tspan><tspan class="value" id="commit_data">{commits}</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> ....... </tspan><tspan class="value" id="follower_data">{followers}</tspan>
<tspan x="{px}" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">. </tspan><tspan class="value" id="loc_data">{loc}</tspan> ( <tspan class="addColor" id="loc_add">{loc_add}</tspan><tspan class="addColor">++</tspan>, <tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">{loc_del}</tspan><tspan class="delColor">--</tspan> )
</text>
</svg>
'''


def main() -> None:
    print("Source:", SRC.name)
    lines = make_ascii(44, 25)
    (ASSETS / "me_ascii.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    stats = {
        "age": "22 years, 9 months, 23 days",
        "repos": "23",
        "contrib": "24",
        "stars": "9",
        "commits": "0",
        "followers": "12",
        "loc": "0",
        "loc_add": "0",
        "loc_del": "0",
    }
    (ROOT / "dark_mode.svg").write_text(build_svg(lines, dark=True, stats=stats), encoding="utf-8")
    (ROOT / "light_mode.svg").write_text(build_svg(lines, dark=False, stats=stats), encoding="utf-8")
    print("Wrote SVGs")


if __name__ == "__main__":
    main()
