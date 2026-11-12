#!/usr/bin/env python3
"""Build the Ironclad docs site (static, no runtime deps).

    python3 docs/build.py

Reads docs/pages/*.md (frontmatter + markdown), writes site/ with one
directory per page (index.html), a shared sidebar, per-page TOC, search
index, and assets. Dependency: python3-markdown (build time only).
"""

import json
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("build-time dependency missing: pip install markdown (or apt install python3-markdown)")

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages"
ASSETS = ROOT / "assets"
OUT = ROOT.parent / "site"
AVER = ""  # set in main(): version + content hash for cache-busting

SITE_TITLE = "Ironclad"
TAGLINE = "Aturan engineering tim, ditegakkan mesin."
VERSION = "0.4.0"


def asset_ver() -> str:
    """Cache-bust on content, not on release: a file edited without a version
    bump must still reach the browser, otherwise a deployed fix looks broken."""
    import hashlib
    h = hashlib.sha1()
    for name in ("docs.css", "docs.js"):
        h.update((ASSETS / name).read_bytes())
    return f"{VERSION}-{h.hexdigest()[:8]}"


def split_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5:]
    meta = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"[-\s]+", "-", s).strip("-")


def collect():
    pages = []
    for path in sorted(PAGES.glob("*.md")):
        meta, body = split_frontmatter(path.read_text())
        slug = meta.get("slug") or path.stem
        pages.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "group": meta.get("group", "Docs"),
            "summary": meta.get("summary", ""),
            "order": int(meta.get("order", 99)),
            "body": body,
            "src": path.name,
        })
    pages.sort(key=lambda p: (p["order"], p["title"]))
    return pages


def render_md(text):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "attr_list", "sane_lists", "toc"],
                           extension_configs={"toc": {"permalink": False}})
    html = md.convert(text)
    return html, md.toc_tokens


def add_copy_buttons(html):
    """Every <pre> gets a copy button. Assets are static, so this is a plain string insert."""
    def repl(m):
        return ('<div class="codewrap"><button class="copy" type="button" '
                'aria-label="Salin perintah">SALIN</button>' + m.group(0) + "</div>")
    return re.sub(r"<pre>.*?</pre>", repl, html, flags=re.S)


SEV_RE = re.compile(r"<td>(<strong>)?(error|warn|off)(</strong>)?</td>")


def decorate_tables(html):
    """Wrap tables so they scroll inside themselves, and make severity cells
    readable at a glance instead of relying on the word alone."""
    def sev(m):
        word = m.group(2)
        return f'<td><span class="sev sev-{word}">{word}</span></td>'
    html = SEV_RE.sub(sev, html)
    return html.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")


LINK_RE = re.compile(r'href="/(?!/|#|http)([^"]*)"')


def fix_links(html, pages):
    """Absolute /slug/ links get the site prefix so the build is portable."""
    return LINK_RE.sub(lambda m: f'href="/ironclad/{m.group(1).lstrip("/")}"', html)


def build_toc(tokens):
    """Flatten the nested token tree: markdown.py nests h2/h3 under h1."""
    out = []

    def walk(nodes):
        for t in nodes:
            if t["level"] in (2, 3):
                out.append((t["level"], t["name"], t["id"]))
            walk(t.get("children") or [])

    walk(tokens)
    return out


NAV_ICON = {
    "Mulai": "01",
    "Konsep": "02",
    "Referensi": "03",
    "Operasional": "04",
}


def sidebar_html(pages, current):
    groups = {}
    for p in pages:
        groups.setdefault(p["group"], []).append(p)
    parts = []
    for gi, (group, items) in enumerate(groups.items(), 1):
        parts.append(f'<div class="navgroup"><div class="navlabel">'
                     f'<span>{gi:02d}</span>{group}</div><ul>')
        for p in items:
            active = ' class="active" aria-current="page"' if p["slug"] == current else ""
            parts.append(f'<li><a href="/ironclad/{p["slug"]}/"{active}>{p["title"]}</a></li>')
        parts.append("</ul></div>")
    return "\n".join(parts)


LAYOUT = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Ironclad</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://wilsench.my.id/ironclad/{slug}/">
<meta name="color-scheme" content="light">
<link rel="stylesheet" href="/ironclad/assets/docs.css?v={ver}">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>

<a class="skip" href="#main">Lompat ke isi</a>

<div class="shell">

  <aside class="side" id="side">
    <a class="brand" href="/ironclad/">
      <span class="mark" aria-hidden="true">IC</span>
      <span>
        <b>Ironclad</b>
        <i>v{ver} · MIT</i>
      </span>
    </a>

    <button class="searchbtn" type="button" id="searchbtn">
      <span>Cari dokumentasi</span><kbd>/</kbd>
    </button>

    <nav class="nav" aria-label="Dokumentasi">
      {nav}
    </nav>

    <div class="sidefoot">
      <a href="https://github.com/wilsench/ironclad">GitHub</a>
      <a href="https://wilsench.my.id/">wilsench.my.id</a>
    </div>
  </aside>

  <div class="scrim" id="scrim" hidden></div>

  <main id="main">
    <header class="topbar">
      <button class="burger" type="button" id="burger" aria-label="Buka menu" aria-expanded="false">
        <span></span><span></span>
      </button>
      <span class="crumb">{group} / <b>{title}</b></span>
      <button class="searchmini" type="button" id="searchmini" aria-label="Cari">/<span>Cari</span></button>
    </header>

    <div class="pagegrid">
      <article class="prose">
        {body}
        <nav class="pager" aria-label="Halaman berikutnya">
          {pager}
        </nav>
        <footer class="docfoot">
          <span>Ironclad v{ver}</span>
          <span>MIT</span>
          <span>Chia Wilsen</span>
        </footer>
      </article>

      <aside class="{tocclass}" aria-label="Di halaman ini">
        <div class="navlabel"><span>§</span>Di halaman ini</div>
        <ul>{toc}</ul>
      </aside>
    </div>
  </main>
</div>

<div class="search" id="search" hidden>
  <div class="searchbox">
    <input id="q" type="search" placeholder="Cari: install, preset, DB-04, CI…" autocomplete="off" spellcheck="false">
    <button id="closeSearch" type="button">ESC</button>
  </div>
  <ul id="results"></ul>
  <p class="hint">↑ ↓ pilih · ↵ buka · ESC tutup</p>
</div>

<script src="/ironclad/assets/docs.js?v={ver}" defer></script>
<script src="/ironclad/assets/search-index.js?v={ver}" defer></script>
</body>
</html>
"""


def main():
    global AVER
    AVER = asset_ver()
    pages = collect()
    if not pages:
        sys.exit("no pages found in docs/pages/")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(ASSETS / "docs.css", OUT / "assets" / "docs.css")
    shutil.copy(ASSETS / "docs.js", OUT / "assets" / "docs.js")

    index = []
    for i, p in enumerate(pages):
        html, tokens = render_md(p["body"])
        html = add_copy_buttons(html)
        html = decorate_tables(html)
        html = fix_links(html, pages)

        toc = build_toc(tokens)
        toc_html = "\n".join(
            f'<li class="lvl{lvl}"><a href="#{tid}">{name}</a></li>' for lvl, name, tid in toc
        ) or '<li class="lvl2"><a href="#main">Ringkas</a></li>'
        toc_class = "toc thin" if len(toc) < 3 else "toc"

        prev_p = pages[i - 1] if i > 0 else None
        next_p = pages[i + 1] if i + 1 < len(pages) else None
        pager = []
        if prev_p:
            pager.append(f'<a class="prev" href="/ironclad/{prev_p["slug"]}/">'
                         f'<span>Sebelumnya</span><b>{prev_p["title"]}</b></a>')
        if next_p:
            pager.append(f'<a class="next" href="/ironclad/{next_p["slug"]}/">'
                         f'<span>Berikutnya</span><b>{next_p["title"]}</b></a>')

        page_html = LAYOUT.format(
            title=p["title"], desc=p["summary"] or TAGLINE, slug=p["slug"], ver=AVER,
            nav=sidebar_html(pages, p["slug"]), group=p["group"], body=html,
            toc=toc_html, pager="\n".join(pager), tocclass=toc_class,
        )
        dest = OUT / p["slug"]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(page_html)

        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        index.append({"t": p["title"], "g": p["group"], "u": f"/ironclad/{p['slug']}/",
                      "s": p["summary"], "x": text[:1400]})

    (OUT / "assets" / "search-index.js").write_text(
        "window.IRONCLAD_INDEX=" + json.dumps(index, ensure_ascii=False) + ";\n")

    # /ironclad/ serves the first page directly (no redirect: the first page IS
    # the landing), but its canonical points at the stable /overview/ URL.
    first = OUT / pages[0]["slug"] / "index.html"
    (OUT / "index.html").write_text(first.read_text())

    print(f"built {len(pages)} pages → {OUT}")
    for p in pages:
        print(f"  /ironclad/{p['slug']}/  {p['title']}")


if __name__ == "__main__":
    main()
