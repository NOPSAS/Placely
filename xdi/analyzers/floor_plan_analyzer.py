"""
Romplan-analyse
Tar inn ett bilde eller én PDF → returnerer BRA, romplan, kalkyle.
"""
import base64
import json
import re
from typing import Optional

import anthropic

PROMPT = """\
Du er en norsk takstmann og arkitekt. Analyser denne plantegningen nøyaktig.

Ekstraher ALL synlig informasjon:
- Adresse (hvis synlig på tegningen)
- Bygningstype
- Antall etasjer
- Hvert enkelt rom: navn, type, estimert areal (m²), hvilken etasje
- Total BRA (bruksareal) = sum av alle innvendige rom-arealer
- BYA (bebygd areal) = fotavtrykk inkl. yttervegger
- Antall soverom og bad
- Spesielle rom (kjeller, loft, bod, garasje, terrasse)

Returner KUN gyldig JSON uten markdown:
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
      "etasje": 1
    }
  ],
  "merknad": null,
  "confidence": 0.8
}\
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

        user_text = "Analyser denne plantegningen og returner JSON."
        if address:
            user_text = f"Adresse: {address}\n{user_text}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": b64},
                    },
                    {"type": "text", "text": user_text},
                ],
            }],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)

        # Berik med beregnede felt
        data["kalkyle"] = self._kalkyle(data)
        return data

    def _kalkyle(self, data: dict) -> dict:
        bra = data.get("bra_total_m2") or 0
        return {
            "bra_m2":        round(bra, 1),
            "soverom":       data.get("soverom", 0),
            "bad":           data.get("bad", 0),
            "estimert_verdi_nok": int(bra * 55_000) if bra > 0 else None,
            "merknad_verdi": "Grovt estimat 55 000 kr/m² – avhenger sterkt av beliggenhet",
        }
