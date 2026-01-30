#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================


import pytest
from pathlib import Path

from job_search_pipeline.utils.parse.job_level import transform


INTERN_KEYWORDS = {
    # EN
    "intern",
    "internship",
    "co-op",
    "coop",
    # FR
    "stage",
    "stagiaire",
    "coop étudiant",
    "co-op étudiant",
}

ENTRY_KEYWORDS = {
    # EN
    "entry level",
    "entry-level",
    "new grad",
    "new graduate",
    "graduate role",
    "graduate program",
    # FR
    "débutant",
    "debutant",
    "jeune diplômé",
    "jeune diplome",
    "nouveau diplômé",
    "nouveau diplome",
    "premier emploi",
}

JUNIOR_KEYWORDS = {
    # EN
    "junior",
    "junior level",
    "junior-level",
    # FR
    "junior",
}

MID_KEYWORDS = {
    # EN
    "mid level",
    "mid-level",
    "intermediate level",
    # FR
    "intermédiaire",
    "intermediaire",
}

SENIOR_KEYWORDS = {
    # EN
    "senior",
    "senior level",
    "senior-level",
    "principal engineer",
    "staff engineer",
    # FR
    "sénior",
    "senior",
    "ingénieur principal",
}

EXECUTIVE_KEYWORDS = {
    # EN
    "cto",
    "chief technology officer",
    "vice president",
    "vp engineering",
    "head of engineering",
    "engineering director",
    "managing director",
    # FR
    "directeur technique",
    "directeur ingénierie",
    "cto",
}


@pytest.mark.parametrize("kw", sorted(INTERN_KEYWORDS))
def test_intern_keywords_map(kw: str):
    assert transform(kw, True) == "intern"


@pytest.mark.parametrize("kw", sorted(ENTRY_KEYWORDS))
def test_entry_keywords_map(kw: str):
    assert transform(kw, True) == "entry"


@pytest.mark.parametrize("kw", sorted(JUNIOR_KEYWORDS))
def test_junior_keywords_map(kw: str):
    assert transform(kw, True) == "junior"


@pytest.mark.parametrize("kw", sorted(MID_KEYWORDS))
def test_mid_keywords_map(kw: str):
    assert transform(kw, True) == "mid"


@pytest.mark.parametrize("kw", sorted(SENIOR_KEYWORDS))
def test_senior_keywords_map(kw: str):
    assert transform(kw, True) == "senior"


@pytest.mark.parametrize("kw", sorted(EXECUTIVE_KEYWORDS))
def test_executive_keywords_map(kw: str):
    assert transform(kw, True) == "executive"


@pytest.mark.parametrize(
    "title,expected",
    [
        pytest.param("Senior Software Engineer", "senior"),
        pytest.param("Junior Developer", "junior"),
        pytest.param("Lead Data Scientist", "senior"),
        pytest.param("Intern", "intern"),
        pytest.param("VP of Engineering", "executive"),
        pytest.param("Software Engineer", None),
    ],
)
def test_transform_title_levels(title: str, expected: str):
    assert transform(title, True) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        pytest.param("Sr. Software Engineer", "senior"),
        pytest.param("Sr Software Engineer", "senior"),
        pytest.param("SENIOR SOFTWARE ENGINEER", "senior"),
        pytest.param("Principal Engineer", "senior"),
        pytest.param("Staff Engineer", "senior"),
        pytest.param("Chief Technology Officer", "executive"),
        pytest.param("CTO", "executive"),
        pytest.param("Vice President of Engineering", "executive"),
        pytest.param("jr. backend developer", "junior"),
        pytest.param("Entry Level QA", "entry"),
        pytest.param("Mid-Level Developer", "mid"),
        pytest.param("Intermediate Data Engineer", "mid"),
    ],
)
def test_transform_edge_cases_and_variations(title: str, expected: str):
    assert transform(title, True) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        pytest.param("Ingénieur stagiaire", "intern"),
        pytest.param("Early-stage - Développeur", None),
        pytest.param("Stage - Développeur", "intern"),
        pytest.param("Développeur débutant", "entry"),
        pytest.param("Software Developer I", "entry"),
        pytest.param("Nouveau diplômé Développeur", "entry"),
        pytest.param("Développeur junior", "junior"),
        pytest.param("Développeur confirmé", "mid"),
        pytest.param("Ingénieur intermédiaire", "mid"),
        pytest.param("Développeur sénior", "senior"),
        pytest.param("Développeur expérimenté", "senior"),
        pytest.param("Directeur technique", "executive"),
    ],
)
def test_transform_french_levels(title: str, expected: str):
    assert transform(title, True) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        pytest.param("Staff Software Engineer", "senior"),
        pytest.param("Senior Staff Engineer", "senior"),
        pytest.param("Principal Architect", "senior"),
        pytest.param("Tech Lead Backend", "senior"),
        pytest.param("Engineering Manager", "executive"),
        pytest.param("Head of Data", "executive"),
        pytest.param("Lead Developer", "senior"),
        pytest.param("Jeune diplômé développeur", "entry"),
        pytest.param("Développeur confirmé", "mid"),
    ],
)
def test_transform_extended_matrix(title: str, expected: str):
    assert transform(title, True) == expected


@pytest.mark.parametrize(
    "path",
    sorted(
        (Path(__file__).parent / ".test-files").glob("*.txt"),
        key=lambda p: str(getattr(p, "name")).lower(),
    ),
    ids=lambda p: p.name,
)
def test_job_level_from_files(path: Path):
    # Filename convention: <level>-<n>.txt e.g. mid-0.txt
    text = path.read_text(encoding="utf-8")
    stem = path.stem.split("-")[0]
    expected_level = None if stem.startswith("na") else stem.lower()
    assert transform(text) == expected_level
