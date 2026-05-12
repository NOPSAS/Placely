"""
XDi iGuide Parser
Parser for iGuide Radix-eksporter (PDF-snitt + romplan)
Bruker PDF-parseren som base + iGuide-spesifikk logikk
"""
import re
import io
from typing import Optional

import pdfplumber

from models.slimbim import SlimBIMDocument, SourceInfo
from parsers.pdf_parser import PDFParser


# iGuide Radix rapporter inneholder standardiserte feltnavn
IGUIDE_ROOM_PATTERN = re.compile(
    r"(?P<name>[A-Za-zÆØÅæøå\s]+)\s+(?P<area>[\d,\.]+)\s*m[²2]",
    re.IGNORECASE
)
IGUIDE_HEIGHT_PATTERN = re.compile(
    r"[Hh]øyde[:\s]+(?P<h>[\d,\.]+)\s*m"
)


class IGuideParser:
    def __init__(self, api_key: str):
        self.pdf_parser = PDFParser(api_key=api_key)

    def parse(
        self,
        pdf_bytes: bytes,
        address: Optional[str] = None,
    ) -> SlimBIMDocument:
        """
        Parse en iGuide Radix-rapport til SlimBIM JSON.
        Ekstraherer:
          - Romplan med arealer
          - Etasjehøyder fra snitt
          - Oppmålte mål
        """
        text = self._extract_text(pdf_bytes)
        context = self._build_context(text, address)

        doc = self.pdf_parser.parse(
            pdf_bytes=pdf_bytes,
            address=address,
            page_index=0,
        )

        # Berik med iGuide-spesifikk data
        self._enrich_from_text(doc, text)

        # Marker alle objekter som iGuide-kilde
        for building in doc.property.buildings:
            for floor in building.floors:
                for room in floor.rooms:
                    room.source_info = SourceInfo(
                        source="iguide_radix", confidence=0.92
                    )
                for wall in floor.walls:
                    wall.source_info = SourceInfo(
                        source="iguide_radix", confidence=0.90
                    )

        doc.created_by = "xdi-iguide-parser-v1"
        return doc

    def _extract_text(self, pdf_bytes: bytes) -> str:
        texts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
        return "\n".join(texts)

    def _build_context(self, text: str, address: Optional[str]) -> str:
        lines = [f"Kilde: iGuide Radix-rapport"]
        if address:
            lines.append(f"Adresse: {address}")

        rooms = IGUIDE_ROOM_PATTERN.findall(text)
        if rooms:
            lines.append("Detekterte rom fra tekst:")
            for name, area in rooms[:20]:
                lines.append(f"  - {name.strip()}: {area} m²")

        heights = IGUIDE_HEIGHT_PATTERN.findall(text)
        if heights:
            lines.append(f"Etasjehøyder fra tekst: {', '.join(set(heights))} m")

        return "\n".join(lines)

    def _enrich_from_text(self, doc: SlimBIMDocument, text: str) -> None:
        """Oppdater romarealer fra tekst der Claude ikke fikk dem riktig"""
        text_rooms: dict[str, float] = {}
        for name, area_str in IGUIDE_ROOM_PATTERN.findall(text):
            try:
                text_rooms[name.strip().lower()] = float(area_str.replace(",", "."))
            except ValueError:
                pass

        if not text_rooms:
            return

        for building in doc.property.buildings:
            for floor in building.floors:
                for room in floor.rooms:
                    key = (room.name or "").lower()
                    if key in text_rooms and room.area_m2 is None:
                        room.area_m2 = text_rooms[key]
