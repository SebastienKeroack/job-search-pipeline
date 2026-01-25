#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================


import pytest

from job_search_pipeline.utils.format.job_level import transform


@pytest.mark.parametrize(
    "title,description,expected",
    [
        pytest.param("Software Engineer", "We are looking for a Senior candidate.", "senior"),
        pytest.param("Developer", "Entry-level position available.", "entry"),
        pytest.param("Engineer", "This is an internship role.", "intern"),
        pytest.param("Analyst", "Mid-level experience required.", "mid"),
        pytest.param("Designer", "No level specified.", "N/A"),
    ],
)
def test_transform_description_levels(title: str, description: str, expected: str):
    assert transform(title, description) == expected


@pytest.mark.parametrize(
    "title,description,expected",
    [
        pytest.param("Senior Developer", "Entry-level position.", "senior"),
        pytest.param("Intern", "Senior responsibilities.", "intern"),
    ],
)
def test_transform_priority_title_over_description(title: str, description: str, expected: str):
    assert transform(title, description) == expected
