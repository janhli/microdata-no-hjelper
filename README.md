# microdata-no-hjelper

En skill for AI-assistenter (Claude Code, claude.ai og andre) som skal skrive skript for
[microdata.no](https://www.microdata.no/), SSB og Sikts tjeneste for registerdata.

Den inneholder:

- **Lokal variabelkatalog og kodelister** (alle variabler i `no.ssb.fdb`), oppdatert automatisk hver uke
- **Hele brukermanualen** som Markdown, så assistenten kan slå opp eksakt syntaks
- **Fallgruver**: en felles samling feil og overraskelser fra faktiske kjøringer. [Bidra gjerne!](CONTRIBUTING.md)
- **Kodesnutter**: frittstående, kommenterte biter med teststatus (alder, innvandringskategori, utdanning, lavinntekt, mor–barn-kobling osv.)

Skillen kjører ingenting i microdata.no. Assistenten skriver skriptet, du kjører det og limer inn
resultatet eller feilmeldingen.

## Installasjon

**Claude Code:**

```
/plugin marketplace add <github-bruker>/microdata-no-hjelper
/plugin install microdata-no@microdata-no-hjelper
```

**claude.ai:** Last ned repoet, pakk mappen `skills/microdata-no` som zip og last den opp under
Settings → Capabilities → Skills.

**Andre verktøy (Copilot, Codex, Cursor):** Klon repoet inn i prosjektet ditt og pek til
`skills/microdata-no/SKILL.md` i `AGENTS.md` eller tilsvarende.

## Oppdatere metadata selv

Bare standardbiblioteket i Python er nødvendig:

```
cd skills/microdata-no
python verktoy/hent_variabler.py          # nye variabler (--alle: alt på nytt, ca. 6 min)
python verktoy/hent_manual.py
```

## Bidrag og vedlikehold

Alle kan foreslå endringer, men en liten gruppe vedlikeholdere godkjenner dem. Innholdet havner i
Claude-sesjonen til alle som bruker skillen, så alt gjennomgås før det flettes inn. Se
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
- Kodeeksempler: [JOSliper/Microdata-skript](https://github.com/JOSliper/Microdata-skript) (Trøndelag)
  er bare lenket til, ikke kopiert (repoet har ingen lisens).

Dette er et uoffisielt fellesskapsprosjekt og ikke tilknyttet SSB eller Sikt.
