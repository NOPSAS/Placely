"""
XDi API – Intelligensmotor for konvertering av bygningsdata til SlimBIM JSON
NOPS AS / Konsepthus AS
"""
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from core.api_keys import require_api_key
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.differ import diff_slimbim
from core.validator import validate_slimbim
from parsers.image_parser import ImageParser
from parsers.iguide_parser import IGuideParser
from parsers.pdf_parser import PDFParser
from analyzers.floor_plan_analyzer import FloorPlanAnalyzer
from analyzers.compliance_checker import ComplianceChecker
from analyzers.soknadssjekk_analyzer import SoknadssjekKAnalyzer
from analyzers.arkivly_analyzer import ArkivlyAnalyzer
from analyzers.productly_analyzer import ProductlyAnalyzer
from analyzers.estly_analyzer import EstlyAnalyzer
from analyzers.finansly_analyzer import FinanslyAnalyzer

try:
    from parsers.ifc_parser import IfcParser
    HAS_IFC = True
except ImportError:
    HAS_IFC = False

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

app = FastAPI(
    title="XDi API",
    description=(
        "Intelligensmotor som konverterer bygningsdata fra PDF, bilder og IFC "
        "til SlimBIM JSON. Del av Placely-plattformen."
    ),
    version="0.1.0",
    contact={"name": "NOPS AS", "url": "https://nops.no"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_api_key() -> str:
    if not ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY er ikke satt. Legg den til i .env-filen.",
        )
    return ANTHROPIC_API_KEY


# ── Helse ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["helse"])
def root():
    return {
        "name":    "XDi",
        "version": "0.1.0",
        "status":  "ok",
        "docs":    "/docs",
    }


@app.get("/health", tags=["helse"])
def health():
    return {"status": "ok", "api_key_set": bool(ANTHROPIC_API_KEY)}


# ── Parse: bilde ──────────────────────────────────────────────────────────────

@app.post("/parse/image", tags=["parse"])
async def parse_image(
    file:    UploadFile = File(..., description="PNG eller JPG av plantegning/fasade"),
    address: Optional[str] = Form(None, description="Adresse for bygget (valgfritt)"),
    context: Optional[str] = Form(None, description="Tilleggskontekst (f.eks. 'fasadetegning sør')"),
):
    """
    Analyser et bilde av en byggetegning og returner SlimBIM JSON.
    Støtter: plantegning, fasadetegning, snitt, drone-foto.
    """
    api_key = _require_api_key()

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, f"Forventet bildefil, fikk: {file.content_type}")

    image_bytes = await file.read()
    parser      = ImageParser(api_key=api_key)

    try:
        doc = parser.parse(
            image_bytes=image_bytes,
            media_type=file.content_type,
            address=address,
            extra_context=context,
        )
    except Exception as e:
        raise HTTPException(500, f"Parsing feilet: {str(e)}")

    return doc.model_dump()


# ── Parse: PDF ────────────────────────────────────────────────────────────────

@app.post("/parse/pdf", tags=["parse"])
async def parse_pdf(
    file:       UploadFile = File(..., description="PDF-tegning"),
    address:    Optional[str] = Form(None),
    page_index: int = Form(0, description="Hvilken side som skal analyseres (0-indeksert)"),
):
    """
    Analyser en PDF-byggetegning og returner SlimBIM JSON.
    Konverterer første side til bilde og sender til Claude vision.
    """
    api_key = _require_api_key()

    if file.content_type != "application/pdf":
        raise HTTPException(400, "Forventet PDF-fil")

    pdf_bytes = await file.read()
    parser    = PDFParser(api_key=api_key)

    try:
        doc = parser.parse(pdf_bytes=pdf_bytes, address=address, page_index=page_index)
    except Exception as e:
        raise HTTPException(500, f"Parsing feilet: {str(e)}")

    return doc.model_dump()


# ── Parse: iGuide ─────────────────────────────────────────────────────────────

@app.post("/parse/iguide", tags=["parse"])
async def parse_iguide(
    file:    UploadFile = File(..., description="iGuide Radix PDF-rapport"),
    address: Optional[str] = Form(None),
):
    """
    Analyser en iGuide Radix-rapport og returner SlimBIM JSON.
    Ekstraherer romplan, arealer, etasjehøyder og oppmålte mål.
    """
    api_key = _require_api_key()

    pdf_bytes = await file.read()
    parser    = IGuideParser(api_key=api_key)

    try:
        doc = parser.parse(pdf_bytes=pdf_bytes, address=address)
    except Exception as e:
        raise HTTPException(500, f"Parsing feilet: {str(e)}")

    return doc.model_dump()


# ── Validering ────────────────────────────────────────────────────────────────

@app.post("/validate", tags=["verktøy"])
async def validate(doc: dict):
    """
    Valider et SlimBIM JSON-dokument mot SlimBIM schema v1.0.0.
    Returnerer liste med feil, eller tom liste hvis gyldig.
    """
    errors = validate_slimbim(doc)
    return {
        "valid":  len(errors) == 0,
        "errors": errors,
        "count":  len(errors),
    }


# ── Parse: IFC ────────────────────────────────────────────────────────────────

@app.post("/parse/ifc", tags=["parse"])
async def parse_ifc(
    file:    UploadFile = File(..., description="IFC-fil (.ifc)"),
    address: Optional[str] = Form(None),
):
    """
    Konverter en IFC-fil til SlimBIM JSON.
    Krever at ifcopenshell er installert (pip install ifcopenshell).
    """
    if not HAS_IFC:
        raise HTTPException(
            501,
            "ifcopenshell er ikke installert på denne serveren. "
            "Kjør: pip install ifcopenshell"
        )

    ifc_bytes = await file.read()
    parser    = IfcParser()

    try:
        doc = parser.parse(ifc_bytes=ifc_bytes, address=address)
    except Exception as e:
        raise HTTPException(500, f"IFC-parsing feilet: {str(e)}")

    return doc.model_dump()


# ── Analyse: Romplan ─────────────────────────────────────────────────────────

@app.post("/analyse/romplan", tags=["analyse"])
async def analyse_romplan(
    file:    UploadFile = File(..., description="Plantegning – PNG, JPG eller PDF"),
    address: Optional[str] = Form(None, description="Adresse (valgfritt)"),
    _key:    str = Depends(require_api_key),
):
    """
    Analyser en plantegning og returner BRA, romplan og grovkalkyle.
    Støtter PNG, JPG og PDF (første side).
    """
    api_key = _require_api_key()
    raw = await file.read()

    if file.content_type == "application/pdf":
        from parsers.pdf_parser import PDFParser
        parser = PDFParser(api_key=api_key)
        # Konverter PDF til bilde for analyse
        img_bytes = parser._pdf_page_to_image(raw)
        mime      = "image/png"
    else:
        img_bytes = raw
        mime      = file.content_type or "image/jpeg"

    try:
        analyzer = FloorPlanAnalyzer(api_key=api_key)
        result   = analyzer.analyze(img_bytes, mime, address)
    except Exception as e:
        raise HTTPException(500, f"Analyse feilet: {str(e)}")

    return result


# ── Analyse: Byggesjekk ───────────────────────────────────────────────────────

@app.post("/analyse/byggesjekk", tags=["analyse"])
async def analyse_byggesjekk(
    godkjent:  UploadFile = File(..., description="Godkjent tegning fra kommunen (PDF/PNG/JPG)"),
    navarende: UploadFile = File(..., description="Nåværende plantegning fra Finn.no/befaring (PNG/JPG/PDF)"),
    address:   Optional[str] = Form(None, description="Adresse (valgfritt)"),
    _key:      str = Depends(require_api_key),
):
    """
    Sammenlign godkjent kommunetegning med nåværende plantegning.
    Identifiserer potensielt ulovlige endringer etter plan- og bygningsloven.
    """
    api_key = _require_api_key()

    approved_bytes = await godkjent.read()
    current_bytes  = await navarende.read()

    try:
        checker = ComplianceChecker(api_key=api_key)
        result  = checker.check(
            approved_bytes = approved_bytes,
            approved_type  = godkjent.content_type  or "image/jpeg",
            current_bytes  = current_bytes,
            current_type   = navarende.content_type or "image/jpeg",
            address        = address,
        )
    except Exception as e:
        raise HTTPException(500, f"Byggesjekk feilet: {str(e)}")

    return result


# ── Analyse: Søknadssjekk ─────────────────────────────────────────────────────

@app.post("/analyse/soknadssjekk", tags=["analyse"])
async def analyse_soknadssjekk(
    beskrivelse: str = Form(..., description="Beskriv de planlagte byggearbeidene"),
    adresse:     Optional[str] = Form(None, description="Adresse (valgfritt)"),
    _key:        str = Depends(require_api_key),
):
    """
    Sjekk om planlagte byggearbeider krever søknad etter PBL/SAK10.
    Returnerer søknadsplikt per arbeidspost med begrunnelse og TEK17-krav.
    """
    api_key = _require_api_key()
    try:
        analyzer = SoknadssjekKAnalyzer(api_key=api_key)
        result   = analyzer.analyze(beskrivelse, adresse)
    except Exception as e:
        raise HTTPException(500, f"Søknadssjekk feilet: {str(e)}")
    return result


# ── Analyse: Estly ───────────────────────────────────────────────────────────

@app.post("/analyse/estly", tags=["analyse"])
async def analyse_estly(
    file1:       UploadFile = File(..., description="Fasadebilde 1"),
    file2:       Optional[UploadFile] = File(None, description="Fasadebilde 2"),
    file3:       Optional[UploadFile] = File(None, description="Fasadebilde 3"),
    file4:       Optional[UploadFile] = File(None, description="Fasadebilde 4"),
    beskrivelse: Optional[str] = Form(None, description="Prosjektbeskrivelse"),
    municipality: Optional[str] = Form(None, description="Kommune"),
    bygningstype: Optional[str] = Form(None, description="Bygningstype"),
    _key:         str = Depends(require_api_key),
):
    """Estetisk vurdering mot §29.2 plan- og bygningsloven."""
    api_key = _require_api_key()
    images, types = [], []
    for f in [file1, file2, file3, file4]:
        if f:
            images.append(await f.read())
            types.append(f.content_type or "image/jpeg")
    try:
        result = EstlyAnalyzer(api_key=api_key).analyze(
            images, types, beskrivelse, municipality, bygningstype
        )
    except Exception as e:
        raise HTTPException(500, f"Estly-analyse feilet: {str(e)}")
    return result


# ── Analyse: Finansly ────────────────────────────────────────────────────────

@app.post("/analyse/finansly", tags=["analyse"])
async def analyse_finansly(
    file:         UploadFile = File(..., description="Plantegning (PDF/PNG/JPG)"),
    address:      Optional[str] = Form(None),
    year:         Optional[int] = Form(None, description="Byggeår"),
    bygningstype: Optional[str] = Form(None),
    tilstand:     Optional[str] = Form(None),
    _key:         str = Depends(require_api_key),
):
    """Generer bankdokumentasjon og verdiestimat fra plantegning."""
    api_key = _require_api_key()
    raw = await file.read()
    if file.content_type == "application/pdf":
        from parsers.pdf_parser import PDFParser
        img_bytes = PDFParser(api_key=api_key)._pdf_page_to_image(raw)
        mime = "image/png"
    else:
        img_bytes, mime = raw, file.content_type or "image/jpeg"
    try:
        result = FinanslyAnalyzer(api_key=api_key).analyze(
            img_bytes, mime, address, year, bygningstype, tilstand
        )
    except Exception as e:
        raise HTTPException(500, f"Finansly-analyse feilet: {str(e)}")
    return result


# ── Analyse: Arkivly ─────────────────────────────────────────────────────────

@app.post("/analyse/arkivly", tags=["analyse"])
async def analyse_arkivly(
    file:    UploadFile = File(..., description="Skannet arkivdokument (PDF, PNG, JPG)"),
    address: Optional[str] = Form(None),
    context: Optional[str] = Form(None, description="Tilleggskontekst om bygget"),
    _key:    str = Depends(require_api_key),
):
    """Analyser skannede kommunale arkivdokumenter og historiske byggetegninger."""
    api_key = _require_api_key()
    raw = await file.read()

    if file.content_type == "application/pdf":
        from parsers.pdf_parser import PDFParser
        img_bytes = PDFParser(api_key=api_key)._pdf_page_to_image(raw)
        mime = "image/png"
    else:
        img_bytes, mime = raw, file.content_type or "image/jpeg"

    try:
        result = ArkivlyAnalyzer(api_key=api_key).analyze(img_bytes, mime, address, context)
    except Exception as e:
        raise HTTPException(500, f"Arkivly-analyse feilet: {str(e)}")
    return result


# ── Analyse: Productly ────────────────────────────────────────────────────────

@app.post("/analyse/productly", tags=["analyse"])
async def analyse_productly(
    address:      Optional[str] = Form(None),
    byggeaar:     Optional[int] = Form(None),
    bygningstype: Optional[str] = Form(None),
    etasjer:      Optional[int] = Form(None),
    bra_m2:       Optional[float] = Form(None),
    tilstand:     Optional[str] = Form(None),
    _key:         str = Depends(require_api_key),
):
    """Generer FDV-register og produktspesifikasjoner for en bygning."""
    api_key = _require_api_key()
    try:
        result = ProductlyAnalyzer(api_key=api_key).analyze(
            address=address, byggeaar=byggeaar, bygningstype=bygningstype,
            etasjer=etasjer, bra_m2=bra_m2, tilstand=tilstand,
        )
    except Exception as e:
        raise HTTPException(500, f"Productly-analyse feilet: {str(e)}")
    return result


# ── Diff ──────────────────────────────────────────────────────────────────────

@app.post("/diff", tags=["verktøy"])
async def diff(base: dict, updated: dict):
    """
    Sammenlign to SlimBIM-dokumenter og returner strukturerte endringer.
    Nyttig for å finne forskjellen mellom 'sist godkjent' og 'as_built'.
    """
    return diff_slimbim(base, updated)


# ── Kjør lokalt ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
