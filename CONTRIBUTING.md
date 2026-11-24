# Bidra

Det viktigste bidraget er **fallgruver**: feil og overraskelser du har møtt i microdata.no som ikke
står tydelig i manualen. Én fallgruve kan spare neste person (og neste AI-assistent) for en time.

## Slik bidrar du med en fallgruve

**Enklest:** Opprett en issue med malen «Ny fallgruve». Da formulerer og legger vi den inn.

**Direkte:** Lag en pull request mot
[`skills/microdata-no/referanser/fallgruver.md`](skills/microdata-no/referanser/fallgruver.md):

1. Legg den under riktig overskrift, eller lag en ny. Gjelder den bare analyse, geografi, Klass eller FHI-data,
   legges den i temafilen (`fallgruver_analyse.md`, `fallgruver_geografi.md`, `fallgruver_klass.md` eller
   `fallgruver_fhi.md`), så hovedfilen holdes kort.
2. Bruk formatet **Symptom** (gjerne med eksakt feilmelding), **Årsak** og **Løsning**.
3. Oppgi datalagerversjon/dato hvis fallgruven kan bli utdatert (f.eks. data som mangler for siste år).
4. Hold den kort og generell. Skriv om hva som gjelder alle, ikke ditt spesifikke prosjekt.

## Slik bidrar du med en kodesnutt

Kodesnutter ligger i [`skills/microdata-no/kodesnutter/`](skills/microdata-no/kodesnutter/).

1. Kopier toppseksjonen fra en eksisterende snutt: tittel, status, variabler med kilde-URL, hva den
   lager, og fallgruver.
2. Snutten skal være **frittstående**: den har `require`, oppretter sitt eget datasett og avslutter med
   en `textblock` og en `tabulate`, så den kan limes inn og kjøres direkte.
3. Grupperinger skal alltid ha en kategori for ukjent (`sysmiss`).
4. Sett status ærlig: `testet` (kjørt alene uten feil), `testet i større skript` eller `utkast`, med
   datalagerversjon og måned.
5. Legg den inn i tabellen i `kodesnutter/README.md`, og fjern den fra ønskelisten hvis den sto der.
6. Kjør `python skills/microdata-no/verktoy/sjekk_skript.py --snutt <snutt>`. Testene gjør det samme for
   alle snuttene og feiler på det sjekken finner.

Har du kjørt en snutt som står som `utkast` eller `testet i større skript` uten feil? Send en liten
pull request som oppgraderer statuslinjen. Det er et svært nyttig bidrag.

## Viktig: ingen registerdata

Ikke legg inn resultater eller tall fra microdata.no i issues eller pull requests, bare kode,
feilmeldinger og beskrivelser. Tabeller fra analysemiljøet er underlagt microdata.no sine vilkår.

## Metadata og manual

`skills/microdata-no/metadata/` oppdateres hver uke av en GitHub Action, som åpner en pull request
når noe er endret. Ikke rediger filene der for hånd. Feil i hentescriptene rettes i `skills/microdata-no/verktoy/`.

## Tester

Endrer du noe i `skills/microdata-no/verktoy/`, kjør testene fra repoets rot (ingen avhengigheter):

    python -m unittest discover -s tests

De kjøres også av GitHub Actions ved push og pull request. Testene for `klass.py` bruker SSB Klass og
hoppes over uten nett (eller med `UTEN_NETT=1`). Testene sjekker at `recode`-utskriften gir riktig
resultat slik manualen beskriver `recode`. Om microdata.no oppfører seg slik, står i
[`TESTLISTE.md`](TESTLISTE.md).

## Oppsett på GitHub (én gang, for eieren av repoet)

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
