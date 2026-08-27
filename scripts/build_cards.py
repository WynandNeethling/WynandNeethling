#!/usr/bin/env python3
"""Render the static profile cards in assets/.

Everything animates with CSS @keyframes rather than SMIL: GitHub's image
pipeline does not run SMIL, so <animate> elements render as a still frame (or,
where content is hidden until an animation reveals it, as nothing at all).
Curved motion is sampled into translate keyframes so no exotic CSS is needed.
"""
import math
import os

OUT = "assets"
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace"
BG, PANEL, LINE, DIM, FG, MID = "#0B0F14", "#0E141B", "#1F2A37", "#5C6B7E", "#E4EAF2", "#8B97A8"
VIO, CYA, PNK = "#7C5CFF", "#22D3EE", "#F471B5"


def bezier(p0, p1, p2, p3, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def travel_keyframes(name, pts):
    """A translate keyframe track that walks `pts`, spaced by arc length."""
    d = [0.0]
    for i in range(1, len(pts)):
        d.append(d[-1] + math.dist(pts[i - 1], pts[i]))
    total = d[-1] or 1
    rows = [f"  {100 * v / total:.2f}% {{ transform: translate({pts[i][0]:.1f}px, {pts[i][1]:.1f}px); }}"
            for i, v in enumerate(d)]
    return f"@keyframes {name} {{\n" + "\n".join(rows) + "\n}"


def card(w, h, extra_defs="", rx=18):
    return f'''  <defs>
    <pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
      <path d="M26 0H0V26" fill="none" stroke="#151D27" stroke-width="1"/>
    </pattern>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>
{extra_defs}  </defs>
  <g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="{BG}"/>
    <rect width="{w}" height="{h}" fill="url(#grid)" opacity="0.55"/>'''


def frame(w, h, rx=18):
    return f'''    <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="{LINE}"/>
  </g>
</svg>
'''


def write(name, body):
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/{name}", "w").write(body)
    print(f"wrote {OUT}/{name}")


BASE_CSS = """
    .flow { animation: flow 1.6s linear infinite; }
    @keyframes flow { to { stroke-dashoffset: -26; } }
    .flow-slow { animation: flow-slow 2.4s linear infinite; }
    @keyframes flow-slow { to { stroke-dashoffset: 26; } }
    .halo { transform-box: fill-box; transform-origin: center; animation: halo 3.2s ease-in-out infinite; }
    @keyframes halo { 0%, 100% { transform: scale(0.85); opacity: 0.22; } 50% { transform: scale(1.5); opacity: 0.03; } }
    .blink { animation: blink 1.1s steps(1, end) infinite; }
    @keyframes blink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }
    .sweep { animation: sweep 5.5s linear infinite; }
    @keyframes sweep { from { transform: translateX(-320px); } to { transform: translateX(1000px); } }
"""


# ------------------------------------------------------------------ header
def header():
    W, H = 1000, 280
    nodes = [(665, 62, VIO), (800, 40, CYA), (930, 78, PNK), (700, 148, CYA),
             (905, 168, VIO), (650, 228, PNK), (800, 245, CYA), (945, 225, VIO)]
    hub = (790, 140)
    ring = [(0, 1), (1, 2), (2, 4), (4, 7), (7, 6), (6, 5), (5, 3), (3, 0)]

    packets = [(hub, nodes[1][:2], 2.6, 0.0, PNK), (hub, nodes[4][:2], 3.1, 0.5, CYA),
               (hub, nodes[5][:2], 2.9, 1.1, VIO), (nodes[1][:2], nodes[2][:2], 3.4, 0.8, CYA),
               (nodes[7][:2], nodes[6][:2], 3.8, 1.6, PNK), (nodes[5][:2], nodes[3][:2], 3.2, 2.1, VIO)]

    css = [BASE_CSS]
    for i, (a, b, *_rest) in enumerate(packets):
        css.append(travel_keyframes(f"pk{i}", [a, b]))
    css.append(".rule { animation: rule 6s ease-in-out infinite; }")
    css.append("@keyframes rule { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(374px); } }")
    css.append(".hubring { transform-box: fill-box; transform-origin: center; animation: hubring 2.6s ease-in-out infinite; }")
    css.append("@keyframes hubring { 0%, 100% { transform: scale(0.8); } 50% { transform: scale(1.3); } }")
    css.append(".core { animation: core 1.3s ease-in-out infinite; }")
    css.append("@keyframes core { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }")

    defs = f'''    <linearGradient id="nameGrad" gradientUnits="userSpaceOnUse" x1="52" y1="0" x2="522" y2="0">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="55%" stop-color="{CYA}"/><stop offset="100%" stop-color="{PNK}"/>
    </linearGradient>
    <linearGradient id="edgeGrad" gradientUnits="userSpaceOnUse" x1="640" y1="40" x2="950" y2="250">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="100%" stop-color="{CYA}"/>
    </linearGradient>
    <linearGradient id="sweepGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYA}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{CYA}" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="{CYA}" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="glowVio"><stop offset="0%" stop-color="{VIO}" stop-opacity="0.55"/><stop offset="100%" stop-color="{VIO}" stop-opacity="0"/></radialGradient>
    <radialGradient id="glowCya"><stop offset="0%" stop-color="{CYA}" stop-opacity="0.45"/><stop offset="100%" stop-color="{CYA}" stop-opacity="0"/></radialGradient>
'''

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Wynand Neethling — Founding AI Engineer at Ubundi">',
         '  <title>Wynand Neethling — Founding AI Engineer @ Ubundi</title>',
         '  <style>' + "\n".join(css) + '  </style>',
         card(W, H, defs)]
    a = s.append
    a(f'    <ellipse cx="790" cy="140" rx="260" ry="170" fill="url(#glowVio)" opacity="0.35"/>')
    a(f'    <ellipse cx="120" cy="250" rx="220" ry="140" fill="url(#glowCya)" opacity="0.22"/>')

    a(f'    <g fill="none" stroke-linecap="round">')
    a(f'      <g class="flow" stroke="url(#edgeGrad)" stroke-width="1.4" opacity="0.75" stroke-dasharray="5 7">')
    for x, y, _ in nodes:
        a(f'        <path d="M{hub[0]} {hub[1]} L{x} {y}"/>')
    a('      </g>')
    a(f'      <g class="flow-slow" stroke="{CYA}" stroke-width="1" opacity="0.28" stroke-dasharray="3 6">')
    for i, j in ring:
        a(f'        <path d="M{nodes[i][0]} {nodes[i][1]} L{nodes[j][0]} {nodes[j][1]}"/>')
    a('      </g>')
    a('    </g>')

    for i, (_a, _b, dur, delay, col) in enumerate(packets):
        a(f'    <circle r="2.8" fill="{col}" style="animation: pk{i} {dur}s linear {delay}s infinite"/>')

    for i, (x, y, col) in enumerate(nodes):
        a(f'    <g>')
        a(f'      <circle class="halo" cx="{x}" cy="{y}" r="14" fill="{col}" style="animation-delay: {i*0.4:.1f}s"/>')
        a(f'      <circle cx="{x}" cy="{y}" r="5.5" fill="{BG}" stroke="{col}" stroke-width="2"/>')
        a(f'    </g>')
    a(f'    <circle class="hubring" cx="{hub[0]}" cy="{hub[1]}" r="26" fill="url(#glowVio)"/>')
    a(f'    <circle cx="{hub[0]}" cy="{hub[1]}" r="9" fill="{BG}" stroke="url(#nameGrad)" stroke-width="2.5"/>')
    a(f'    <circle class="core" cx="{hub[0]}" cy="{hub[1]}" r="3.2" fill="{CYA}"/>')

    a(f'    <g font-family="{MONO}">')
    a(f'      <text x="54" y="58" font-size="12" letter-spacing="3.4" fill="{CYA}">UBUNDI &#183; STELLENBOSCH, ZA &#183; UTC+2</text>')
    a(f'      <text x="52" y="128" font-size="40" font-weight="700" letter-spacing="1.5" fill="url(#nameGrad)">WYNAND NEETHLING</text>')
    a(f'      <rect x="52" y="146" width="470" height="2" fill="{LINE}"/>')
    a(f'      <rect class="rule" x="52" y="146" width="96" height="2" fill="url(#nameGrad)"/>')
    a(f'      <g font-size="13.5" fill="{MID}">')
    a(f'        <text x="54" y="180"><tspan fill="{VIO}">&#9656;</tspan> founding ai engineer &#183; <tspan fill="#C9D4E3">ubundi</tspan></text>')
    a(f'        <text x="54" y="204"><tspan fill="{CYA}">&#9656;</tspan> knowledge graphs &#183; graphrag &#183; context-aware systems</text>')
    a(f'        <text x="54" y="228"><tspan fill="{PNK}">&#9656;</tspan> building the data engine for physical ai</text>')
    a(f'      </g>')
    a(f'      <rect class="blink" x="426" y="217" width="8" height="15" fill="{CYA}"/>')
    a(f'    </g>')
    a(f'    <rect class="sweep" x="0" y="0" width="320" height="{H}" fill="url(#sweepGrad)"/>')
    s.append(frame(W, H))
    write("header-graph.svg", "\n".join(s))


# ------------------------------------------------------------------ typing
def typing():
    LINES = [("founding ai engineer @ ubundi", CYA),
             ("knowledge graphs · graphrag · context-aware ai", VIO),
             ("enterprise ai that survives real data", PNK),
             ("ex-data consultant, amsterdam → stellenbosch", CYA),
             ("now: a data engine for physical ai", VIO)]
    W, H, FS = 900, 46, 17.0
    CW = FS * 0.6
    SLOT, TYPE_T, HOLD = 4.0, 1.6, 1.75
    T = SLOT * len(LINES)
    CX, BASE = W / 2, 30

    css = ["    .cursor { animation: cursorblink 1s steps(1, end) infinite; }",
           "    @keyframes cursorblink { 0%, 49% { opacity: 1; } 50%, 100% { opacity: 0; } }"]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Founding AI Engineer at Ubundi">',
         '  <title>Founding AI Engineer @ Ubundi</title>']
    body = []
    for i, (txt, col) in enumerate(LINES):
        n = len(txt)
        w = n * CW
        xl = CX - w / 2
        st = i * SLOT
        # per-character reveal: plain opacity keyframes, nothing exotic
        for c in range(n):
            on = (st + TYPE_T * (c + 1) / n) / T
            off = (st + TYPE_T + HOLD) / T
            css.append(f"    @keyframes c{i}_{c} {{ 0%, {max(on-0.0008,0)*100:.3f}% {{ opacity: 0; }} {on*100:.3f}%, {off*100:.3f}% {{ opacity: 1; }} {min(off+0.0008,1)*100:.3f}%, 100% {{ opacity: 0; }} }}")
        css.append(f"    .l{i} tspan {{ animation-duration: {T}s; animation-iteration-count: infinite; animation-timing-function: steps(1, end); }}")
        for c in range(n):
            css.append(f"    .l{i} tspan:nth-child({c+1}) {{ animation-name: c{i}_{c}; }}")
        # caret walks the line, then parks
        css.append(f"""    .k{i} {{ animation: k{i} {T}s steps({n}, end) infinite; }}
    @keyframes k{i} {{
      0%, {st/T*100:.3f}% {{ transform: translateX(0); opacity: 0; }}
      {(st+0.001)/T*100:.3f}% {{ transform: translateX(0); opacity: 1; }}
      {(st+TYPE_T)/T*100:.3f}%, {(st+TYPE_T+HOLD)/T*100:.3f}% {{ transform: translateX({w:.1f}px); opacity: 1; }}
      {(st+TYPE_T+HOLD+0.001)/T*100:.3f}%, 100% {{ transform: translateX({w:.1f}px); opacity: 0; }}
    }}""")
        spans = "".join(
            f'<tspan>{ch.replace("&","&amp;").replace("<","&lt;")}</tspan>' if ch != " " else '<tspan> </tspan>'
            for ch in txt)
        body.append(f'  <text class="l{i}" x="{xl:.1f}" y="{BASE}" xml:space="preserve" font-family="{MONO}" font-size="{FS}" font-weight="600" fill="{col}">{spans}</text>')
        body.append(f'  <rect class="k{i} cursor" x="{xl:.1f}" y="{BASE-14:.0f}" width="2.6" height="18" fill="{col}" opacity="0"/>')
    s.append('  <style>\n' + "\n".join(css) + '\n  </style>')
    s.extend(body)
    s.append('</svg>')
    write("typing.svg", "\n".join(s) + "\n")


# ------------------------------------------------------------------ thread
def thread():
    W, H, SPINE = 1000, 240, 110
    main = [(150, "DATA ENGINEERING", "pipelines · warehouses", VIO),
            (390, "DATA CONSULTING", "amsterdam", CYA),
            (630, "FOUNDING AI ENGINEER", "ubundi · stellenbosch", PNK)]
    br1 = bezier((660, SPINE), (730, SPINE), (760, 62), (818, 62))
    br2 = bezier((660, SPINE), (730, SPINE), (760, 168), (818, 168))

    css = [BASE_CSS,
           travel_keyframes("tspine", [(56, SPINE), (660, SPINE)]),
           travel_keyframes("tbr1", br1),
           travel_keyframes("tbr2", br2)]

    defs = f'''    <linearGradient id="tGrad" gradientUnits="userSpaceOnUse" x1="56" y1="0" x2="660" y2="0">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="55%" stop-color="{CYA}"/><stop offset="100%" stop-color="{PNK}"/>
    </linearGradient>
'''
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Career thread">',
         '  <title>The thread — data engineering to physical AI</title>',
         '  <style>' + "\n".join(css) + '  </style>', card(W, H, defs)]
    a = s.append
    a(f'    <path class="flow" d="M56 {SPINE} L660 {SPINE}" stroke="url(#tGrad)" stroke-width="2" fill="none" stroke-dasharray="6 7" opacity="0.8"/>')
    a(f'    <path class="flow" d="M660 {SPINE} C 730 {SPINE}, 760 62, 818 62" stroke="{CYA}" stroke-width="1.6" fill="none" stroke-dasharray="5 7" opacity="0.7"/>')
    a(f'    <path class="flow" d="M660 {SPINE} C 730 {SPINE}, 760 168, 818 168" stroke="{PNK}" stroke-width="1.6" fill="none" stroke-dasharray="5 7" opacity="0.7"/>')
    a(f'    <circle r="3.6" fill="#FFFFFF" style="animation: tspine 3.4s linear infinite"/>')
    a(f'    <circle r="3" fill="{CYA}" style="animation: tbr1 3.4s linear 1.2s infinite"/>')
    a(f'    <circle r="3" fill="{PNK}" style="animation: tbr2 3.4s linear 2s infinite"/>')

    def station(x, y, title, sub, col, ty, sy, delay):
        a('    <g>')
        a(f'      <circle class="halo" cx="{x}" cy="{y}" r="14" fill="{col}" style="animation-delay: {delay}s"/>')
        a(f'      <circle cx="{x}" cy="{y}" r="7" fill="{BG}" stroke="{col}" stroke-width="2.2"/>')
        a(f'      <g font-family="{MONO}" text-anchor="middle">')
        a(f'        <text x="{x}" y="{ty}" font-size="11.5" font-weight="700" letter-spacing="1.4" fill="{FG}">{title}</text>')
        a(f'        <text x="{x}" y="{sy}" font-size="10" letter-spacing="0.6" fill="{DIM}">{sub}</text>')
        a('      </g>')
        a('    </g>')

    for i, (x, title, sub, col) in enumerate(main):
        station(x, SPINE, title, sub, col, SPINE - 30, SPINE + 32, i * 0.8)
    station(830, 62, "CONTEXT-AWARE AI", "rag &#183; graphrag &#183; kgs", CYA, 28, 44, 1.4)
    station(830, 168, "FIRST MOTIVE", "the data engine for physical ai", PNK, 199, 216, 2.0)
    a(f'    <g font-family="{MONO}"><text x="28" y="30" font-size="10.5" letter-spacing="2.6" fill="{DIM}">THE THREAD &#183; <tspan fill="{VIO}">SAME QUESTION, NEW MODALITY</tspan></text></g>')
    s.append(frame(W, H))
    write("thread.svg", "\n".join(s))


# ---------------------------------------------------------------- pipeline
def pipeline():
    stages = [("SENSE", "arms · cams · imu", VIO), ("CAPTURE", "mcap · rosbag", VIO),
              ("VALIDATE", "sync · schema", CYA), ("CURATE", "slice · label", CYA),
              ("TRAIN", "policy", PNK), ("DEPLOY", "fleet", PNK)]
    W, H, CW, GAP, Y, CH = 1000, 240, 132, 18, 70, 62
    xs = [59 + i * (CW + GAP) for i in range(6)]
    cyc = 7.2
    loop = bezier((xs[5] + CW - 20, Y + CH), (xs[5] + CW - 20, 200), (xs[0] + 20, 200), (xs[0] + 20, Y + CH))

    css = [BASE_CSS,
           "    .lit { animation: lit 7.2s linear infinite; }",
           "    @keyframes lit { 0%, 9% { opacity: 1; } 30%, 100% { opacity: 0.16; } }",
           travel_keyframes("ploop", loop)]
    for i in range(5):
        css.append(travel_keyframes(f"pc{i}", [(xs[i] + CW + 2, Y + CH / 2), (xs[i + 1] - 6, Y + CH / 2)]))

    defs = f'''    <linearGradient id="pGrad" gradientUnits="userSpaceOnUse" x1="59" y1="0" x2="941" y2="0">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="50%" stop-color="{CYA}"/><stop offset="100%" stop-color="{PNK}"/>
    </linearGradient>
'''
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="First Motive data engine for physical AI">',
         '  <title>First Motive — the data engine for physical AI</title>',
         '  <style>' + "\n".join(css) + '  </style>', card(W, H, defs)]
    a = s.append
    a(f'    <g font-family="{MONO}">')
    a(f'      <circle class="core" cx="63" cy="34" r="4" fill="{PNK}"/>')
    a(f'      <text x="78" y="38" font-size="12" letter-spacing="3" fill="{MID}">FIRST MOTIVE &#183; <tspan fill="{CYA}">DATA ENGINE FOR PHYSICAL AI</tspan></text>')
    a('    </g>')
    css.append("    .core { animation: core 1.6s ease-in-out infinite; }")

    for i, (name, sub, col) in enumerate(stages):
        x, cx = xs[i], xs[i] + CW / 2
        d = round(i * (cyc / 6), 2)
        a('    <g>')
        a(f'      <rect x="{x}" y="{Y}" width="{CW}" height="{CH}" rx="10" fill="{PANEL}" stroke="{LINE}"/>')
        a(f'      <rect class="lit" x="{x}" y="{Y}" width="{CW}" height="{CH}" rx="10" fill="none" stroke="{col}" stroke-width="1.4" opacity="0.16" style="animation-delay: {d}s"/>')
        a(f'      <rect class="lit" x="{x+14}" y="{Y-1}" width="{CW-28}" height="2.5" rx="1.2" fill="{col}" opacity="0.25" style="animation-delay: {d}s"/>')
        a(f'      <g font-family="{MONO}" text-anchor="middle">')
        a(f'        <text x="{cx}" y="{Y+30}" font-size="13" font-weight="700" letter-spacing="1.6" fill="{FG}">{name}</text>')
        a(f'        <text x="{cx}" y="{Y+48}" font-size="10" letter-spacing="0.6" fill="{DIM}">{sub}</text>')
        a('      </g>')
        a('    </g>')

    for i in range(5):
        x0, x1, y = xs[i] + CW, xs[i + 1], Y + CH / 2
        a(f'    <path class="flow" d="M{x0+2} {y} L{x1-6} {y}" stroke="url(#pGrad)" stroke-width="1.4" fill="none" stroke-dasharray="4 5" opacity="0.8"/>')
        a(f'    <path d="M{x1-7} {y-3.5} L{x1-2} {y} L{x1-7} {y+3.5} Z" fill="{CYA}" opacity="0.85"/>')
        a(f'    <circle r="3" fill="#FFFFFF" opacity="0.9" style="animation: pc{i} {1.1+i*0.05:.2f}s linear {i*0.28:.2f}s infinite"/>')

    a(f'    <path class="flow-slow" d="M{xs[5]+CW-20} {Y+CH} C {xs[5]+CW-20} 200, {xs[0]+20} 200, {xs[0]+20} {Y+CH}" fill="none" stroke="{VIO}" stroke-width="1.3" stroke-dasharray="5 7" opacity="0.55"/>')
    a(f'    <path d="M{xs[0]+20} {Y+CH-2} L{xs[0]+15.5} {Y+CH+7} L{xs[0]+24.5} {Y+CH+7} Z" fill="{VIO}" opacity="0.85"/>')
    a(f'    <circle r="2.6" fill="{PNK}" style="animation: ploop 4.2s linear infinite"/>')
    a(f'    <rect x="352" y="176" width="296" height="22" rx="11" fill="{BG}" stroke="{LINE}"/>')
    a(f'    <text x="500" y="191" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1.2" fill="{MID}">real&#8209;world deltas &#8594; new demonstrations</text>')
    s[2] = '  <style>' + "\n".join(css) + '  </style>'
    s.append(frame(W, H))
    write("pipeline.svg", "\n".join(s))


# ----------------------------------------------------------- company graph
def company_graph():
    W, H = 1000, 260
    nodes = [("EMPLOYEE", 200, 82, VIO), ("PROJECT", 360, 152, CYA), ("DECISION", 530, 82, PNK),
             ("DOCUMENT", 700, 152, CYA), ("CUSTOMER", 872, 88, VIO)]
    QX, QY = 74, 120
    DUR = 7.0
    pts = [(QX + 18, QY)] + [(x, y) for _, x, y, _ in nodes]
    d = "M" + " L".join(f"{x} {y}" for x, y in pts)

    css = [BASE_CSS, travel_keyframes("probe", pts),
           f"""    .probe {{ animation: probe {DUR}s linear infinite, probefade {DUR}s linear infinite; }}
    @keyframes probefade {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: 0; }} }}
    .beam {{ stroke-dasharray: 1400; animation: beam {DUR}s linear infinite; }}
    @keyframes beam {{ 0% {{ stroke-dashoffset: 1400; }} 55%, 85% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: 1400; }} }}
    .qglow {{ transform-box: fill-box; transform-origin: center; animation: qglow 2.4s ease-in-out infinite; }}
    @keyframes qglow {{ 0%, 100% {{ transform: scale(0.8); }} 50% {{ transform: scale(1.25); }} }}"""]
    for i in range(len(nodes)):
        b = 0.55 + i * 0.72
        p = b / DUR * 100
        css.append(f"""    .hit{i} {{ animation: hit{i} {DUR}s linear infinite; }}
    @keyframes hit{i} {{ 0%, {p:.2f}% {{ opacity: 0; }} {p+6:.2f}% {{ opacity: 1; }} {p+50:.2f}%, 100% {{ opacity: 0.35; }} }}""")

    defs = f'''    <linearGradient id="qGrad" gradientUnits="userSpaceOnUse" x1="74" y1="0" x2="872" y2="0">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="50%" stop-color="{CYA}"/><stop offset="100%" stop-color="{PNK}"/>
    </linearGradient>
    <radialGradient id="qglowGrad"><stop offset="0%" stop-color="{CYA}" stop-opacity="0.5"/><stop offset="100%" stop-color="{CYA}" stop-opacity="0"/></radialGradient>
'''
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Company knowledge graph traversal">',
         '  <title>Company knowledge graph — one question, many hops</title>',
         '  <style>' + "\n".join(css) + '  </style>', card(W, H, defs)]
    a = s.append
    a(f'    <g font-family="{MONO}"><text x="54" y="36" font-size="12" letter-spacing="3" fill="{MID}">COMPANY KNOWLEDGE GRAPH &#183; <tspan fill="{PNK}">ONE QUESTION, MANY HOPS</tspan></text></g>')
    a(f'    <g stroke="{CYA}" stroke-width="1" opacity="0.16" fill="none">')
    a('      <path d="M268 205 L360 152"/><path d="M452 40 L530 82"/><path d="M620 208 L700 152"/><path d="M800 42 L872 88"/><path d="M952 178 L872 88"/><path d="M150 190 L200 82"/>')
    a('      <path d="M268 205 L200 82"/><path d="M620 208 L530 82"/><path d="M452 40 L360 152"/>')
    a('    </g>')
    a(f'    <g fill="{BG}" stroke="#334155" stroke-width="1.5">')
    for x, y in [(268, 205), (452, 40), (620, 208), (800, 42), (952, 178), (150, 190)]:
        a(f'      <circle cx="{x}" cy="{y}" r="4"/>')
    a('    </g>')
    a(f'    <path d="{d}" fill="none" stroke="{LINE}" stroke-width="2"/>')
    a(f'    <path class="beam" d="{d}" fill="none" stroke="url(#qGrad)" stroke-width="2.4" stroke-linecap="round"/>')
    for i, (label, x, y, col) in enumerate(nodes):
        w = len(label) * 7.6 + 30
        bx, by = x - w / 2, y - 15
        a('    <g>')
        a(f'      <rect x="{bx:.1f}" y="{by}" width="{w:.1f}" height="30" rx="15" fill="{PANEL}" stroke="#25313F" stroke-width="1.2"/>')
        a(f'      <rect class="hit{i}" x="{bx:.1f}" y="{by}" width="{w:.1f}" height="30" rx="15" fill="none" stroke="{col}" stroke-width="1.6" opacity="0"/>')
        a(f'      <circle cx="{bx+15:.1f}" cy="{y}" r="3.4" fill="{col}"/>')
        a(f'      <text x="{x+8}" y="{y+4.5}" text-anchor="middle" font-family="{MONO}" font-size="11.5" letter-spacing="1.3" fill="#D5DEEA">{label}</text>')
        a('    </g>')
    a(f'    <circle class="qglow" cx="{QX}" cy="{QY}" r="26" fill="url(#qglowGrad)"/>')
    a(f'    <circle cx="{QX}" cy="{QY}" r="18" fill="{PANEL}" stroke="url(#qGrad)" stroke-width="2.2"/>')
    a(f'    <text x="{QX}" y="{QY+7}" text-anchor="middle" font-family="{MONO}" font-size="18" font-weight="700" fill="{CYA}">?</text>')
    a('    <circle class="probe" r="4.5" fill="#FFFFFF"/>')
    a(f'    <g font-family="{MONO}"><text x="54" y="234" font-size="12.5" fill="{DIM}"><tspan fill="{CYA}">&gt;</tspan> who owns the churn model, what did they decide in june, and which doc says why?</text></g>')
    s.append(frame(W, H))
    write("company-graph.svg", "\n".join(s))


# ------------------------------------------------------------------ footer
def footer():
    W, H = 1000, 90
    css = [BASE_CSS, travel_keyframes("fdot", [(40, 46), (960, 46)])]
    defs = f'''    <linearGradient id="fGrad" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="960" y2="0">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="50%" stop-color="{CYA}"/><stop offset="100%" stop-color="{PNK}"/>
    </linearGradient>
    <linearGradient id="fFade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYA}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{CYA}" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="{CYA}" stop-opacity="0"/>
    </linearGradient>
'''
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="footer">',
         '  <title>graphs · context · robots</title>',
         '  <style>' + "\n".join(css) + '  </style>', card(W, H, defs, rx=16)]
    a = s.append
    a(f'    <path class="flow" d="M40 46 L960 46" stroke="url(#fGrad)" stroke-width="1.6" fill="none" opacity="0.55" stroke-dasharray="6 8"/>')
    for i, (x, col) in enumerate([(180, VIO), (400, CYA), (620, PNK), (840, VIO)]):
        a(f'    <circle class="halo" cx="{x}" cy="46" r="12" fill="{col}" style="animation-delay: {i*0.7}s"/>')
        a(f'    <circle cx="{x}" cy="46" r="5" fill="{BG}" stroke="{col}" stroke-width="2"/>')
    a('    <circle r="3.4" fill="#FFFFFF" opacity="0.9" style="animation: fdot 4.6s linear infinite"/>')
    a(f'    <circle r="2.6" fill="{PNK}" opacity="0.9" style="animation: fdot 4.6s linear 2.3s infinite"/>')
    a(f'    <text x="500" y="76" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="3.6" fill="{DIM}">GRAPHS &#183; CONTEXT &#183; ROBOTS</text>')
    a(f'    <rect class="sweep" x="0" y="0" width="300" height="{H}" fill="url(#fFade)"/>')
    s.append(frame(W, H, rx=16))
    write("footer.svg", "\n".join(s))


if __name__ == "__main__":
    header(); typing(); thread(); pipeline(); company_graph(); footer()
