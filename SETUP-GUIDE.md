# Placely – Kom i gang

## XDi er live

XDi API kjører på Railway og er tilgjengelig for alle:

**`https://xdi-production.up.railway.app`**

- Status: https://xdi-production.up.railway.app/health
- API-dokumentasjon: https://xdi-production.up.railway.app/docs

---

## For far (og andre brukere): Kom i gang med Placely

### Det du trenger
- SketchUp (gratis prøveversjon på sketchup.com eller Pro)
- Filen `placely.rbz` (last ned fra github.com/NOPSAS/Placely eller få av Jakob)

XDi-URL er allerede innebygd i extensionen – du trenger ikke gjøre noe ekstra.

### Steg 1 – Installer Placely-extensionen
1. Åpne SketchUp
2. Gå til **Window → Extension Manager**
3. Klikk **Install Extension...**
4. Velg filen `placely.rbz`
5. Godkjenn installasjonen
6. Restart SketchUp

Du finner nå **Placely** under **Plugins**-menyen.

### Steg 2 – Tegn din første vegg
1. Gå til **Plugins → Placely → Tegn vegg**
2. Klikk i modellen for startpunkt
3. Klikk for sluttpunkt
   - `←` låser til grønn akse
   - `→` låser til rød akse
   - `ESC` avbryter
4. Juster høyde og tykkelse i dialogen
5. Klikk **Lagre og bygg**

### Steg 3 – Importer en tegning automatisk
1. Gå til **Plugins → Placely → Importer fra XDi (PDF/bilde)**
2. Velg en PDF-tegning eller et bilde av en plantegning
3. Skriv inn adressen (valgfritt)
4. Klikk OK – vegger og rom opprettes automatisk i SketchUp

### Steg 4 – Eksporter og se bygget i nettleseren
1. Gå til **Plugins → Placely → Eksporter SlimBIM JSON**
2. Lagre JSON-filen
3. Åpne `viewer/index.html` i Chrome
4. Slipp JSON-filen inn – bygget vises med vegger, rom og målestokk

---

## Endre XDi-URL (kun ved behov)
Hvis du vil bruke en annen XDi-instans:
**Plugins → Placely → Innstillinger (XDi URL)**

Standard URL: `https://xdi-production.up.railway.app`

---

## Trenger du hjelp?
Ta kontakt med jakob@tegnebua.no
