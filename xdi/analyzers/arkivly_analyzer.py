"""
Arkivly – analyserer skannede kommunale arkivdokumenter og historiske byggetegninger.
Ekstraherer bygningsdata fra gamle PDFer, mikrofilm-skann og håndtegnede dokumenter.
"""
import base64
import json
import re
from typing import Optional

import anthropic

SYSTEM = """\
Du er en norsk arkivspesialist og bygningshistoriker med ekspertise på:
- Kommunale byggesaksarkiver (1900–2000-tallet)
- Gamle norske byggetegninger og tegnekonvensjoner
- Historiske arealberegninger og planstandarder
- Håndtegnede arkitekttegninger fra ulike epoker
- Plan- og bygningsloven i historisk kontekst

Du analyserer skannede arkivdokumenter og historiske tegninger for å:
1. Identifisere byggeår, godkjenningsdato og saksbehandler
2. Ekstrahere etasjeplan, rom og mål fra gamle tegninger
3. Identifisere registrerte endringer og tilbygg over tid
4. Avdekke discrepanser mellom godkjent og faktisk bygg
5. Gi historisk kontekst for bygningens utvikling

TEGNEKONVENSJONER:
- Før 1960: Oftest håndtegnet, mål i cm/m, nordpil
- 1960–1990: Letraset-tekst, standardiserte symboler
- Etter 1990: CAD-tegninger med titleblokk
- Vanlige stempler: "Godkjent", "Revidert", "For tillatelse", dato
- Skravur: yttervegger (tett), innervegger (medium), søyler (fylt)

KVALITETSVURDERING AV SKAN:
- God: Alle mål lesbare, skravur tydelig, tittelblokk komplett
- Middels: Noen mål utydelige, men geometri lesbar
- Dårlig: Kaffe-/vannflekker, dårlig oppløsning, viktig info mangler
"""

PROMPT = """\
Analyser dette skannede arkivdokumentet/den historiske byggetegningen.

Ekstraher ALL tilgjengelig informasjon:
- Dokumenttype (byggesøknad, godkjenning, tegning, korrespondanse, etc.)
- Byggeår / dato for godkjenning
- Saksnummer og saksbehandler (hvis synlig)
- Adresse og eiendomsidentifikasjon
- Bygningstype og formål
- Registrerte endringer fra original tegning
- Etasjeplan med rom (navn og estimert areal)
- Registrerte mål
- Eventuelle merknader, betingelser eller påtegninger

Returner KUN gyldig JSON uten markdown:
{
  "dokumenttype": "byggesøknad|godkjenning|situasjonsplan|tegning|korrespondanse|ukjent",
  "dato": null,
  "saksnummer": null,
  "adresse": null,
  "eiendom": null,
  "bygningstype": null,
  "byggeaar_estimat": null,
  "skan_kvalitet": "god|middels|dårlig",
  "etasjer": [],
  "rom": [],
  "registrerte_endringer": [],
  "maal": [],
  "betingelser": [],
  "historisk_kontekst": null,
  "merknader": null,
  "confidence": 0.7,
  "mangler": []
}
"""


class ArkivlyAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(
        self,
        image_bytes: bytes,
        media_type: str = "image/jpeg",
        address: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict:
        b64 = base64.standard_b64encode(image_bytes).decode()

        user_parts: list = [
            {"type": "text", "text": PROMPT, "cache_control": {"type": "ephemeral"}},
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
        ]
        if address:
            user_parts.append({"type": "text", "text": f"Kjent adresse: {address}"})
        if context:
            user_parts.append({"type": "text", "text": f"Tilleggskontekst: {context}"})
        user_parts.append({"type": "text", "text": "Analyser arkivdokumentet og returner JSON."})

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
            m = re.search(r'\{[\s\S]+\}', raw)
            data = json.loads(m.group()) if m else {"raw": raw, "error": "JSON parse failed"}

        if address and not data.get("adresse"):
            data["adresse"] = address

        return data
