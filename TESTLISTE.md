# Testliste

Ting som ikke er prøvd i microdata.no, eller som bygger på antakelser. Avklarte punkter står i [`TESTLOGG.md`](TESTLOGG.md).
Når en test avklarer noe, flytt raden dit med datalagerversjon, dato og tallene fra kjøringen. Skriv regelen inn i riktig fallgruvefil ([`fallgruver.md`](skills/microdata-no/referanser/fallgruver.md) eller temafilen), uten tallene, og endre teststatus i berørte snutter.

Numrene er felles for de to filene: et nytt punkt får neste ledige nummer i sin del. Delene som ikke har åpne punkter, står bare i loggen.

Prioritet: **P1** kan gi feil resultat uten at det synes, **P2** kan stoppe skriptet, **P3** er kvalitetssjekk.

Det som kan sjekkes uten microdata.no, er automatisert i [`tests/`](tests/) (`python -m unittest discover -s tests`). Listen her gjelder det som bare kan avklares ved å kjøre i microdata.no.

## 5. Kodesnutter

| # | Hva | Pri |
|---|---|---|
| 5.9 | Kjør `neet.txt` på nytt etter at kategorien ukjent ble lagt til (`'9'` i `aldgr` og `innv`, `'99'` i `fylke`). Forventet: kategorien er tom eller nesten tom, og tallene er som i 5.8. Prøv også SSBs regel om grunnskole for 15–16-åringer: sett `utdniv = '1'` for 15–16-åringer uten registrert utdanning, og sammenlign med tabell 12423. Gjenstår da bare imputeringen for innvandrere som forskjell, kan regelen legges inn i snutten | P3 |

## 6. Henting og vedlikehold

| # | Hva | Hvordan | Forventet | Pri |
|---|---|---|---|---|
| 6.2 | Delvis feilet henting | Simulert i `tests/test_hent_variabler.py` og `tests/test_hent_manual.py`. Se første gang det skjer i workflowen | Jobben feiler, og ingen PR åpnes | P3 |

## 7. Agentatferd (evaluering)

Sammenlign agentens svar med og uten skillen på disse oppgavene. Oppgavetekster og kriterier ligger i
[`evals/`](evals/README.md) (én mappe per oppgave, 2026-11-20).

Runde 1 er kjørt (7.1–7.13 og 7.15–7.18). 7.14 er kjørt med Codex og Copilot CLI, men ikke med Cursor. Resultatene står i
[`TESTLOGG.md`](TESTLOGG.md) del 7.

| # | Oppgave | Hva som måles |
|---|---|---|
| 7.1 | Variabel som ikke dekker perioden | Sjekker `fra`/`til` før skriptet skrives |
| 7.2 | Pseudonymisert ID | Bruker ikke ID-en direkte |
| 7.3 | Gamle kommunenumre | Bruker `kommuneomkoding.py`, melder om delte kommuner |
| 7.4 | Manglende verdier | Avslutter grupperinger med `sysmiss` |
| 7.5 | Feil statistikkopsjon | Retter og forklarer |
| 7.6 | Region fra kommune | Bruker `regionomkoding.py` uten sluttregel i egen kommando |
| 7.7 | Næring/yrke til grupper | Bruker `klass.py` og setter riktig `--dato` |
| 7.8 | Usikkerhet | Skiller mellom det som er kontrollert mot kildene, det som bygger på testet snutt, og det som må kjøres |
| 7.9 | Ja/nei-utfall | Velger `logit`/`probit`, lager utfallet som 0/1 med eksplisitt håndtering av `sysmiss`, og bruker `mfx(dydx)` eller `or` når effekten skal tolkes |
| 7.10 | Faktorvariabler og standardfeil | Bruker `i.` for kategorier, `cluster()` når enhetene er gruppert (ikke sammen med `robust`), og forklarer valget |
| 7.11 | Tid til hendelse | Lager populasjonen av alle i risiko, sensurerer ved død og utvandring, og tolker `cox` som hazard |
| 7.12 | Diff-in-diff | Lager etter-dummyen for alle enheter, ikke bare behandlingsgruppen, og nevner forutsetningen om parallelle trender |
| 7.13 | Instrumentvariabel | Skriver `( endogen = instrument )` riktig vei og drøfter om instrumentet er gyldig |
| 7.14 | Andre agenter (Copilot, Codex, Cursor) | Skillen lenket til `~/.agents/skills/microdata-no` som i README: finnes med `/skills`, lastes ved en microdata.no-oppgave, finner `variabler.csv` og `fallgruver.md`, og kjører `verktoy/klass.py`. Oppgave 7.3 og 7.7 gir samme type svar som i Claude |
| 7.15 | Sjeldent utfall (død i 2025, 25–66 år) | Advarer om at `logit` gir meningsløse tall under 1 %, foreslår `cox` eller avgrensning, viser andelen med antall |
| 7.16 | Andregradsledd | Lager `alder2` med `generate`, ikke `c.alder#c.alder` |
| 7.17 | Sjelden gruppe som forklaringsvariabel (Eritrea) | Ser at gruppen er under 1 %, bruker `i.x` |
| 7.18 | Bydel | Bruker `BEFOLKNING_BYDEL`, ikke omkoding fra grunnkrets |

## Rester fra avklarte punkter

Ikke testet, men så lite at punktene er flyttet til loggen:
- **TESTLOGG 6.5:** `python -I` på macOS.
- **TESTLOGG 8.15:** `i.` på tekst uten ledende null (`'3'`, `'11'`).
