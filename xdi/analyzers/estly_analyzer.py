"""
Estly – AI-basert estetisk vurdering etter §29.2 plan- og bygningsloven.
Tar inn fasadebilder/skisser + prosjektbeskrivelse + kommune + bygningstype
og returnerer strukturert JSON-risikovurdering.
"""
import base64
import json
import re
from typing import List, Optional

import anthropic

SYSTEM = """\
Du er en erfaren norsk arkitekt og byggesaksbehandler med spesialkompetanse i \
estetisk vurdering etter plan- og bygningsloven § 29-2, kommunal praksis og \
norsk vernacular byggeskikk. Du gir presis, profesjonell risikovurdering.

REGELVERKSGRUNNLAG – § 29-2 PBL:
"Ethvert tiltak etter § 20-1 skal ha estetisk god utforming i samsvar med tiltakets \
funksjon og med respekt for naturgitte og bygde omgivelser."

Paragrafens tre krav:
1. Estetisk god utforming (absolutt minimumskrav)
2. I samsvar med tiltakets funksjon (funksjonell logikk skal reflekteres)
3. Respekt for naturgitte og bygde omgivelser (kontekstuell tilpasning)

NORSK REGIONAL BYGGESKIKK (vernacular):
- Trøndersk: tun-organisering, enkle saltakshus, rød/oker farge, bratte tak (40–50°), trepanel
- Vestlandsk: smale tomter, høyreiste hus, liggende kledning, variabel topografi, mørke farger
- Østlandsk: store flate tomter, panelte trehus med valmet tak (30–40°), lyse farger, symmetriske fasader
- Nordnorsk: lavere profil pga. vind, torv/trebord, robuste konstruksjoner, fargerike kontraster tillatt
- Urban tradisjon (Oslo/Bergen): murgårder, erker, klassiske proporsjoner, 2-5 etasjer
- Kystkultur: sjøboder, naust, rødmalt ytterkledning, saltaksprofil

TEK17 VISUELLE KRAV OG KUTYMER:
- Fasadematerialer skal ha dokumentert holdbarhet og vedlikeholdsvennlighet
- Takvinkel bør harmonere med nabobygg (±10° som tommelfingerregel)
- Vinduers høyde/bredde-forhold: tradisjonell norsk er stående rektangel (2:1 til 1.5:1)

VANLIGE AVVISNINGSGRUNNER § 29-2:
1. Feil skala/volum – for dominerende i forhold til omgivelsene
2. Dårlige materialvalg – materialer som bryter med lokal tradisjon uten god begrunnelse
3. Upassende takform – flatt tak i område med bratte saltak, eller omvendt
4. Kontrast med omgivelsene – farge/form skiller seg radikalt uten arkitektonisk begrunnelse
5. Stykkevis fasade – ingen sammenheng mellom volum, vinduer og materialer
6. Manglende lokal tilpasning – ignorerer stedskarakter og eksisterende bebyggelse

LOKAL TILPASNING I PRAKSIS:
- Studere eksisterende bebyggelse innenfor 100 m
- Tilpasse takvinkel, gesimshøyde og fasadematerialer
- Bruke naturlige og lokale materialer der mulig
- Unngå brå stilkontraster uten arkitektonisk begrunnelse
- Vurdere siktlinjer og fjernvirkning

ANALYSEDIMENSJONER:
1. Takform: vinkel, profil, materialer, harmoni med nabolaget
2. Vindusproporsjoner: format (stående/liggende), rytme, plassering
3. Fasadematerialer: tradisjonelt/moderne, holdbarhet, farger
4. Volumoppbygning: høyde, fotavtrykk, massing, skala mot nabolag
5. Forhold til gaterommet: tilbaketrekk, gesimshøyde, inngangssone

SVAR ALLTID med gyldig JSON uten markdown-kodeblokk.
"""

PROMPT_TMPL = """\
Vurder dette byggeprosjektets estetiske risiko etter plan- og bygningsloven § 29-2.

PROSJEKTBESKRIVELSE:
{beskrivelse}

KOMMUNE: {kommune}
BYGNINGSTYPE: {bygningstype}

{bilde_info}

Analyser fasadebilder/skisser og beskriv:
- Takform og -vinkel (grader hvis synlig)
- Vinduenes proporsjoner og rytme
- Fasadematerialer og fargevalg
- Volumoppbygning og skala
- Samlet estetisk inntrykk vs. lokal byggeskikk

Returner KUN gyldig JSON uten markdown:
{{
  "kommune": "{kommune}",
  "prosjekttype": "{bygningstype}",
  "samlet_vurdering": "god|akseptabel|utfordrende|risikofylt",
  "risiko_29_2": "LAV|MIDDELS|HØY",
  "sammendrag": "2-3 setninger som oppsummerer den estetiske vurderingen",
  "styrker": ["styrke 1", "styrke 2"],
  "utfordringer": ["utfordring 1"],
  "anbefalinger": ["konkret anbefaling 1", "konkret anbefaling 2"],
  "lokal_byggeskikk": "Beskrivelse av lokal byggeskikk for kommunen/regionen",
  "materialer": {{
    "vurdering": "Vurdering av valgte materialer",
    "anbefalinger": ["anbefaling 1"]
  }},
  "volum_proporsjoner": {{
    "vurdering": "Vurdering av volum og proporsjoner",
    "anbefalinger": ["anbefaling 1"]
  }},
  "takform": {{
    "vurdering": "Vurdering av takform",
    "anbefalinger": ["anbefaling 1"]
  }},
  "disclaimer": "Denne vurderingen er AI-generert og ikke bindende. §29.2-tolkninger varierer mellom kommuner."
}}
"""


class EstlyAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def analyze(
        self,
        image_bytes_list: List[bytes],
        media_types_list: List[str],
        beskrivelse: str,
        municipality: str,
        bygningstype: str,
    ) -> dict:
        # Cap at 4 images
        images = list(zip(image_bytes_list, media_types_list))[:4]

        bilde_info = f"ANTALL BILDER VEDLAGT: {len(images)}" if images else "INGEN BILDER VEDLAGT – base vurdering på beskrivelse alene."

        prompt = PROMPT_TMPL.format(
            beskrivelse=beskrivelse.strip(),
            kommune=municipality.strip(),
            bygningstype=bygningstype.strip(),
            bilde_info=bilde_info,
        )

        user_parts = [
            {"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}},
        ]

        for img_bytes, media_type in images:
            b64 = base64.standard_b64encode(img_bytes).decode()
            user_parts.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": b64},
            })

        user_parts.append({"type": "text", "text": "Analyser og returner JSON."})

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

        # Ensure required fields with fallbacks
        data.setdefault("kommune", municipality)
        data.setdefault("prosjekttype", bygningstype)
        data.setdefault("disclaimer",
            "Denne vurderingen er AI-generert og ikke bindende. "
            "§29.2-tolkninger varierer mellom kommuner.")

        return data
