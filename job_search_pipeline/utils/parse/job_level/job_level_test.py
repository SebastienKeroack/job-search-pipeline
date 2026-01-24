#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================


import pytest
from pathlib import Path

from job_search_pipeline.utils.parse.job_level import transform


INTERN_KEYWORDS = {
    # EN
    "intern", "internship", "trainee", "apprentice", "apprenticeship",
    "co-op", "coop", "placement",

    # FR
    "stagiaire", "stage", "alternant", "alternance",
    "apprenti", "apprentissage",
}

ENTRY_KEYWORDS = {
    # EN
    "entry level", "entry-level", "graduate", "new grad",
    "beginner", "no experience",

    # FR
    "débutant", "debutant",
    "jeune diplômé", "jeune diplome",
    "nouveau diplômé", "nouveau diplome",
    "premier emploi",
}

JUNIOR_KEYWORDS = {
    # EN
    "junior", "jr", "jr.", "associate",

    # FR
    "junior", "profil junior",
}

MID_KEYWORDS = {
    # EN
    "mid", "mid-level", "intermediate",
    "experienced", "3+ years", "4+ years",

    # FR
    "confirmé", "confirme",
    "intermédiaire", "intermediaire",
    "autonome",
}

SENIOR_KEYWORDS = {
    # EN
    "senior", "sr", "sr.",
    "lead", "tech lead", "technical lead",
    "principal", "staff", "senior staff",
    "architect", "software architect",
    "expert", "distinguished",

    # FR
    "sénior", "senior",
    "lead développeur", "lead dev",
    "expert", "expertise",
    "architecte", "architecte logiciel",
    "ingénieur principal",
    "très expérimenté",
}

EXECUTIVE_KEYWORDS = {
    # EN
    "cto", "chief technology officer",
    "vp", "vice president",
    "head of", "director", "managing director",
    "engineering manager", "head of engineering",
    "chief architect",

    # FR
    "directeur", "direction",
    "responsable technique",
    "responsable ingénierie",
    "head of",
    "cto",
}


@pytest.mark.parametrize("kw", sorted(INTERN_KEYWORDS))
def test_intern_keywords_map(kw: str):
    assert transform(kw) == "intern"


@pytest.mark.parametrize("kw", sorted(ENTRY_KEYWORDS))
def test_entry_keywords_map(kw: str):
    assert transform(kw) == "entry"


@pytest.mark.parametrize("kw", sorted(JUNIOR_KEYWORDS))
def test_junior_keywords_map(kw: str):
    assert transform(kw) == "junior"


@pytest.mark.parametrize("kw", sorted(MID_KEYWORDS))
def test_mid_keywords_map(kw: str):
    assert transform(kw) == "mid"


@pytest.mark.parametrize("kw", sorted(SENIOR_KEYWORDS))
def test_senior_keywords_map(kw: str):
    assert transform(kw) == "senior"


@pytest.mark.parametrize("kw", sorted(EXECUTIVE_KEYWORDS))
def test_executive_keywords_map(kw: str):
    assert transform(kw) == "executive"


@pytest.mark.parametrize(
    "title,expected",
    [
        pytest.param("Senior Software Engineer", "senior"),
        pytest.param("Junior Developer", "junior"),
        pytest.param("Lead Data Scientist", "senior"),
        pytest.param("Intern", "intern"),
        pytest.param("VP of Engineering", "executive"),
        pytest.param("Software Engineer", None),
        pytest.param("Associate Product Manager", "junior"),
    ],
)
def test_transform_title_levels(title: str, expected: str):
    assert transform(title) == expected


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
    assert transform(title) == expected


@pytest.mark.parametrize(
    "title,expected",
    [
        pytest.param("Ingénieur stagiaire", "intern"),
        pytest.param("Stage - Développeur", "intern"),
        pytest.param("Développeur débutant", "entry"),
        pytest.param("Nouveau diplômé Développeur", "entry"),
        pytest.param("Développeur junior", "junior"),
        pytest.param("Développeur confirmé", "mid"),
        pytest.param("Ingénieur intermédiaire", "mid"),
        pytest.param("Développeur sénior", "senior"),
        pytest.param("Développeur expérimenté", "senior"),
        pytest.param("Directeur technique", "executive"),
        pytest.param("Responsable produit", "executive"),
    ],
)
def test_transform_french_levels(title: str, expected: str):
    assert transform(title) == expected


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
        pytest.param("Alternant Développeur", "intern"),
        pytest.param("Apprenti Ingénieur Logiciel", "intern"),
        pytest.param("Jeune diplômé développeur", "entry"),
        pytest.param("Développeur confirmé", "mid"),
    ],
)
def test_transform_extended_matrix(title: str, expected: str):
    assert transform(title) == expected

@pytest.mark.parametrize(
    "path",
    sorted((Path(__file__).parent / "job_level.test").glob("*.txt"), key=lambda p: p.name.lower()),
    ids=lambda p: p.name,
)
def test_job_level_from_files(path: Path):
    # Filename convention: <level>-<n>.txt e.g. mid-0.txt
    text = path.read_text(encoding="utf-8")
    stem = path.stem
    expected_level = None if stem.startswith("na-") else stem.lower()
    assert transform(text) == expected_level

