<!-- Kilde: https://microdata.no/manual/brukermanual/Oppretting%20og%20endring%20av%20datasett/ -->

# 2. Oppretting og endring av datasett

Dataanalyser i microdata.no krever at en først knytter seg opp mot en databank, deretter oppretter et tomt datasett, og så importerer de ønskede variabler inn i datasettet. Sistnevnte gjøres gjennom bruk av import-kommandoer (se kapittel 2.3.1, 2.3.2 og 2.4).

Om en ønsker å justere på utvalget eller fjerne variabler en ikke ønsker å jobbe videre med, brukes kommandoene `drop` eller `keep` (se kapittel 2.6 og 2.7). En kan spesifisere hvilken variabel en ønsker å slette. Dersom ingen variabel spesifiseres, slettes hele records i kombinasjon med en if-betingelse.
