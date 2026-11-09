<!-- Kilde: https://microdata.no/manual/eksempel/Deskriptiv%20statistikk/S%C3%B8ylediagrammer%20-%20histogram%20og%20barchart -->

# Søylediagrammer - histogram og barchart

Kommandoen `histogram` brukes til å vise frekvensfordelinger/verdidistribusjoner for numeriske variabler på en grafisk måte der verdiene grupperes i passende intervaller og tilegnes søyler som viser graden av forekomst for hvert intervall. Det er mulig å styre hvor mange søyler (maks 30) eller hvor brede søyleintervallene skal være, gjennom opsjoner. Ved begrensede antall verdier, anbefales det å bruke opsjonen `discrete`. Dette gir en graf som viser en søyle per verdi (i stedet for intervaller).

Kommandoen `barchart` brukes til å lage søylediagrammer for numeriske variabler, altså grafisk visning av verdiene man får ut gjennom kommandoen `summarize`. Det er mulig å gruppere søylene etter kategoriske verdier.

```
 // Histogram og barchart

require no.ssb.fdb:45 as db

create-dataset demografidata
import db/INNTEKT_WYRKINNT 2023-12-31 as innt
import db/INNTEKT_BER_BRFORM 2023-12-31 as formue
import db/BEFOLKNING_KJOENN as kjønn
import db/BEFOLKNING_FOEDSELS_AAR_MND as faarmnd

// Lager alder per 2024
generate alder = 2024 - int(faarmnd/100)

// Histogram (frekvensfordelinger)
// Dette er en måte å vise frekvensfordelinger for metriske/kontinuerlige variabler på en grafisk måte der verdiene
// grupperes i passende intervaller og tilegnes søyler som viser graden av forekomst. Søylearealene i diagrammet summerer
// seg til 1 som default, men en kan overstyre dette gjennom options. Gjennom options kan en dessuten selv velge
// inndelingen av av verdier (hvor mange søyler en ønsker), legge på en normalfordelingskurve som referanse m.m.

histogram innt
histogram innt, freq
histogram innt, fraction
histogram innt, percent

histogram innt, normal freq
histogram innt, bin(6) freq
histogram innt, width(100000) freq

histogram innt, by(kjønn) freq
histogram innt if innt > 100000, freq

// Ved bruk av discrete-option kan en også lage histogrammer for diskrete variabler.
// Da vil hver kategori representeres av respektive søyler

histogram alder, discrete percent

// Søylediagram
// Slike diagrammer er fine til å fremstille statistikk for kontinuerlige/metriske variabler på en oversiktlig måte.
// En kan kombinere flere variabler og bryte ned tallene på kategoriske egenskaper (kjønn, utdanningsnivå etc)

barchart (mean) innt, over(kjønn)
barchart (mean) innt formue, over(kjønn)

```
