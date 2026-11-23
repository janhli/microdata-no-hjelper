# TESTLISTE 7.14: skillen i andre agenter

Skillen ble lenket til `~/.agents/skills/microdata-no` slik README beskriver (`mklink /J`, Windows).
Hver oppgave ble kjørt i en tom mappe utenfor repoet. Agenten hadde derfor ingen `AGENTS.md`, `evals/` eller
`skills/` i arbeidsmappen, og kunne bare finne skillen via `~/.agents/skills`. Oppgaveteksten var ordrett
fra `prompt.md`, med en linje til slutt om å liste skills, filer og kommandoer.

## Codex (gpt-6.2-sol, 2026-11-23)

| Oppgave | Poeng | Claude med skill, runde 1 |
|---|---|---|
| `kommune-2015-mot-2024` (7.3) | 4/4 (kriterium 02 delvis, se under) | 3/4 |
| `naering-hovedomrader` (7.7) | 3/3 | 2/3 (gammelt kriterium 03) |

**Skillen ble funnet og lastet** i begge kjøringene: første handling var å lese
`C:/Users/janli_a/.agents/skills/microdata-no/SKILL.md`. Etter det brukte agenten stiene i skillen:
`metadata/variabler.csv`, `referanser/fallgruver.md`, `kodesnutter/mal_analyse.txt` og verktøyene.

**7.7:** Agenten fant i `variabler.csv` at `REGSYS_VIRK_NACE1_SN07` slutter i november 2019. Den sa fra
om det, brukte 2019-11-16 med en tydelig merknad og viste til Statistikkbanken (tabell 08536) for 2024.
Hovedområdene ble laget med `klass.py grupper 6 --nivaa 1 --dato 2019-11-16`.

**7.3, første kjøring (forkastet):** Agenten leste T3-tråden som startet den, og der sto kriteriene.
Den kjørte `kommuneomkoding.py --fra 2015 --til 2026` og listet Stokke, Snillfjord og Tysfjord som delte
kommuner. Svaret telles ikke.

**7.3, ny kjøring (med beskjed om ikke å lese andre tråder):** Agenten gikk lenger enn kriteriene. Den
brukte funksjonene i `kommuneomkoding.py`, `grunnkrets.py` og `recode_regler.py`. Med dem plasserte den
innbyggerne i delte kommuner og grensejusteringer etter grunnkrets (f.eks. Stokke-kretsene til 3907).
Bosatte som ikke kan plasseres, havnet på raden «Uavklart».
- `BEFOLKNING_KOMMNR_FORMELL` er hentet på begge datoene.
- `require no.ssb.fdb:60` står i skriptet.
- Tabellen ble laget med `reshape-to-panel` og `tabulate-panel`.
- **Kriterium 02 bare delvis:** svaret nevner ikke de delte kommunene ved navn, men sier hva som skjer med
  dem.
- Skriptet er ikke kjørt i microdata.no. Usikre punkter: at `reshape-to-panel` godtar suffiksene 2015 og
  2025, og at grunnkretsomkodingen gir rimelige tall.

**Lærdom for evalueringen:** Agenter i T3 kan lese tråden som startet dem. Start oppgavene fra en tråd
uten fasit, eller si i oppgaven at andre tråder ikke skal leses.

## Copilot

Ikke kjørt ennå.
