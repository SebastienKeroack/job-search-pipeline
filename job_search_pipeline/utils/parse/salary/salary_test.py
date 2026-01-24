#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from pathlib import Path
import re

import pytest

from job_search_pipeline.utils import format as fmt
from job_search_pipeline.utils import parse


def _normalize_salary_string(s: str) -> str:
    # Filenames don't contain the '/' used by _format_salary (e.g. "CAD 22-23 / hourly").
    # Normalize by removing '/', then collapsing whitespace.
    return re.sub(r"\s+", " ", s.replace("/", " ")).strip()


@pytest.mark.parametrize("salary_str", [None, ""])
def test_empty_input_returns_nones(salary_str):
    assert parse.salary.transform(salary_str) == (None, None, None, None)


@pytest.mark.parametrize(
    "salary_str, expected",
    [
        ("$85,000 - $110,000",       ("yearly",  85000, 110000, "USD")),
        ("$85k–110k",                ("yearly",  85000, 110000, "USD")),
        ("85 000,00$ à 110 000,00$", ("yearly",  85000, 110000, "USD")),
        ("$22 - $28",                ("hourly",  22,    28,     "USD")),
        ("$4,000 - $5,000",          ("monthly", 4000,  5000,   "USD")),
        ("20,00$ à 22,00$",          ("hourly",  20,    22,     "USD")),
        ("21,17$ per hour" ,         ("hourly",  21.17, None,   "USD")),
        ("$21,17 par heure",         ("hourly",  21.17, None,   "USD")),
        ("25,00$ par heure",         ("hourly",  25,    None,   "USD")),
        ("18$ et 32$",               ("hourly",  18,    32,     "USD")),
    ],
)
def test_extract_salary_common_formats(salary_str, expected):
    assert parse.salary.transform(salary_str) == expected


@pytest.mark.parametrize(
    "salary_str, expected",
    [
        ("$22 - $28",       ("hourly",  22 * 2080, 28 * 2080, "USD")),
        ("$4,000 - $5,000", ("monthly", 4000 * 12, 5000 * 12, "USD")),
    ],
)
def test_enforced_annual_salary(salary_str, expected):
    assert parse.salary.transform(salary_str, enforce_annual_salary=True) == expected


def test_k_suffix_applies_per_bound_not_globally():
    # Only min has 'k'; max is already in full dollars.
    assert parse.salary.transform("$85k - $110000") == ("yearly", 85000, 110000, "USD")


@pytest.mark.parametrize(
    "path",
    sorted((Path(__file__).parent / "salary.test").glob("*.txt"), key=lambda p: p.name.lower()),
    ids=lambda p: p.name,
)
def test_jobs_fixtures_roundtrip(path: Path):
    text = path.read_text(encoding="utf-8")

    interval, min_amount, max_amount, currency = parse.salary.transform(text, currency="CAD")
    if interval is None and min_amount is None and max_amount is None and currency is None:
        # Convention: files named like na-*.txt contain no parseable salary.
        assert path.stem.startswith("na-"), f"Unexpected no-salary fixture: {path.name}"
        assert fmt.salary.transform(None, None, None, None) == "N/A"
        return

    assert interval is not None, f"transform() returned None interval for {path.name}"
    assert currency is not None, f"transform() returned None currency for {path.name}"

    formatted = fmt.salary.transform(min_amount, max_amount, currency, interval)
    expected = path.stem
    assert _normalize_salary_string(formatted) == expected
