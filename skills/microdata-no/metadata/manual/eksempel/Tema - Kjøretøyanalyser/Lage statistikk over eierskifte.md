<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Kj%C3%B8ret%C3%B8yanalyser/Lage%20statistikk%20over%20eierskifte -->

# Lage statistikk over eierskifte

Skriptet under viser hvordan man kan lage statistikk på antall eierskifter av kjøretøy (personbiler) i løpet av et år.

Siden det ikke er tillatt å kjøre analyser på pseudonymiserte identifikatorvariabler som KJORETOY_KJORETOYID_FNR, kan man i stedet lage en pseudo-personidentifikator som består av produktet av et sett med relativt unike personopplysninger. Vi har i dette tilfellet valgt variablene fødselsdato, beregnet bruttoformue, seksifret utdanningskode for høyeste fullførte utdanning, og bostedskommune. Ved å multiplisere disse fire variablene (alle må være numeriske) får man i prinsippet et tall som skal være unikt for så og si alle individer.

Siste trinn består i å koble pseudo-personidentifikatorene på kjøretøydatasettet via eieropplysningen for de respektive kjøretøy (KJORETOY_KJORETOYID_FNR) for de to årene man måler fra-til. Dersom eieridentifikatoren for et kjøretøy er lik for de to årene, er altså eier den samme. Dersom eieridentifikatoren derimot har missingverdi for det siste året (2023), kan man konkludere med at kjøretøyet har skiftet eier. Kjøretøyidentifikatoren, altså enhetstypen til kjøretøydatasettet, er nemlig en kompositt av kjøretøyets registreringsnummer og eiers fødselsnummer, slik at dersom eier endres, vil også kjøretøyidentifikator endre seg, og den eksisterende identifikatorverdien blir dermed ugyldig i det kjøretøyet får ny eier.

```
 require no.ssb.fdb:41 as ds

//Oppretter personbildatasett med eierinfo i 2022 og 2023
create-dataset biler
import ds/KJORETOY_KJORETOYID_FNR 2022-12-31 as eier22
import ds/KJORETOY_KJORETOYID_FNR 2023-12-31 as eier23
import ds/KJORETOY_KJT_GRUP 2022-12-31 as klasse
keep if klasse == '101' // Behold kun personbiler


//Oppretter persondatasett (totalpopulasjon) for å lage pseudo-personid
create-dataset totalpopulasjon
import ds/BEFOLKNING_FOEDSELS_AAR_MND as fdato
import ds/INNTEKT_BER_BRFORM 2022-12-31 as formue
import ds/NUDB_BU 2022-12-31 as utd
import ds/BOSATTEFDT_BOSTED 2022-12-31 as kommune
destring utd kommune

//Lager en pseudo-personid vha. de unike variablene fødselsdato, formue, høyeste fullførte utdanning og bostedskommune, og kobler på biler-datasettet for årene 2022 og 2023
for i in formue utd kommune
  replace $i = 1 if sysmiss($i)
end

generate pseudoid22 = fdato * formue * utd * kommune
clone-variables pseudoid22 -> pseudoid23

merge pseudoid22 into biler on eier22
merge pseudoid23 into biler on eier23


//Bruker opplysningene til å finne biler som skiftet eier i 2023 
use biler
drop if sysmiss(pseudoid22) // Fjern om bilen ikke hadde eieropplysninger ved utgangen av 2022

generate eierskifte23 = 0 if pseudoid22 == pseudoid23
replace eierskifte23 = 1 if sysmiss(pseudoid23)

define-labels skiftetlbl 0 'Samme eier' 1 'Eierskifte'
assign-labels eierskifte23 skiftetlbl

textblock
Antall eierskifter av personbiler i løpet av 2023
endblock
tabulate eierskifte23, missing

```
