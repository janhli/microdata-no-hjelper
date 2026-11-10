---
name: vedlikehold
description: Gjennomgang av vedlikeholdsbehov i microdata-no-hjelper. Ser over GitHub-issues, åpne pull requests, mislykkede workflow-kjøringer, TESTLISTE.md og teststatus i kodesnuttene, og foreslår en prioritert arbeidsliste. Bruk når brukeren ber om å se over issues, testlisten, «hva bør vi gjøre», eller skriver /vedlikehold.
---

# Vedlikeholdsøkt

Hukommelsen mellom økter er repoet: `TESTLISTE.md`, GitHub-issues, `skills/microdata-no/referanser/fallgruver.md`,
statuslinjene i `skills/microdata-no/kodesnutter/` og git-historikken. Les dem, ikke anta.

## 1. Samle status (kjør fra repoets rot)

```
git status --short && git log --oneline -5
gh issue list --state open --limit 50
gh pr list --state open
gh run list --limit 15
python -I -c "import json;print(json.load(open('skills/microdata-no/metadata/datalager.json',encoding='utf-8'))['versions'][0]['version'])"
grep -h "^// Status:" skills/microdata-no/kodesnutter/*.txt
```

Les så `TESTLISTE.md` (bare åpne punkter, de uten avkrysning) og eventuelle issues som trenger innhold
(`gh issue view <nr>`).

Se etter:
- **Issues:** `nyhet` (innlegg fra microdata.no som skal vurderes), `fallgruve` (innspill fra brukere), andre.
- **PR-er:** Den ukentlige metadata-PR-en (`automatisk/metadata`). Se på diffen i `variabler.csv` og
  manualsider med reelle endringer (`git diff -w --ignore-blank-lines`). GitHub viser ikke differ over
  300 filer, så hent grenen lokalt.
- **Workflows:** Mislykkede kjøringer av «Tester», «Oppdater metadata og manual» og «Nyheter».
  «action_required» på en bot-PR er ikke en feil (GitHub venter på godkjenning).
- **Snutter:** Status testet med en eldre datalagerversjon enn den gjeldende. Det er ikke feil, men
  kandidater for ny kjøring.
- **Endringer i manualen** som kan påvirke fallgruver eller snutter (f.eks. nye regler for `collapse`).

## 2. Prioriter

Rekkefølge:
1. Det som kan gi **feil resultat uten at det synes** (P1 i testlisten, feil i verktøy eller snutter).
2. Det som **blokkerer annet** (f.eks. TESTLISTE 1.9: antakelsen om `recode` som omkodingsverktøyene bygger på).
3. Det som **stopper skript** (P2), og ventende metadata-PR-er.
4. **Raske gevinster** (nyhetsissues som bare trenger «ingen handling», små rettelser).
5. Kvalitetssjekk (P3) og ønskelisten i `kodesnutter/README.md`.

## 3. Presenter

Kort status (én linje per kilde), deretter forslag delt i tre grupper, hver med begrunnelse og omtrentlig
innsats:

- **Kan gjøres nå uten microdata.no:** kode, dokumentasjon, fallgruver, vurdering av nyhetsissues.
- **Krever kjøring i microdata.no:** samle flere testpunkter i **ett** skript per økt (se under).
- **Trenger beslutning fra brukeren.**

Avslutt med et konkret forslag til hva vi starter med, og spør. Ikke start arbeidet før brukeren har valgt.

## 4. Testskript for microdata.no

Brukeren kjører, du tolker. Lag ett skript som dekker flere punkter i testlisten:
- Følg `skills/microdata-no/SKILL.md` og les `fallgruver.md` først.
- Én `textblock` per test med punktnummer (f.eks. «Test 1.9»), hva som testes, og hva resultatet
  **skal** vise hvis antakelsen stemmer.
- Unngå små grupper (avsløringskontroll, 10-enhetsregelen). Ett feilende punkt skal helst ikke stoppe
  resten. Sett det mest usikre sist.
- Oppgi datalagerversjon i `require` (gjeldende fra `datalager.json`, men spør om brukerens miljø er på
  samme versjon).
- For kodesnuttene: `python .claude/skills/vedlikehold/samle_snutter.py > testskript.txt` setter alle
  snutter som ikke er testet med gjeldende versjon sammen til ett skript (eller bare dem du nevner).
  Snuttene tas med ordrett, og datasettene slettes mellom dem.

## 5. Etter arbeidet

- **Testlisten:** Kryss av med versjon og dato. Når en test avklarer noe, flytt konklusjonen til
  `fallgruver.md` (symptom, årsak, løsning, versjon/dato) og fjern eller forkort punktet.
- **Snutter:** Oppdater statuslinjen (`testet (no.ssb.fdb:<v>, <år-mnd>)`) bare når snutten faktisk er kjørt.
- **Issues:** Lukk med en kommentar om hva som ble gjort (`gh issue close <nr> --comment "..."`).
  Nyhetsinnlegg skal vurderes og omformes, ikke kopieres inn i skillen.
- **Verktøy:** Kjør `python -m unittest discover -s tests` etter endringer i `skills/microdata-no/verktoy/`.
- **Commit og push bare når brukeren ber om det.** Avslutt økten med en kort oppsummering av hva som er
  endret og hva som gjenstår.
