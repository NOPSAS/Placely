# Installasjon – Placely SketchUp Extension

## Alternativ 1: Installer .rbz (anbefalt)

1. Pakk mappen `sketchup-extension/` til en ZIP-fil
2. Gi den navn `placely.rbz`
3. Åpne SketchUp
4. Gå til **Window → Extension Manager**
5. Klikk **Install Extension...**
6. Velg `placely.rbz`
7. Godkjenn installasjon

## Alternativ 2: Manuell installasjon (for utvikling)

Kopier følgende til SketchUp plugins-mappen:

**Windows:**
```
C:\Users\<brukernavn>\AppData\Roaming\SketchUp\SketchUp 20XX\SketchUp\Plugins\
```

Kopier:
- `placely.rb`  → rett inn i `Plugins\`
- `placely\`    → hele mappen inn i `Plugins\`

Restart SketchUp. Extensionen dukker opp under **Plugins → Placely**.

## Bruk

### Tegn en vegg
1. Klikk **Plugins → Placely → Tegn vegg**
2. Klikk i modellen for startpunkt
3. Klikk for sluttpunkt
   - `←` låser til grønn akse
   - `→` låser til rød akse
   - `Shift` frigjør akselåsing
   - `ESC` avbryter
4. Veggegenskaper-dialogen åpner automatisk
5. Juster høyder, tykkelse og knekkpunkter
6. Klikk **Lagre og bygg**

### Rediger en eksisterende vegg
1. Velg vegggruppen i modellen
2. Klikk **Plugins → Placely → Rediger valgt vegg**

### Eksporter til SlimBIM JSON
1. Klikk **Plugins → Placely → Eksporter SlimBIM JSON**
2. Velg lagringssted
3. Filen inneholder alle Placely-vegger i SlimBIM 1.0.0-format

## Krav
- SketchUp 2020 eller nyere
- Windows eller macOS
