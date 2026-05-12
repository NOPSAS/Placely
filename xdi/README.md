# XDi – Intelligensmotor for SlimBIM

XDi tar inn bygningsdata fra hvilken som helst kilde og leverer ut **SlimBIM JSON**.

## Arkitektur

```
PDF · PNG · JPG · iGuide Radix
          ↓
      XDi API (FastAPI)
      + Claude Sonnet (vision + tekst)
          ↓
      SlimBIM JSON v1.0.0
```

## Endepunkter

| Metode | Rute | Beskrivelse |
|---|---|---|
| GET | `/` | Status |
| POST | `/parse/image` | PNG/JPG plantegning → SlimBIM JSON |
| POST | `/parse/pdf` | PDF-tegning → SlimBIM JSON |
| POST | `/parse/iguide` | iGuide Radix PDF → SlimBIM JSON |
| POST | `/validate` | Valider SlimBIM JSON mot schema |
| POST | `/diff` | Sammenlign to SlimBIM-dokumenter |

## Kom i gang

```bash
cd xdi
cp .env.example .env
# Legg inn ANTHROPIC_API_KEY i .env

pip install -r requirements.txt
python main.py
# API kjører på http://localhost:8001
# Dokumentasjon: http://localhost:8001/docs
```

## Med Docker

```bash
cd xdi
docker build -t xdi .
docker run -p 8001:8001 -e ANTHROPIC_API_KEY=sk-ant-... xdi
```

## Eksempel – parse en plantegning

```bash
curl -X POST http://localhost:8001/parse/image \
  -F "file=@plantegning.png" \
  -F "address=Birkeveien 3A, Oslo"
```

Respons (SlimBIM JSON):
```json
{
  "slimbim_version": "1.0.0",
  "created_by": "xdi-image-parser-v1",
  "property": {
    "id": "prop_a1b2",
    "type": "property",
    "address": "Birkeveien 3A, Oslo",
    "buildings": [...]
  }
}
```

## Parsere

| Parser | Kilde | Metode |
|---|---|---|
| `ImageParser` | PNG/JPG | Claude Sonnet vision |
| `PDFParser` | PDF | pdfplumber → PNG → Claude vision |
| `IGuideParser` | iGuide Radix PDF | PDFParser + iGuide-spesifikk ekstraksjon |

## Neste i v0.2
- IFC-parser (ifcopenshell)
- SketchUp `.skp` import
- Batch-parsing av flere filer
- Webhook-støtte
