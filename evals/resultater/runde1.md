# Runde 1 (2026-11-20): med og uten skill

Én kjøring per oppgave og betingelse, 34 underagenter (general-purpose, Opus 5.5). Uten skill: bare nettet, beskjed om ikke å lese repoet. Vurdert av en egen agent mot `graders/`.

**Endret etter runden:** kriterium 03 i `naering-hovedomrader` krevde en næringsvariabel for november 2024, som ikke finnes (siste er `REGSYS_VIRK_NACE1_SN07`, til 2019-11-16). Begge svarene oppdaget det og fikk 0. Kriteriet er skrevet om, så runde 2 belønner at agenten oppdager det.

Vurderingen sier at nedsamplingen står ulikt i skillen («1–3» og «1–11»). Det stemmer ikke: 1–3 gjelder de
fleste analyser og 1–11 `regress`, `ivregress` og `anova` (`fallgruver.md`).

Svarene fra agentene er ikke lagret i repoet.

---

# Vurdering av evalueringsrunde 1 (17 oppgaver, med og uten skill)

Vurdert strengt: 1 = svaret gjør eller sier det kriteriet beskriver, 0 = ikke. Variabelnavn er sjekket mot
`skills/microdata-no/metadata/variabler.csv`, syntaks mot `fallgruver.md` og `metadata/manual/.../kommandoer.md`.

## 1. Samletabell

| Oppgave | Med | Uten |
|---|---|---|
| andregradsledd | 2/2 | 1/2 |
| bydel-oslo | 3/3 | 2/3 |
| dekning-aap-2010-2024 | 4/4 | 1/4 |
| diff-in-diff | 3/3 | 3/3 |
| faktor-og-cluster | 3/3 | 2/3 |
| feil-statistikkopsjon | 2/2 | 1/2 |
| inntektsgrupper-sysmiss | 2/3 | 0/3 |
| instrumentvariabel | 3/3 | 3/3 |
| kommune-2015-mot-2024 | 3/4 | 2/4 |
| logit-sysselsatt | 4/4 | 3/4 |
| naering-hovedomrader | 2/3 | 0/3 |
| pseudonym-mor-mangler | 3/3 | 3/3 |
| region-politidistrikt | 3/3 | 2/3 |
| sjelden-gruppe-i-x | 3/3 | 3/3 |
| sjeldent-utfall-logit | 3/3 | 1/3 |
| tid-til-hendelse | 4/4 | 4/4 |
| usikkerhet-merket | 3/3 | 3/3 |

## 2. Totalt

| | Poeng | Andel |
|---|---|---|
| Med skill | 50/53 | 94 % |
| Uten skill | 34/53 | 64 % |

Med skill: full uttelling på 14 av 17 oppgaver. Uten skill: full uttelling på 7 av 17.
Uten er aldri bedre enn med på noen oppgave.

## 3. Per oppgave

### andregradsledd

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 alder2 med generate | 1 | 1 | Begge: `generate alder2 = alder * alder`. |
| 02 sier at c.x#c.x utelates uten melding | 1 | 0 | Med: «blir det leddet utelatt fra modellen uten noen melding». Uten sier tvert imot at «microdata.no støtter også interaksjonsnotasjonen `c.alder#c.alder`». |

Ekstra feil: Uten bruker `no.ssb.fdb:40` og analyseår 2023 uten grunn; påstanden om at `c.alder#c.alder` virker er faktafeil.

### bydel-oslo

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 BEFOLKNING_BYDEL, ikke grunnkrets | 1 | 1 | Begge importerer `BEFOLKNING_BYDEL 2025-01-01`. |
| 02 Oslo 0301, 25–66, lønn 2024 | 1 | 1 | Med: `values("0301")`, Uten: `keep if kommune == '0301'`; begge alder 25–66 og `INNTEKT_WLONN 2024-12-31`. |
| 03 sier at lønn er winsorisert per bydel | 1 | 0 | Med: «winsoriserer lønn (1 % i hver ende) i hver bydel for seg». Uten nevner bare støy og at høye lønninger påvirker snittet. |

Ekstra feil: ingen vesentlige. Uten skriver bydelsetiketter fra Klass for hånd, men tabulerer først som kontroll.

### dekning-aap-2010-2024

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 sier at SKATT_BA_AAP starter 2015, sjekket | 1 | 0 | Med: «finnes bare for inntektsårene 2015–2024 (`fra` 2015-01-01 i metadataene)». Uten ber brukeren selv sjekke i variabelbeskrivelsen. |
| 02 løsning for hele perioden | 1 | 0 | Med bruker `INNTEKT_SUM_ARBAVKL` for 2010–2014 og nevner `ARBSTATUS_AKT_ARBAP`. Uten foreslår bare å ta bort år som mangler. |
| 03 importerer ikke SKATT_BA_AAP før 2015 uten å si fra | 1 | 0 | Med importerer SKATT_BA_AAP bare 2015–2024. Uten har `import-panel db/SKATT_BA_AAP ... 2010-12-31 ...` for alle år. |
| 04 fylke i 2024-inndeling | 1 | 1 | Med: omkoding med `kommuneomkoding.py --fra 2010 --til 2024`. Uten: egen `fylke2024` via kommunenummer. |

Ekstra feil uten: `require no.ssb.fdb:latest` (ikke en versjon), `generate fylke2024 = .` (Stata-syntaks, trolig ugyldig), fylkes- og kommunekoder skrevet fra hukommelsen. `BOSATTEFDT_BOSTED` finnes (1991–2024).

### diff-in-diff

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 etter-dummy for alle | 1 | 1 | Med: `etter = 1 for ALLE fra 2020`. Uten: `post2020 = 1` for begge grupper. |
| 02 parallelle trender, se før 2020 | 1 | 1 | Begge har event study med 2019 som referanse og drøfter forutsetningen. |
| 03 regress-panel-diff med riktig tolkning | 1 | 1 | Begge `regress-panel-diff syss gruppe etter/post` og tolker samspillet som effekten. |

Ekstra feil uten: `drop if sysmiss(mor)` på den pseudonymiserte mors-ID-en (gir «Ulovlig bruk av pseudonymvariabel»), `require no.ssb.fdb:38`, sysselsatt = kode `'1'` i `REGSYS_ARB_ARBMARK_STATUS` (bare lønnstakere, selvstendige med kode `'2'` blir 0). Variabelnavnene finnes.

### faktor-og-cluster

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 i.utdanning, numerisk, lavest kode ref. | 1 | 1 | Med `i.utdniv` (1 = grunnskole), Uten `i.utd5` (1 = grunnskole). |
| 02 cluster på kommune, destring, ikke robust | 1 | 1 | Begge `cluster(kommnum/kommune_nr)` etter `destring`, uten `robust`. |
| 03 forklarer cluster og at lønn winsoriseres | 1 | 0 | Begge forklarer cluster. Bare Med sier at lønn winsoriseres i regresjonen. |

Ekstra feil uten: `keep if lonn > 0 & lonn != .` (Stata-missing), `require no.ssb.fdb:38`, data for 2022.

### feil-statistikkopsjon

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 median ugyldig, rett til p50 | 1 | 1 | Begge. |
| 02 winsorisert/støylagt eller collapse (median) | 1 | 0 | Med nevner både `collapse (median)` og winsorisering/støy. Uten nevner ingen av delene. |

Ekstra feil uten: sier at medianen trekkes ned av «alle som ikke har lønn» og foreslår `keep if lonn > 0`. `INNTEKT_WLONN` har ikke verdien 0, så de uten lønn mangler allerede.

### inntektsgrupper-sysmiss

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 manglende havner ikke stille i en gruppe | 1 | 0 | Med: variant B gir egen kode `'0'` «Ingen lønnsinntekt», og teksten sier hva som er valgt. Uten setter `lonn = 0` og legger dem i «Under 300 000», bare med et alternativ i kommentar. |
| 02 ikke konstruksjon der manglende faller i laveste gruppe | 0 | 0 | Med hovedvariant: `generate inntgr = '1'` + `replace`, «blir stående i '1' ... med vilje». Uten: `replace lonn = 0 if sysmiss(lonn)`. |
| 03 sammenligninger med manglende ≠ Stata | 1 | 0 | Med: «en sammenligning med manglende verdi er usann i microdata.no» (riktig etter fallgruver, men nevner ikke Stata eksplisitt; grensetilfelle). Uten: «fant ingen dokumentasjon». |

Ekstra feil uten: `require no.ssb.fdb:30`.

### instrumentvariabel

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 (endogen = instrument) | 1 | 1 | Med `(utdaar = uh_kom uh_region)`, Uten `(utdaar = hogskole16)`. |
| 02 drøfter gyldighet | 1 | 1 | Begge drøfter relevans (førstetrinn) og eksklusjon (byeffekter, familiebakgrunn). |
| 03 sier om avstand finnes, og alternativ | 1 | 1 | Med: søkt i variabler.csv, ingen avstandsvariabel, bruker `NUDB_KOMM_16` + kursdata. Uten: «Så vidt jeg kan se finnes det ingen ... avstandsvariabler» (ikke sjekket i metadata, men sier det), bruker bostedskommune ved 16 år. |

Ekstra feil med: `tabulate naerhet, summarize(utdaar) mean sd freq`: `sd` er ikke en gyldig statistikk (riktig er `std`), så skriptet stopper der. `i.fylke16`, `i.sentral16` og `i.sosbak` er tekstvariabler; det er ikke dokumentert at `i.` virker på tekst (fallgruver beskriver `i.` på numeriske koder). Ekstra feil uten: `require no.ssb.fdb:40`, kommuneliste for høgskoler skrevet fra hukommelsen (merket som utkast).

### kommune-2015-mot-2024

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 bruker kommuneomkoding.py | 1 | 0 | Med kjørte `kommuneomkoding.py --fra 2015 --til 2026`. Uten laget lister fra Klass-API-et. |
| 02 delte kommuner og hva som skjer | 1 | 1 | Med: Stokke, Snillfjord og Tysfjord står med gammelt nummer, med en valgfri sammenslåing. Uten: fordeler dem etter bosted rett etter delingen og sier at det «ikke er eksakt». |
| 03 BEFOLKNING_KOMMNR_FORMELL begge datoer, omkoding bare på 2015 | 0 | 1 | Med kjører samme `recode` også på 2025-dataene (ufarlig, men bryter kriteriet). Uten omkoder bare `kommune2015`. |
| 04 require med versjon fra datalager.json | 1 | 0 | Med `no.ssb.fdb:60`. Uten `no.ssb.fdb:NN`. |

Ekstra feil uten: påstår at `collapse (count)` mot kommune winsoriseres. Fallgruver sier at `count` ikke påvirkes. Kriterium 03 er kanskje for strengt (omkodingen av 2025 endrer ingen koder).

### logit-sysselsatt

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 logit/probit | 1 | 1 | Begge `logit`. |
| 02 utfall 0/1, manglende status håndtert | 1 | 0 | Med: `drop if sysmiss(status)` før `syss`. Uten: `generate sysselsatt = inlist(arbmstatus, '1', '2')`, så manglende status blir 0 uten at det håndteres. |
| 03 mfx(dydx)/or, OR ≠ RR når vanlig | 1 | 1 | Begge bruker `mfx(dydx)` og `or` og forklarer at OR overdriver når de fleste er sysselsatt. |
| 04 ikke-lineær alder | 1 | 1 | Med: `i.aldgr` (aldersgrupper). Uten: `alder2` med `generate`. |

Ekstra feil uten: `require no.ssb.fdb:38`, data for 2022, sier at `mfx(dydx)` er «målt ved gjennomsnittsverdiene» (fallgruver: gjennomsnittlige marginaleffekter).

### naering-hovedomrader

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 bruker klass.py | 1 | 0 | Med: `klass.py grupper 6 --nivaa 1 --dato 2019-01-01`. Uten grupperer 2-siffer for hånd. |
| 02 --dato passer dataene | 1 | 0 | Med setter `--dato 2019-01-01`, som passer dataene (2019) skriptet faktisk bruker. Uten bruker ikke verktøyet. |
| 03 næringsvariabel dekker nov. 2024 | 0 | 0 | Ingen av dem, og det går ikke: variabler.csv har ingen næringsvariabel etter 2019-11-16 (`REGSYS_VIRK_NACE1_SN07` slutter 2019). Begge sier dette riktig. **Kriteriet bør endres.** |

Ekstra: Uten har et kreativt anslag for 2024 (virksomhetens næring i 2019 koblet på `REGSYS_VIRK_ID_SSB` 2024). Variablene finnes. Uten antar at alle med `REGSYS_ARB_ARBMARK_STATUS` er sysselsatte, men kodelisten har også 0 (utenfor) og 3 (ledig). Det sier svaret selv at må sjekkes.

### pseudonym-mor-mangler

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 sysmiss(fnr_mor) gir feil fordi pseudonym | 1 | 1 | Med: «gir feilmeldingen «Ulovlig bruk av pseudonymvariabel»». Uten: «kommer trolig ikke til å virke», begrunnet med FAQ-en. |
| 02 ID bare i merge on / by() | 1 | 1 | Begge bruker `fnr_mor` bare i `merge ... on fnr_mor`. |
| 03 filtrerer på variabel fra mor | 1 | 1 | Med: `kjonn_mor`, Uten: `mor_kjonn`. |

Ekstra feil: ingen vesentlige.

### region-politidistrikt

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 regionomkoding.py politidistrikt | 1 | 0 | Med kjørte `regionomkoding.py politidistrikt`. Uten hentet koblingen fra Klass-API-et. |
| 02 ingen stille sluttregel | 1 | 1 | Ingen `* = ...` hos noen av dem. Uten setter ukjente koder til manglende og viser dem med `missing`. |
| 03 ikke fra hukommelsen | 1 | 1 | Med: verktøyet. Uten: generert maskinelt fra Klass 109/131 og kontrollert. |

Ekstra feil uten: `require no.ssb.fdb:30` (har neppe data for 2025), `BEFOLKNING_KOMMNR_FAKTISK` i stedet for FORMELL (finnes, 2014–2025, men er ikke folkeregistrert bosted).

### sjelden-gruppe-i-x

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 under 1 %, 0/1 utelates uten melding | 1 | 1 | Begge: rundt 0,5 %, og variabelen faller ut uten (tydelig) melding. |
| 02 i.dummy | 1 | 1 | Begge `i.eritrea`. |
| 03 be brukeren sjekke at raden finnes | 1 | 1 | Med: «Sjekk ... at det står en rad for «eritrea '1'»». Uten: «Se etter linjen `1.eritrea`». |

Ekstra feil uten: `INNVANDRING_LANDBAK` og `INNVANDRING_INNVKAT` **finnes ikke** (riktig: `BEFOLKNING_LANDBAK3GEN`, `BEFOLKNING_INVKAT`). Sysselsatt = bare kode `'1'` (selvstendige blir 0), manglende status blir 0, `require no.ssb.fdb:33`, alder bare lineær.

### sjeldent-utfall-logit

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 under 1 %, logit/regress gir tull pga. winsorisering | 1 | 0 | Med: 0,19 %, «alle dødsfallene blir gjort om til 0», «logit/regress gir da meningsløse tall uten feilmelding». Uten sier at utfallet er sjeldent, men kjører `logit` som hovedmodell. |
| 02 alternativ som virker (cox / avgrensning) | 1 | 0 | Med: `cox`. Uten: bare grovere kategorier. |
| 03 andel døde med krysstabell | 1 | 1 | Begge `tabulate ... , rowpct`. |

Ekstra feil uten: `doedsdato >= date(2025, 1, 1)` sammenligner tallet ÅÅÅÅMMDD med dager siden 1970, så `doed2025` blir 0 for alle. `month(doedsdato)` er feil av samme grunn. Uten setter også manglende lønn til 0 og bruker `require no.ssb.fdb:30`. Med skriver «1–3 tilfeldige observasjoner fjernes», mens fallgruver sier 1–11 (liten unøyaktighet).

### tid-til-hendelse

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 alle bosatte 70+ ved start | 1 | 1 | Med: bosatte 1.1.2016. Uten: bosatte 1.1.2013. |
| 02 sensur ved utvandring | 1 | 1 | Begge bruker årlig `BEFOLKNING_STATUSKODE` og sensurerer ved første 1.1. som ikke-bosatt. |
| 03 dødsdato ÅÅÅÅMMDD → dager med date() | 1 | 1 | Med: aritmetikk + `date()`. Uten: `substr` + `destring` + `date()`. |
| 04 cox tolket som hazard | 1 | 1 | Begge. |

Ekstra feil uten: `BEFOLKNING_DOEDS_DATO` er `Long`, ikke tekst, så `substr(doddato,1,4)` feiler trolig. Kriterium 03 er gitt fordi omregningen med `date()` er gjort, men den virker neppe slik den står (grensetilfelle). Uten bruker også `require no.ssb.fdb:23` og følger opp bare til 2023.

### usikkerhet-merket

| Kriterium | Med | Uten | Begrunnelse |
|---|---|---|---|
| 01 ikke et bestemt tall som om kjent | 1 | 1 | Begge sier at tallet kommer når skriptet kjøres, og gir intervaller merket som ukontrollerte anslag. |
| 02 skiller sjekket fra ikke testet | 1 | 1 | Med: avsnittene «sikkert», «mine anslag» og «usikkerhet». Uten: «Det jeg er usikker på» og «Ikke sjekket: variabelkatalogen». |
| 03 variablene finnes og dekker 2024 | 1 | 1 | `INNTEKT_KODE218`, `INNTEKT_LONN` og `INNTEKT_WLONN` finnes alle til 2024-12-31. |

Ekstra feil uten: `require no.ssb.fdb:41`, `BEFOLKNING_KOMMNR_FORMELL 2024-12-31` (variabelen måles per 1.1., så datoen gir bosted 1.1.2024, ikke ved utgangen av året slik teksten sier).

## 4. Mønstre

### Hvor skillen hjalp mest
- **Fallgruver som er særegne for microdata.no og bare finnes i skillen:**
  - at `c.x#c.x` utelates uten melding (andregradsledd)
  - at winsoriseringen gjelder tabeller per gruppe og regresjoner (bydel, faktor-og-cluster, feil-statistikkopsjon)
  - sjeldne utfall og cox (sjeldent-utfall)
  - sammenligninger med manglende verdi (inntektsgrupper)

  Uten skill mangler denne kunnskapen helt, eller svaret påstår det motsatte (c.alder#c.alder «støttes»).
- **Metadata:** dekning (SKATT_BA_AAP fra 2015), siste versjon (`fdb:60` mot 23/30/33/38/40/41/NN/latest uten skill) og riktige variabelnavn. Uten skill kom det variabler som ikke finnes (`INNVANDRING_*`) og feil datatyper (`BEFOLKNING_DOEDS_DATO` som tekst eller som dager).
- **Verktøyene:** `kommuneomkoding.py`, `regionomkoding.py` og `klass.py` ble brukt hver gang med skill. Uten skill ble det Klass-API eller håndskrevne lister (3 av 3 verktøykriterier tapt).
- **Utfall som 0/1 med håndtering av manglende status:** med skill gjort i alle sysselsettingsoppgavene. Uten skill blir manglende status 0 (logit, sjelden-gruppe, diff-in-diff).

### Hvor skillen ikke hjalp (like resultater)
- Generell metode: diff-in-diff, instrumentvariabel, tid-til-hendelse, pseudonym-mor, sjelden-gruppe-i-x og usikkerhet-merket ga full eller nesten full uttelling også uten skill. Grunnmodellen kjente selv `regress-panel-diff`, `ivregress`-rekkefølgen, sensurering, pseudonym-regelen (fra FAQ-en på nett) og `i.` for sjeldne dummyer. Skillen ga bedre skript i disse oppgavene (gyldige variabler, riktig versjon), men det gir ikke poeng.

### Feil i svar med skill som kan tyde på hull i skillen
1. **inntektsgrupper-sysmiss (kriterium 02):** Med-svaret kjenner regelen (sammenligning med manglende er usann), men bruker den bevisst til å legge «ingen lønn» i laveste gruppe i hovedvarianten. Skillen bør si tydelig at manglende inntekt skal ha egen kode eller tas ut, ikke legges i en gruppe via `generate g = 1` + `replace`. Kanskje bør en kodesnutt vise mønsteret.
2. **instrumentvariabel:** `summarize(...) mean sd freq`: `sd` er ugyldig (riktig: `std`). Fallgruver lister de gyldige statistikkene under median-avsnittet, men nevner ikke `sd`. Legg til «`sd` heter `std`» der. Svaret bruker også `i.` på tekstvariabler (`fylke16`, `sentral16`, `sosbak`). Skillen sier ikke om det er lov. Bør testes og dokumenteres.
3. **kommune-2015-mot-2024 (kriterium 03):** omkodingen ble også kjørt på 2025-dataene «for like navn». Det er ufarlig, men skillen kan si at omkoding bare trengs på den gamle årgangen. Alternativt er kriteriet for strengt.
4. **naering-hovedomrader (kriterium 03):** dette er ikke en feil i svaret. Kriteriet krever en næringsvariabel for november 2024, og den finnes ikke (siste er `REGSYS_VIRK_NACE1_SN07` 2019-11-16). Begge svarene oppdaget det. Kriteriet (og forventet resultat i case.yaml) bør skrives om, f.eks. til «svaret oppdager at næring ikke finnes etter 2019 og velger 2019 eller et alternativ».
5. **Mindre unøyaktighet:** sjeldent-utfall-med skriver at «1–3» observasjoner fjernes (fallgruver: 1–11). Det kan tyde på at tallet står ulikt flere steder i skillen. Verdt et søk.

### Kort om svarene uten skill
De taper mest på dekning og metadata (gjetter versjon og variabelnavn), på verktøykriteriene og på winsorisering og sjeldne utfall. Flere av skriptene ville stoppet eller gitt tull:
- `drop if sysmiss(mor)` i diff-in-diff
- `substr` på et `Long`-felt i tid-til-hendelse
- ÅÅÅÅMMDD sammenlignet med `date()` i sjeldent-utfall, så alle får 0 dødsfall
- variabler som ikke finnes i sjelden-gruppe
