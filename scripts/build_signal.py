#!/usr/bin/env python3
"""Render assets/signal.svg from live GitHub data.

No third-party badge services: everything is queried from the GitHub GraphQL
API and drawn here, so the card cannot break when someone else's Vercel
deployment goes down.
"""
import json
import os
import subprocess
import sys
from datetime import date, datetime

LOGIN = os.environ.get("GH_LOGIN", "WynandNeethling")
OUT = os.environ.get("SIGNAL_OUT", "assets/signal.svg")

BG, PANEL, LINE, DIM, FG = "#0B0F14", "#0E141B", "#1F2A37", "#5C6B7E", "#D5DEEA"
VIO, CYA, PNK = "#7C5CFF", "#22D3EE", "#F471B5"
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace"

QUERY = """
query($login:String!) {
  user(login:$login) {
    followers { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first:12, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch():
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={LOGIN}"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        sys.exit(f"gh api failed: {out.stderr.strip()}")
    return json.loads(out.stdout)["data"]["user"]


def streak(days):
    """Current streak, counting back from today (today may still be empty)."""
    run = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            run += 1
        elif i == 0:
            continue
        else:
            break
    return run


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    repos = user["repositories"]["nodes"]

    stars = sum(r["stargazerCount"] for r in repos)
    # Weight each repo equally. Raw byte counts let notebooks (which embed their
    # own output) drown out everything else, which is not a useful picture.
    langs = {}
    colors = {}
    for r in repos:
        edges = r["languages"]["edges"]
        repo_total = sum(e["size"] for e in edges)
        if not repo_total:
            continue
        for e in edges:
            n = e["node"]["name"]
            langs[n] = langs.get(n, 0) + e["size"] / repo_total
            colors[n] = e["node"]["color"] or CYA
    top = [kv for kv in sorted(langs.items(), key=lambda kv: -kv[1]) if kv[1] > 0][:6]
    total_bytes = sum(v for _, v in top) or 1

    tiles = [
        ("CONTRIBUTIONS", f"{cal['totalContributions']:,}", "past 12 months", VIO),
        ("CURRENT STREAK", f"{streak(days)}", "days", CYA),
        ("PUBLIC REPOS", f"{user['repositories']['totalCount']}", "public repositories", PNK),
        ("STARS EARNED", f"{stars}", "across public work", VIO),
    ]

    W, H = 1000, 384
    pad, gap = 28, 16
    tw = (W - 2 * pad - 3 * gap) / 4
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub signal for {LOGIN}">')
    a(f'  <title>GitHub signal — {LOGIN}</title>')
    a(f'''  <defs>
    <linearGradient id="sGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{VIO}"/><stop offset="50%" stop-color="{CYA}"/><stop offset="100%" stop-color="{PNK}"/>
    </linearGradient>
    <linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{CYA}" stop-opacity="0.32"/><stop offset="100%" stop-color="{CYA}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="shimmer" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#FFFFFF" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <pattern id="sgrid" width="26" height="26" patternUnits="userSpaceOnUse">
      <path d="M26 0H0V26" fill="none" stroke="#151D27" stroke-width="1"/>
    </pattern>
    <clipPath id="sbar"><rect x="28" y="310" width="944" height="14" rx="7"/></clipPath>
    <clipPath id="scard"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#scard)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#sgrid)" opacity="0.55"/>''')

    a(f'    <g font-family="{MONO}">')
    a(f'      <circle cx="{pad+4}" cy="34" r="4" fill="{CYA}"><animate attributeName="opacity" values="1;0.2;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    a(f'      <text x="{pad+19}" y="38" font-size="12" letter-spacing="3" fill="#8B97A8">SIGNAL &#183; <tspan fill="{VIO}">LIVE FROM THE GITHUB API</tspan></text>')
    a(f'      <text x="{W-pad}" y="38" text-anchor="end" font-size="10" letter-spacing="1.6" fill="{DIM}">updated {date.today().isoformat()}</text>')
    a('    </g>')

    for i, (label, value, sub, col) in enumerate(tiles):
        x = pad + i * (tw + gap)
        a(f'    <g>')
        a(f'      <rect x="{x:.1f}" y="56" width="{tw:.1f}" height="84" rx="12" fill="{PANEL}" stroke="{LINE}"/>')
        a(f'      <rect x="{x+14:.1f}" y="55" width="{tw-28:.1f}" height="2.5" rx="1.2" fill="{col}" opacity="0.3">')
        a(f'        <animate attributeName="opacity" values="0.3;1;0.3" dur="4.8s" begin="{i*1.2}s" repeatCount="indefinite"/>')
        a(f'      </rect>')
        a(f'      <g font-family="{MONO}">')
        a(f'        <text x="{x+18:.1f}" y="80" font-size="10" letter-spacing="2" fill="{DIM}">{label}</text>')
        a(f'        <text x="{x+18:.1f}" y="113" font-size="28" font-weight="700" fill="{FG}">{value}</text>')
        a(f'        <text x="{x+18:.1f}" y="130" font-size="9.5" letter-spacing="0.8" fill="{col}">{sub}</text>')
        a(f'      </g>')
        a(f'    </g>')

    # sparkline
    sx0, sx1, sy0, sy1 = pad, W - pad, 190, 268
    peak = max(weekly) or 1
    n = len(weekly)
    pts = [(sx0 + (sx1 - sx0) * i / max(n - 1, 1), sy1 - (sy1 - sy0) * (v / peak)) for i, v in enumerate(weekly)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = line + f" L{sx1:.1f} {sy1} L{sx0:.1f} {sy1} Z"
    a(f'    <g font-family="{MONO}">')
    a(f'      <text x="{pad}" y="172" font-size="10" letter-spacing="2.4" fill="{DIM}">52&#8209;WEEK CONTRIBUTION RHYTHM &#183; peak {peak}/week</text>')
    a(f'    </g>')
    a(f'    <line x1="{sx0}" y1="{sy1}" x2="{sx1}" y2="{sy1}" stroke="{LINE}"/>')
    a(f'    <path d="{area}" fill="url(#sparkFill)"/>')
    a(f'    <path id="spark" d="{line}" fill="none" stroke="url(#sGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.32"/>')
    a(f'    <path d="{line}" fill="none" stroke="url(#sGrad)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2600" stroke-dashoffset="2600">')
    a(f'      <animate attributeName="stroke-dashoffset" values="2600;0" dur="2.6s" begin="0.2s" fill="freeze"/>')
    a(f'    </path>')
    a(f'    <circle r="4" fill="#FFFFFF"><animateMotion dur="5.5s" repeatCount="indefinite"><mpath xlink:href="#spark" href="#spark"/></animateMotion></circle>')

    # language mix
    a(f'    <g font-family="{MONO}">')
    a(f'      <text x="{pad}" y="300" font-size="10" letter-spacing="2.4" fill="{DIM}">LANGUAGE MIX &#183; each public repo weighted equally</text>')
    a(f'    </g>')
    bar_y, bar_h, bw = 310, 14, W - 2 * pad
    a(f'    <rect x="{pad}" y="{bar_y}" width="{bw}" height="{bar_h}" rx="7" fill="{PANEL}" stroke="{LINE}"/>')
    a(f'    <g>')
    cur = pad
    for i, (name, size) in enumerate(top):
        seg = bw * size / total_bytes
        a(f'      <rect x="{cur:.1f}" y="{bar_y}" width="{seg:.1f}" height="{bar_h}" fill="{colors[name]}" opacity="0.9">')
        a(f'        <animate attributeName="opacity" values="0.9;1;0.9" dur="4.8s" begin="{i * 0.5:.2f}s" repeatCount="indefinite"/>')
        a(f'      </rect>')
        cur += seg
    a(f'    </g>')
    a(f'    <g clip-path="url(#sbar)"><rect x="{pad-200}" y="{bar_y}" width="200" height="{bar_h}" fill="url(#shimmer)" opacity="0.55">')
    a(f'      <animate attributeName="x" values="{pad-200};{W}" dur="4.5s" repeatCount="indefinite"/>')
    a(f'    </rect></g>')
    a(f'    <rect x="{pad}" y="{bar_y}" width="{bw}" height="{bar_h}" rx="7" fill="none" stroke="{LINE}"/>')

    lx = pad
    a(f'    <g font-family="{MONO}" font-size="10.5" fill="{FG}">')
    for name, size in top:
        pct = 100 * size / total_bytes
        a(f'      <circle cx="{lx+4:.1f}" cy="350" r="4" fill="{colors[name]}"/>')
        a(f'      <text x="{lx+14:.1f}" y="354">{esc(name)} <tspan fill="{DIM}">{pct:.0f}%</tspan></text>')
        lx += 14 + (len(name) + len(f"{pct:.0f}%") + 2) * 6.6 + 20
    a(f'    </g>')

    a(f'    <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{LINE}"/>')
    a('  </g>')
    a('</svg>')
    return "\n".join(s) + "\n"


if __name__ == "__main__":
    svg = build(fetch())
    svg = svg.replace("<svg ", '<svg xmlns:xlink="http://www.w3.org/1999/xlink" ', 1)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    open(OUT, "w").write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes)")
