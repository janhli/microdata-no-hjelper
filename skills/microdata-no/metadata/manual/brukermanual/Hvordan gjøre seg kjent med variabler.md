<!-- Kilde: https://microdata.no/manual/brukermanual/Hvordan%20gj%C3%B8re%20seg%20kjent%20med%20variabler/ -->

# 4. Hvordan gjøre seg kjent med variabler

I microdata.no kan en bruke ulike teknikker for å utforske variabler og datasett. Den enkleste er bruk av tabeller (enveis- eller krysstabeller) eller oppsummeringsstatistikk (for metriske variabler). En kan også visualisere gjennom histogrammer, søylediagrammer, kakediagrammer og anonymiserte plotdiagrammer (hexbinplot) på en oversiktlig måte.

Analyseverktøyet i microdata.no har følgende kommandoer tilgjengelig for produksjon av deskriptiv statistikk:

-

`tabulate`

-

`summarize`

-

`boxplot`

-

`hexbin`

-

`piechart`

-

`histogram`

-

`barchart`

-

`sankey`

I tillegg kan følgende kommandoer brukes på paneldata (les mer om disse i kapittel 5.9.1):

-

`tabulate-panel`

-

`summarize-panel`

-

`transitions-panel`

Gjennom opsjoner kan en vise alternative fremstillinger av de samme fordelingene, og en kan utelate enheter fra tabellene/figurene gjennom `if`-betingelser.

OBS!

Verdier for gjennomsnitt, standardavvik og gini påvirkes av at statistikkpopulasjonen winsoriseres før utregningen av tall i deskriptive statistikker. Winsorisering vil si at man koder om ekstremverdier og setter dem til grenseverdien for hhv. første og siste percentil, jfr. verdiene for 1% og 99% i summarize-resultatet. Dette påvirker gjennomsnitt, standardavvik og gini slik at beregnet verdi blir noe lavere enn faktisk verdi. Dette kommer an på hvor skjev fordelingen for de respektive variabelpopulasjonene er. Ved normalfordeling vil ikke winsorisering gi noe særlig utslag.

Prosentil-, kvartil- og medianverdier påvirkes ikke av winsorisering, men vises med tresifret nøyaktighet.

Grafiske visninger av numeriske utregniner gjennom kommandoer som `boxplot`, `barchart`, `histogram` og `hexbin` påvirkes også av de nevnte personverntiltakene.

Regresjonsanalyser returnerer hovedsaklig estimater og i liten grad personidentifiserende opplysninger. Derfor er ikke disse gjenstand for tiltakene nevnt over. Du finner beskrivelser av tilgjengelige regresjonsanalyser i kapittel 5.

 ⊳\rhd⊳ Mer info om winsorisering og øvrige personverntiltak finner du her
