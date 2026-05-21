"""
XDi Validator
Validerer SlimBIM JSON-dokumenter mot schema
"""
import json
from pathlib import Path
from typing import Any

import jsonschema

# Last schema – kopiert inn i xdi/ slik at det er med i Docker-imaget
_SCHEMA_PATH = Path(__file__).parent.parent / "slimbim-schema.json"


def load_schema() -> dict:
    if _SCHEMA_PATH.exists():
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    # Fallback: minimal inline-schema
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["slimbim_version", "property"],
        "properties": {
            "slimbim_version": {"type": "string"},
            "property": {"type": "object"},
        },
    }


_SCHEMA = load_schema()


def validate_slimbim(doc: Any) -> list[str]:
    """
    Valider et SlimBIM-dokument.
    Returnerer tom liste hvis gyldig, ellers liste med feilmeldinger.
    """
    if hasattr(doc, "model_dump"):
        data = doc.model_dump()
    elif isinstance(doc, dict):
        data = doc
    else:
        return ["Ugyldig type – forventet dict eller SlimBIMDocument"]

    errors = []
    validator = jsonschema.Draft7Validator(_SCHEMA)
    for err in validator.iter_errors(data):
        errors.append(f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}")

    return errors
