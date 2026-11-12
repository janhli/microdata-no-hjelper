# Manuelt lastede regioninndelinger

Filer her finnes ikke i SSB Klass og er lagt inn for hånd. De leses av `verktoy/hent_regioninndelinger.py`.

## bo_og_arbeidsmarkedsregioner_2024.csv

- **Hva:** Bo- og arbeidsmarkedsregioner (BA-regioner), TØIs inndeling for Kommunal- og
  moderniseringsdepartementet (2019, 159 regioner for kommunestrukturen 2020).
  Rapport: https://www.regjeringen.no/no/dokumenter/inndeling-av-kommuner-i-bo--og-arbeidsmarkedsregioner/id2662614/
- **Finnes bare som rapport og regneark**, ikke i Klass eller som API.
- **Omkodet til kommunestrukturen 2024** (kolonnen `kommunenr_2024`). Haram (1580), skilt ut fra Ålesund
  i 2024, er lagt til i regionen «79 Ålesund» (se kolonnen `Inkluderingsgrunnlag`).
- **Hentet fra** `data-pipeline/source/bo_og_arbeidsmarkedsregioner_2024.csv` i
  https://github.com/jahili/norge-administrative-grenser (2026-11-09), uendret kopi.
- **Kontrollert** 2026-11-12 mot originalen (`baregioner_2020.xlsx` på rapportsiden): alle 357 kommuner har
  samme region etter omkoding fra 2020 til 2024 (Rindal, Lunner og Jevnaker byttet nummer 1.1.2020).
- **Kolonnene** `Reisetid`, `Ut-pendling`, `Inn-pendling` og `Inkluderingsgrunnlag` brukes ikke av verktøyet.
- **Gjengangere:** Filen har 366 rader for 357 kommuner. Duplikatene må være identiske. Regionnummeret
  skrives både «05» og «5» for Oslo/Bærum, og normaliseres til tre sifre (`005`).
- **Ved nye kommuneendringer** må filen oppdateres for hånd, og `hent_regioninndelinger.py` kjøres på nytt.
