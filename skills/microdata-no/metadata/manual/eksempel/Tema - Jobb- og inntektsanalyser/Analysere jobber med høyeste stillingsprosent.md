<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Jobb-%20og%20inntektsanalyser/Analysere%20jobber%20med%20h%C3%B8yeste%20stillingsprosent -->

# Analysere jobber med høyeste stillingsprosent

Variabler med prefiksene `ARBLONN_ARB_` og `ARBLONN_LONN_` inneholder opplysninger knyttet til alle arbeidstakerforhold registrert gjennom A-ordningen. Disse dataene har jobb/arbeidsforhold som enhetsnivå, og ikke person. Og individer kan i prinsippet ha mer enn én jobb til enhver tid. Altså vil det være flere observasjoner enn antall individer til enhver tid i datasettet.

Når man vil lage statistikk eller analyser av jobber på individnivå, er man ofte interessert i opplysninger knyttet til et utvalgt type arbeidsforhold per individ, f.eks. hovedarbeidsforholdet, jobben med høyeste stillingsprosent, jobben med høyeste avtalte arbeidstid eller jobben med høyeste månedslønn.

Eksempelet under viser hvordan man går frem for å analysere jobber med høyeste stillingsprosent per individ.

```
 require no.ssb.fdb:31 as db

// Lager jobbdatasett av aktive jobber per 16/7 2023, og finner jobben med høyeste stillingsprosent per individ
create-dataset jobbdata_max
import db/ARBLONN_ARB_YRKE_STYRK08 2023-07-16 as yrke
import db/ARBLONN_ARB_STILLINGSPST 2023-07-16 as stillingspst
import db/ARBLONN_ARB_HOVEDARBEID 2023-07-16 as hovedjobb
import db/ARBLONN_ARB_ANSETTELSESFORM 2023-07-16 as ansettelsesform
import db/ARBLONN_ARB_ARBEIDSTID 2023-07-16 as arbeidstid
import db/ARBEIDSFORHOLD_PERSON as personid

textblock
Stillingsprosent for alle aktive jobber per 16/7 2023 i jobbdatasettet:
endblock
summarize stillingspst
tabulate hovedjobb
tabulate hovedjobb, summarize(stillingspst)

// Lager en kopi av jobbdatasettet før det aggregeres opp
clone-dataset jobbdata_max jobbdata

// Aggregerer jobbdatasettet til personnivå, med opplysning om høyeste stillingsprosent per individ
collapse(max) stillingspst -> max_stillingspst, by(personid)
textblock
Stillingsprosent for jobber med høyeste stillingsprosent per individ:
endblock
summarize max_stillingspst

// Kobler opplysning om høyeste stillingsprosent på det komplette jobbdatasettet
merge max_stillingspst into jobbdata on personid

// Bruker opplysningen til å fjerne jobber i jobbdatasettet som ikke har høyest stillingsprosent
use jobbdata
keep if stillingspst == max_stillingspst
textblock
Stillingsprosent for jobber med høyeste stillingsprosent per individ.

Merk at antallet jobber øker når man selekterer på jobber med høyeste stillingsprosent i jobbdatasettet. Dette skyldes
forekomst av dubletter siden man kan ha f.eks. to 100%-stillinger (eller flere). Men omfanget av disse tilfellene er
ikke stort:
endblock
summarize stillingspst
histogram stillingspst, bin(5) percent

textblock
Stillingsprosent og avtalt arbeidstid for jobber med høyeste stillingsprosent, fordelt på ansettelsesform:
endblock
tabulate ansettelsesform, missing
tabulate ansettelsesform, summarize(stillingspst, arbeidstid)

// Aggregerer jobbdataene opp til personnivå og kobler på persondata for å kunne lage personstatistikk
collapse(mean) stillingspst arbeidstid, by(personid)

create-dataset personer
import db/BEFOLKNING_KJOENN as kjønn
merge kjønn into jobbdata

use jobbdata
textblock
Stillingsprosent og avtalt arbeidstid for jobber med høyeste stillingsprosent, fordelt på kjønn:
endblock
tabulate kjønn, missing
tabulate kjønn, summarize(stillingspst, arbeidstid)

```
