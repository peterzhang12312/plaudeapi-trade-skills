"""Snapshot builder against saved copies of the public pages (no network)."""
from pathlib import Path

import pytest

import build_snapshot as b

FX = Path(__file__).parent / "fixtures"


def read(name):
    return (FX / f"{name}.html").read_text(encoding="utf-8")


def fake_fetch(url):
    if url.endswith("/trade/guides/"):
        return read("guides")
    slug = url.rstrip("/").split("/")[-1]
    return read(slug)


def test_parse_index():
    idx = b.parse_index(read("guides"))
    by = {g["slug"]: g for g in idx}
    assert by["foreign-ior"]["date_label"] == "Verified" and by["foreign-ior"]["date"] == "2026-11-13"
    assert by["cf28"]["date_label"] == "Updated"


def test_parse_guide_key_dates_and_authorities():
    g = b.parse_guide(read("foreign-ior"))
    assert g["published"] == "2026-11-14"
    assert ("2027-01-05", "69977") == (g["key_dates"][1]["date"], g["key_dates"][1]["source"].split("p. ")[1].split(";")[0])
    assert g["authorities"][0]["urls"][0].startswith("https://www.federalregister.gov/")
    assert "2026-11-13" in g["reading_note"]


def test_parse_cf28_keeps_unlinked_authorities_and_finds_note():
    g = b.parse_guide(read("cf28"))
    assert len(g["authorities"]) == 11
    unlinked = [a for a in g["authorities"] if not a["urls"]]
    assert [a["citation"].split(" ")[2] for a in unlinked] == ["1509(a)", "1484"]
    assert "read on 2026-09-20" in g["reading_note"]  # note sits before a Related-guides paragraph


def test_page_cite_notes_are_not_authorities_but_unlinked_authorities_stay():
    g = b.parse_guide(read("foreign-ior"))
    assert len(g["authorities"]) == 2
    assert not any(a["citation"].lower().startswith("page cite") for a in g["authorities"])
    cf = b.parse_guide(read("cf28"))
    assert sum(1 for a in cf["authorities"] if not a["urls"]) == 2


def test_parse_eu_has_no_authorities_section():
    g = b.parse_guide(read("eu"))
    assert g["authorities"] == [] and g["key_dates"] == []


def test_parse_fee():
    assert b.parse_fee(read("trade")) == "495"
    for bad in ("<p>no fee here</p>", "<strong>Fee</strong> <span>$500</span>"):
        with pytest.raises(b.BuildError):
            b.parse_fee(bad)


def test_build_with_real_fixtures_only_reads_public_site():
    seen = []

    def spy(url):
        seen.append(url)
        return fake_fetch(url)

    snap = b.build(spy, today="2026-11-16")
    assert snap["generated"] == "2026-11-16"
    assert all(u.startswith("https://plaudeapi.com/trade/") for u in seen)
    assert snap["firm"] == "Bandi & Associates PLLC"
    assert snap["diagnostic"]["label"] == "US$495 attorney-signed diagnostic"
    by = {g["slug"]: g for g in snap["guides"]}
    assert len(by["cf28"]["authorities"]) == 11 and by["cf28"]["reading_note"]
    assert by["eu"]["authorities"] == []
    assert "freshness_override" not in snap


def test_build_refuses_a_fee_that_is_not_495():
    def f(url):
        return fake_fetch(url).replace("<span>$495</span>", "<span>$500</span>")

    with pytest.raises(b.BuildError):
        b.build(f, today="2026-11-16")


def test_build_fails_when_verified_date_is_over_14_days_old():
    # foreign-ior verified 2026-11-13: 14 days is allowed, 15 is not.
    assert b.build(fake_fetch, today="2026-11-27")["generated"] == "2026-11-27"
    with pytest.raises(b.BuildError, match="foreign-ior"):
        b.build(fake_fetch, today="2026-11-28")


def test_freshness_override_is_recorded_in_the_snapshot():
    snap = b.build(fake_fetch, today="2026-12-20", ack="re-checked pages by hand 2026-12-20")
    ov = snap["freshness_override"]
    assert ov["reason"] == "re-checked pages by hand 2026-12-20"
    assert any(x.startswith("foreign-ior") for x in ov["guides"])
    with pytest.raises(b.BuildError):
        b.build(fake_fetch, today="2026-12-20", ack="  ")
