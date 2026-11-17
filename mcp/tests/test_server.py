"""Offline tests: in-memory MCP client against the bundled snapshot. No network."""
import json
import logging

import anyio
import pytest
from mcp import Client

from plaudeapi_trade_mcp.server import build_server, load_snapshot



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
        ("get_sources", {"guide": "eu"}),
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


def test_sources_have_urls():
    s = run(lambda c: c.call_tool("get_sources", {"guide": "ieepa-refund"})).structured_content
    assert s["authorities"]
    assert all(u.startswith("https://") for a in s["authorities"] for u in a["urls"])


@pytest.mark.parametrize("args", [{"guide": "anything we typed about our shipment"}, {"guide": "eu"}])
def test_free_text_is_rejected(args):
    r = run(lambda c: c.call_tool("get_rule_dates", args))
    assert r.is_error


def test_no_input_is_logged(caplog):
    secret = "ACME-ENTRY-123-SECRET"
    with caplog.at_level(logging.DEBUG):
        run(lambda c: c.call_tool("get_rule_dates", {"guide": secret}))
        run(lambda c: c.call_tool("get_sources", {"guide": "eu", "note": secret}))
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
