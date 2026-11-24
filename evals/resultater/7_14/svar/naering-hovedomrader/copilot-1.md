# naering-hovedomrader: copilot, kjøring 1

- Modell: Copilot CLI 1.0.114, MAI Code 2 Flash
- Dato: 2026-11-23
- Skill: med, via `~/.agents/skills`

## Svar

Opprettet `skript_naering.txt` i arbeidsmappen. Skriptet bruker 2024-status, men merker tydelig at siste næringsdata er fra 2019.

**Skills:** microdata-no

**Filer lest:** `variabler.csv`, `datalager.json`, `fallgruver.md`, `arbeidsstyrkestatus.txt`, `logistisk_regresjon.txt`, `alder.txt`, `kodesnutter/README.md`

**Kommandoer/verktøy:** PowerShell, `klass.py grupper 6`, `rg`, `view` og `apply_patch`

## Skript

```
// =====================================================================
// Sysselsatte etter næringshovedområde i november 2024
// Status: utarbeidet for no.ssb.fdb:60
//
// VIKTIG: Microdata.no har ingen næringsvariabel som dekker november 2024.
// Siste variabel er REGSYS_VIRK_NACE1_SN07, og den dekker bare til november 2019.
// Dette skriptet viser derfor personer som var sysselsatt i november 2024,
// etter næring registrert i november 2019. Dette er ikke næringen i november
// 2024, men den siste tilgjengelige historiske næringsfordelingen.
//
// Variabler:
// ARBSTATUS_PERS_STATUS8
// https://microdata.no/discovery/variable/no.ssb.fdb/60/ARBSTATUS_PERS_STATUS8
//
// REGSYS_VIRK_NACE1_SN07
// https://microdata.no/discovery/variable/no.ssb.fdb/60/REGSYS_VIRK_NACE1_SN07
// =====================================================================

require no.ssb.fdb:60 as fdb

create-dataset personer

// Prioritert arbeidsstyrkestatus i november 2024.
import fdb/ARBSTATUS_PERS_STATUS8 2024-11-16 as status
generate status4 = substr(status, 1, 4)

generate syss = 0
replace syss = 1 if status4 == '0808' | status4 == '0816' | status4 == '0832' | status4 == '1608'

// Behold bare personer som er sysselsatt i november 2024.
keep if syss == 1

// Siste tilgjengelige næringsdata.
import fdb/REGSYS_VIRK_NACE1_SN07 2019-11-16 as naring2019

// Gruppér SN2007-koden etter divisjonen (de to første tegnene).
// Divisjoner 01–03 = A, 05–09 = B, 10–33 = C, osv.
generate divisjon = substr(naring2019, 1, 2)
generate divisjonsnr = divisjon
destring divisjonsnr

generate naring = 'X'
replace naring = 'A' if divisjonsnr >= 1 & divisjonsnr <= 3
replace naring = 'B' if divisjonsnr >= 5 & divisjonsnr <= 9
replace naring = 'C' if divisjonsnr >= 10 & divisjonsnr <= 33
replace naring = 'D' if divisjonsnr == 35
replace naring = 'E' if divisjonsnr >= 36 & divisjonsnr <= 39
replace naring = 'F' if divisjonsnr >= 41 & divisjonsnr <= 43
replace naring = 'G' if divisjonsnr >= 45 & divisjonsnr <= 47
replace naring = 'H' if divisjonsnr >= 49 & divisjonsnr <= 53
replace naring = 'I' if divisjonsnr >= 55 & divisjonsnr <= 56
replace naring = 'J' if divisjonsnr >= 58 & divisjonsnr <= 63
replace naring = 'K' if divisjonsnr >= 64 & divisjonsnr <= 66
replace naring = 'L' if divisjonsnr == 68
replace naring = 'M' if divisjonsnr >= 69 & divisjonsnr <= 75
replace naring = 'N' if divisjonsnr >= 77 & divisjonsnr <= 82
replace naring = 'O' if divisjonsnr == 84
replace naring = 'P' if divisjonsnr == 85
replace naring = 'Q' if divisjonsnr >= 86 & divisjonsnr <= 88
replace naring = 'R' if divisjonsnr >= 90 & divisjonsnr <= 93
replace naring = 'S' if divisjonsnr >= 94 & divisjonsnr <= 96
replace naring = 'T' if divisjonsnr == 97
replace naring = 'U' if divisjonsnr == 99

define-labels naringtxt 'A' 'A Jordbruk, skogbruk og fiske' 'B' 'B Bergverksdrift og utvinning' 'C' 'C Industri' 'D' 'D Elektrisitets-, gass-, damp- og varmtvannsforsyning' 'E' 'E Vannforsyning, avløps- og renovasjonsvirksomhet' 'F' 'F Bygge- og anleggsvirksomhet' 'G' 'G Varehandel, reparasjon av motorvogner' 'H' 'H Transport og lagring' 'I' 'I Overnattings- og serveringsvirksomhet' 'J' 'J Informasjon og kommunikasjon' 'K' 'K Finansierings- og forsikringsvirksomhet' 'L' 'L Omsetning og drift av fast eiendom' 'M' 'M Faglig, vitenskapelig og teknisk tjenesteyting' 'N' 'N Forretningsmessig tjenesteyting' 'O' 'O Offentlig administrasjon og forsvar, trygdeordninger' 'P' 'P Undervisning' 'Q' 'Q Helse- og sosialtjenester' 'R' 'R Kulturell virksomhet, underholdning og fritidsaktiviteter' 'S' 'S Annen tjenesteyting' 'T' 'T Lønnet arbeid i private husholdninger' 'U' 'U Internasjonale organisasjoner og organer' 'X' 'Uoppgitt eller mangler 2019-data'
assign-labels naring naringtxt

textblock
# Sysselsatte etter næring: november 2024, siste næringsdata november 2019

Populasjonen er personer som var sysselsatte i november 2024 ifølge
ARBSTATUS_PERS_STATUS8. Næringen kommer fra REGSYS_VIRK_NACE1_SN07 i november
2019, siden variabelen ikke er oppdatert etter denne datoen. Tabellen viser
derfor ikke dagens næringsfordeling for 2024.

Tallene er SN2007-hovedområder (A–U). «Uoppgitt eller mangler 2019-data»
samler personer uten gyldig næringsopplysning i 2019.
endblock
tabulate naring, missing

citation
```
