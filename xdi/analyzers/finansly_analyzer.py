"""
Finansly – genererer profesjonell eiendomsdokumentasjon for bank og finansiering.
Tar inn plantegning(er) + bygningsinformasjon og returnerer strukturert JSON.
"""
import base64
import json
import re
from typing import Optional

import anthropic

SYSTEM = """\
Du er en erfaren norsk takstmann og eiendomsmegler med spesialisering i \
verdivurdering, arealberegning (NS 3940) og bankdokumentasjon. Du er nøyaktig, \
strukturert og markerer tydelig usikkerhet der den finnes.

AREALBEREGNING (NS 3940):
- BRA (bruksareal): innvendig nettoareal til innside av yttervegg
- Takhøyde ≥ 1.90 m er krav for å inkluderes i BRA
- P-ROM: primærrom = BRA minus boder og sekundærarealer
- BYA: bebygd areal inkl. yttervegger (fotavtrykk)
- Oppgi alltid usikkerhetsspenn (min/max BRA) basert på bildekvalitet

VERDIVURDERING – METODIKK:
- Bruker kvadratmeterpris som er relevant for bygningstype og tilstand
- Norske snitt 2024/2025 (per m² BRA):
  * Enebolig god stand, urbant: 45 000–80 000 kr/m²
  * Enebolig middels, distrikt: 25 000–50 000 kr/m²
  * Leilighet sentral: 60 000–120 000 kr/m²
  * Hytte/fritid god: 35 000–60 000 kr/m²
  * Næringsbygg: avhenger sterkt av beliggenhet og leieinntekter
- Tilstandsgrad (TG 0–3) etter NS 3600 påvirker verdi:
  * TG 0 (ny/god): full markedsverdi
  * TG 1 (normal slitasje): -5 til -10%
  * TG 2 (behov for utbedring): -10 til -25%
  * TG 3 (alvorlige feil): -25% eller mer

BANKDOKUMENTASJON – STANDARD INNHOLD:
1. Bekreftet arealdata (BRA, soverom, bad)
2. Bygningsår og konstruksjonstype
3. Tilstandsvurdering
4. Estimert markedsverdi (fra-til)
5. Usikre punkter som bør avklares
6. Anbefalt oppfølging (takstmann, tilstandsrapport, etc.)

DOKUMENTASJONSKVALITET-SCORE (0.0–1.0):
- 1.0: Målsatte tegninger, fullstendig informasjon, god bildekvalitet
- 0.8: God tegning men mangler noe informasjon
- 0.6: Skisse/mangelfulle mål, usikre arealberegninger
- 0.4: Dårlig bildekvalitet, minimalt grunnlag
- Under 0.4: Utilstrekkelig grunnlag for bankdokumentasjon

SVAR ALLTID med gyldig JSON uten markdown-kodeblokk.
"""

PROMPT_TMPL = """\
Generer profesjonell eiendomsdokumentasjon for bank basert på plantegning og \
bygningsinformasjon.

ADRESSE: {adresse}
BYGGEÅR: {year}
BYGNINGSTYPE: {bygningstype}
TILSTAND: {tilstand}

{bilde_info}

Analyser plantegningen og ekstraher:
1. Romplan: alle rom med navn, type og estimert areal
2. Total BRA og usikkerhetsspenn (min/max)
3. Antall soverom og bad
4. Dokumentasjonskvalitet (er det målsatte tegninger?)
5. Estimert markedsverdi basert på kjent informasjon

Returner KUN gyldig JSON uten markdown:
{{
  "adresse": "{adresse}",
  "bygningstype": "{bygningstype}",
  "byggeaar": {year_val},
  "bra_m2": 0.0,
  "bra_range": {{"min": 0.0, "max": 0.0}},
  "rom_antall": 0,
  "soverom": 0,
  "bad": 0,
  "rom": [
    {{
      "navn": "Stue",
      "type": "living_room",
      "areal_m2": 0.0,
      "etasje": 1
    }}
  ],
  "dokumentasjonskvalitet": {{
    "score": 0.0,
    "nivaa": "høy|middels|lav",
    "mangler": ["liste over manglende informasjon"]
  }},
  "tilstand": {{
    "vurdering": "god|middels|usikker",
    "kommentar": "Kommentar til tilstand basert på tilgjengelig informasjon"
  }},
  "estimert_verdi": {{
    "fra": 0,
    "til": 0,
    "per_m2": 0,
    "metodikk": "Kort beskrivelse av verdivurderingsmetodikken brukt"
  }},
  "bankdokumentasjon": {{
    "bekreftede_fakta": ["faktum 1", "faktum 2"],
    "usikre_punkter": ["usikkert punkt 1"],
    "anbefalt_oppfolging": ["anbefaling 1", "anbefaling 2"]
  }},
  "disclaimer": "Estimater er basert på AI-analyse og er ikke bindende verdivurdering. Kontakt godkjent takstmann for offisiell takst."
}}
"""


class FinanslyAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(
        self,
        image_bytes: bytes,
        media_type: str,
        address: str,
        year: Optional[str],
        bygningstype: str,
        tilstand: str,
    ) -> dict:
        b64 = base64.standard_b64encode(image_bytes).decode()

        year_val = year if year else "null"
        bilde_info = "PLANTEGNING VEDLAGT – analyser romplan og mål."

        prompt = PROMPT_TMPL.format(
            adresse=address.strip() if address else "Ikke oppgitt",
            year=year if year else "Ukjent",
            year_val=year_val,
            bygningstype=bygningstype.strip(),
            tilstand=tilstand.strip(),
            bilde_info=bilde_info,
        )

        user_parts = [
            {"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}},
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": b64},
            },
            {"type": "text", "text": "Analyser plantegningen og returner JSON."},
        ]

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM,
            messages=[{"role": "user", "content": user_parts}],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r'\{[\s\S]+\}', raw)
            if m:
                data = json.loads(m.group())
            else:
                raise

        # Ensure required fields
        data.setdefault("adresse", address)
        data.setdefault("bygningstype", bygningstype)
        data.setdefault("disclaimer",
            "Estimater er basert på AI-analyse og er ikke bindende verdivurdering. "
            "Kontakt godkjent takstmann for offisiell takst.")

        # Sort rooms by area if present
        if data.get("rom"):
            data["rom"] = sorted(data["rom"], key=lambda r: r.get("areal_m2", 0), reverse=True)

        return data
