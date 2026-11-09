# Mønstre i microdata.no

Oppskrifter som har fungert i praksis. Sjekk alltid syntaks og variabeldekning mot `metadata/`.

## Verdi ved hendelsesdato

Bruk mønsteret når du trenger en kjennetegnsverdi (bosted, inntekt ...) fra året en hendelse skjedde
(f.eks. en fødsel).

1. Importer variabelen for flere år i en `for`-løkke på personnivå (`bo2021`, `bo2022`, ...).
2. Koble til hendelsesdatasettet med `merge ... into hendelser on <nøkkel>`.
3. Velg riktig år: `replace x = $var if aar == $aar` i en løkke.

## Mor–barn-kobling

- `BEFOLKNING_MOR_FNR` (fast) kobler barn til mor, og `BEFOLKNING_PARITET` gir barnets nummer i
  rekken av barn mor har født.
- Koble med `merge ... into barn on fnr_mor`. Se kursmaterialet om familiedata i
  `metadata/manual/`.
- Begrens barna til en mødrepopulasjon med
  `import fdb/BEFOLKNING_MOR_FNR as fnr_mor, values_from(mor)`.

## Lavinntekt (EU-60)

1. Lag et eget datasett per år med `INNTEKT_HUSH_IES_EU`.
2. `keep if INNTEKT_KODE_PRIVATHUSH2 == '1'` (privathusholdninger).
3. `generate alle = 1` og `aggregate (median) ... , by(alle)`.
4. Merk personer under 0,6 × median, og koble flagget til persondatasettet.

## Forløp til personnivå

1. Bruk `import-event ...` i et eget datasett.
2. Bruk `collapse (min) START@x -> ... (max) STOP@x -> ..., by(PERSONID_1)`.
3. Koble resultatet til persondatasettet med `merge`.

## Lesbare resultater

Sett en `textblock` ... `endblock` foran hver tabell:

```
textblock
## Fødsler etter mors alder, 2024
Antall levendefødte etter mors alder ved utgangen av året før. Små celler er undertrykt.
endblock
tabulate mor_aldersgr if fodeaar == 2024
```

Ikke legg tabeller med tittel inne i `for`-løkker, for da kan ikke årstallet stå i tittelen. Skriv
dem ut for hvert år.
