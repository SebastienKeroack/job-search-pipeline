#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import importlib.util
from pathlib import Path
import re

import pytest


_SALARY_PY = Path(__file__).with_name("salary.py")
_spec = importlib.util.spec_from_file_location("salary", _SALARY_PY)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load salary module from {_SALARY_PY}")
salary = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(salary)
extract_salary = salary.extract_salary
format_salary = salary._format_salary


@pytest.mark.parametrize("salary_str", [None, ""])
def test_empty_input_returns_nones(salary_str):
    assert extract_salary(salary_str) == (None, None, None, None)


@pytest.mark.parametrize(
    "salary_str, expected",
    [
        ("$85,000 - $110,000", ("yearly", 85000, 110000, "CAD")),
        ("$85k–110k", ("yearly", 85000, 110000, "CAD")),
        ("85 000,00$ à 110 000,00$", ("yearly", 85000, 110000, "CAD")),
        ("$22 - $28", ("hourly", 22, 28, "CAD")),
        ("$4,000 - $5,000", ("monthly", 4000, 5000, "CAD")),
        ("20,00$ à 22,00$", ("hourly", 20, 22, "CAD")),
        ("21,17$ per hour", ("hourly", 21.17, None, "CAD")),
        ("$21,17 par heure", ("hourly", 21.17, None, "CAD")),
        ("25,00$ par heure", ("hourly", 25, None, "CAD")),
        ("18$ et 32$", ("hourly", 18, 32, "CAD")),
    ],
)
def test_extract_salary_common_formats(salary_str, expected):
    assert extract_salary(salary_str) == expected


@pytest.mark.parametrize(
    "salary_str, expected",
    [
        ("$22 - $28", ("hourly", 22 * 2080, 28 * 2080, "CAD")),
        ("$4,000 - $5,000", ("monthly", 4000 * 12, 5000 * 12, "CAD")),
    ],
)
def test_enforced_annual_salary(salary_str, expected):
    assert extract_salary(salary_str, enforce_annual_salary=True) == expected


def test_k_suffix_applies_per_bound_not_globally():
    # Only min has 'k'; max is already in full dollars.
    assert extract_salary("$85k - $110000") == ("yearly", 85000, 110000, "CAD")

@pytest.mark.parametrize(
    "job, expected",
    [
        ({"min_amount": None,    "max_amount": None,  "currency": None,  "interval": None  }, "N/A"),
        ({"min_amount": None,    "max_amount": None,  "currency": None,  "interval": None  }, "N/A"),
        ({"min_amount": "",      "max_amount": "",    "currency": None,  "interval": None  }, "N/A"),
        ({"min_amount": "abc",   "max_amount": "def", "currency": None,  "interval": None  }, "N/A"),
        ({"min_amount": "nan",   "max_amount": "nan", "currency": None,  "interval": None  }, "N/A"),
        ({"min_amount": 80000,   "max_amount": None,  "currency": None,  "interval": None  }, "80,000"),
        ({"min_amount": None,    "max_amount": 95000, "currency": None,  "interval": None  }, "95,000"),
        ({"min_amount": 80000,   "max_amount": 95000, "currency": None,  "interval": None  }, "80,000-95,000"),
        ({"min_amount": 80000,   "max_amount": 80000, "currency": None,  "interval": None  }, "80,000"),
        ({"min_amount": 80000,   "max_amount": 95000, "currency": "CAD", "interval": None  }, "CAD 80,000-95,000"),
        ({"min_amount": 80000,   "max_amount": 95000, "currency": None,  "interval": "year"}, "80,000-95,000 / year"),
        ({"min_amount": 80000,   "max_amount": 95000, "currency": "CAD", "interval": "year"}, "CAD 80,000-95,000 / year"),
        # Rounds to 0 decimals
        ({"min_amount": 20.37,   "max_amount": None,  "currency": None,  "interval": "hour"}, "20 / hour"),
        ({"min_amount": "21.17", "max_amount": None,  "currency": "CAD", "interval": "hour"}, "CAD 21 / hour"),
        # Interval or currency set to N/A should not appear
        ({"min_amount": 80000,   "max_amount": None,  "currency": "N/A", "interval": "year"}, "80,000 / year"),
        ({"min_amount": 80000,   "max_amount": None,  "currency": "CAD", "interval": "N/A" }, "CAD 80,000"),
    ],
)
def test_format_salary(job, expected):
    assert format_salary(job) == expected


def _normalize_salary_string(s: str) -> str:
    # Filenames don't contain the '/' used by _format_salary (e.g. "CAD 22-23 / hourly").
    # Normalize by removing '/', then collapsing whitespace.
    return re.sub(r"\s+", " ", s.replace("/", " ")).strip()


@pytest.mark.parametrize(
    "path",
    sorted((Path(__file__).parent / "salary").glob("*.txt"), key=lambda p: p.name.lower()),
    ids=lambda p: p.name,
)
def test_jobs_fixtures_roundtrip(path: Path):
    text = path.read_text(encoding="utf-8")

    interval, min_amount, max_amount, currency = extract_salary(text)
    if interval is None and min_amount is None and max_amount is None and currency is None:
        # Convention: files named like na_*.txt contain no parseable salary.
        assert path.stem.lower().startswith("na_"), f"Unexpected no-salary fixture: {path.name}"
        assert format_salary({"min_amount": None, "max_amount": None, "currency": None, "interval": None}) == "N/A"
        return

    assert interval is not None, f"extract_salary() returned None interval for {path.name}"
    assert currency is not None, f"extract_salary() returned None currency for {path.name}"

    job = {
        "min_amount": min_amount,
        "max_amount": max_amount,
        "currency": currency,
        "interval": interval,
    }
    formatted = format_salary(job)

    expected = path.stem
    assert _normalize_salary_string(formatted) == expected