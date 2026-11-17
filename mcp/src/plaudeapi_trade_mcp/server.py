"""PlaudeAPI Trade public-facts MCP server (read-only, stateless, no user facts).

Serves dates, sources and guide links from a bundled snapshot of the public
plaudeapi.com/trade guides. Inputs are enums only: a client cannot submit free text,
so no client facts can reach this server. Nothing is stored; inputs are not logged.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel

SNAPSHOT_PATH = Path(__file__).with_name("snapshot.json")
INSTRUCTIONS = (
    "Public facts about U.S. import rules from the free guides at https://plaudeapi.com/trade/guides/. "
    "Tools take no free text and keep nothing. General information only, not legal advice; "
    "no attorney-client relationship. Published by Bandi & Associates PLLC."
)

GuideSlug = Literal["foreign-ior", "ieepa-refund", "cf28", "eu"]
DatedGuideSlug = Literal["foreign-ior", "ieepa-refund"]  # guides that publish a Key dates table

READ_ONLY = ToolAnnotations(
    readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False
)


class NextStep(BaseModel):
    free_check: str
    attorney_diagnostic: str
    attorney_diagnostic_label: str


class Provenance(BaseModel):
    disclaimer: str
    attribution: str
    verified: str | None  # date the page records as verified; None when the page records only an update date
    updated: str | None
    snapshot_generated: str
    source: str
    next_step: NextStep


class GuideEntry(BaseModel):
    slug: str
    title: str
    url: str
    zh_url: str | None
    description: str
    verified: str | None
    updated: str | None


class GuideList(Provenance):
    guides: list[GuideEntry]


class DateRow(BaseModel):
    date: str
    event: str
    source: str


class RuleDates(Provenance):
    guide: str
    guide_url: str
    title: str
    dates: list[DateRow]
    reading_note: str | None


class Authority(BaseModel):
    citation: str
    urls: list[str]


class Sources(Provenance):
    guide: str
    guide_url: str
    title: str
    authorities: list[Authority]
    reading_note: str | None


@lru_cache(maxsize=1)
def load_snapshot(path: str | None = None) -> dict:
    return json.loads(Path(path or SNAPSHOT_PATH).read_text(encoding="utf-8"))


def _prov(snap: dict, g: dict | None = None) -> dict:
    """Fields every result carries: disclaimer, firm, verification date, next step."""
    g = g or {}
    return {
        "disclaimer": snap["disclaimer"],
        "attribution": snap["firm"],
        "verified": g.get("verified") if g else None,
        "updated": g.get("updated") if g else None,
        "snapshot_generated": snap["generated"],
        "source": snap["origin"],
        "next_step": {
            "free_check": snap["free_check_url"],
            "attorney_diagnostic": snap["diagnostic"]["url"],
            "attorney_diagnostic_label": snap["diagnostic"]["label"],
        },
    }


def _guide(snap: dict, slug: str) -> dict:
    for g in snap["guides"]:
        if g["slug"] == slug:
            return g
    raise ValueError(f"unknown guide: {slug}")


def build_server(snapshot_path: str | None = None) -> MCPServer:
    snap = load_snapshot(snapshot_path)
    mcp = MCPServer(
        name="plaudeapi-trade-public-facts",
        title="PlaudeAPI Trade public facts",
        instructions=INSTRUCTIONS,
        website_url="https://plaudeapi.com/trade/agent/",
        version="0.1.0",
        log_level="WARNING",
    )

    @mcp.tool(
        name="list_guides",
        title="List PlaudeAPI Trade guides",
        description=(
            "List the public U.S. import guides with their page links and the date each page records "
            "as verified or updated. Takes no input. General information, not legal advice."
        ),
        annotations=READ_ONLY,
    )
    def list_guides() -> GuideList:
        return GuideList(
            **_prov(snap),
            guides=[
                GuideEntry(**{k: g[k] for k in GuideEntry.model_fields})
                for g in snap["guides"]
            ],
        )

    @mcp.tool(
        name="get_rule_dates",
        title="Get dated milestones for a guide",
        description=(
            "Return the dated milestones a guide publishes (for example the foreign importer-of-record "
            "rule effective 2027-01-05, FR Doc. 2026-22735) with each date's source citation and the "
            "guide's verification date. The only input is a guide slug from a fixed list. "
            "Dates are as published; check the primary source before relying on one."
        ),
        annotations=READ_ONLY,
    )
    def get_rule_dates(guide: DatedGuideSlug) -> RuleDates:
        g = _guide(snap, guide)
        return RuleDates(
            **_prov(snap, g),
            guide=g["slug"],
            guide_url=g["url"],
            title=g["title"],
            dates=[DateRow(**r) for r in g["key_dates"]],
            reading_note=g.get("reading_note"),
        )

    @mcp.tool(
        name="get_sources",
        title="Get primary sources for a guide",
        description=(
            "Return the primary authorities a guide cites (Federal Register, CBP CSMS messages, court "
            "opinions, statutes, regulations) with links, and the date they were last read. The only "
            "input is a guide slug from a fixed list."
        ),
        annotations=READ_ONLY,
    )
    def get_sources(guide: GuideSlug) -> Sources:
        g = _guide(snap, guide)
        return Sources(
            **_prov(snap, g),
            guide=g["slug"],
            guide_url=g["url"],
            title=g["title"],
            authorities=[Authority(**a) for a in g["authorities"]],
            reading_note=g.get("reading_note"),
        )

    return mcp


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(prog="plaudeapi-trade-mcp")
    ap.add_argument("--http", action="store_true", help="serve Streamable HTTP instead of stdio")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    server = build_server()
    if args.http:
        server.run("streamable-http", host=args.host, port=args.port)
    else:
        server.run("stdio")


if __name__ == "__main__":
    main()
