#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================


import re

# ordered patterns (priority: executive -> senior -> mid -> junior -> entry -> intern)
_LEVEL_FRAGMENTS = {
    "executive": [
        r"cto",
        r"chief technology officer",
        r"vice president",
        r"vp[- ]\w+",
        r"vp of \w+",
        r"head[- ]\w+",
        r"head of \w+",
        r"engineering[- ]director",
        r"managing[- ]director",
        r"directeur[- ]technique",
        r"directeur[- ]ingénierie",
    ],
    "senior": [
        r"s[eé]nior[- ]",
        r"principal[- ]engineer",
        r"ing[eé]nieur[- ]principal",
        r"d[ée]velo[p]+e[u]?r[- ](?:iv|4)",
    ],
    "mid": [
        r"mid[- ]level",
        r"intermediate",
        r"interm[eé]diaire",
        r"\w+e[u]?r confirm[ée]",
        r"d[ée]velo[p]+e[u]?r[- ](?:iii|3)",
    ],
    "junior": [
        r"junior[- ]",
        r"d[ée]velo[p]+e[u]?r[- ](?:ii|2)",
    ],
    "entry": [
        r"entry[- ]",
        r"new[- ]grad\w*",
        r"graduate[- ]\w+",
        r"d[eé]butant",
        r"jeune[- ]dipl[oô]m[eé]",
        r"nouveau[- ]dipl[oô]m[eé]",
        r"premier[- ]emploi",
        r"d[ée]velo[p]+e[u]?r[- ](?:i|1)",
    ],
    "intern": [
        r"intern",
        r"intern[- ]",
        r"internship",
        r"stagiaire",
        r"(?<![-\w])stage",
        r"co[- ]?op",
    ],
}

# ordered patterns (priority: executive -> senior -> mid -> junior -> entry -> intern)
_LEVEL_FRAGMENTS_FULL = {
    "executive": [
        *_LEVEL_FRAGMENTS["executive"],
        r"director",
        r"manager",
        r"head",
    ],
    "senior": [
        *_LEVEL_FRAGMENTS["senior"],
        r"sr[.]?",
        r"s[ée]nior",
        r"experienced",
        r"exp[ée]riment[éed]",
        r"lead",
        r"staff",
        r"principal",
    ],
    "mid": [*_LEVEL_FRAGMENTS["mid"], r"mid"],
    "junior": [
        *_LEVEL_FRAGMENTS["junior"],
        r"associate",
        r"jr[.]?",
        r"junior",
    ],
    "entry": [
        *_LEVEL_FRAGMENTS["entry"],
        r"entry",
    ],
    "intern": [
        *_LEVEL_FRAGMENTS["intern"],
        r"apprentice",
        r"trainee",
    ],
}


def _compile_from_fragments(fragments_dict):
    patterns = []
    for label, frags in fragments_dict.items():
        # join fragments with alternation, ensure grouping and word-boundary outside fragments
        alt = "|".join(frags)
        regex = rf"\b({alt})\b"
        patterns.append((re.compile(regex, re.I), label))
    return patterns


_LEVEL_PATTERNS = _compile_from_fragments(_LEVEL_FRAGMENTS)
_LEVEL_PATTERNS_FULL = _compile_from_fragments(_LEVEL_FRAGMENTS_FULL)


def transform(text: str, all: bool = False) -> str:
    text = (text or "").lower()
    patterns = _LEVEL_PATTERNS_FULL if all else _LEVEL_PATTERNS
    for pattern, label in patterns:
        if pattern.search(text):
            return label
    return None
