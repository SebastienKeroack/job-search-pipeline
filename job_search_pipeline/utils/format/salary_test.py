#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import pytest

from job_search_pipeline.utils.format.salary import transform


@pytest.mark.parametrize(
    "args, expected",
    [
        ((None,    None,  None,  None  ), "N/A"),
        ((None,    None,  None,  None  ), "N/A"),
        (("",      "",    None,  None  ), "N/A"),
        (("abc",   "def", None,  None  ), "N/A"),
        (("nan",   "nan", None,  None  ), "N/A"),
        ((80000,   None,  None,  None  ), "80,000"),
        ((None,    95000, None,  None  ), "95,000"),
        ((80000,   95000, None,  None  ), "80,000-95,000"),
        ((80000,   80000, None,  None  ), "80,000"),
        ((80000,   95000, "CAD", None  ), "CAD 80,000-95,000"),
        ((80000,   95000, None,  "year"), "80,000-95,000 / year"),
        ((80000,   95000, "CAD", "year"), "CAD 80,000-95,000 / year"),
        # Rounds to 0 decimals
        ((20.37,   None,  None,  "hour"), "20 / hour"),
        (("21.17", None,  "CAD", "hour"), "CAD 21 / hour"),
        # Interval or currency set to N/A should not appear
        ((80000,   None,  "N/A", "year"), "80,000 / year"),
        ((80000,   None,  "CAD", "N/A" ), "CAD 80,000"),
    ],
)
def test_format_salary(args, expected):
    assert transform(*args) == expected
