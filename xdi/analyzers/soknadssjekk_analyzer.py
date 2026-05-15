"""
Søknadssjekk – analyserer om planlagte byggearbeider krever søknad
etter plan- og bygningsloven (PBL), SAK10 og TEK17.
"""
import json
import re
from typing import Optional

import anthropic

SYSTEM = """\
Du er en norsk ekspert på plan- og bygningsloven (PBL), byggesaksforskriften (SAK10) \
og byggteknisk forskrift (TEK17). Du gir presis, strukturert veiledning om \
søknadsplikt for byggearbeider i Norge.

REGELVERKSGRUNNLAG:
1. PBL § 20-1: Tiltak som krever søknad og tillatelse (store byggetiltak)
2. PBL § 20-3: Tiltak som er unntatt krav om ansvarlig foretak (mindre tiltak, men krever søknad)
3. PBL § 20-4: Tiltak som kan utføres uten søknad (ingen søknad nødvendig)
4. SAK10 § 2-1: Tiltak som er unntatt søknadsplikt (vedlikehold, innvendig arbeid m.m.)
5. SAK10 § 4-1: Tiltak som kan utføres uten søknad men med nabovarsel

VIKTIGE KATEGORIER:

KREVER IKKE SØKNAD (vedlikehold/reparasjon):
- Utskifting av armaturer, hvitevarer, innredning
- Maling, tapetsering, flislegging av overflater
- Utskifting av dører/vinduer til tilsvarende (uten endre energi/brann)
- Reparasjon av tak, vegger, gulv (uten endre konstruksjon)

UNNTATT SØKNADSPLIKT MEN TEK17 GJELDER (SAK10 § 2-1):
- Totalrehabilitering av bad/våtrom innenfor én bruksenhet og branncelle
- Skifte av sluk i betongdekke med innstøpt avløpsrør
- Flis/støp/varmekabler lagt oppå betongdekke
- Bytte av vinduer med tilsvarende konstruksjon

KREVER SØKNAD (PBL § 20-3 eller § 20-1):
- Arbeid som bryter brannskille mellom bruksenheter
- Innlemme tilleggsareal (bod/loft) i boenheten
- Fasadeendringer som endrer bygningens karakter
- Tilbygg, påbygg, underbygg
- Ny garasje/uthus
- Endre bruk av rom (f.eks. bod til soverom)
- Riving av bærende konstruksjoner
- Ny rørføring mellom boenheter/brannceller
- Skifte av sluk i tredekkekonstruksjon mellom boenheter

ALLTID GJELDENDE:
- TEK17 krav til luftkvalitet, energi, universell utforming, brannsikkerhet
- Kommunale reguleringsplaner kan stille strengere krav
- Vernede bygg: kontakt Riksantikvaren/fylkeskommune

SVAR ALLTID med gyldig JSON uten markdown-kodeblokk.
"""

PROMPT_TMPL = """\
Analyser disse planlagte byggearbeidene og vurder søknadsplikt:

PLANLAGTE ARBEIDER:
{beskrivelse}
{adresse_linje}

Returner JSON med denne strukturen:
{{
  "adresse": null,
  "sammendrag": "Kort oppsummering av vurderingen (2-3 setninger)",
  "arbeid": [
    {{
      "tittel": "Kort navn på arbeidet",
      "soknadsplikt": "nei" | "ja" | "mulig",
      "kortforklaring": "Én setning",
      "begrunnelse": "Detaljert forklaring inkl. lovhenvisning",
      "grunnlag": ["PBL § 20-4", "SAK10 § 2-1"],
      "tek17_krav": ["TEK17 § 14-2 energikrav gjelder", "..."],
      "unntak": "Beskriver eventuelle unntak eller forutsetninger",
      "anbefaling": "Praktisk anbefaling til huseier"
    }}
  ],
  "usikkerhet": "Hva er usikkert og bør avklares med kommunen",
  "disclaimer": "Veiledningen er ikke juridisk rådgivning. Kontakt kommunen for bindende svar."
}}

Skill opp i separate arbeidsposter hvis beskrivelsen inneholder flere typer arbeid.
soknadsplikt = "nei" (ikke søknadspliktig), "ja" (søknadspliktig), "mulig" (avhenger av forhold).
"""


class SoknadssjekKAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(self, beskrivelse: str, adresse: Optional[str] = None) -> dict:
        adresse_linje = f"ADRESSE: {adresse}" if adresse else ""
        prompt = PROMPT_TMPL.format(
            beskrivelse=beskrivelse.strip(),
            adresse_linje=adresse_linje,
        )

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}},
                ],
            }],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: wrap raw text
            data = {
                "sammendrag": "Kunne ikke parse JSON-svar.",
                "arbeid": [],
                "raw": raw,
                "disclaimer": "Se råtekst for analyse.",
            }

        if adresse and not data.get("adresse"):
            data["adresse"] = adresse

        return data
