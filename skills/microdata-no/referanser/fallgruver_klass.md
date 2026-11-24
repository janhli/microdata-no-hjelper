# Fallgruver med Klass

- **Velg riktig versjon med `--dato`.** `klass.py` bruker kodene som gjelder på datoen (standard i dag). SN2007-variabler
  må ha en dato før 2025-01-01, ellers får du SN2025 (Klass 6 har fire versjoner: SN 1994, SN 2002, SN 2007 og SN 2025).
  For NUS, STYRK og landkoder er det samme prinsipp: bruk en dato fra perioden dataene dekker.
- **Variablene har koder som ikke finnes i Klass.** Med `--variabel` listes slike koder i en kommentar og står uendret:
  - Landkoder: utgåtte land (Sovjetunionen 135, DDR 151), «uspesifisert»/«Resten av …» (194, 394, 594 osv.) og 989
    (uoppgitt utenlandsk statsborgerskap). Omkod dem for hånd, f.eks. til «Uoppgitt».
  - STYRK: `XXXX` (uoppgitt/ukjent).
  - SN2007: sammenfattede koder som `01.000` og `43.220`, og koder som ikke finnes i SN2007 i Klass på datoen. `grupper` plasserer
    dem via nærmeste overordnede kode (43.220 → 43.22 → F) og lister dem i en kommentar. Bare `00.000` (uoppgitt) står uendret.
    Det samme gjelder andre prefiksbaserte klassifikasjoner (STYRK, NUS), men ikke landkoder.
- **Resultatet er en kopi av kodene i Klass akkurat nå.** Klassifikasjoner endres. Oppgi hentedato i skriptet (verktøyet
  skriver den i en kommentar).
- **Koblinger med koder som har flere mål blander kodeverk.** SN2002 → SN2007 lot 42 % av sysselsatte
  (november 2006) stå med SN2002-kode. Gruppering på de første sifrene blir da feil (f.eks. «85» er helse
  i SN2002 og undervisning i SN2007).
- **Næring for personer finnes bare til november 2019** (versjon 60, fra variabelbeskrivelsene):
  | Variabel | Standard | Dekning |
  |---|---|---|
  | `REGSYS_NARING_SN94` | SN94 | 2000–2001 |
  | `REGSYS_NARING_SN2002` | SN2002 | 2002–2007 |
  | `REGSYS_NARING_SN2007` | SN2007 | november 2008 – november 2014 |
  | `REGSYS_VIRK_NACE1_SN07` | SN2007 | november 2015 – november 2019 |
  - Begge SN2007-variablene er næringen til virksomheten der personen har hovedarbeidsforholdet (høyest avtalt
    arbeidstid) i november, for sysselsatte bosatte 15–74 år. De andre har manglende verdi.
  - `REGSYS_VIRK_NACE1_SN07` erstatter `REGSYS_NARING_SN2007` fra 2015, samtidig med overgangen til
    a-ordningen. Regn med et brudd i tidsserien mellom 2014 og 2015, og si det når næring sammenlignes over
    bruddet.
  - SSB oppdaterer ikke `REGSYS_VIRK_NACE1_SN07` lenger, fordi den kan avsløre konfidensiell informasjon om
    foretak. Spør brukeren om næring etter 2019, si at den ikke finnes, og tilby 2019 med en tydelig merknad.
- **Bruk `kobling --nivaa 1` (eller 2) for næring over tid.** Målene løftes til seksjon (A–U) eller
  divisjon, så koder med flere detaljerte mål blir entydige: 91 % omkodet på nivå 1 og 83 % på nivå 2
  (november 2007), mot 57 % på femsifret nivå. Omkodede og uendrede koder kan skilles på lengden (1 eller
  2 tegn mot `xx.xxx`).
- **Koblingstabeller kan være mange-til-mange.** `kobling` utelater koder som går til flere mål, og koder uten
  motpart (Klass har rader uten mål, f.eks. `46.890` i SN2025–SN2007), og lister dem i en kommentar.
- **Samme kode som kilde i én regel og mål i en annen** (vanlig mellom versjoner, f.eks. `25.300 -> 25.400` og
  `25.400 -> 25.500`): står reglene i ulike `recode`-kommandoer, omkodes verdien to ganger. Verktøyene samler
  slike regler i første kommando. Ikke del den linjen, og ikke flytt regler mellom linjene.
- **`recode` på strenger.** Koder som `'01.110'` og `'0110'` må skrives som strenger. Landkodene i `BEFOLKNING_LANDBAK3GEN` er
  strenger. Snutten `landbakgrunn_region.txt` bruker `destring` og tallintervaller. Det går også, men verktøyets
  utskrift er strenger og skal ikke kombineres med `destring`.
- **Statsløs og uoppgitt er små.** `grupper 545` gir egne målkoder for statsløs og uoppgitt (`V9`, eller `V91` og
  `V92` på nivå 2). De har under 10 bosatte. Omkodingen godtas (TESTLISTE 1.13), og de vises som 0 i tabeller.
  Klass 545 er autoritet for verdensdel (Kypros i Europa, Bermuda og Saint-Pierre-et-Miquelon i Nord-Amerika).
  `landbakgrunn_region.txt` følger Klass og skiller i tillegg EU/EØS fra resten av Europa, som Klass ikke gjør.
- **Dataene kan ha nyere koder enn kodelisten.** `NUDB_BU` 1.7.2024 hadde NUS-koder (f.eks. 754144 Master, kunstig
  intelligens) som verken står i kodelisten i microdata.no eller i Klass 2024-01, bare i nyere Klass-versjoner. Bruk
  standarddatoen (i dag) for NUS. `grupper --variabel` tar med alle detaljkoder fra Klass på datoen.
- **Koblinger gir målnavnene fra Klass.** Er flere navn like (ISCED 2011: fem «Not further defined»), får de navnene
  over seg i hierarkiet («Bachelor’s or equivalent level – Academic – Not further defined»).
- **Landkodene i microdata er SSB-3 (Klass 91).** Verdensinndeling (545) bruker samme landkoder som blader. Gruppering
  av land (546) skiller EU/EFTA fram til 2004 fra nye EU-land etter 2004. Det er ikke dagens EU/EØS-medlemskap.
