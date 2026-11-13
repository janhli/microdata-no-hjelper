# Testresultater for kodesnuttene

Her står hva som kom ut da snuttene ble kjørt i microdata.no, og hva resultatene er kontrollert mot.
Statuslinjen i hver snutt sier *at* den er testet. Denne filen sier *hva* testen viste.

Kildene er toppseksjonene i snuttene (`Kontroll:`), [`TESTLISTE.md`](../../../TESTLISTE.md) del 5 og
git-historikken. Når en snutt kjøres på nytt, oppdaterer du statuslinjen i snutten og raden her.

## Oversikt

Alle snuttene er kjørt frittstående med datalagerversjon 59 (`no.ssb.fdb:59`) i november 2026, satt sammen
til ett skript med `samle_snutter.py`. `lavinntekt_vedvarende.txt` ble kjørt for seg.

| Snutt | Kjørt | Kontrollert mot | Resultat |
|---|---|---|---|
| [alder.txt](alder.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [arbeidsstyrkestatus.txt](arbeidsstyrkestatus.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [bolig.txt](bolig.txt) | v59, 2026-11 | SSB 14897 | Antall husholdninger stemmer. Eierstatus avviker, men årsaken er kjent (se under) |
| [forlop_til_person.txt](forlop_til_person.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [husholdning.txt](husholdning.txt) | v59, 2026-11 | SSB 06079 | Stemmer |
| [innvandringskategori.txt](innvandringskategori.txt) | v59, 2026-11 | SSB 09817 | Stemmer (avvik under 0,03 %) |
| [landbakgrunn_region.txt](landbakgrunn_region.txt) | v59, 2026-11 | Klass 545 | Stemmer etter retting av EU/EØS-listen |
| [lavinntekt_eu60.txt](lavinntekt_eu60.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [lavinntekt_vedvarende.txt](lavinntekt_vedvarende.txt) | v59, 2026-11 | SSB 09571, 04204 | Stemmer innen 0,3 prosentpoeng |
| [mal_analyse.txt](mal_analyse.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [mor_barn.txt](mor_barn.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [samlivsstatus.txt](samlivsstatus.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [sektor_lonnstakere.txt](sektor_lonnstakere.txt) | v59, 2026-11 | SSB 13926 | Stemmer for totalen. Offentlig foretak ca. 2 % lavere, med kjent årsak |
| [utdanningsniva.txt](utdanningsniva.txt) | v59, 2026-11 | – | Kjørt uten feil |
| [verdi_ved_hendelse.txt](verdi_ved_hendelse.txt) | v59, 2026-11 | – | Kjørt uten feil |

«–» betyr at snutten er kjørt uten feil og at resultatet ser rimelig ut, men at det ikke er sammenlignet med
publiserte tall.

## Kontroll mot publiserte tall

### husholdning.txt

Privathusholdninger etter størrelse 1.1.2025, mot SSB tabell 06079:

| Personer | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|
| Snutten og SSB | 41,2 % | 30,8 % | 11,8 % | 11,2 % | 5,0 % |

Eget antall personer per husholdning (`collapse` på `hushnr`) er lik `BEFOLKNING_PERS_I_HUSHNR` for alle.

Funnet under testen: personer utenfor privathusholdning (ca. 39 000) har `hushnr`, men ikke størrelse og type.
Uten `drop if sysmiss(hushstr)` blir de egne «husholdninger», og 32 822 kontaktpersoner kommer med i
`if kontakt == '1'` (2025). Det står nå som fallgruve i snutten.

### innvandringskategori.txt

1.1.2025, mot SSB tabell 09817:

| Gruppe | Snutten | SSB |
|---|---|---|
| Innvandrere | 964 834 | 965 113 |
| Norskfødte med innvandrerforeldre | 230 180 | 230 237 |

656 bosatte mangler innvandringskategori. Like mange mangler fødselsår og landbakgrunn.

### landbakgrunn_region.txt

Bosatte 1.1.2025, mot Klass 545 (verdensinndeling) og `klass.py grupper 545` (TESTLISTE 4.1, 5.3 og 5.5):

- Hver gruppe ligger innenfor sin Klass-region. EU/EØS: 710 473, Europa utenom EU/EØS: 267 378.
- Grønland og Færøyene (4 367) er Norden i Klass, men Europa utenom EU/EØS i snutten. Det er med vilje.
- Første kjøring avdekket feil som er rettet:
  - Uspesifiserte koder (x94–x99, 142, 989) ble ikke omkodet.
  - Regelen for statsløse og uoppgitt (980, 989, 990, under 10 bosatte til sammen) ble stoppet av
    avsløringskontrollen. Kodene står nå uomkodet med navn.
  - Kypros, Bermuda og Saint-Pierre lå i feil verdensdel sammenlignet med Klass.
  - EU/EØS-listen hadde med Sveits, Grønland, Færøyene, Gibraltar og småstatene, og manglet Kypros.

### lavinntekt_vedvarende.txt

Kontrollert i TESTLISTE 5.2. Barn under 18 år, 2021–2023, mot SSB tabell 09571 (EU-60):

| Krav om privathusholdning | Landet | Oslo |
|---|---|---|
| Bare siste år (brukt i snutten) | 10,0 % | 13,6 % |
| Alle tre år | 9,8 % | 13,3 % |
| Ingen krav | 10,1 % | 13,9 % |
| **SSB 09571** | **9,9 %** | **13,8 %** |

Alle fylker (2020-inndeling) ligger innen 0,3 prosentpoeng.

Hele befolkningen, mot SSB tabell 04204:

| Periode | Snutten | SSB «studenter er utelatt» | Uten krav om privathusholdning | SSB «omfatter også studenter» |
|---|---|---|---|---|
| 2022–2024 | 9,6 % | 9,5 % | 10,6 % | 10,6 % |
| 2021–2023 | 9,5 % | 9,2 % | 10,5 % | 10,3 % |

Antall personer stemmer innen 0,2 %.

Kommunal median, barn 2022–2024. Dette finnes ikke i Statistikkbanken, så det er bare sjekket for rimelighet:

| | Nasjonal median | Kommunal median |
|---|---|---|
| Landet | 10,1 % | 10,1 % |
| Oslo | 13,0 % | 15,4 % |
| Bærum | 6,1 % | 11,0 % |
| Stavanger | 8,7 % | 11,6 % |
| Østfold | 14,8 % | 11,3 % |

Kommunal median i Bærum er 608 500 kr og i Oslo 528 000 kr.

Rettet etter kjøring: `merge` ble kjørt fra feil datasett, og KPI-faktorene for 2023 og 2024 var feil.

### bolig.txt

1.1.2024, mot SSB tabell 14897 (TESTLISTE 5.4):

| | Snutten | SSB |
|---|---|---|
| Husholdninger koblet til bolig | 2 584 506 | 2 584 517 |
| Selveier | 1 621 806 | 1 530 670 |
| Andels-/aksjeeier | 352 863 | 346 063 |
| Leier | 609 826 (23,6 %) | 707 784 (27,4 %) |

Husholdningene er de samme, men ca. 98 000 står som selveiere i `BOFORHOLD_EIE_LEIE` og som leiere i
Statistikkbanken. Årsaken er bekreftet: statistisk koblede husholdninger (`STAT`, 293 143) har eierstatus
anslått med SSBs gamle metode (51,6 % eiere). SSB har revidert dette til 13–15 % eiere (notat 2026/17), og
med det går avviket opp. Se [`fallgruver.md`](../referanser/fallgruver.md).

### sektor_lonnstakere.txt

4. kvartal 2025, mot SSB tabell 13926 (region = arbeidssted):

| Sektor | Snutten | SSB |
|---|---|---|
| Hele landet | 2 839 294 | 2 839 039 |
| Stat | 344 081 | 344 350 |
| Kommune og fylkeskommune | 577 957 | 577 897 |
| Privat | 1 791 576 | 1 796 696 |
| Offentlig foretak | 117 323 | 120 096 |
| Arbeidssted Bergen | 182 609 | 182 619 |
| Bergen, stat | 30 734 | 30 769 |

Avvik med kjent årsak: SSB fordeler ukjent sektor (ca. 0,3 %) på privat og offentlig foretak, mens snutten
gir dem kode 8. Offentlig foretak avviker også fordi SSB grupperer etter eierskap. Logikken er kjørt.
Den renskrevne versjonen har bare fått nye navn, kommentarer og titler.

## Observasjoner fra snutter uten publiserte tall

- **mor_barn.txt:** `BEFOLKNING_PARITET` mangler for det siste fødselskullet (2025 per november 2026).
- **husholdning.txt** og **innvandringskategori.txt:** 656 bosatte mangler fødselsår. Tell personer med
  `(sum)` på en variabel som alltid er 1, ikke `(count)` på en variabel som kan mangle.

## Neste gang

- Når datalageret får ny versjon, setter du sammen alle snuttene med
  `python .claude/skills/vedlikehold/samle_snutter.py > testskript.txt`, kjører dem og oppdaterer
  versjonskolonnen.
- Snutter med kontroll mot Statistikkbanken bør sammenlignes på nytt for den nyeste årgangen.
- KPI-faktorene i `lavinntekt_vedvarende.txt` må oppdateres når perioden flyttes.
