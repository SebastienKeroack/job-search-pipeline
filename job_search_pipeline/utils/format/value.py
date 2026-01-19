#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

from dataclasses import fields


def na(v, default="N/A"):
    match v:
        case None:
            return default
        case float() as f if f != f:  # NaN
            return default
        case str() as s if not s.strip() or s.lower() == "nan":
            return default
        case _:
            return v


def optional_float(v):
    if v is None:
        return None
    try:
        f = float(v)
        if f != f:  # NaN
            return None
        return f
    except (TypeError, ValueError):
        return None


def repr_dataclass_short(cls) -> str:
    cls_name = cls.__class__.__name__  # <- no "<locals>"
    body = ", ".join(f"{f.name}={getattr(cls, f.name)!r}" for f in fields(cls))
    return f"{cls_name}({body})"
