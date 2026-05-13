# Placely – Kom i gang

## For Jakob: Deploy XDi til skyen (gjøres én gang)

Slik unngår du at alle som bruker Placely trenger egen API-nøkkel.

### Steg 1: Få Anthropic API-nøkkel
1. Gå til **console.anthropic.com**
2. Registrer deg eller logg inn
3. Klikk **API Keys** i venstremenyen
4. Klikk **Create Key** – gi den et navn (f.eks. "Placely XDi")
5. Kopier nøkkelen (ser slik ut: `sk-ant-api03-...`)
6. **Ta vare på den** – den vises bare én gang

### Steg 2: Deploy XDi til Render.com (gratis)
1. Gå til **render.com** og logg inn med GitHub
2. Klikk **New → Web Service**
3. Koble til GitHub-repoet **NOPSAS/Placely**
4. Render oppdager `render.yaml` automatisk
5. Legg inn `ANTHROPIC_API_KEY` i Environment-feltet (fra steg 1)
6. Klikk **Deploy**
7. Etter 2–3 minutter får du en URL: `https://placely-xdi.onrender.com`

### Steg 3: Del URL-en med alle brukere
Send `https://placely-xdi.onrender.com` til far og alle andre som skal bruke Placely.  
De trenger ikke egen API-nøkkel.

---

## For far (og andre brukere): Kom i gang med Placely

### Det du trenger
- SketchUp (gratis prøveversjon på sketchup.com eller Pro)
- Filen `placely.rbz` (får du av Jakob)
- XDi-URL fra Jakob (f.eks. `https://placely-xdi.onrender.com`)

### Installer Placely-extensionen
1. Åpne SketchUp
2. Gå til **Window → Extension Manager**
3. Klikk **Install Extension...**
4. Velg filen `placely.rbz`
5. Godkjenn installasjonen
6. Restart SketchUp

### Sett inn XDi-URL (gjøres én gang)
1. Gå til **Plugins → Placely → Innstillinger (XDi URL)**
2. Lim inn URL-en du fikk av Jakob
3. Klikk OK

### Tegn din første vegg
1. Gå til **Plugins → Placely → Tegn vegg**
2. Klikk i modellen for startpunkt
3. Klikk for sluttpunkt
4. Juster høyde og tykkelse i dialogen som åpner
5. Klikk **Lagre og bygg**

### Importer en plantegning (PDF eller bilde)
1. Gå til **Plugins → Placely → Importer fra XDi (PDF/bilde)**
2. Velg en PDF-tegning eller et bilde av en plantegning
3. Skriv inn adressen (valgfritt)
4. Klikk OK – vegger opprettes automatisk i SketchUp

### Se bygget i nettleseren (uten SketchUp)
1. Åpne filen `viewer/index.html` i Chrome eller Edge
2. Slipp en SlimBIM JSON-fil inn i vinduet
3. Bygget vises med vegger, rom og etasjer

---

## Trenger du hjelp?
Ta kontakt med jakob@tegnebua.no
