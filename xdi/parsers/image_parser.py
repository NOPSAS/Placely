"""
XDi Image Parser
Analyserer plantegninger og bygningsfoto med Claude vision → SlimBIM JSON
"""
import base64
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic

from models.slimbim import (
    SlimBIMDocument, Property, Building, Floor, Wall, Room,
    Roof, SourceInfo, TopPoint, RoomType, WallType, FloorType
)

# Systemsprompt caches mellom kall (prompt caching sparer tokens)
PARSE_PROMPT = """\
Du er XDi – en AI-motor som konverterer byggetegninger til SlimBIM JSON.

OPPGAVE: Analyser bildet (plantegning, fasadetegning, snitt, eller bygningsfoto) og \
returner et SlimBIM JSON-objekt.

REGLER:
- Alle mål i METER (float, 2 desimaler)
- Koordinater [x, y, z] er i meter fra nedre venstre hjørne
- z = 0 er gulvnivå
- Confidence: 1.0 = eksakt mål fra tegning, 0.8 = skalert estimat, 0.5 = kvalifisert gjetning
- Returner KUN gyldig JSON – ingen forklaring, ingen markdown-blokk

SlimBIM-struktur:
{
  "slimbim_version": "1.0.0",
  "created_by": "xdi-image-parser-v1",
  "property": {
    "id": "prop_001",
    "type": "property",
    "address": "<adresse hvis synlig, ellers Ukjent>",
    "source_info": {"source": "image_parse", "confidence": 0.8},
    "buildings": [{
      "id": "bygg_001",
      "type": "building",
      "version_status": "as_built",
      "floors": [{
        "id": "etg_01",
        "type": "floor",
        "level_index": 0,
        "floor_type": "ground",
        "bra_m2": <estimert BRA>,
        "rooms": [
          {
            "id": "rom_001",
            "type": "room",
            "name": "<romnavn>",
            "room_type": "<living_room|kitchen|bedroom|bathroom|hallway|utility|storage|garage|office|other>",
            "area_m2": <areal>,
            "ceiling_height_m": <høyde hvis synlig>,
            "source_info": {"source": "image_parse", "confidence": 0.8}
          }
        ],
        "walls": [
          {
            "id": "wall_001",
            "type": "wall",
            "start": [x, y, 0],
            "end": [x, y, 0],
            "thickness_m": <tykkelse>,
            "wall_type": "<exterior|interior|load_bearing|partition>",
            "height_left_m": <høyde>,
            "height_right_m": <høyde>,
            "top_points": [{"x_m": 0, "z_m": <høyde>}, {"x_m": <lengde>, "z_m": <høyde>}],
            "source_info": {"source": "image_parse", "confidence": 0.7}
          }
        ]
      }]
    }]
  }
}

VIKTIG for FASADETEGNINGER: Fyll inn top_points med knekkpunkter som beskriver takprofilen.
VIKTIG for PLANTEGNINGER: Fyll inn rom og vegger med koordinater.
VIKTIG: Oppgi alltid minst 1 bygg, 1 etasje, og minst 1 rom eller vegg.\
"""


class ImageParser:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def parse(
        self,
        image_bytes: bytes,
        media_type: str = "image/jpeg",
        address: Optional[str] = None,
        extra_context: Optional[str] = None,
    ) -> SlimBIMDocument:
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        user_text = "Analyser dette byggetegningen og returner SlimBIM JSON."
        if address:
            user_text = f"Adresse: {address}\n{user_text}"
        if extra_context:
            user_text += f"\nTilleggskontekst: {extra_context}"

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        # Cache systemprompten (konstant på tvers av kall)
                        {
                            "type": "text",
                            "text": PARSE_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": user_text},
                    ],
                }
            ],
        )

        raw = response.content[0].text.strip()
        # Fjern eventuell markdown-wrapper
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)
        data["created_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        data["created_by"] = "xdi-image-parser-v1"

        return SlimBIMDocument(**data)
