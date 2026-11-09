# Bidra

Det viktigste bidraget er **fallgruver**: feil og overraskelser du har møtt i microdata.no som ikke
står tydelig i manualen. Én fallgruve kan spare neste person (og neste AI-assistent) for en time.

## Slik bidrar du med en fallgruve

**Enklest:** Opprett en issue med malen «Ny fallgruve». Da formulerer og legger vi den inn.

**Direkte:** Lag en pull request mot
[`skills/microdata-no/referanser/fallgruver.md`](skills/microdata-no/referanser/fallgruver.md):

1. Legg den under riktig overskrift, eller lag en ny.
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

Har du kjørt en snutt som står som `utkast` eller `testet i større skript` uten feil? Send en liten
pull request som oppgraderer statuslinjen. Det er et svært nyttig bidrag.

## Viktig: ingen registerdata

Ikke legg inn resultater eller tall fra microdata.no i issues eller pull requests, bare kode,
feilmeldinger og beskrivelser. Tabeller fra analysemiljøet er underlagt microdata.no sine vilkår.

## Metadata og manual

`skills/microdata-no/metadata/` oppdateres hver uke av en GitHub Action, som åpner en pull request
når noe er endret. Ikke rediger filene der for hånd. Feil i hentescriptene rettes i `skills/microdata-no/verktoy/`.
