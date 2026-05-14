"""
Byggesjekk
Sammenligner godkjent kommunetegning (PDF/bilde) med nåværende plantegning
(f.eks. fra Finn.no) og identifiserer potensielt ulovlige endringer.
"""
import base64
import io
import json
import re
from typing import Optional

import anthropic

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

COMPLIANCE_PROMPT = """\
Du er en norsk byggesaksekspert med god kjennskap til plan- og bygningsloven (PBL).

Du får se TO plantegninger:
- Bilde 1: GODKJENT TEGNING fra kommunen (det som er lovlig godkjent)
- Bilde 2: NÅVÆRENDE SITUASJON fra boligannonse (Finn.no eller befaring)

Sammenlign dem grundig og identifiser avvik som kan utgjøre ulovlige tiltak.

Se spesielt etter:
1. Nye rom som ikke finnes i godkjent plan (ulovlig tilbygg/bruksendring)
2. Bruksendring: kjeller/bod/garasje omgjort til soverom/stue/bad
3. Nye våtrom (bad, vaskerom) – krever søknad etter PBL § 20-1
4. Vesentlige arealendringer (> 10 % av romstørrelse)
5. Sammenslåing/fjerning av rom (kan påvirke bærende konstruksjoner)
6. Ny/endret veranda, terrasse eller balkong over 15 m²
7. Endret fasade eller takform synlig

For hvert funn: vurder alvorlighetsgrad etter PBL:
- HØY: klart søknadspliktig, potensielt ulovlig oppført tiltak
- MIDDELS: mulig søknadspliktig, bør undersøkes nærmere
- LAV: trolig ikke søknadspliktig, men bør avklares

Returner KUN gyldig JSON uten markdown:
{
  "risiko_totalt": "HØY|MIDDELS|LAV|INGEN",
  "sammendrag": "2-3 setninger om de viktigste funnene",
  "funn": [
    {
      "type": "Bruksendring kjeller",
      "beskrivelse": "Kjeller fremstår som innredet soverom i annonsen, ikke synlig i godkjent plan",
      "risiko": "HØY",
      "pbl_paragraf": "§ 20-1 bokstav d",
      "handling": "Be om dokumentasjon på søknad og tillatelse for bruksendring"
    }
  ],
  "anbefaling": "Samlet anbefaling til kjøper eller megler",
  "usikkerhet": "Beskriv eventuelle usikkerheter i analysen"
}\
"""


class ComplianceChecker:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def check(
        self,
        approved_bytes: bytes,
        approved_type: str,
        current_bytes: bytes,
        current_type: str,
        address: Optional[str] = None,
    ) -> dict:
        approved_b64 = self._to_image_b64(approved_bytes, approved_type)
        approved_mime = "image/png" if approved_type == "application/pdf" else approved_type

        current_b64 = self._to_image_b64(current_bytes, current_type)
        current_mime = "image/png" if current_type == "application/pdf" else current_type

        user_text = "Sammenlign de to plantegningene og returner JSON med alle funn."
        if address:
            user_text = f"Adresse: {address}\n{user_text}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": COMPLIANCE_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {"type": "text", "text": "BILDE 1 – GODKJENT TEGNING (fra kommunen):"},
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": approved_mime, "data": approved_b64},
                    },
                    {"type": "text", "text": "BILDE 2 – NÅVÆRENDE SITUASJON (fra Finn.no/befaring):"},
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": current_mime, "data": current_b64},
                    },
                    {"type": "text", "text": user_text},
                ],
            }],
        )

        raw = response.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)

    def _to_image_b64(self, data: bytes, mime: str) -> str:
        if mime == "application/pdf" and HAS_PDF:
            data = self._pdf_to_png(data)
        return base64.standard_b64encode(data).decode()

    def _pdf_to_png(self, pdf_bytes: bytes) -> bytes:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page = pdf.pages[0]
            img  = page.to_image(resolution=200)
            buf  = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
