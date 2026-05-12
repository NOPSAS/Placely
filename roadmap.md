# Placely – Roadmap

## Prinsipp
Bygg smalt og dypt fremfor bredt og grunt. Én brukerreise skal fungere perfekt før neste starter.

---

## Fase 0 – Fundament (nå → 4 uker)

**Mål:** Alle vet hva Placely er og hva som bygges først.

- [x] vision.md
- [x] architecture.md
- [x] slimbim-schema.json
- [ ] Definer MVP-brukerreise (velg én av tre nedenfor)
- [ ] Sett opp GitHub-repo med mappestruktur
- [ ] Bestem teknologistack

**Kritisk beslutning – MVP-inngang:**

| Alternativ | Fordel | Ulempe |
|---|---|---|
| A) SketchUp-extension | Prototypen finnes, nær produksjon | Smal målgruppe (arkitekter) |
| B) Web floorplanner | Bred målgruppe, ingen installasjon | Lengre byggetid |
| C) XDi PDF-parser | Høy verdi, ingen konkurrenter | Teknisk kompleks |

**Anbefaling: Start med A (SketchUp), valider B parallelt som konsept.**

---

## Fase 1 – SketchUp MVP (4 → 12 uker)

**Mål:** En arkitekt kan måle opp et eksisterende hus med iGuide Radix og få en SlimBIM-modell i SketchUp på under 30 minutter.

### Milepæler

**Uke 4–6: Vegg-motor**
- [ ] `PH_Wall_Segment` Dynamic Component fungerer stabilt
- [ ] Akse-låsing til rød/grønn (snap-hjelp)
- [ ] Redigering bevarer data (ikke blank ved re-åpning)
- [ ] Input i metrisk (mm/cm), ikke inches
- [ ] Vegg-ID og GUID genereres automatisk

**Uke 6–8: Takprofil**
- [ ] `roof_driver: true` på vegg → takprofil auto-beregnes
- [ ] Pulttak, saltak og mansard støttes
- [ ] TopPointCount N → N-1 segmenter fungerer

**Uke 8–10: SlimBIM-eksport**
- [ ] Export til SlimBIM JSON fra SketchUp
- [ ] Validering mot schema
- [ ] Enkel viewer (web) som leser JSON-filen

**Uke 10–12: iGuide-import**
- [ ] Les iGuide Radix PDF/snitt
- [ ] Ekstraher rom, høyder og etasjeinndeling via XDi
- [ ] Pre-fyll SketchUp-extension med verdier

**Leveranse:** Intern beta brukt på ett reelt prosjekt (Tegnebua-kunde).

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

## Fase 3 – XDi som API (24 → 36 uker)

**Mål:** Tredjeparter kan sende inn en PDF eller IFC og få ut SlimBIM JSON.

- [ ] REST API: POST /parse → SlimBIM JSON
- [ ] Støtte for: PDF-tegning, IFC, SketchUp-fil, iGuide
- [ ] Konfidensscoring per objekt
- [ ] Diff-funksjon: sammenlign to versjoner
- [ ] Webhook: varsle når parsing er ferdig

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
