# Placely – Visjon

## Én setning
Placely er bygg-konfiguratoren som lar alle aktører jobbe på samme digitale bygning – fra ulike faglige perspektiver – ved hjelp av et universelt dataspråk.

---

## Problemet vi løser
Dagens byggebransje mangler ett felles lag mellom datakilder og fagverktøy. Arkitekter tegner i SketchUp, Revit og Archicad. Takstmenn skriver PDF-rapporter. Håndverkere bruker papirblokk. Kommuner behandler utprintede tegninger. Ingen snakker samme språk – selv om alle jobber på den samme bygningen.

Resultatet: data mistes, feil oppstår, og historikken forsvinner.

---

## Løsningen

### SlimBIM JSON – det universelle byggspråket
Et lettvekts, maskinlesbart format som beskriver bygningsobjekter på en enkel og forståelig måte:

```json
{
  "type": "wall",
  "id": "wall_101",
  "start": [0, 0, 0],
  "end": [4.2, 0, 0],
  "height": 2.4,
  "thickness": 0.198,
  "room": "Sov1",
  "level": "01"
}
```

Tar inn data fra: SKP · RVT · PLN · DWG · IFC · PDF · punktsky · manuell måling · kartdata · konfiguratorer

### XDi – intelligenslaget
Tolker, samler, mapper, validerer og beriker data fra alle kilder til SlimBIM JSON. XDi er "hjernen" som gjør det mulig å bruke data på tvers av alle produkter i plattformen.

---

## Plattformen

```
INPUT
PDF / PNG / punktsky / måling / Revit / Archicad / SketchUp / konfigurator
          ↓
    SlimBIM / XDi
    (tolker, rydder, oversetter)
          ↓
  ┌───────────────────┐
  │     PLACELY       │  Bygg-konfiguratoren
  │     TOMTLY        │  Tomt- og terrengmotoren
  └───────────────────┘
```

### Produkter

| Produkt | Rolle | Brukes av |
|---|---|---|
| **Placely** | Bygg-konfigurator: floorplanner, rom-wizard, modellering, produkter, kalkyle, byggversjoner | Arkitekt, utbygger, eier |
| **Tomtly** | Tomt/terreng/regler: plassering X/Y/Z, situasjonskart, 3D terreng, utnyttelse, mulighetsanalyse | Eiendomsmegler, utbygger, kommune |
| **Takstly** | Tilstandsmotor: TG på eiendom/bygg/rom/flate/objekt – koblet direkte til geometrien | Takstmann, bank, forsikring |
| **Finansly** | Økonomi: verdi, lån, prosjektøkonomi, kalkyle, budsjett, investering | Bank, utbygger, eier |
| **Insurancely** | Forsikring/risiko: skade, historikk, tilstand, sensordata | Forsikringsselskap, eier |
| **Handly** | Håndverkerplattform: planlegge, bestille, fremdrift, logg, sjekklister, FDV | Håndverker, byggmester |
| **ByggSnap** | Dokumentasjonsmotor: bilde → rom → flate → objekt → tiltak → samsvarserklæring | Håndverker, byggherre, kommune |

---

## Kjernetanken
> Alle aktører jobber på den **samme digitale bygningen** – men fra ulike faglige perspektiver.

Placely sier *hva* og *hvor*.  
Handly sier *hvem*, *når* og *hvordan*.  
ByggSnap beviser at det er gjort riktig.

---

## Datamodell – tilstand på alle nivåer

```
EIENDOM
  └── BYGG
        └── ETASJE
              └── ROM
                    └── FLATE
                          └── OBJEKT
```

Hvert nivå kan ha: TG · risiko · levetid · avvik · fukt · anbefaling · tiltak · verdi · historikk · dokumentasjon

---

## Historikk – tre lag av sannhet

En bygning har alltid tre parallelle sannheter:

1. **Sist godkjent** – hva kommunen har akseptert
2. **As-built** – hva som faktisk er bygget
3. **Nå-situasjon** – hva som faktisk brukes i dag

Placely behandler disse som separate lag, ikke én enkelt sannhet.

---

## Teknisk tilnærming (SketchUp-prototype)

- **Parent-komponent:** holder SlimBIM-data, IFC-metadata og topologi
- **Child-segmenter:** dum geometri definert av `H_Left`, `H_Right`, `Width`, `Thickness`
- **TopPointCount-logikk:** N punkter → N-1 segmenter → profil genereres automatisk
- **Takprofil:** avledes automatisk fra vegger som er markert som takstyrende
- **Datakilder:** iGuide Radix (målbare snitt), punktsky, drone/skråfoto, manuell måling

---

## Markedsposisjon

Placely er ikke en IFC-editor eller BIM-verktøy.  
Placely er **eiendommens digitale sannhetsmodell** – lett nok for en eier, presis nok for en arkitekt.

Konkurransefortrinn:
- Kilde-agnostisk (tar inn data fra hva som helst)
- Historikk som første-klasseborger
- Alle aktører på samme modell
- Lett nok til å faktisk bli brukt

---

*Basert på samtaler med Placely GPT, mai 2026*
