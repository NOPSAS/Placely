# Placely

Bygg-konfiguratoren som lar alle aktører jobbe på samme digitale bygning – fra ulike faglige perspektiver.

## Hva er Placely?

Placely er kjernen i en PropTech-plattform som gjør bygningsdata universelt tilgjengelig. I stedet for å låse data i fagverktøy som Revit, SketchUp eller ArchicCad, oversetter Placely alt til ett felles, lettvekts dataspråk – **SlimBIM JSON** – via et intelligensmotor kalt **XDi**.

Resultatet: arkitekten, takstmannen, håndverkeren, banken og kjøperen jobber alle på den **samme digitale bygningen**.

## Plattformen

```
INPUT
PDF · PNG · Punktsky · Måling · Revit · Archicad · SketchUp · Kartdata
          ↓
    SlimBIM / XDi
    (tolker, rydder, oversetter)
          ↓
  ┌──────────────────────────────────────────┐
  │  Placely    Tomtly    Takstly    Finansly │
  │  Handly     ByggSnap  Insurancely         │
  └──────────────────────────────────────────┘
```

| Produkt | Rolle |
|---|---|
| **Placely** | Bygg-konfigurator: floorplanner, rom-wizard, modellering, kalkyle |
| **Tomtly** | Tomt/terreng/regler: plassering, situasjonskart, utnyttelse |
| **Takstly** | Tilstandsmotor: TG koblet direkte til geometri |
| **Finansly** | Økonomi: verdi, lån, prosjektøkonomi, budsjett |
| **Insurancely** | Forsikring og risiko |
| **Handly** | Håndverkerplattform: planlegge, bestille, dokumentere |
| **ByggSnap** | Dokumentasjonsmotor: bilde → rom → flate → samsvar |

## SlimBIM JSON

Det universelle byggspråket. Lett, maskinlesbart og AI-vennlig.

```json
{
  "slimbim_version": "1.0.0",
  "property": {
    "id": "prop_001",
    "type": "property",
    "address": "Birkeveien 3A, Oslo",
    "buildings": [{
      "id": "bygg_001",
      "type": "building",
      "version_status": "as_built",
      "floors": [{
        "walls": [{
          "id": "wall_101",
          "type": "wall",
          "start": [0, 0, 0.3],
          "end": [9.66, 0, 0.3],
          "thickness_m": 0.248,
          "is_roof_driver": true
        }]
      }]
    }]
  }
}
```

Se [`slimbim-schema.json`](slimbim-schema.json) for full spesifikasjon.

## Tre lag av sannhet

En bygning har alltid tre parallelle versjoner:

- **Sist godkjent** – hva kommunen har akseptert
- **As-built** – hva som faktisk er bygget
- **Nå-situasjon** – hva som faktisk brukes i dag

Placely behandler disse som separate lag, ikke én enkelt sannhet.

## Kom i gang

### SketchUp-extension (for arkitekter)

1. Last ned [`placely.rbz`](placely.rbz)
2. SketchUp → Window → Extension Manager → Install Extension
3. Bruk **Plugins → Placely → Tegn vegg**

Se [`sketchup-extension/INSTALL.md`](sketchup-extension/INSTALL.md) for detaljer.

### XDi API (for utviklere)

```bash
cd xdi
cp .env.example .env          # Legg inn ANTHROPIC_API_KEY
pip install -r requirements.txt
python main.py                # Starter på http://localhost:8001
```

Parse en plantegning:
```bash
curl -X POST http://localhost:8001/parse/image \
  -F "file=@plantegning.png" \
  -F "address=Birkeveien 3A, Oslo"
```

Se [`xdi/README.md`](xdi/README.md) for full API-dokumentasjon.

## Repo-struktur

```
Placely/
├── sketchup-extension/    SketchUp-extension (Ruby)
│   ├── placely.rb
│   └── placely/
├── xdi/                   XDi intelligensmotor (Python/FastAPI)
│   ├── main.py
│   ├── parsers/
│   ├── models/
│   └── core/
├── placely.rbz            Ferdig installasjonspakke
├── slimbim-schema.json    SlimBIM JSON Schema v1.0.0
├── vision.md
├── architecture.md
└── roadmap.md
```

## Dokumentasjon

| Dokument | Innhold |
|---|---|
| [`vision.md`](vision.md) | Overordnet visjon, problem og løsning |
| [`architecture.md`](architecture.md) | Lagdeling, komponenter og teknologistack |
| [`roadmap.md`](roadmap.md) | Faser og status |
| [`slimbim-schema.json`](slimbim-schema.json) | JSON Schema for SlimBIM v1.0.0 |
| [`xdi/README.md`](xdi/README.md) | XDi API-dokumentasjon |
| [`sketchup-extension/INSTALL.md`](sketchup-extension/INSTALL.md) | Installasjonsinstrukser |

## Status

| Komponent | Status |
|---|---|
| SlimBIM JSON Schema v1.0.0 | ✅ Ferdig |
| SketchUp-extension v0.1 | ✅ Ferdig – klar for beta |
| XDi API v0.1 | ✅ Ferdig – klar for test |
| Web floorplanner | Fase 2 |
| IFC-parser | Fase 3 (XDi v0.2) |

---

Et produkt av [NOPS AS](https://nops.no) / [Konsepthus AS](https://konsepthus.no)
