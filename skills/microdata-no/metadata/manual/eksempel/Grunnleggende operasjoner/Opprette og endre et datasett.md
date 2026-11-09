<!-- Kilde: https://microdata.no/manual/eksempel/Grunnleggende%20operasjoner/Opprette%20og%20endre%20et%20datasett -->

# Opprette og endre et datasett

Man lager et standard wide-format datasett ved å

1. lage en kobling mot en database ved hjelp av kommandoen `require` (trenger bare gjøres en gang per skript),
1. opprette et tomt datasett ved hjelp av kommandoen `create-dataset`,
1. og importere minst en variabel inn i det tomme datasettet ved hjelp av kommandoen `import`.

Med mindre man har spesielle behov, anbefales det å koble seg mot den nyeste versjonen av den aktuelle databasen. Man får da tilgang til alle de nyeste variablene og de siste oppdateringene. Versjonsnummeret finner man ved å se oppe til venstre i [variabeloversikten](https://microdata.no/discovery/variables?sortBy=NAME&sortType=ASC).

Man kan bare importere en variabel om gangen når man lager et wide-format datasett gjennom kommandoen `import`. Denne gjør to ting:

- Henter dataobservasjoner for et gitt tidspunkt (måletidspunkt angis ikke for faste opplysninger som f.eks. kjønn)
- Kobler dataene mot gjeldende populasjon via en unik innebygd enhetsidentifikatorserie (ved første import hentes alle observasjoner for det gitte tidspunktet)

TIPS

Det er mulig å overstyre det såkalte left-join-prinsippet ved å bruke import-opsjonen `outer_join`. Da vil man i stedet hente alle observasjoner for det gitte tidspunktet, også for dem som ikke finnes i datasettpopulasjonen fra før. Dette kan være nyttig dersom man ønsker å hente data på alle individer over et lengre tidsrom (gjennom gjentatte målinger for en gitt variabel), og ikke bare for dem som hadde en observasjon ved første måletidspunkt. Kapittel 2.3.1 i brukermanualen forklarer mer om dette.

Etter at datasettet er opprettet, kan man endre det etter behov. For eksempel kan man endre navn på datasett eller variabler, fjerne variabler, eller fjerne observasjoner.

Eksempel:

```
 require no.ssb.fdb:23 as db

create-dataset demografidata
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
import db/SIVSTANDFDT_SIVSTAND 2020-01-01 as sivstand
import db/INNTEKT_BRUTTOFORM 2020-01-01 as formue

// Endrer navn på variabler ved å legge til årsangivelse
rename sivstand sivstand20
rename formue formue20

// Sletter variabelen kjonn fra datasettet
drop kjønn

// Beholder kun gifte personer i datasettet
keep if sivstand20 == '2'

```
