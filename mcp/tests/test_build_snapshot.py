"""Snapshot builder against saved copies of the public pages (no network)."""
from pathlib import Path

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


def test_build_with_fixture_fetch_only_reads_public_site(monkeypatch):
    seen = []

    def spy(url):
        seen.append(url)
        slug = url.rstrip("/").split("/")[-1]
        if slug in ("eu", "cf28"):
            return read("foreign-ior")  # shape is enough here
        return fake_fetch(url)

    snap = b.build(spy, today="2026-11-16")
    assert snap["generated"] == "2026-11-16"
    assert all(u.startswith("https://plaudeapi.com/trade/") for u in seen)
    assert snap["firm"] == "Bandi & Associates PLLC"
