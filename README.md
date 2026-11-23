# microdata-no-hjelper

En skill for AI-assistenter og kodeagenter (Claude, GitHub Copilot, Codex, Cursor, Gemini CLI og andre)
som skal skrive skript for [microdata.no](https://www.microdata.no/), SSB og Sikts tjeneste for
registerdata. Skillen følger det åpne [Agent Skills](https://agentskills.io/)-formatet (`SKILL.md` med
referansefiler), og verktøyene er Python-skript uten avhengigheter.

Den inneholder:

- **Lokal variabelkatalog og kodelister** (alle variabler i `no.ssb.fdb`), oppdatert automatisk hver uke
- **Hele brukermanualen** som Markdown, så assistenten kan slå opp eksakt syntaks
- **Fallgruver**: en felles samling feil og overraskelser fra faktiske kjøringer. [Bidra gjerne!](CONTRIBUTING.md)
- **Kodesnutter**: frittstående, kommenterte biter med teststatus (alder, innvandringskategori, utdanning, lavinntekt, mor–barn-kobling osv.)

Skillen kjører ingenting i microdata.no. Assistenten skriver skriptet, du kjører det og limer inn
resultatet eller feilmeldingen.

## Ansvar

Skillen og KI-agenten er hjelpemidler, ikke kvalitetssikring. Agenten kan velge feil variabel, populasjon
eller periode, og resultatene kan se rimelige ut selv om de er feil. Det er du som bruker som er ansvarlig
for skriptet, for å kontrollere variabler, dekning og resultater, og for hvordan resultatene brukes. At en
kodesnutt er merket «testet», betyr at den har kjørt uten feil med en gitt datalagerversjon, ikke at den er
riktig for ditt spørsmål. Skript agenten skriver, får en linje om dette øverst.

## Installasjon

Skillen er mappen [`skills/microdata-no`](skills/microdata-no). Klon repoet ett sted og lenk mappen inn
der agenten din leter etter skills. Med en lenke (ikke kopi) får du den ukentlige metadataoppdateringen
med `git pull`.

```
git clone https://github.com/janhli/microdata-no-hjelper.git
```

**GitHub Copilot (VS Code, CLI), Codex, Cursor og Gemini CLI** leser alle personlige skills fra
`~/.agents/skills/`:

```
# macOS / Linux
mkdir -p ~/.agents/skills
ln -s "$PWD/microdata-no-hjelper/skills/microdata-no" ~/.agents/skills/microdata-no

# Windows (cmd, ingen administratorrettigheter trengs)
mkdir "%USERPROFILE%\.agents\skills"
mklink /J "%USERPROFILE%\.agents\skills\microdata-no" "%CD%\microdata-no-hjelper\skills\microdata-no"
```

For ett prosjekt i stedet: lenk mappen til `.agents/skills/microdata-no` i prosjektet. Agentene har i
tillegg egne mapper (`~/.copilot/skills`, `~/.cursor/skills`, `~/.gemini/skills`, `.github/skills`).
I Gemini CLI må skills foreløpig slås på i innstillingene. Sjekk at skillen er funnet med `/skills`.

**Claude Code:**

```
/plugin marketplace add janhli/microdata-no-hjelper
/plugin install microdata-no@microdata-no-hjelper
```

Eller lenk mappen til `~/.claude/skills/microdata-no` som over.

**claude.ai:** Last ned repoet, pakk mappen `skills/microdata-no` som zip og last den opp under
Settings → Capabilities → Skills.

**Agenter uten støtte for skills:** Legg en linje i prosjektets `AGENTS.md` (eller tilsvarende
instruksjonsfil) om at agenten skal lese `<sti>/skills/microdata-no/SKILL.md` når den skriver skript
for microdata.no. Se [`AGENTS.md`](AGENTS.md) i dette repoet for et eksempel.

Skillen bruker bare lesing av filer, søk og Python 3 (standardbiblioteket), så den virker i alle
agenter som kan det.

### Oppdatere skillen

Skillen har ikke versjonsnummer. Hver endring på GitHub er en ny versjon, og metadataene oppdateres
når microdata.no endrer seg. Ingen agent henter endringene av seg selv uten at du har slått det på:

| Installert som | Slik oppdaterer du |
|---|---|
| Klonet repo med lenke (`~/.agents/skills`, `~/.claude/skills`) | `git pull` i repoet. Gjelder fra neste økt |
| Plugin i Claude Code | `claude plugin update microdata-no@microdata-no-hjelper`, eller slå på automatisk oppdatering under `/plugin` → Marketplaces |
| Kopi av mappen, eller zip på claude.ai | Last ned på nytt og bytt ut mappen (eller last opp zip-filen på nytt) |

## Oppdatere metadata selv

Bare standardbiblioteket i Python er nødvendig:

```
cd skills/microdata-no
python verktoy/hent_variabler.py          # nye variabler (--alle: alt på nytt, ca. 6 min)
python verktoy/hent_manual.py
```

## Bidrag og vedlikehold

Alle kan foreslå endringer, men en liten gruppe vedlikeholdere godkjenner dem. Innholdet havner i
agentsesjonen til alle som bruker skillen, så alt gjennomgås før det flettes inn. Se
[CONTRIBUTING.md](CONTRIBUTING.md).

Vedlikeholdere står i [`.github/CODEOWNERS`](.github/CODEOWNERS).

### Oppsett på GitHub (én gang, for eieren av repoet)

1. **Settings → Branches → Add branch ruleset** (eller «Add rule») for `main`:
   - Require a pull request before merging
   - Require approvals: 1
   - Require review from Code Owners
   - Block force pushes
2. **Settings → Actions → General → Workflow permissions:** velg «Read and write permissions» og kryss
   av for «Allow GitHub Actions to create and approve pull requests». Da kan den ukentlige
   metadataoppdateringen åpne pull requests.
3. **Issues → Labels:** opprett etikettene `fallgruve` og `metadata`.
4. Ny vedlikeholder: gi personen rollen *Write* under Settings → Collaborators, og legg brukernavnet
   til i `CODEOWNERS`.

## Kilder og kreditering

- Variabelmetadata og manual: [microdata.no](https://microdata.no/) (SSB og Sikt). Innholdet tilhører
  dem og er hentet fra de åpne sidene. <!-- TODO: avklar lisens før publisering -->
- Kreftformer og verdier for `no.fhi.kreftregisteret`: Kreftregisterets metadatabase
  [ELVIS](https://metadata.kreftregisteret.no) (FHI), hentet med `verktoy/kreftregisteret.py hent`.
- Kreftformene i Cancer in Norway (`metadata/fhi/kreftregisteret/cancer_in_norway.csv`): tabell 2.3 i
  [Cancer in Norway 2025](https://www.fhi.no/publ/2026/cancer-in-norway-2025/) (FHI), skrevet av fra gjengivelsen på
  [fhi.no](https://fhi.no/is/ncd/dodelighet-sykelighet/kreft).
- Kommune-, region-, grunnkrets- og næringskoder: [SSB Klass](https://www.ssb.no/klass/).
- Kodeeksempler: [JOSliper/Microdata-skript](https://github.com/JOSliper/Microdata-skript) (Trøndelag)
  er bare lenket til, ikke kopiert (repoet har ingen lisens).

Dette er et uoffisielt fellesskapsprosjekt og ikke tilknyttet SSB eller Sikt.
