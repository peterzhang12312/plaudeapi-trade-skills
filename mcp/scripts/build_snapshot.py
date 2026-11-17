"""Build snapshot.json from the PUBLIC pages of plaudeapi.com/trade (stdlib only).

Reads only: /trade/guides/ (index) and each guide page listed there.
No private data, no Firm App, no credentials. Run: python scripts/build_snapshot.py
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

BASE = "https://plaudeapi.com"
OUT = Path(__file__).resolve().parent.parent / "src" / "plaudeapi_trade_mcp" / "snapshot.json"

FIRM = "Bandi & Associates PLLC"
DISCLAIMER = (
    "General information only, not legal advice. Using this server does not create an "
    "attorney-client relationship. Published by Bandi & Associates PLLC."
)
FREE_CHECK_URL = f"{BASE}/trade/"
DIAGNOSTIC_URL = f"{BASE}/trade/#diagnostic"
EXPECTED_FEE = "495"
STALE_AFTER_DAYS = 14
ACK_ENV = "MCP_FRESHNESS_ACK"  # non-empty reason overrides the freshness gate; recorded in the snapshot


class BuildError(RuntimeError):
    pass


def fetch(url: str) -> str:
    if not url.startswith(BASE + "/"):
        raise ValueError("only the public plaudeapi.com site is read")
    req = urllib.request.Request(url, headers={"User-Agent": "plaudeapi-trade-mcp-snapshot/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (fixed https host)
        return r.read().decode("utf-8")


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


class _Article(HTMLParser):
    """Collect table rows and list items (with absolute links) per <h2> inside <article>."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.in_article = False
        self.h2 = ""
        self.h2_buf: list[str] = []
        self.tables: dict[str, list[list[str]]] = {}
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.li: list[str] | None = None
        self.li_links: list[str] = []
        self.lis: dict[str, list[tuple[str, list[str]]]] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.stack.append(tag)
        if tag == "article":
            self.in_article = True
        if not self.in_article:
            return
        if tag == "h2":
            self.h2_buf = []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "li":
            self.li, self.li_links = [], []
        elif tag == "a" and self.li is not None and (a.get("href") or "").startswith("http"):
            self.li_links.append(a["href"])

    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()
        if tag == "article":
            self.in_article = False
        if not self.in_article:
            return
        if tag == "h2":
            self.h2 = "".join(self.h2_buf).strip()
        elif tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.tables.setdefault(self.h2, []).append(self.row)
            self.row = None
        elif tag == "li" and self.li is not None:
            text = re.sub(r"\s+", " ", "".join(self.li)).strip()
            self.lis.setdefault(self.h2, []).append((text, self.li_links))
            self.li = None

    def handle_data(self, data):
        if not self.in_article:
            return
        if self.stack and self.stack[-1] == "h2":
            self.h2_buf.append(data)
        if self.cell is not None:
            self.cell.append(data)
        if self.li is not None:
            self.li.append(data)


def parse_index(page: str) -> list[dict]:
    """Guides index -> [{slug, title, date_label, date, zh_path, description}]."""
    out = []
    for li in re.findall(r'<li>\s*<a class="guide-title".*?</li>', page, re.S):
        href, title = re.search(r'href="([^"]+)">(.*?)</a>', li, re.S).group(1, 2)
        meta = re.search(r'<p class="guide-meta">(Verified|Updated) <time datetime="([\d-]+)"', li)
        desc = re.search(r'<p class="guide-desc">(.*?)</p>', li, re.S)
        zh = re.search(r'href="([^"]+)" hreflang="zh"', li)
        out.append({
            "slug": href.strip("/").split("/")[-1],
            "title": _clean(title),
            "date_label": meta.group(1),
            "date": meta.group(2),
            "zh_path": zh.group(1) if zh else None,
            "description": _clean(desc.group(1)) if desc else "",
        })
    return out


def parse_guide(page: str) -> dict:
    p = _Article()
    p.feed(page)
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
    meta = json.loads(ld.group(1)) if ld else {}
    key_dates = [
        {"date": _clean(r[0]), "event": r[1], "source": r[2]}
        for r in p.tables.get("Key dates", [])
        if len(r) >= 3 and r[0] != "Date"
    ]
    authorities = []
    for text, links in p.lis.get("Primary authorities", []):
        cite = re.sub(r"\s*(—\s*)?https?://\S+", "", text).strip(" —")
        authorities.append({"citation": cite, "urls": links})  # unlinked statutes keep urls: []
    sec = re.search(r"<h2>Primary authorities</h2>(.*?)(?=<h2|</article>)", page, re.S)
    note = re.search(r"<p[^>]*>([^<]*(?:was read on|were read on)[^<]*)</p>", sec.group(1)) if sec else None
    return {
        "published": meta.get("datePublished"),
        "modified": meta.get("dateModified"),
        "key_dates": key_dates,
        "authorities": authorities,
        "reading_note": _clean(note.group(1)) if note else None,
    }


def parse_fee(page: str) -> str:
    m = re.search(r"<strong>Fee</strong>\s*<span>\$([\d,]+)</span>", page)
    if not m:
        raise BuildError("fee not found on /trade/; refusing to build")
    fee = m.group(1).replace(",", "")
    if fee != EXPECTED_FEE:
        raise BuildError(f"/trade/ shows ${fee}, expected ${EXPECTED_FEE}; update the builder deliberately")
    return fee


def build(fetch_fn=fetch, today: str | None = None, ack: str | None = None) -> dict:
    today = today or date.today().isoformat()
    fee = parse_fee(fetch_fn(f"{BASE}/trade/"))
    guides = []
    for g in parse_index(fetch_fn(f"{BASE}/trade/guides/")):
        page = parse_guide(fetch_fn(f"{BASE}/trade/{g['slug']}/"))
        guides.append({
            "slug": g["slug"],
            "title": g["title"],
            "url": f"{BASE}/trade/{g['slug']}/",
            "zh_url": urljoin(BASE, g["zh_path"]) if g["zh_path"] else None,
            "description": g["description"],
            "verified": g["date"] if g["date_label"] == "Verified" else None,
            "updated": g["date"] if g["date_label"] == "Updated" else None,
            **page,
        })
    stale = [
        f"{g['slug']} verified {g['verified']}"
        for g in guides
        if g["verified"] and (date.fromisoformat(today) - date.fromisoformat(g["verified"])).days > STALE_AFTER_DAYS
    ]
    override = None
    if stale:
        if not (ack or "").strip():
            raise BuildError(
                f"verified date more than {STALE_AFTER_DAYS} days before {today}: {'; '.join(stale)}. "
                f"Re-verify the guide, or set {ACK_ENV}=<reason> to override (recorded in the snapshot)."
            )
        override = {"reason": ack.strip(), "guides": stale}
    snap = {
        "schema_version": 1,
        "generated": today,
        "origin": f"{BASE}/trade/guides/",
        "firm": FIRM,
        "disclaimer": DISCLAIMER,
        "free_check_url": FREE_CHECK_URL,
        "diagnostic": {"label": f"US${fee} attorney-signed diagnostic", "url": DIAGNOSTIC_URL},
        "guides": guides,
    }
    if override:
        snap["freshness_override"] = override
    return snap


def main() -> int:
    try:
        snap = build(ack=os.environ.get(ACK_ENV))
    except BuildError as e:
        print(f"build refused: {e}", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(snap['guides'])} guides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
