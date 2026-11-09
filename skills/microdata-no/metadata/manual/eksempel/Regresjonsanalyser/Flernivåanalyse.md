<!-- Kilde: https://microdata.no/manual/eksempel/Regresjonsanalyser/Flerniv%C3%A5analyse -->

# Flernivåanalyse

Skriptet under viser et eksempel på hvordan man tilrettelegger data for og kjører flernivåanalyser.

To tilfeller demonstreres: Geografiske flernivåer, og nivåer knyttet til utdanning og yrke.

Ellers er populasjon og variabeloppsett det samme i begge tilfeller, riktignok med litt justeringer for å unngå at man bruker samme variabel både som forklaringsvariabel og gruppevariabel (må unngås). Responsvariabel i begge tilfellene er lønn.

Merk at variansestimatene for gruppevariablene landsdel og fylke blir like i eksempelet under. Dette skyldes mest sannsynlig at variansen for disse to variablene er tilnærmet like og at de fanger opp svært lik informasjon om variansen i lønn. En løsning på dette kan være å droppe den ene gruppevariabelen og kjøre en tonivåanalyse. I det andre tilfellet med gruppevariabler for utdanningsnivå og yrkesgruppe er variansen mer ulik for de to gruppevariablene, og dermed blir også forskjellen i variansestimatene i flernivåmodellen større.

Kommandoene `boxplot` og `histogram` er gode verktøy for å studere gruppevise fordelinger mht. responsvariabelen. Du benytter i praksis responsvariabelen (lønn) som input til kommandoen, og grupperer på aktuelle gruppevariabler i tråd med syntakskonvensjonene for den aktuelle kommandoen. I skriptet under brukes `boxplot` for å studere gruppevariablene.

Om du bruker kommandoen `tabulate fylke, summarize(lønn) std`, vises konkrete tall for standardavvik fordelt på hver gruppe i gruppevariabelen fylke, jfr. eksemplene under (overordnet standardavvik for lønn finner du nederst i samme tabell). Det samme kan gjøres for øvrige gruppevariabler, som landsdel. Ved å sammenlikne standardavvikene for fylke og landsdel ser man tydelig at forskjellene i standardavvik ikke er store verken innad for hver gruppevariabel, eller mellom de to gruppevariablene. Dette er ikke tilfelle for gruppevariablene utdanningsnivå og yrkesgruppe.

```
 require no.ssb.fdb:30 as db

// Importerer og tilrettelegger data for flernivåanalyse
create-dataset mldata
import db/BOSATTEFDT_BOSTED 2022-12-31 as kommune
import db/BEFOLKNING_FOEDSELS_AAR_MND as fdato
generate alder = 2022 - int(fdato/100)
keep if inrange(alder,20,60)

import db/BEFOLKNING_KJOENN as kjønn
import db/INNTEKT_LONN 2022-12-31 as lønn
import db/SIVSTANDFDT_SIVSTAND 2022-12-31 as sivstand
import db/BEFOLKNING_BARN_I_REGSTAT_FAMNR 2022-01-01 as ant_barn
import db/NUDB_SOSBAK as sos_bakgrunn
import db/NUDB_BU 2022-09-01 as utd
import db/REGSYS_ARB_YRKE_STYRK08 2022-11-16 as yrke

generate mann = kjønn == '1'
generate gift = sivstand == '2'
generate utdnivå = substr(utd,1,1)
generate yrkesgr = substr(yrke,1,1)
generate fylke = substr(kommune,1,2)
generate sos_bakgrunn_høy = inlist(sos_bakgrunn,'1','2')

generate region = 1 if inlist(fylke,'03','30','34','38') // Østlandet
replace region = 2 if inlist(fylke,'11','42') //Sørlandet og Rogaland
replace region = 3 if inlist(fylke,'46') // Vestlandet
replace region = 4 if inlist(fylke,'15','50') // Midtnorge
replace region = 5 if inlist(fylke,'18','54') // Nordnorge

generate landsdel = 1 if inlist(region,1,2,3)
replace landsdel = 2 if inlist(region,4,5)

define-labels landsdeltxt 1 "Sør-Norge" 2 "Midt-/Nord-Norge"
assign-labels landsdel landsdeltxt

destring fylke utdnivå yrke yrkesgr

define-labels fylketext \
	3 "Oslo" \
	11 "Rogaland" \
	15 "Møre og Romsdal" \
	18 "Nordland" \
	30 "Viken" \
	34 "Innlandet" \
	38 "Vestfold og Telemark" \
	42 "Agder" \
	46 "Vestland" \
	50 "Trøndelag" \
	54 "Troms og Finnmark"
assign-labels fylke fylketext

generate utdgruppe = 1 if inrange(utdnivå,0,4)
replace utdgruppe = 2 if inrange(utdnivå,5,6)
replace utdgruppe = 3 if inrange(utdnivå,7,8)

define-labels utdgrtxt 1 "Lav utd" 2 "Middels utd" 3 "Høy utd"
assign-labels utdgruppe utdgrtxt

//  --------- Case 1: Lønn vs landsdel og fylke -------------
tabulate fylke landsdel

boxplot lønn, over(fylke)
boxplot lønn, over(landsdel)

tabulate fylke, summarize(lønn) std
tabulate landsdel, summarize(lønn) std

// Ettnivåanalyse (OLS)
regress lønn mann gift ant_barn sos_bakgrunn_høy alder i.utdgruppe

// Tonivåanalyse
regress-mml lønn mann gift ant_barn sos_bakgrunn_høy alder i.utdgruppe by landsdel
regress-mml lønn mann gift ant_barn sos_bakgrunn_høy alder i.utdgruppe by fylke

// Trenivåanalyse
regress-mml lønn mann gift ant_barn sos_bakgrunn_høy alder i.utdgruppe by landsdel fylke

//  ---------- Case 2: Lønn vs utdanningsnivå og yrkeshierarki ---------
tabulate utdnivå, missing
tabulate utdgruppe, missing
tabulate yrkesgr, missing

boxplot lønn, over(utdnivå)
boxplot lønn, over(utdgruppe)
boxplot lønn, over(yrkesgr)

tabulate utdnivå, summarize(lønn) std
tabulate utdgruppe, summarize(lønn) std
tabulate yrkesgr, summarize(lønn) std

// Ettnivåanalyse (OLS)
regress lønn mann gift ant_barn sos_bakgrunn_høy alder i.fylke

// Tonivåanalyse
regress-mml lønn mann gift ant_barn sos_bakgrunn_høy alder i.fylke by utdnivå
regress-mml lønn mann gift ant_barn sos_bakgrunn_høy alder i.fylke by yrkesgr

// Trenivåanalyse
regress-mml lønn mann gift ant_barn sos_bakgrunn_høy alder i.fylke by utdnivå yrkesgr

```
