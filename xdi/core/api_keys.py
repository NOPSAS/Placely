"""
Enkel API-nøkkel-validering for Placely-kunder.
Nøkler settes som PLACELY_API_KEYS i Railway-miljøvariabler (kommaseparert).
Ny kunde: generer UUID, legg til i Railway, send til kunden.
"""
import os
import uuid

from fastapi import Header, HTTPException


def _valid_keys() -> set[str]:
    raw = os.environ.get("PLACELY_API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    keys = _valid_keys()
    if not keys:
        # Ingen nøkler konfigurert = åpen tilgang (lokal utvikling)
        return "dev"
    if not x_api_key or x_api_key not in keys:
        raise HTTPException(
            status_code=401,
            detail="Ugyldig eller manglende API-nøkkel. "
                   "Kjøp tilgang på placely.no eller kontakt jakob@tegnebua.no",
        )
    return x_api_key


def generate_key() -> str:
    """Generer en ny nøkkel – kjør én gang per ny kunde."""
    return str(uuid.uuid4())
