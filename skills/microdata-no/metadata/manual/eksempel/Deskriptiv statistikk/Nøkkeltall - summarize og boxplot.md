<!-- Kilde: https://microdata.no/manual/eksempel/Deskriptiv%20statistikk/N%C3%B8kkeltall%20-%20summarize%20og%20boxplot -->

# Nøkkeltall - summarize og boxplot

Skriptet nedenfor demonstrerer ulike måter å bruke kommandoene `summarize` og `boxplot` til å lage deskriptiv statistikk. Disse brukes på numeriske variabler for å lage oppsummerende statistikk som gjennomsnitt, standardavvik, antall enheter med gyldig verdi etc.

```
 // Nøkkelstatistikk for metriske/kontinuerlige variabler
// Kommandoen summarize brukes for å vise nøkkelinformasjon om metriske/kontinuerlige variabler. Verdier som vises er
// gjennomsnitt, kvartiler m.m. Kommandoen boxplot viser de samme tallene grafisk gjennom standard boxplotfremstilling

require no.ssb.fdb:23 as db

create-dataset demografidata
import db/INNTEKT_WYRKINNT 2020-01-01 as innt
import db/INNTEKT_BRUTTOFORM 2020-01-01 as formue
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd
import db/BOSATTEFDT_BOSTED 2020-01-01 as bosted

// Koder om fra kommune- til fylkesnivå
generate fylke = substr(bosted,1,2)

// Lager alder per 2020
generate alder = 2020 - int(faarmnd/100)

summarize innt formue
summarize formue if alder > 50
summarize formue if bosted == '0301'

boxplot innt formue
boxplot innt, over(kjønn)

```
