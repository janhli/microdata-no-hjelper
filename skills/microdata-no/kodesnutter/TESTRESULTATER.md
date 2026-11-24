# Testresultater for kodesnuttene

Her står hva som kom ut da snuttene ble kjørt i microdata.no, og hva resultatene er kontrollert mot.
Statuslinjen i hver snutt sier *at* den er testet. Denne filen sier *hva* testen viste.

Kildene er toppseksjonene i snuttene (`Kontroll:`), [`TESTLISTE.md`](../../../TESTLISTE.md) del 5 og
git-historikken. Når en snutt kjøres på nytt, oppdaterer du statuslinjen i snutten og raden her.

## Oversikt

Alle snuttene er kjørt frittstående med datalagerversjon 59 (`no.ssb.fdb:59`) i november 2026, satt sammen
til ett skript med `samle_snutter.py`. `lavinntekt_vedvarende.txt` ble kjørt for seg. De 14 som fortsatt
gjelder, er kjørt på nytt med versjon 60 (2026-11-19, TESTLISTE 5.6), uten feil og med de samme tallene
innen støyen (f.eks. innvandrere 964 836 mot 964 834, husholdninger koblet til bolig 2 584 502 mot
2 584 506, husholdningsstørrelsene 41,2/30,8/11,8/11,2/5,0 %). `sektor_lonnstakere.txt` er utgått og ligger i `arkiv/kodesnutter/` i repoet.

| Snutt | Kjørt | Kontrollert mot | Resultat |
|---|---|---|---|
| [alder.txt](alder.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [arbeidsstyrkestatus.txt](arbeidsstyrkestatus.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [bolig.txt](bolig.txt) | v60, 2026-11 | SSB 14897 | Antall husholdninger stemmer. Eierstatus avviker, men årsaken er kjent (se under) |
| [fylke.txt](fylke.txt) | v60, 2026-11 | SSB 07459 | Stemmer (alle fylker innen ±5) |
| [forlop_til_person.txt](forlop_til_person.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [husholdning.txt](husholdning.txt) | v60, 2026-11 | SSB 06079 | Stemmer |
| [innvandringskategori.txt](innvandringskategori.txt) | v60, 2026-11 | SSB 09817 | Stemmer (avvik under 0,03 %) |
| [landbakgrunn_region.txt](landbakgrunn_region.txt) | v60, 2026-11 | Klass 545 | Stemmer etter retting av EU/EØS-listen |
| [lavinntekt_eu60.txt](lavinntekt_eu60.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [lavinntekt_vedvarende.txt](lavinntekt_vedvarende.txt) | v60, 2026-11 | SSB 09571, 04204, FHI 403 | Stemmer innen 0,3 prosentpoeng (kommunal median: storbyene opptil 0,5 over FHI) |
| [logistisk_regresjon.txt](logistisk_regresjon.txt) | v60, 2026-11 | Predikert mot observert | Treffer 25–54 år, avvik ±4 prosentpoeng for 55–66 år (se under) |
| [neet.txt](neet.txt) | v60, 2026-11 | SSB 13556, 12423 | Stemmer innen 0,1 prosentpoeng (status, alder, kjønn, fylke, innvandrere). Utdanningsnivå avviker (se under) |
| [mal_analyse.txt](mal_analyse.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [mor_barn.txt](mor_barn.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [overlevelse.txt](overlevelse.txt) | v60, 2026-11 | Med og uten sensurering (TESTLISTE 8.6) | Sensurering ved utvandring endrer innvandrerkoeffisienten fra −0,242 til −0,209 |
| [paneldata.txt](paneldata.txt) | v60, 2026-11 | fe mot re mot pooled | Fixed effects mye mindre enn pooled, som ventet. Hausman velger fe |
| [samlivsstatus.txt](samlivsstatus.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [sektor_lonnstakere.txt](../../../arkiv/kodesnutter/sektor_lonnstakere.txt) (arkivert) | v59, 2026-11 | SSB 13926 | Stemmer for totalen. Offentlig foretak ca. 2 % lavere, med kjent årsak |
| [utdanningsniva.txt](utdanningsniva.txt) | v60, 2026-11 | – | Kjørt uten feil |
| [verdi_ved_hendelse.txt](verdi_ved_hendelse.txt) | v60, 2026-11 | – | Kjørt uten feil |

«–» betyr at snutten er kjørt uten feil og at resultatet ser rimelig ut, men at det ikke er sammenlignet med
publiserte tall.

## Kontroll mot publiserte tall

### fylke.txt

Bosatte 1.1.2025 etter fylke (`tabulate fylke`), mot SSB tabell 07459 (kjørt 2026-11-20, versjon 60):

| Fylke | Snutten | SSB |
|---|---|---|
| Østfold | 314 409 | 314 407 |
| Akershus | 740 683 | 740 680 |
| Oslo | 724 291 | 724 290 |
| Innlandet | 377 557 | 377 556 |
| Buskerud | 271 250 | 271 248 |
| Vestfold | 258 073 | 258 071 |
| Telemark | 177 865 | 177 863 |
| Agder | 322 188 | 322 188 |
| Rogaland | 504 495 | 504 496 |
| Vestland | 655 209 | 655 210 |
| Møre og Romsdal | 272 411 | 272 413 |
| Trøndelag | 486 818 | 486 815 |
| Nordland | 243 583 | 243 582 |
| Troms | 170 479 | 170 479 |
| Finnmark | 75 047 | 75 042 |
| Hele landet | 5 594 337 | 5 594 340 |

`tabulate fylkenum` ga de samme tallene innen støyen. Ingen bosatte hadde fylke 21, 99 eller manglende kommune.

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

Kommunal median, barn 2022–2024 (versjon 60). Finnes ikke i Statistikkbanken, men hos FHI
(nøkkeltall-tabell 403 «Vedvarende lavinntekt, kommunegrense», EU60 kommunal median, hentet 2026-11-19):

| | Nasjonal median | Kommunal median | FHI 403 |
|---|---|---|---|
| Landet | 10,1 % | 10,1 % | 10,1 % |
| Oslo | 13,0 % | 15,4 % | 14,9 % |
| Bergen | 9,1 % | 9,9 % | 9,6 % |
| Trondheim | 7,4 % | 8,1 % | 7,8 % |
| Stavanger | 8,8 % | 11,5 % | 11,3 % |
| Bærum | 6,1 % | 11,0 % | 10,9 % |
| Bodø | 6,8 % | 7,7 % | 7,5 % |
| Østfold | 14,8 % | 11,3 % | 11,4 % |

Alle fylkene ligger innen 0,25 prosentpoeng av FHI. Storbyene ligger 0,1–0,5 prosentpoeng over, mest Oslo,
Bergen og Trondheim. Det tyder på at medianen er beregnet litt ulikt i byer med mange studenter (FHI holder
studenthusholdninger utenfor). Årsaken er ikke undersøkt.

Kommunal median i Bærum er 608 500 kr og i Oslo 528 000 kr.

Kjørt på nytt med versjon 60 (2026-11-19, TESTLISTE 5.6): samme tall innen 0,1 prosentpoeng (Stavanger
8,8 og 11,5 %).

Avviket i storbyene undersøkt (TESTLISTE 5.7, 2026-11-23). Barn 2022–2024, andel med vedvarende lavinntekt:

| | Snutten | Median over husholdninger | Uten studenthusholdning alle tre år | Studenter med i medianen | Bosted 1.1.2024 | FHI 403 |
|---|---|---|---|---|---|---|
| Oslo | 15,4 | 12,7 | 15,6 | 14,6 | 15,4 | 14,9 |
| Bergen | 9,9 | 8,1 | 9,6 | 9,4 | 9,8 | 9,6 |
| Trondheim | 8,1 | 6,2 | 8,1 | 7,6 | 8,2 | 7,8 |
| Stavanger | 11,6 | 9,6 | 11,4 | 11,1 | 11,4 | 11,3 |
| Bærum | 11,0 | 8,6 | 11,0 | 10,7 | 11,0 | 10,9 |
| Bodø | 7,8 | 6,3 | 7,9 | 7,4 | 7,8 | 7,5 |
| Østfold | 11,3 | 9,3 | 10,9 | 11,1 | 11,3 | 11,4 |
| Landet | 10,1 | 8,4 | 10,0 | 9,8 | 10,1 | 10,1 |

- Medianen er over personer, ikke husholdninger (husholdningsmedianen er 5–8 % lavere overalt og gir for lave
  andeler). FHIs «medianinntekt for husholdninger» betyr husholdningsinntekten.
- Bostedsdatoen betyr nesten ingenting.
- Med studenthusholdningene i medianen (`INNTEKT_KODE_PRIVATHUSH1`) faller medianen mest i studentbyene (Oslo
  −8 400 kr, Trondheim −9 200, Bodø −3 200), men den varianten bommer for alle aldre (se under).

Alle aldre og aldersgrupper (runde 3, mot FHI 403 hentet fra det åpne API-et
`statistikk-data.fhi.no/api/open/v1/nokkel/Table/403`):

| | Alle aldre: snutten | Studenter i medianen | FHI | 18–24: snutten | FHI | 75+: snutten | FHI |
|---|---|---|---|---|---|---|---|
| Landet | 9,6 | 9,2 | 9,6 | 15,8 | 16,1 | 11,0 | 10,2 |
| Oslo | 14,5 | 13,8 | 14,4 | 28,4 | 28,2 | 13,8 | 13,0 |
| Bergen | 10,8 | 10,2 | 10,6 | 18,8 | 19,0 | 11,6 | 10,4 |
| Trondheim | 9,9 | 9,2 | 9,7 | 19,1 | 19,3 | 10,6 | 9,2 |
| Stavanger | 11,7 | 11,3 | 11,6 | 20,7 | 20,7 | 13,9 | 12,9 |
| Bærum | 13,4 | 13,0 | 13,3 | 22,2 | 22,2 | 17,0 | 16,1 |
| Bodø | 8,1 | 7,8 | 8,1 | 13,9 | 14,4 | 9,4 | 8,9 |
| Østfold | 8,7 | 8,4 | 8,7 | | | | |

- **Grensen i snutten er riktig:** for alle aldre og for 18–24 år treffer snutten FHI innen 0,2 prosentpoeng.
  Med studentene i medianen bommer den med 0,3–0,6.
- Avviket for barn i storbyene (opptil 0,5) ligger i hvordan barna telles (FHI: «gjennomsnittlig årlig antall»),
  ikke i grensen.
- 75+ ligger 0,5–1,4 prosentpoeng over FHI overalt. FHI bruker NAV-data for å finne flere institusjonsbeboere,
  som trolig holder flere eldre utenfor. Ikke undersøkt.
Skript: `testskript/del5_7_lavinntekt_storbyer.txt`, `del5_7b_lavinntekt_storbyer.txt` og `del5_7c_lavinntekt_aldre.txt`.

Rettet etter kjøring: `merge` ble kjørt fra feil datasett, og KPI-faktorene for 2023 og 2024 var feil.

### logistisk_regresjon.txt

Bosatte 25–66 år 1.1.2025 (3 076 000), sysselsatt i 4. kvartal 2024 (78,1 %). Kjørt to ganger, versjon 60:

- Første versjon hadde `c.alder#c.alder`. Leddet ble stille utelatt fra modellen (TESTLISTE 8.11), og
  sammenligningen av predikert og observert andel per utdanning var meningsløs (utdanning var i modellen).
- Rettet versjon med `alder2` og kontroll per aldersgruppe:

| Alder | Observert | Predikert |
|---|---|---|
| 25–34 | 80,7 % | 80,0 % |
| 35–44 | 82,0 % | 83,4 % |
| 45–54 | 81,6 % | 81,9 % |
| 55–61 | 77,1 % | 73,3 % |
| 62–66 | 56,2 % | 59,8 % |

Andregradskurven fanger ikke fallet ved 62 år (pensjon). Marginaleffekter mot grunnskole: videregående +17,
UH lang +29 prosentpoeng. Innvandrer −10,7 og mann +6,4. Cluster på kommune gir z-verdier rundt 50 mot 290 uten.
Første versjon traff andelen per utdanning med avvik på 0,03 prosentpoeng, fordi utdanning var i modellen.

### neet.txt

NEET 15–29 år, november 2024, mot SSB 13556 og 12423 (hentet fra SSBs API 2026-11-23, kjørt 2026-11-23,
versjon 60):

| | Snutten | SSB |
|---|---|---|
| Personer 15–29 år | 1 044 100 | 1 044 101 |
| NEET | 102 977 (9,86 %) | 102 976 (9,9 %) |
| Registrert ledige | 11 659 | 11 656 |
| AAP/uføretrygd | 27 131 | 27 134 |
| Andre, ikke på tiltak (ukjent 54 420 + andre 9 765) | 64 185 | 64 186 |
| 15–19 / 20–24 / 25–29 år | 5,24 / 10,79 / 13,27 % | 5,2 / 10,8 / 13,3 % |
| Menn / kvinner | 9,97 / 9,75 % | 10,0 / 9,7 % |
| Innvandrere / resten | 22,72 / 7,30 % | 22,7 / 7,3 % |
| Grunnskole / vgs / UH / uoppgitt | 14,0 / 6,8 / 5,6 / 16,1 % | 12,9 / 7,5 / 6,9 / 54,4 % |

- Alle 15 fylker innen 0,1 prosentpoeng (Oslo 9,93 mot 9,9, Østfold 11,70 mot 11,7, Finnmark 10,42 mot 10,4).
- Hovedstatus mot NEET: bare sysselsatte, ordinær utdanning og tiltak (inkl. tiltakspenger, introduksjonsprogram
  og nedsatt arbeidsevne på tiltak) er utenfor NEET. Dagpenger (1 043) og sykepenger (1 078) er NEET.
- Ukjent status er 53 % av NEET. Blant innvandrerne er 16,3 % NEET med ukjent status, mot 3,0 % for resten.
- Utdanningsnivået fra `NUDB_BU` 2024-08-01 treffer ikke 12423. Antall personer per nivå:

  | | Snutten | SSB 12423 | Forskjell |
  |---|---|---|---|
  | Grunnskolenivå | 351 190 | 425 984 | −74 794 |
  | Videregående nivå | 324 039 | 333 069 | −9 030 |
  | Universitet og høgskole | 263 955 | 277 630 | −13 675 |
  | Uoppgitt eller ingen | 104 911 | 7 417 | +97 494 |

  Snutten viser registrert utdanning per 1. august. SSB bruker 1. oktober, imputerer utdanningsnivå for innvandrere
  med uoppgitt nivå og koder de fleste 15-åringene og en del 16-åringer som å ha fullført grunnskolen. Den samlede
  forskjellen i tabellen viser ikke hvor mye hver metodeforskjell bidrar. [SSBs metodebeskrivelse](https://www.ssb.no/arbeid-og-lonn/sysselsetting/statistikk/tilknytning-til-arbeid-utdanning-og-velferdsordninger/#om-statistikken)

### overlevelse.txt

Bosatte 70 år og eldre 1.1.2016 (575 859), fulgt til 1.1.2026. Kjørt frittstående 2026-11-19 med de samme
tallene som testskriptet for TESTLISTE 8.6: 291 700 døde, 1 729 sensurert ved utvandring (1 135 av dem
innvandrere). Snittid i oppfølging 7,4 år (innvandrere 7,7). Cox: innvandrer −0,209 (hazardrate 0,81),
alder 1,135 per år, mann 1,336. Uten sensurering ved utvandring var innvandrerkoeffisienten −0,242.
Med `hazard` vises ingen standardfeil, men konfidensintervallet.

### paneldata.txt

Utvalg på 100 000 født 1985–1994, bosatt 1.1.2018, fulgt 2018–2024: 599 984 person-år for 93 382 personer.
Lønn i 1000 kr, med årseffekter:

| | Gift | Samboer | Oslo |
|---|---|---|---|
| Fixed effects | 13,0 | 7,5 | 45,8 |
| Random effects | 29,2 | 18,7 | 50,1 |
| Pooled | 93,9 | 89,1 | 69,8 |

Hausman chi2(9) = 1 269, p = 0. Robuste standardfeil i fe er ca. 45 % større enn de vanlige (1,52 mot 1,05
for gift). `tabulate-panel samliv, colpct` virker med én variabel (kolonnene er årene): gifte 16,7 % i 2018 og 29,5 % i
2024, uten par 48,8 % og 32,0 %. Overganger mellom samlivsformer fra år til år: 97,7 % av de gifte var gift året etter, 83,6 % av
samboerne var samboere og 81,4 % av dem uten par var fortsatt uten par.

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
med det går avviket opp: 716 000–721 000 leiere mot 707 784. Direkte koblede husholdninger (`DIR`) har 20,4 %
leiere. SSB-tabellen ligger på 27–28 % leiere for hele 2015–2025. Se [`fallgruver.md`](../referanser/fallgruver.md).

### sektor_lonnstakere.txt (arkivert)

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

Etter bosted ga Bergen 154 082 i 2025K4.

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
