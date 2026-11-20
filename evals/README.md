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
| `naering-hovedomrader` | 7.7 | `klass.py` med riktig `--dato` |
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
  agenten ikke lese `skills/` eller `evals/`. Svarene vurderes mot `graders/`, og resultatet føres i
  TESTLISTE del 7.
- **Med CLI:** `claude plugin eval` kjører mappene med og uten skillen fra skillmappen. Kopier da
  `evals/` til `skills/microdata-no/evals/` midlertidig, og fjern den etterpå. Kjøringene koster.

Kriteriene sjekker valgene agenten gjør, ikke om skriptet kjører i microdata.no. Kjør gjerne et utvalg
av skriptene for hånd etterpå.
