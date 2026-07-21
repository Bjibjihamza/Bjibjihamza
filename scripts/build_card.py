"""Rebuild whoami SVGs as info panel only (portrait is assets/ascii-me.png)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_svg(*, dark: bool, stats: dict) -> str:
    if dark:
        bg, fg, cc = "#161b22", "#c9d1d9", "#616e7f"
        key, val = "#ffa657", "#a5d6ff"
        add, delete = "#3fb950", "#f85149"
    else:
        bg, fg, cc = "#ffffff", "#24292f", "#6e7781"
        key, val = "#953800", "#0550ae"
        add, delete = "#1a7f37", "#cf222e"

    W, H = 620, 530
    x = 20

    def v(name: str) -> str:
        return (
            str(stats[name])
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{W}px" height="{H}px" font-size="15px">
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
<text x="{x}" y="30" fill="{fg}">
<tspan x="{x}" y="30">hamza@bjibji</tspan> -———————————————————————————————-—-
<tspan x="{x}" y="50" class="cc">. </tspan><tspan class="key">OS</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">Windows 11, Linux (WSL)</tspan>
<tspan x="{x}" y="70" class="cc">. </tspan><tspan class="key">Uptime</tspan>:<tspan class="cc" id="age_data_dots"> ...................... </tspan><tspan class="value" id="age_data">{v("age")}</tspan>
<tspan x="{x}" y="90" class="cc">. </tspan><tspan class="key">Host</tspan>:<tspan class="cc"> ............................. </tspan><tspan class="value">ENSA Tetouan — Big Data &amp; AI</tspan>
<tspan x="{x}" y="110" class="cc">. </tspan><tspan class="key">Kernel</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">AI &amp; Data Engineer</tspan>
<tspan x="{x}" y="130" class="cc">. </tspan><tspan class="key">IDE</tspan>:<tspan class="cc"> ........................ </tspan><tspan class="value">Cursor, VS Code</tspan>
<tspan x="{x}" y="150" class="cc">. </tspan>
<tspan x="{x}" y="170" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Programming</tspan>:<tspan class="cc"> ..... </tspan><tspan class="value">Python, JavaScript, TypeScript, C#, SQL</tspan>
<tspan x="{x}" y="190" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Computer</tspan>:<tspan class="cc"> ......... </tspan><tspan class="value">HTML, CSS, JSON, YAML, Docker</tspan>
<tspan x="{x}" y="210" class="cc">. </tspan><tspan class="key">Languages</tspan>.<tspan class="key">Real</tspan>:<tspan class="cc"> ......................... </tspan><tspan class="value">Arabic, French, English</tspan>
<tspan x="{x}" y="230" class="cc">. </tspan>
<tspan x="{x}" y="250" class="cc">. </tspan><tspan class="key">Interests</tspan>.<tspan class="key">Software</tspan>:<tspan class="cc"> .... </tspan><tspan class="value">Real-Time Pipelines, MLOps, Full-Stack</tspan>
<tspan x="{x}" y="270" class="cc">. </tspan><tspan class="key">Interests</tspan>.<tspan class="key">Domains</tspan>:<tspan class="cc"> ............. </tspan><tspan class="value">Cybersecurity, Smart Energy</tspan>
<tspan x="{x}" y="310">- Contact</tspan> -—————————————————————————————————————-—-
<tspan x="{x}" y="330" class="cc">. </tspan><tspan class="key">Email</tspan>:<tspan class="cc"> ..................... </tspan><tspan class="value">hamzabjibji@gmail.com</tspan>
<tspan x="{x}" y="350" class="cc">. </tspan><tspan class="key">GitHub</tspan>:<tspan class="cc"> .................... </tspan><tspan class="value">Bjibjihamza</tspan>
<tspan x="{x}" y="370" class="cc">. </tspan><tspan class="key">LinkedIn</tspan>:<tspan class="cc"> .................................... </tspan><tspan class="value">hamzabjibji</tspan>
<tspan x="{x}" y="390" class="cc">. </tspan><tspan class="key">Phone</tspan>:<tspan class="cc"> ..................................... </tspan><tspan class="value">+212 636 376 992</tspan>
<tspan x="{x}" y="450">- GitHub Stats</tspan> -—————————————————————————————————-—-
<tspan x="{x}" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .... </tspan><tspan class="value" id="repo_data">{v("repos")}</tspan> {{<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">{v("contrib")}</tspan>}} | <tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> ........... </tspan><tspan class="value" id="star_data">{v("stars")}</tspan>
<tspan x="{x}" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> ................. </tspan><tspan class="value" id="commit_data">{v("commits")}</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> ....... </tspan><tspan class="value" id="follower_data">{v("followers")}</tspan>
<tspan x="{x}" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">. </tspan><tspan class="value" id="loc_data">{v("loc")}</tspan> ( <tspan class="addColor" id="loc_add">{v("loc_add")}</tspan><tspan class="addColor">++</tspan>, <tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">{v("loc_del")}</tspan><tspan class="delColor">--</tspan> )
</text>
</svg>
'''


def main() -> None:
    stats = {
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
    (ROOT / "dark_mode.svg").write_text(build_svg(dark=True, stats=stats), encoding="utf-8")
    (ROOT / "light_mode.svg").write_text(build_svg(dark=False, stats=stats), encoding="utf-8")
    print("Wrote panel-only SVGs")


if __name__ == "__main__":
    main()
