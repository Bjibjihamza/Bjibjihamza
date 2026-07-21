"""Build polished neofetch info panels (dark/light). Portrait is separate for GitHub."""
from __future__ import annotations

import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SRC_CANDIDATES = [
    ASSETS / "me_face2.png",
    ASSETS / "me_face.png",
    ASSETS / "me.png",
]


def load_source() -> Image.Image:
    for p in SRC_CANDIDATES:
        if p.exists():
            return Image.open(p).convert("RGBA")
    raise FileNotFoundError("No source photo found in assets/")


def prep_portrait(img: Image.Image, size: int = 512) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, (h - side) // 2 - side // 12)
    img = img.crop((left, top, left + side, top + side))
    bg = Image.new("RGBA", img.size, (13, 17, 23, 255))
    bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)
    rgb = bg.convert("RGB")
    rgb = ImageOps.autocontrast(rgb, cutoff=2)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
    rgb = ImageEnhance.Sharpness(rgb).enhance(1.3)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=2))
    return rgb.resize((size, size), Image.Resampling.LANCZOS)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def build_svg(
    *,
    dark: bool,
    age: str,
    repos: str,
    contrib: str,
    stars: str,
    commits: str,
    followers: str,
    loc: str,
    loc_add: str,
    loc_del: str,
) -> str:
    if dark:
        bg, fg, cc = "#0d1117", "#c9d1d9", "#6e7681"
        key, val = "#ffa657", "#79c0ff"
        add, delete = "#3fb950", "#f85149"
        user = "#58a6ff"
    else:
        bg, fg, cc = "#ffffff", "#24292f", "#6e7781"
        key, val = "#953800", "#0550ae"
        add, delete = "#1a7f37", "#cf222e"
        user = "#0969da"

    W, H = 720, 520
    x = 24

    def row(y: int, inner: str) -> str:
        return f'<tspan x="{x}" y="{y}" class="cc">. </tspan>{inner}'

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     font-family="ConsolasFallback,Consolas,ui-monospace,monospace"
     width="{W}px" height="{H}px" font-size="14.5px" viewBox="0 0 {W} {H}">
<style>
@font-face {{
  src: local('Consolas'), local('Cascadia Mono'), local('Courier New');
  font-family: 'ConsolasFallback';
  font-display: swap;
  size-adjust: 105%;
}}
.key {{ fill: {key}; }}
.value {{ fill: {val}; }}
.user {{ fill: {user}; font-weight: 700; }}
.addColor {{ fill: {add}; }}
.delColor {{ fill: {delete}; }}
.cc {{ fill: {cc}; }}
.hdr {{ fill: {fg}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{W}" height="{H}" fill="{bg}" rx="14"/>

<text x="{x}" y="36" fill="{fg}">
  <tspan x="{x}" y="36" class="user">hamza@bjibji</tspan>
  <tspan class="cc"> ----------------------------------------------- </tspan>

  {row(64, f'<tspan class="key">OS</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">Windows 11 · Linux (WSL)</tspan>')}
  {row(88, f'<tspan class="key">Uptime</tspan>:<tspan class="cc" id="age_data_dots"> ..................... </tspan><tspan class="value" id="age_data">{esc(age)}</tspan>')}
  {row(112, f'<tspan class="key">Host</tspan>:<tspan class="cc"> ....................... </tspan><tspan class="value">ENSA Tetouan — Big Data &amp; AI</tspan>')}
  {row(136, f'<tspan class="key">Kernel</tspan>:<tspan class="cc"> ..................... </tspan><tspan class="value">AI &amp; Data Engineer</tspan>')}
  {row(160, f'<tspan class="key">IDE</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">Cursor · VS Code</tspan>')}

  <tspan x="{x}" y="188" class="cc">. </tspan>
  {row(212, f'<tspan class="key">Languages</tspan>.<tspan class="key">Programming</tspan>:<tspan class="cc"> .. </tspan><tspan class="value">Python, JS, TS, C#, SQL</tspan>')}
  {row(236, f'<tspan class="key">Languages</tspan>.<tspan class="key">Computer</tspan>:<tspan class="cc"> ...... </tspan><tspan class="value">HTML, CSS, JSON, YAML, Docker</tspan>')}
  {row(260, f'<tspan class="key">Languages</tspan>.<tspan class="key">Real</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">Arabic, French, English</tspan>')}

  <tspan x="{x}" y="288" class="cc">. </tspan>
  {row(312, f'<tspan class="key">Interests</tspan>.<tspan class="key">Software</tspan>:<tspan class="cc"> ..... </tspan><tspan class="value">Pipelines, MLOps, Full-Stack</tspan>')}
  {row(336, f'<tspan class="key">Interests</tspan>.<tspan class="key">Domains</tspan>:<tspan class="cc"> ...... </tspan><tspan class="value">Cybersecurity, Smart Energy</tspan>')}

  <tspan x="{x}" y="368" class="hdr">- Contact</tspan><tspan class="cc"> ------------------------------------------- </tspan>
  {row(396, f'<tspan class="key">Email</tspan>:<tspan class="cc"> ...................... </tspan><tspan class="value">hamzabjibji@gmail.com</tspan>')}
  {row(420, f'<tspan class="key">GitHub</tspan>:<tspan class="cc"> ..................... </tspan><tspan class="value">github.com/Bjibjihamza</tspan>')}
  {row(444, f'<tspan class="key">LinkedIn</tspan>:<tspan class="cc"> ................... </tspan><tspan class="value">linkedin.com/in/hamzabjibji</tspan>')}
  {row(468, f'<tspan class="key">Phone</tspan>:<tspan class="cc"> ...................... </tspan><tspan class="value">+212 636 376 992</tspan>')}

  <tspan x="{x}" y="496" class="hdr">- GitHub Stats</tspan><tspan class="cc"> -------------------------------------- </tspan>
</text>
<text x="{x}" y="520" fill="{fg}" font-size="13.5px">
  <tspan x="{x}" y="508" class="cc">. </tspan>
  <tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .. </tspan><tspan class="value" id="repo_data">{esc(repos)}</tspan>
  <tspan class="cc"> {{</tspan><tspan class="key">+</tspan><tspan class="cc">: </tspan><tspan class="value" id="contrib_data">{esc(contrib)}</tspan><tspan class="cc">}} | </tspan>
  <tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> .. </tspan><tspan class="value" id="star_data">{esc(stars)}</tspan>
  <tspan class="cc"> | </tspan>
  <tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> .. </tspan><tspan class="value" id="commit_data">{esc(commits)}</tspan>
  <tspan class="cc"> | </tspan>
  <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> .. </tspan><tspan class="value" id="follower_data">{esc(followers)}</tspan>
</text>
<!-- bump canvas: put LOC inside by increasing H - rendered via second pass below -->
</svg>
'''


# Rebuild with proper height including LOC line
def build_svg_full(**kwargs) -> str:
    dark = kwargs.pop("dark")
    body = build_svg(dark=dark, **kwargs)
    # Replace closing bits with LOC + correct height
    if dark:
        bg, fg, cc = "#0d1117", "#c9d1d9", "#6e7681"
        key, val = "#ffa657", "#79c0ff"
        add, delete = "#3fb950", "#f85149"
        user = "#58a6ff"
    else:
        bg, fg, cc = "#ffffff", "#24292f", "#6e7781"
        key, val = "#953800", "#0550ae"
        add, delete = "#1a7f37", "#cf222e"
        user = "#0969da"

    W, H = 720, 545
    x = 24
    age = esc(kwargs["age"])
    repos = esc(kwargs["repos"])
    contrib = esc(kwargs["contrib"])
    stars = esc(kwargs["stars"])
    commits = esc(kwargs["commits"])
    followers = esc(kwargs["followers"])
    loc = esc(kwargs["loc"])
    loc_add = esc(kwargs["loc_add"])
    loc_del = esc(kwargs["loc_del"])

    def row(y: int, inner: str) -> str:
        return f'<tspan x="{x}" y="{y}" class="cc">. </tspan>{inner}'

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     font-family="ConsolasFallback,Consolas,ui-monospace,monospace"
     width="{W}px" height="{H}px" font-size="14.5px" viewBox="0 0 {W} {H}">
<style>
@font-face {{
  src: local('Consolas'), local('Cascadia Mono'), local('Courier New');
  font-family: 'ConsolasFallback';
  font-display: swap;
  size-adjust: 105%;
}}
.key {{ fill: {key}; }}
.value {{ fill: {val}; }}
.user {{ fill: {user}; font-weight: 700; }}
.addColor {{ fill: {add}; }}
.delColor {{ fill: {delete}; }}
.cc {{ fill: {cc}; }}
.hdr {{ fill: {fg}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{W}" height="{H}" fill="{bg}" rx="14"/>

<text x="{x}" y="34" fill="{fg}">
  <tspan x="{x}" y="34" class="user">hamza@bjibji</tspan>
  <tspan class="cc"> ----------------------------------------------- </tspan>

  {row(62, f'<tspan class="key">OS</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">Windows 11 · Linux (WSL)</tspan>')}
  {row(86, f'<tspan class="key">Uptime</tspan>:<tspan class="cc" id="age_data_dots"> ..................... </tspan><tspan class="value" id="age_data">{age}</tspan>')}
  {row(110, f'<tspan class="key">Host</tspan>:<tspan class="cc"> ....................... </tspan><tspan class="value">ENSA Tetouan — Big Data &amp; AI</tspan>')}
  {row(134, f'<tspan class="key">Kernel</tspan>:<tspan class="cc"> ..................... </tspan><tspan class="value">AI &amp; Data Engineer</tspan>')}
  {row(158, f'<tspan class="key">IDE</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">Cursor · VS Code</tspan>')}

  <tspan x="{x}" y="182" class="cc">. </tspan>
  {row(206, f'<tspan class="key">Languages</tspan>.<tspan class="key">Programming</tspan>:<tspan class="cc"> .. </tspan><tspan class="value">Python, JS, TS, C#, SQL</tspan>')}
  {row(230, f'<tspan class="key">Languages</tspan>.<tspan class="key">Computer</tspan>:<tspan class="cc"> ...... </tspan><tspan class="value">HTML, CSS, JSON, YAML, Docker</tspan>')}
  {row(254, f'<tspan class="key">Languages</tspan>.<tspan class="key">Real</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">Arabic, French, English</tspan>')}

  <tspan x="{x}" y="278" class="cc">. </tspan>
  {row(302, f'<tspan class="key">Interests</tspan>.<tspan class="key">Software</tspan>:<tspan class="cc"> ..... </tspan><tspan class="value">Pipelines, MLOps, Full-Stack</tspan>')}
  {row(326, f'<tspan class="key">Interests</tspan>.<tspan class="key">Domains</tspan>:<tspan class="cc"> ...... </tspan><tspan class="value">Cybersecurity, Smart Energy</tspan>')}

  <tspan x="{x}" y="358" class="hdr">- Contact</tspan><tspan class="cc"> ------------------------------------------- </tspan>
  {row(386, f'<tspan class="key">Email</tspan>:<tspan class="cc"> ...................... </tspan><tspan class="value">hamzabjibji@gmail.com</tspan>')}
  {row(410, f'<tspan class="key">GitHub</tspan>:<tspan class="cc"> ..................... </tspan><tspan class="value">github.com/Bjibjihamza</tspan>')}
  {row(434, f'<tspan class="key">LinkedIn</tspan>:<tspan class="cc"> ................... </tspan><tspan class="value">linkedin.com/in/hamzabjibji</tspan>')}
  {row(458, f'<tspan class="key">Phone</tspan>:<tspan class="cc"> ...................... </tspan><tspan class="value">+212 636 376 992</tspan>')}

  <tspan x="{x}" y="490" class="hdr">- GitHub Stats</tspan><tspan class="cc"> -------------------------------------- </tspan>
  {row(518, f'''<tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .. </tspan><tspan class="value" id="repo_data">{repos}</tspan><tspan class="cc"> {{</tspan><tspan class="key">+</tspan><tspan class="cc">:</tspan><tspan class="value" id="contrib_data">{contrib}</tspan><tspan class="cc">}} | </tspan><tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> .. </tspan><tspan class="value" id="star_data">{stars}</tspan><tspan class="cc"> | </tspan><tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> .. </tspan><tspan class="value" id="commit_data">{commits}</tspan><tspan class="cc"> | </tspan><tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> .. </tspan><tspan class="value" id="follower_data">{followers}</tspan>''')}
  {row(538, f'''<tspan class="key">Lines of Code</tspan>:<tspan class="cc" id="loc_data_dots"> ............ </tspan><tspan class="value" id="loc_data">{loc}</tspan><tspan class="cc"> ( </tspan><tspan class="addColor" id="loc_add">{loc_add}</tspan><tspan class="addColor">++</tspan><tspan class="cc">, </tspan><tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">{loc_del}</tspan><tspan class="delColor">--</tspan><tspan class="cc"> )</tspan>''')}
</text>
</svg>
'''


def main() -> None:
    src = load_source()
    portrait = prep_portrait(src, size=640)
    portrait_path = ASSETS / "me_portrait.png"
    portrait.save(portrait_path, optimize=True)
    print("Saved", portrait_path)

    common = dict(
        age="22 years, 9 months, 23 days",
        repos="23",
        contrib="24",
        stars="9",
        commits="0",
        followers="12",
        loc="0",
        loc_add="0",
        loc_del="0",
    )
    (ROOT / "dark_mode.svg").write_text(build_svg_full(dark=True, **common), encoding="utf-8")
    (ROOT / "light_mode.svg").write_text(build_svg_full(dark=False, **common), encoding="utf-8")
    print("Wrote dark_mode.svg + light_mode.svg")


if __name__ == "__main__":
    main()
