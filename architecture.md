# Placely – Arkitektur

## Overordnet lagdeling

```
┌─────────────────────────────────────────────────────────┐
│                     AKTØRER                             │
│  Arkitekt · Utbygger · Takstmann · Håndverker · Eier    │
│  Bank · Forsikring · Kommune · Kjøper                   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   PRODUKTLAG                            │
│  Placely · Tomtly · Takstly · Finansly                  │
│  Insurancely · Handly · ByggSnap                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     XDi                                 │
│  Samler · Tolker · Mapper · Validerer · Beriker         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                 SlimBIM JSON                            │
│  Universelt dataspråk for bygg og eiendom               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  DATAKILDER                             │
│  SKP · RVT · PLN · DWG · IFC · PDF · PNG                │
│  Punktsky · iGuide · Drone · Manuell måling · Kartdata  │
└─────────────────────────────────────────────────────────┘
```

---

## SlimBIM JSON

Det universelle dataspråket. Lett, maskinlesbart og AI-vennlig.

**Prinsipper:**
- Minimalisme – bare nødvendige felt er obligatoriske
- Hierarkisk – eiendom → bygg → etasje → rom → flate → objekt
- Kilde-agnostisk – samme format uavhengig av hvor data kommer fra
- Versjonert – hvert objekt har `status`, `source` og `confidence`

Se `slimbim-schema.json` for full spesifikasjon.

---

## XDi – Intelligens- og tolkningslaget

XDi er motoren mellom rådata og produktene. Den gjør én ting: tar inn data i ethvert format og leverer ut SlimBIM JSON.

**Ansvarsområder:**

| Funksjon | Beskrivelse |
|---|---|
| **Parse** | Les SKP, RVT, IFC, DWG, PDF, PNG, punktsky |
| **Tolke** | Identifiser vegger, rom, etasjer, tak, åpninger |
| **Kartlegge** | Mapper kildedata til SlimBIM JSON-objekter |
| **Validere** | Sjekk geometrisk konsistens og regelkrav |
| **Berike** | Legg til manglende felt via AI, kart-API og register |
| **Koble** | Knytt bygg til tomt, rom til etasje, vegg til rom |
| **Diff** | Sammenlign to versjoner og beregn avvik |

**XDi er ikke:**
- En viewer
- En editor
- En database

XDi er en **dataprosessor**. Den konsumeres via API.

---

## Placely – Bygg-konfiguratoren

**Kjerneansvar:** La brukeren bygge, redigere og forstå en digital bygning.

### Komponenter

```
Placely
├── Floorplanner        – 2D planvisning med rom og vegger
├── Room Wizard         – veiledet rom-oppsett (type, størrelse, funksjon)
├── Build Wizard        – veiledet bygg-oppsett (hustype, etasjer, tak)
├── 3D Viewer           – enkel volumvisning
├── Produktkobling      – produkter og materialer per flate/objekt
├── Mengdekalkyle       – automatisk fra geometrien
├── Byggversjoner       – "sist godkjent", "as-built", "foreslått"
└── IFC/SKP Export      – ut til fagverktøy
```

### SketchUp-extension (første MVP)

Basert på Dynamic Components med SlimBIM-logikk:

- **Parent:** holder SlimBIM-data, IFC-metadata, GUID
- **Child-segmenter:** `PH_Wall_Segment` med `H_Left`, `H_Right`, `Width`, `Thickness`
- **TopPointCount:** N punkter → N-1 segmenter → profil auto-generert
- **Takprofil:** avledes fra vegger markert som `roof_driver: true`
- **Akse-hjelp:** låsing til rød/grønn akse, snap til eksisterende punkter

---

## Tomtly – Tomt- og terrengmotoren

**Kjerneansvar:** Plassere og vurdere bygg i kontekst av tomt, terreng og regelverk.

### Komponenter

```
Tomtly
├── Situasjonskart      – eiendomsgrenser, nabobygg, atkomst
├── 3D Terreng          – høydedata fra kartverket
├── Bygg-plassering     – drag-and-drop i X/Y/Z med snapping til grenser
├── Reguleringsmotor    – hent og tolke reguleringsplan
├── Utnyttelsesberegner – BYA, BRA, u-grad, høyder automatisk
└── Mulighetsanalyse    – hva kan bygges på tomten?
```

---

## Historikk – tre sannhetslag

Alle produkter støtter tre parallelle versjoner av enhver bygning:

```
SIST GODKJENT   →  hva kommunen har akseptert (kilde: byggesak, PDF)
AS-BUILT        →  hva som faktisk er bygget (kilde: måling, scan, iGuide)
NÅ-SITUASJON   →  hva som faktisk brukes i dag (kilde: befaring, foto)
```

Ingen av disse er "sannheten". De er alle gyldige versjoner med ulike formål.

---

## Dataflyt – eksempel: eksisterende bolig

```
1. iGuide Radix-scan av bolig
       ↓
2. XDi parser målbare snitt og romplan
       ↓
3. SlimBIM JSON: vegger, rom, etasjer, høyder
       ↓
4. Placely viser interaktiv planløsning
       ↓
5. Bruker redigerer og legger til manglende info
       ↓
6. Takstly setter TG per rom og flate
       ↓
7. Finansly beregner verdi og vedlikeholdskostnad
       ↓
8. ByggSnap dokumenterer tiltak med bilde → rom → samsvar
```

---

## Integrasjoner (prioritert)

| Integrasjon | Prioritet | Beskrivelse |
|---|---|---|
| SketchUp DC API | Høy | Første MVP – extension |
| iGuide Radix | Høy | Målbare snitt, romplan |
| Kartverket høydedata | Høy | Terreng for Tomtly |
| SE API (byggesak) | Medium | Historikk og "sist godkjent" |
| Matrikkelen | Medium | Eiendomsdata, adresse, areal |
| Revit/IFC-import | Lav | For fagbrukere |
| Punktsky (E57/LAS) | Lav | For komplekse bygg |

---

## Teknologistack (forslag)

| Lag | Teknologi |
|---|---|
| SlimBIM format | JSON Schema (draft-07) |
| XDi API | Python (FastAPI) eller Node.js |
| Placely web | React + Three.js / React Three Fiber |
| SketchUp extension | Ruby API + SketchUp DC |
| Database | Supabase (PostgreSQL + PostGIS) |
| Fillagring | Supabase Storage |
| AI/tolkning | Claude API (Sonnet) |
| Kart | Mapbox / Leaflet + Kartverket WMS |
