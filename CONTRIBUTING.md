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

Mønstre (oppskrifter som fungerer) legges til i `referanser/monstre.md` på samme måte.

## Viktig: ingen registerdata

Ikke legg inn resultater eller tall fra microdata.no i issues eller pull requests, bare kode,
feilmeldinger og beskrivelser. Tabeller fra analysemiljøet er underlagt microdata.no sine vilkår.

## Metadata og manual

`skills/microdata-no/metadata/` oppdateres automatisk hver uke av en GitHub Action. Ikke rediger
filene der for hånd. Feil i hentescriptene rettes i `skills/microdata-no/verktoy/`.
