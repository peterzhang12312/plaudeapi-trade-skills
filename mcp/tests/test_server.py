"""Offline tests: in-memory MCP client against the bundled snapshot. No network."""
import json
import logging
from datetime import date

import anyio
import pytest
from mcp import Client

from plaudeapi_trade_mcp import server as srv
from plaudeapi_trade_mcp.server import build_server, load_snapshot



@pytest.fixture(autouse=True)
def frozen_clock(monkeypatch):
    """Default: the day the snapshot was generated, so results are fresh."""
    monkeypatch.setattr(srv, "_today", lambda: date(2026, 11, 16))


def run(coro_fn):
    result = {}

    async def main():
        async with Client(build_server()) as c:
            result["v"] = await coro_fn(c)

    anyio.run(main)
    return result["v"]


def test_protocol_revision():
    assert run(lambda c: _ret(c.protocol_version)) == "2026-07-28"


async def _ret(x):
    return x


def test_three_read_only_tools():
    tools = run(lambda c: _tools(c))
    assert sorted(t.name for t in tools) == ["get_rule_dates", "get_sources", "list_guides"]
    for t in tools:
        a = t.annotations
        assert a.read_only_hint is True
        assert a.destructive_hint is False
        assert a.idempotent_hint is True
        assert a.open_world_hint is False
        assert t.output_schema


async def _tools(c):
    return (await c.list_tools()).tools


def test_inputs_are_enums_only_no_free_text():
    for t in run(lambda c: _tools(c)):
        for name, prop in t.input_schema.get("properties", {}).items():
            assert "enum" in prop, f"{t.name}.{name} accepts free text"


def test_descriptions_have_no_price_or_checkout():
    for t in run(lambda c: _tools(c)):
        text = (t.description or "").lower()
        for bad in ("$", "495", "checkout", "buy", "pay", "order"):
            assert bad not in text, (t.name, bad)


@pytest.mark.parametrize(
    "tool,args",
    [
        ("list_guides", {}),
        ("get_rule_dates", {"guide": "foreign-ior"}),
        ("get_rule_dates", {"guide": "ieepa-refund"}),
        ("get_sources", {"guide": "cf28"}),
    ],
)
def test_every_result_carries_disclaimer_firm_date_and_next_step(tool, args):
    r = run(lambda c: c.call_tool(tool, args))
    assert not r.is_error
    s = r.structured_content
    assert "not legal advice" in s["disclaimer"]
    assert "attorney-client relationship" in s["disclaimer"]
    assert s["attribution"] == "Bandi & Associates PLLC"
    assert s["snapshot_generated"]
    assert s["verified"] or s["updated"] or tool == "list_guides"
    assert 0 <= s["age_days"] <= 3 and s["stale"] is False
    ns = s["next_step"]
    assert ns["free_check"] == "https://plaudeapi.com/trade/"
    assert ns["attorney_diagnostic"].startswith("https://plaudeapi.com/trade/")
    assert "US$495" in ns["attorney_diagnostic_label"]
    # text content mirrors the structured result (spec: also return serialized JSON)
    assert json.loads(r.content[0].text) == s


def test_foreign_ior_rule_date_and_citation():
    s = run(lambda c: c.call_tool("get_rule_dates", {"guide": "foreign-ior"})).structured_content
    eff = [d for d in s["dates"] if d["date"] == "2027-01-05" and "effective" in d["event"]]
    assert eff and "69977" in eff[0]["source"]
    assert any("2026-22735" in d["event"] for d in s["dates"])
    assert s["verified"] == "2026-11-13"


def test_sources_have_urls_and_unlinked_authorities_are_kept():
    s = run(lambda c: c.call_tool("get_sources", {"guide": "ieepa-refund"})).structured_content
    assert s["authorities"]
    assert all(u.startswith("https://") for a in s["authorities"] for u in a["urls"])
    cf = run(lambda c: c.call_tool("get_sources", {"guide": "cf28"})).structured_content
    assert any(a["urls"] == [] for a in cf["authorities"])
    assert "read on 2026-09-20" in cf["reading_note"]


def test_every_get_sources_enum_slug_yields_an_authority():
    tool = next(t for t in run(lambda c: _tools(c)) if t.name == "get_sources")
    slugs = tool.input_schema["properties"]["guide"]["enum"]
    assert "eu" not in slugs and slugs
    for slug in slugs:
        s = run(lambda c: c.call_tool("get_sources", {"guide": slug})).structured_content
        assert len(s["authorities"]) >= 1, slug


@pytest.mark.parametrize(
    "tool,args",
    [("get_rule_dates", {"guide": "anything we typed about our shipment"}), ("get_rule_dates", {"guide": "eu"}),
     ("get_sources", {"guide": "eu"})],
)
def test_free_text_and_unsupported_slugs_are_rejected(tool, args):
    assert run(lambda c: c.call_tool(tool, args)).is_error


def test_input_schemas_are_closed_objects():
    for t in run(lambda c: _tools(c)):
        assert t.input_schema["additionalProperties"] is False, t.name


def test_tool_description_example_is_in_the_snapshot():
    desc = next(t for t in run(lambda c: _tools(c)) if t.name == "get_rule_dates").description
    snap = load_snapshot()
    rows = next(g for g in snap["guides"] if g["slug"] == "foreign-ior")["key_dates"]
    assert any(r["date"] == "2027-01-05" and "effective" in r["event"] for r in rows)
    assert "2027-01-05" in desc and "2026-22735" in desc
    assert any("2026-22735" in r["event"] for r in rows)


def test_stale_snapshot_adds_age_flag_and_first_line(monkeypatch):
    monkeypatch.setattr(srv, "_today", lambda: date(2026, 12, 1))  # 15 days after 2026-11-16
    r = run(lambda c: c.call_tool("get_rule_dates", {"guide": "foreign-ior"}))
    s = r.structured_content
    assert s["age_days"] == 18 and s["stale"] is True  # verified 2026-11-13
    assert r.content[0].text == "This snapshot is 18 days old; open guide_url for the current text."
    assert json.loads(r.content[1].text) == s
    assert run(lambda c: c.call_tool("list_guides", {})).structured_content["stale"] is True


def test_fresh_boundary_is_14_days(monkeypatch):
    monkeypatch.setattr(srv, "_today", lambda: date(2026, 11, 27))  # 14 days after verified 11-13
    r = run(lambda c: c.call_tool("get_rule_dates", {"guide": "foreign-ior"}))
    assert r.structured_content["age_days"] == 14 and r.structured_content["stale"] is False
    assert len(r.content) == 1


def test_no_input_is_logged(caplog):
    secret = "ACME-ENTRY-123-SECRET"
    with caplog.at_level(logging.DEBUG):
        run(lambda c: c.call_tool("get_rule_dates", {"guide": secret}))
        run(lambda c: c.call_tool("get_sources", {"guide": "cf28", "note": secret}))
    assert secret not in caplog.text


def test_no_resources_prompts_or_write_surface():
    async def probe(c):
        return (await c.list_resources()).resources, (await c.list_prompts()).prompts

    res, prompts = run(probe)
    assert res == [] and prompts == []


def test_snapshot_shape():
    snap = load_snapshot()
    assert snap["firm"] == "Bandi & Associates PLLC"
    assert {g["slug"] for g in snap["guides"]} >= {"foreign-ior", "ieepa-refund", "cf28", "eu"}
    assert not any("pricing" in k for k in snap)
