# Evaluering av skillen (TESTLISTE del 7)

Måler om en agent med skillen `microdata-no` gjør bedre valg enn en agent uten. Hver mappe er én
oppgave i formatet som `skill-creator` og `claude plugin eval` leser:

| Fil | Innhold |
|---|---|
| `prompt.md` | Oppgaven slik en bruker ville skrevet den (under innstillingsblokken) |
| `case.yaml` | Navn, punkt i TESTLISTE og forventet resultat |
| `graders/NN-*.md` | Ett kriterium per fil, som enten er oppfylt eller ikke |

Mappen ligger utenfor `skills/microdata-no/`, så den følger ikke med når skillen installeres, og en
agent med skillen finner ikke fasiten der. **Når oppgavene kjøres, må agenten ikke lese `evals/`**, si
det i instruksen til underagenten, eller kjør i en kopi uten mappen.

## Oppgavene

| Mappe | TESTLISTE | Hva den måler |
|---|---|---|
| `dekning-aap-2010-2024` | 7.1 | Sjekker `fra`/`til` (SKATT_BA_AAP starter 2015) |
| `pseudonym-mor-mangler` | 7.2 | Bruker ikke pseudonymisert ID i uttrykk |
| `kommune-2015-mot-2024` | 7.3 | `kommuneomkoding.py`, melder om delte kommuner |
| `inntektsgrupper-sysmiss` | 7.4 | Manglende verdier havner ikke stille i en gruppe |
| `feil-statistikkopsjon` | 7.5 | `median` → `p50` i `tabulate ..., summarize()` |
| `region-politidistrikt` | 7.6 | `regionomkoding.py`, ingen sluttregel i samme recode |
| `naering-hovedomrader` | 7.7 | Oppdager at næring mangler etter 2019, `klass.py` med riktig `--dato` |
| `usikkerhet-merket` | 7.8 | Skiller kontrollert, testet og ukjent |
| `logit-sysselsatt` | 7.9 | `logit`, utfall som 0/1, `mfx`/`or` |
| `faktor-og-cluster` | 7.10 | `i.`, `cluster()` uten `robust` |
| `tid-til-hendelse` | 7.11 | Populasjon i risiko, sensurering, hazard |
| `diff-in-diff` | 7.12 | Etter-dummy for alle, parallelle trender |
| `instrumentvariabel` | 7.13 | `( endogen = instrument )`, gyldighet |
| `sjeldent-utfall-logit` | 7.15 | Utfall under 1 %: advarer, foreslår `cox` |
| `andregradsledd` | 7.16 | `alder2` med `generate`, ikke `c.alder#c.alder` |
| `sjelden-gruppe-i-x` | 7.17 | Gruppe under 1 %: `i.x` |
| `bydel-oslo` | 7.18 | `BEFOLKNING_BYDEL` i stedet for grunnkrets |

7.14 (andre agenter: Copilot, Codex, Cursor) er ikke med. Den må kjøres for hånd i de verktøyene.

## Kjøring

- **Med underagenter (trinn 2 i planen):** én agent med skillen og én uten per oppgave. Uten skill: be
  agenten ikke lese `skills/` eller `evals/`. Svarene lagres og vurderes mot `graders/` (se under), og
  resultatet føres i TESTLOGG del 7.
- **Med CLI:** `claude plugin eval` kjører mappene med og uten skillen fra skillmappen. Kopier da
  `evals/` til `skills/microdata-no/evals/` midlertidig (uten `resultater/`, som ikke er en oppgave), og
  fjern den etterpå. Kjøringene koster.

## Resultater

Hver runde har sin mappe, `resultater/<runde>/`:

| Fil | Innhold |
|---|---|
| `svar/<oppgave>/<betingelse>-<kjøring>.md` | Sluttsvaret og skriptet, **lagret før vurderingen**. Øverst: modell, dato, om skillen var med, og commit for skillen. Ta ut lokale stier og tråd-ID-er. Svarene har skript, aldri resultater fra microdata.no |
| `poeng.csv` | `oppgave;nr;betingelse;kjoring;poeng;merknad`, én rad per kriterium. `nr` er de to første sifrene i filnavnet i `graders/` |

Betingelsen er `med`, `uten` eller navnet på agenten (`codex`). `python evals/poeng.py <runde>` summerer, og
`tests/test_evals.py` sjekker at svarene er lagret og at poengene viser til kriterier som finnes.

**Kriterier som krever skillen.** [`kriterier.csv`](kriterier.csv) merker dem, så sammenligningen med og uten skill
kan vises uten dem:
- `verktoy`: krever et av skillens egne verktøy. En agent uten skillen kan ikke få poeng.
- `fil`: viser til filer i skillen, men kan oppfylles med det samme oppslaget på nettet.

Endres et kriterium etter en runde, får det gamle et eget nummer (`r1-03`), så poengene fra runden fortsatt kan summeres.

| Runde | Betingelse | Alle kriterier | Uten `verktoy` | Uten `verktoy` og `fil` |
|---|---|---|---|---|
| 1 | med | 50/53 (94 %) | 46/49 (94 %) | 43/46 (93 %) |
| 1 | uten | 34/53 (64 %) | 34/49 (69 %) | 33/46 (72 %) |

Runde 1 er én kjøring per oppgave, så vi vet ikke hvor mye som er støy. Svarene derfra ble ikke lagret og kan ikke
vurderes på nytt. Vurderingen står i [`resultater/runde1.md`](resultater/runde1.md). Av 7.14 (Codex og Copilot CLI) er
de fire svarene som teller, lagret. Vurderingen står i [`resultater/7_14_andre_agenter.md`](resultater/7_14_andre_agenter.md).

Kriteriene sjekker valgene agenten gjør, ikke om skriptet kjører i microdata.no. Kjør gjerne et utvalg
av skriptene for hånd etterpå.
