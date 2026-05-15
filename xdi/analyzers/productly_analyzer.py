"""
Productly – kobler bygningsdata til faktiske produkter og FDV-informasjon.
Genererer produktspesifikasjoner og vedlikeholdsplaner fra romplan og bygningstype.
"""
import json
import re
from typing import Optional

import anthropic

SYSTEM = """\
Du er en norsk bygningsingeniør og FDV-spesialist (Forvaltning, Drift og Vedlikehold) \
med ekspertise på norske byggestandarder, produktspesifikasjoner og vedlikeholdsintervaller.

Du kobler bygningsdata til konkrete produkter og materialer basert på:
- Byggeår og typiske norske materialer for den perioden
- Bygningstype og bruk
- Gjeldende krav: TEK17, Byggforsk (SINTEF) anbefalinger
- Typiske norske leverandører: Gyproc, Weber, Hunton, Isover, Mapei, Müller, Nordan

FDV-KUNNSKAP:
- Membran/tett sjikt: skiftes normalt hvert 20-30 år
- Utvendig kledning: maling hvert 8-12 år, skifte hvert 30-50 år
- Fliser/fuger bad: fuger tettes hvert 5-8 år
- Vinduer tre: maling hvert 10-12 år, tetting hvert 5 år
- Ventilasjon: filterskift 2x/år, service hvert 5 år
- Røranlegg plast: levetid 50+ år, kontroll hvert 10 år
- Elektrisk: gjennomgang hvert 10-15 år

PRODUKTKATEGORIER:
- Yttervegger: isolasjon, vindsperre, kledning, vinduer, dørpartier
- Innervegger: gipsplater, lydisolasjon, stendertyper
- Gulv: underlag, bjelker/betong, gulvbelegg
- Tak: takstein/-papp, lekter, undertak, isolasjon
- Våtrom: membran, flisklister, fliser, sluk, armatur
- VVS: rørtyper, ventil-typer, radiatortyper
- Elektro: sikringsskap, kabeltyper, stikkontaktnorm
"""

PROMPT = """\
Generer en komplett produktspesifikasjon og FDV-register for denne bygningen.

Bygningsinfo:
{bygningsinfo}

For hvert rom og konstruksjonselement, spesifiser:
1. Sannsynlige produkter/materialer (basert på byggeår og type)
2. Tekniske spesifikasjoner
3. Vedlikeholdsintervall og neste planlagte vedlikehold
4. Estimert restlevetid
5. Anbefalte norske leverandører/merker

Returner KUN gyldig JSON uten markdown:
{{
  "adresse": null,
  "byggeaar": null,
  "bygningstype": null,
  "sist_oppdatert": null,
  "konstruksjon": {{
    "yttervegg": {{
      "type": null,
      "isolasjon": null,
      "kledning": null,
      "u_verdi": null,
      "vedlikehold": []
    }},
    "tak": {{
      "type": null,
      "materiale": null,
      "isolasjon": null,
      "vedlikehold": []
    }},
    "gulv": {{
      "type": null,
      "materiale": null,
      "vedlikehold": []
    }}
  }},
  "rom": [
    {{
      "navn": null,
      "type": null,
      "produkter": [
        {{
          "kategori": null,
          "beskrivelse": null,
          "leverandor": null,
          "installert_aar": null,
          "levetid_aar": null,
          "neste_vedlikehold": null,
          "vedlikeholdsintervall": null
        }}
      ]
    }}
  ],
  "vvs": {{
    "rorsystem": null,
    "varmesystem": null,
    "ventilasjon": null,
    "vedlikehold": []
  }},
  "elektro": {{
    "sikringsskap": null,
    "norm": null,
    "vedlikehold": []
  }},
  "neste_tiltak": [
    {{
      "prioritet": "HOY|MIDDELS|LAV",
      "tiltak": null,
      "anbefalt_aar": null,
      "estimert_kostnad_nok": null
    }}
  ],
  "merknad": null
}}
"""


class ProductlyAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(
        self,
        address: Optional[str] = None,
        byggeaar: Optional[int] = None,
        bygningstype: Optional[str] = None,
        etasjer: Optional[int] = None,
        bra_m2: Optional[float] = None,
        rom: Optional[list] = None,
        tilstand: Optional[str] = None,
    ) -> dict:
        info_parts = []
        if address:       info_parts.append(f"Adresse: {address}")
        if byggeaar:      info_parts.append(f"Byggeår: {byggeaar}")
        if bygningstype:  info_parts.append(f"Bygningstype: {bygningstype}")
        if etasjer:       info_parts.append(f"Etasjer: {etasjer}")
        if bra_m2:        info_parts.append(f"BRA: {bra_m2} m²")
        if tilstand:      info_parts.append(f"Tilstand: {tilstand}")
        if rom:           info_parts.append(f"Rom: {', '.join(str(r) for r in rom)}")

        bygningsinfo = "\n".join(info_parts) if info_parts else "Ukjent – gjør generelle antagelser for norsk enebolig 1980-tall"

        prompt = PROMPT.format(bygningsinfo=bygningsinfo)

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
            m = re.search(r'\{[\s\S]+\}', raw)
            data = json.loads(m.group()) if m else {"raw": raw}

        if address and not data.get("adresse"):
            data["adresse"] = address

        return data
