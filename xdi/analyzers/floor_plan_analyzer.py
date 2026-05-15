"""
Romplan-analyse
Tar inn ett bilde eller én PDF → returnerer BRA, romplan, kalkyle.
Følger NS 3940 / TEK17 for BRA-beregning.
"""
import base64
import json
import re
from typing import Optional

import anthropic

SYSTEM = """\
Du er en erfaren norsk takstmann og bygningsingeniør med spesialisering på arealberegning \
etter NS 3940 og TEK17. Du er presist og metodisk, og oppgir alltid estimert usikkerhet \
på arealberegninger.

REGLER FOR BRA-BEREGNING (NS 3940):
- BRA (bruksareal) = innvendig nettoareal, målt til innside av yttervegg
- Inkluderer: alle rom med takhøyde ≥ 1.90 m (inkl. bad, gang, bod, kjøkken, stue, sov)
- Ekskluderer: rom under 1.90 m høyde, tekniske rom, åpne altaner/terrasser
- Trapperom og heissjakt inkluderes på hver etasje
- Skillevegger inkluderes i BRA
- P-ROM (primærrom) = BRA minus bodens/forradenes areal
- BYA (bebygd areal) = fotavtrykk inkl. yttervegger
- Dersom tegningen har målsatte mål: bruk disse direkte
- Dersom ingen mål: estimer basert på proporsjoner og typiske romstørrelser

METODIKK:
1. Identifiser alle rom med navn og type
2. Estimer hvert roms areal basert på synlige mål eller proporsjoner
3. Summer til total BRA per etasje og totalt
4. Oppgi confidence (0.6-1.0) basert på målkvalitet

TYPISKE ROMSTØRRELSER (bruk som referanse ved usikkerhet):
- Bad/WC: 3-8 m²
- Soverom: 8-16 m²
- Stue: 20-35 m²
- Kjøkken: 10-20 m²
- Gang/hall: 5-15 m²
- Bod: 2-5 m²
"""

PROMPT = """\
Analyser denne plantegningen nøyaktig etter NS 3940.

Ekstraher ALL synlig informasjon:
- Adresse (hvis synlig)
- Bygningstype
- Antall etasjer
- Hvert enkelt rom: navn, type, estimert areal (m²), etasje, målkvalitet
- Total BRA = sum av alle rom med takhøyde ≥ 1.90 m
- BYA = fotavtrykk inkl. yttervegger (estimer ut fra proporsjoner)
- Antall soverom og bad
- Eventuelle arealer under 1.90 m (knevegg etc.)

Dersom tegningen har målsatte mål (mm eller m): bruk disse, de er autoritative.
Dersom ingen mål: estimer basert på proporsjoner og typiske norske romstørrelser.

Returner KUN gyldig JSON uten markdown eller kodeblokk:
{
  "adresse": null,
  "bygningstype": "enebolig|rekkehus|leilighet|tomannsbolig|hytte|annet",
  "etasjer": 1,
  "bra_total_m2": 0.0,
  "bya_m2": null,
  "soverom": 0,
  "bad": 0,
  "rom": [
    {
      "navn": "Stue",
      "type": "living_room",
      "areal_m2": 0.0,
      "etasje": 1,
      "mal_kvalitet": "eksakt|estimert|usikkert"
    }
  ],
  "har_malsatte_mal": false,
  "bra_under_190cm_m2": null,
  "merknad": null,
  "confidence": 0.8
}

Rom-typer å bruke: living_room, kitchen, bedroom, bathroom, toilet, hallway,
utility, storage, garage, office, dining_room, technical
"""


class FloorPlanAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(
        self,
        image_bytes: bytes,
        media_type: str = "image/jpeg",
        address: Optional[str] = None,
    ) -> dict:
        b64 = base64.standard_b64encode(image_bytes).decode()

        user_parts = [
            {"type": "text", "text": PROMPT, "cache_control": {"type": "ephemeral"}},
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
        ]
        if address:
            user_parts.append({"type": "text", "text": f"Adresse: {address}"})
        user_parts.append({"type": "text", "text": "Analyser plantegningen og returner JSON."})

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=SYSTEM,
            messages=[{"role": "user", "content": user_parts}],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Extract JSON block if surrounded by text
            m = re.search(r'\{[\s\S]+\}', raw)
            if m:
                data = json.loads(m.group())
            else:
                raise

        # Sort rooms by area descending for better readability
        if data.get("rom"):
            data["rom"] = sorted(data["rom"], key=lambda r: r.get("areal_m2", 0), reverse=True)

        data["kalkyle"] = self._kalkyle(data)
        return data

    def _kalkyle(self, data: dict) -> dict:
        bra = data.get("bra_total_m2") or 0
        conf = data.get("confidence", 0.8)
        # Confidence-adjusted range
        margin = round(bra * (1 - conf) * 0.5, 1)
        return {
            "bra_m2":          round(bra, 1),
            "bra_min_m2":      round(bra - margin, 1) if margin else None,
            "bra_max_m2":      round(bra + margin, 1) if margin else None,
            "soverom":         data.get("soverom", 0),
            "bad":             data.get("bad", 0),
            "estimert_verdi_nok": int(bra * 55_000) if bra > 0 else None,
            "confidence":      conf,
            "merknad_verdi":   "Grovt estimat 55 000 kr/m² – avhenger sterkt av beliggenhet og standard",
        }
