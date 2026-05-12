"""
XDi PDF Parser
Ekstraherer tekst og geometri fra PDF-tegninger → SlimBIM JSON via Claude
"""
import base64
import io
import json
import re
import uuid
from datetime import datetime
from typing import Optional

import anthropic
import pdfplumber
from PIL import Image

from models.slimbim import SlimBIMDocument
from parsers.image_parser import ImageParser, PARSE_PROMPT


class PDFParser:
    def __init__(self, api_key: str):
        self.client       = anthropic.Anthropic(api_key=api_key)
        self.image_parser = ImageParser(api_key=api_key)

    def parse(
        self,
        pdf_bytes: bytes,
        address: Optional[str] = None,
        page_index: int = 0,
    ) -> SlimBIMDocument:
        """
        Parse en PDF-tegning til SlimBIM JSON.
        Strategi:
          1. Ekstraher tekst fra alle sider (mål, adresser, romnanvn)
          2. Konverter første side til bilde
          3. Send bilde + tekst til Claude vision
        """
        text_context = self._extract_text(pdf_bytes)
        page_image   = self._pdf_page_to_image(pdf_bytes, page_index)

        extra = f"Ekstrahert tekst fra PDF:\n{text_context[:2000]}" if text_context else None

        return self.image_parser.parse(
            image_bytes=page_image,
            media_type="image/png",
            address=address,
            extra_context=extra,
        )

    def _extract_text(self, pdf_bytes: bytes) -> str:
        texts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
        return "\n".join(texts)

    def _pdf_page_to_image(self, pdf_bytes: bytes, page_index: int = 0) -> bytes:
        """Konverter én PDF-side til PNG-bilde via pdfplumber + Pillow"""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if page_index >= len(pdf.pages):
                page_index = 0
            page = pdf.pages[page_index]
            # Render til bilde (300 DPI for god lesbarhet)
            img = page.to_image(resolution=200)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
