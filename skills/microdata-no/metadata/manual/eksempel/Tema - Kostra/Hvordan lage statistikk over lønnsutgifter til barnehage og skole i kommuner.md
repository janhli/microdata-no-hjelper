<!-- Kilde: https://microdata.no/manual/eksempel/Tema%20-%20Kostra/Hvordan%20lage%20statistikk%20over%20l%C3%B8nnsutgifter%20til%20barnehage%20og%20skole%20i%20kommuner -->

# Hvordan lage statistikk over lønnsutgifter til barnehage og skole i kommuner

Skriptet under viser hvordan man kan bruke KOSTRA-data i microdata.no til å lage statistikk over lønnsutgifter til barnehager, grunnskolen og SFO i hver enkelt kommune.

Siden KOSTRA-dataene har kommuner som enhetstype, må man koble de sammen med et persondatasett som inneholder bostedskommune, slik at man kan gruppere og lage kommunefordelte tall.

```
 textblock
Lager noen eksempler på analyser av barnehage, grunnskole/SFO basert på Kostra-data som vi har i vår database.

Merk at FGK-kodene som brukes i eksempelet er sammenslåtte koder som fanger opp litt mer enn bare drift av hhv. barnehage og grunnskole:

- FGK7 = 201 Barnehage + 211 Styrket tilbud til førskolebarn + 221 Barnehagelokaler og skyss
- FGK8b = 202 Grunnskole + 215 Skolefritidstilbud + 222 Skolelokaler + 223 Skoleskyss + 213 Voksenopplæring

Tallene er i utgangspunktet 100% konsistente med tallene for "Lønnsutgifter fratrukket sykelønnsrefusjon" i SB-tabell 12362: https://www.ssb.no/statbank/table/12362. Men i microdata.no kjøres det winsorisering på beløpstallene, slik at kommunene med de aller laveste eller høyeste beløpene settes til en grenseverdi (hhv. første og siste percentil). For kommunene dette gjelder, kan de sanne tallene finnes i den nevnte Statistikkbank-tabellen.
endblock

require no.ssb.fdb:57 as db

let år = 2023

//Lager først et kommunedatasett basert på bosattkommune per 31/12 det aktuelle året
create-dataset bosted
import db/BOSATTEFDT_BOSTED date_fmt($år,12,31) as kommune
aggregate(count) kommune -> bosatte, by(kommune)

//Henter så relevante KOSTRA-data for samme år (årlige akkumulerte verdier)
create-dataset kostradata
import db/SB12362_KOSTRA_LONNSUTGIFTER_F_BARNEHAGE date_fmt($år) as barnehage
import db/SB12362_KOSTRA_LONNSUTGIFTER_F_GRUNNSKOLE date_fmt($år) as grunnskole

//Kobler KOSTRA-opplysningene på kommunedatasettet
merge barnehage grunnskole into bosted on kommune

//Lager til slutt kommunestatistikk for det aktuelle året: 
use bosted
generate barnehage_per_pers = barnehage / bosatte
generate grunnskole_per_pers = grunnskole / bosatte

textblock
Totale lønnsutgifter til barnehage i 1000 kr (FGK7) og antall bosatte i hver kommune
endblock
tabulate kommune, summarize(barnehage) mean freq

textblock
Lønnsutgifter til barnehage per person i 1000 kr (FGK7) i hver kommune
endblock
tabulate kommune, summarize(barnehage_per_pers)

textblock
Antall personer fordelt på lønnsutgifter til barnehage per person i kommunen de bor i.
Merk at de aller laveste og høyeste verdiene winsoriseres og settes til grenseverdien til hhv. første og siste percentil.
endblock
histogram barnehage_per_pers, freq

textblock
Lønnsutgifter til barnehage per person i 1000 kr (FGK7) i hver kommune.
Topp 10 og bottom 10 kommuner sortert etter beløp per person.
Merk at de aller laveste og høyeste verdiene winsoriseres og settes til grenseverdien til hhv. første og siste percentil. Derfor er en del av tallene identiske. Dette er tall som i realiteten er lavere/høyere. De faktiske tallene for de det gjelder kan finnes i Statistikkbank-tabell 12362: https://www.ssb.no/statbank/table/12362. 
endblock
tabulate kommune, summarize(barnehage_per_pers) rowsort() bottom(10)
tabulate kommune, summarize(barnehage_per_pers) rowsort() top(10)


textblock
Totale lønnsutgifter til grunnskole og SFO i 1000 kr (FGK8b) og antall bosatte i hver kommune
endblock
tabulate kommune, summarize(grunnskole) mean freq

textblock
Lønnsutgifter til grunnskole og SFO per person i 1000 kr (FGK8b) i hver kommune
endblock
tabulate kommune, summarize(grunnskole_per_pers)

textblock
Antall personer fordelt på lønnsutgifter til grunnskole og SFO i kommunen de bor i.
Merk at de aller laveste og høyeste verdiene winsoriseres og settes til grenseverdien til hhv. første og siste percentil.
endblock
histogram grunnskole_per_pers, freq

textblock
Lønnsutgifter til grunnskole og SFO per person i 1000 kr (FGK8b) i hver kommune.
Topp 10 og bottom 10 kommuner sortert etter beløp per person.
Merk at de aller laveste og høyeste verdiene winsoriseres og settes til grenseverdien til hhv. første og siste percentil. Derfor er en del av tallene identiske. Dette er tall som i realiteten er lavere/høyere. De faktiske tallene for de det gjelder kan finnes i Statistikkbank-tabell 12362: https://www.ssb.no/statbank/table/12362.
endblock
tabulate kommune, summarize(grunnskole_per_pers) rowsort() bottom(10)
tabulate kommune, summarize(grunnskole_per_pers) rowsort() top(10)

```
