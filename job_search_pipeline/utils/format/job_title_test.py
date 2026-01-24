#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

import pytest

from job_search_pipeline.utils.format.job_title import transform


@pytest.mark.parametrize(
    "value,gender,expected",
    [
        (
            "Développeuse/Développeur d'applications sénior.e",
            "man",
            "Développeur d'applications sénior",
        ),
        (
            "Développeuse/Développeur d'applications sénior.e",
            "woman",
            "Développeuse d'applications sénior",
        ),
        ("Développeur(euse) Full Stack", "man", "Développeur Full Stack"),
        ("Développeur(euse) Full Stack", "woman", "Développeuse Full Stack"),
        ("Développeur.euse Full Stack", "man", "Développeur Full Stack"),
        ("Développeur.euse Full Stack", "woman", "Développeuse Full Stack"),
        ("Chargé(e) de projet", "man", "Chargé de projet"),
        ("Chargé(e) de projet", "woman", "Chargée de projet"),
        ("Développeur sénior.e", "man", "Développeur sénior"),
    ],
)
def test_inclusive_normalization(value: str, gender: str, expected: str):
    assert transform(value, gender=gender) == expected


def test_does_not_truncate_on_slash_when_not_bilingual():
    # Regression: keep full title when the slash isn't used as a bilingual separator.
    value = "Analyste/Développeur BI"
    assert transform(value, gender="man") == value


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Développeur Python (4 mois)", "Développeur Python"),
        ("Développeur Python [Remote]", "Développeur Python"),
        ("Développeur Python {Contract}", "Développeur Python"),
        ("Dev [Remote] (6 mois)", "Dev"),
    ],
)
def test_trailing_encapsulated_segments_removed(value: str, expected: str):
    assert transform(value, gender="man") == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Programmeur d'outils | Tools Programmer", "Programmeur d'outils"),
        ("Programmeur d'outils / Tools Programmer", "Programmeur d'outils"),
        ("Spécialiste des certifications - Certification Specialist", "Spécialiste des certifications"),
        ("Tools Programmer \\ Programmeur d'outils", "Tools Programmer"),
    ],
)
def test_bilingual_separators_keep_left(value: str, expected: str):
    assert transform(value, gender="man") == expected


def test_removes_trailing_duration_stage_suffix_after_dash():
    value = "Développeur(se) en ingénierie des données – 4 mois Stage/Co-op (Été 2026)"
    assert transform(value, gender="man") == "Développeur en ingénierie des données"


def test_removes_stage_prefix_before_colon():
    value = "Stage coopératif - Été 2026: Développeur(euse) Power Platform (4 mois)"
    assert transform(value, gender="man") == "Développeur Power Platform"


def test_encapsulated_segment_not_removed_in_middle():
    value = "Développeur (Python) Backend"
    assert transform(value, gender="man") == value


def test_empty_returns_na():
    assert transform("", gender="man") == "N/A"


def test_invalid_gender_raises():
    with pytest.raises(NotImplementedError):
        transform("Développeur(euse)", gender="other")
