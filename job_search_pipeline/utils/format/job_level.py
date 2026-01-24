#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================


import re

# ordered patterns (priority: executive -> senior -> mid -> junior -> entry -> intern)
_LEVEL_PATTERNS = [
    (re.compile(r"\b(cto|chief technology officer|vp|vice[- ]?president|head of|director|managing director|engineering manager|head of engineering|chief architect|directeur|directrice|direction|responsable|responsable technique|responsable ingénierie|chef)\b", re.I), "executive"),
    (re.compile(r"\b(senior|sr\.?|s[eé]nior|lead|tech lead|technical lead|principal|staff|senior staff|architect|software architect|expert|distinguished|expertise|architecte|architecte logiciel|ing[eè]nieur principal|exp[eé]riment\w*|tr[eè]s expériment\w*)\b", re.I), "senior"),
    (re.compile(r"\b(mid|mid[- ]?level|intermediate|experienced|3\+\s*years|4\+\s*years|interm[eé]diaire|confirm\w*|autonome)\b", re.I), "mid"),
    (re.compile(r"\b(junior|jr\.?|associate|profil junior)\b", re.I), "junior"),
    (re.compile(r"\b(new[- ]grad|graduate|entry[- ]?level|junior entry|beginner|no experience|d[eé]butant|debutant|jeune[- ]dipl[oô]m\w*|nouveau[- ]dipl[oô]m\w*|premier emploi)\b", re.I), "entry"),
    (re.compile(r"\b(intern|internship|trainee|apprentice|apprenticeship|co-?op|coop|placement|stagiaire|stage|alternant|alternance|apprenti|apprentissage)\b", re.I), "intern"),
]

def infer_level_from_text(text: str) -> str:
    text = (text or "").lower()
    for pattern, label in _LEVEL_PATTERNS:
        if pattern.search(text):
            return label
    return None

def transform(title: str, description: str) -> str:
    level = infer_level_from_text(title)
    if not level:
        level = infer_level_from_text(description)
    return level if level else "N/A"
