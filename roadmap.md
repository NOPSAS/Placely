# Placely – Roadmap

## Prinsipp
Bygg smalt og dypt fremfor bredt og grunt. Én brukerreise skal fungere perfekt før neste starter.

---

## Fase 0 – Fundament ✅ FERDIG

**Mål:** Alle vet hva Placely er og hva som bygges først.

- [x] vision.md
- [x] architecture.md
- [x] slimbim-schema.json
- [x] MVP-inngang valgt: **A (SketchUp) + C (XDi) parallelt**
- [x] GitHub-repo opprettet: github.com/NOPSAS/Placely
- [x] Teknologistack besluttet: Ruby (SketchUp) + Python/FastAPI (XDi)

---

## Fase 1 – SketchUp MVP (4 → 12 uker)

**Mål:** En arkitekt kan måle opp et eksisterende hus med iGuide Radix og få en SlimBIM-modell i SketchUp på under 30 minutter.

### Milepæler

**Vegg-motor** ✅ BYGGET
- [x] `PH_Wall_Segment`-logikk i WallBuilder
- [x] Akse-låsing til rød/grønn (← → piltaster + Shift frigjør)
- [x] Redigering bevarer data (SlimBIM-data lagret i AttributeDictionary)
- [x] Input i meter, konvertering til SketchUp-inches internt
- [x] Vegg-ID auto-generert

**Takprofil** ✅ BYGGET
- [x] `is_roof_driver: true` på vegg
- [x] TopPointCount N → N-1 segmenter via knekkpunkter
- [x] Pulttak, saltak og mansard støttes via top_points-array

**SlimBIM-eksport** ✅ BYGGET
- [x] Export til SlimBIM JSON fra SketchUp (SlimbimExporter)
- [x] Validering via XDi `/validate`
- [ ] Enkel web-viewer som leser JSON-filen

**iGuide-import** ✅ BYGGET (XDi)
- [x] XDi `/parse/iguide` parser iGuide Radix PDF
- [x] Ekstraherer rom, høyder og etasjeinndeling via Claude vision
- [ ] Pre-fyll SketchUp-extension med verdier fra XDi (kobling gjenstår)

**Leveranse:** Klar for intern beta på Tegnebua-prosjekt. Installer `placely.rbz`.

---

## Fase 2 – Web Floorplanner (12 → 24 uker)

**Mål:** En eier kan tegne planløsningen sin i nettleseren uten opplæring.

- [ ] 2D editor: vegger, rom, dører, vinduer
- [ ] Automatisk romgjenkjenning (areal, type)
- [ ] SlimBIM JSON inn og ut
- [ ] Kobling mot Tomtly (tomt + situasjonskart)
- [ ] Enkel 3D-visning (volum)
- [ ] Lagring og deling (Supabase)

---

## Fase 3 – XDi som API ✅ BYGGET (fremskyndet)

**Mål:** Tredjeparter kan sende inn en PDF eller IFC og få ut SlimBIM JSON.

- [x] FastAPI REST API – `POST /parse/image`, `/parse/pdf`, `/parse/iguide`
- [x] Støtte for: PNG/JPG, PDF, iGuide Radix
- [x] Konfidensscoring per objekt (source_info.confidence)
- [x] Diff-funksjon: `POST /diff`
- [x] Validator: `POST /validate`
- [x] Dockerfile for deployment
- [ ] IFC-parser (ifcopenshell) – v0.2
- [ ] Webhook – v0.2

---

## Fase 4 – Takstly-integrasjon (36 → 48 uker)

**Mål:** En takstmann kan sette TG direkte på geometrien i Placely.

- [ ] TG-widget per rom, flate og objekt
- [ ] Tilstandsrapport auto-generert fra modell
- [ ] Kobling mot Finansly (verdi + vedlikeholdskostnad)
- [ ] PDF-eksport av rapport

---

## Fase 5 – Handly + ByggSnap (48 → 60 uker)

**Mål:** En håndverker planlegger og dokumenterer arbeid direkte på modellen.

- [ ] Handly: tiltaksplanlegging per rom/flate
- [ ] Bestilling av produkter fra Placely-modell
- [ ] ByggSnap: bilde → rom → flate → objekt → samsvarserklæring
- [ ] FDV-dokumentasjon auto-generert

---

## Kritiske avhengigheter

| Avhengighet | Blokkerer |
|---|---|
| SlimBIM JSON-schema ferdigstilt | Alt |
| SketchUp DC-prototypen stabil | Fase 1 |
| Supabase-oppsett | Fase 2 |
| iGuide Radix API/export-format | Fase 1 uke 10 |
| Tomtly eksisterer | Fase 2 kobling |

---

## Hva Placely ikke er (og ikke skal bli)

- Ikke en full BIM-editor (det er Revit/Archicad)
- Ikke et prosjektstyringsverktøy
- Ikke en 3D game-engine
- Ikke ett verktøy for alt – hvert produkt i plattformen har én jobb

---

## Neste konkrete steg

1. Ta beslutning om MVP-inngang (A, B eller C)
2. Opprett GitHub-repo: `konsepthus/placely`
3. Finaliser `slimbim-schema.json` med ett reelt testbygg
4. Start Fase 1 uke 1: stabiliser `PH_Wall_Segment`
