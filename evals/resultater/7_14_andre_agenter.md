# TESTLISTE 7.14: skillen i andre agenter

Svarene som teller, ligger i [`7_14/svar/`](7_14/svar) og poengene i [`7_14/poeng.csv`](7_14/poeng.csv).

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

## Copilot CLI (1.0.114, 2026-11-23)

Kjørt med `copilot --allow-all -p "<oppgave>"` i hver sin tomme mappe. `copilot skill list` viste `microdata-no`
under «Inherited skills», altså fra `~/.agents/skills`. Modellen ble valgt automatisk: GPT-6 Luna på 7.3 og
MAI Code 2 Flash på 7.7. Begge kjøringene lastet skillen som første steg (`skill(microdata-no)`).

| Oppgave | Poeng |
|---|---|
| `kommune-2015-mot-2024` (7.3) | 4/4 |
| `naering-hovedomrader` (7.7) | 2/3 |

**7.3:** Kjørte `kommuneomkoding.py --fra 2015 --til 2024` og satte reglene inn i skriptet med et lite
Python-skript, ikke for hånd. Stokke, Snillfjord og Tysfjord er nevnt som delte kommuner, og det står at de
mangler i sammenligningen. `BEFOLKNING_KOMMNR_FORMELL` er hentet på begge datoene, omkodingen gjelder bare
2015, og `require no.ssb.fdb:60` er med. Utenfor kriteriene:
- Målet er 2024-inndelingen, ikke 2026. Forskjellen er bare grensejusteringen i Indre Østfold.
- Skriptet bruker `collapse (count)` og `merge` per kommune og summerer så tellingene i `tabulate`. Det er
  mer omstendelig enn `tabulate kommune` på personnivå, og det er ikke testet hvordan anonymiseringen slår ut
  på summerte tellinger.

**7.7:** Fant i `variabler.csv` at `REGSYS_VIRK_NACE1_SN07` slutter i 2019, og merket skriptet tydelig.
- **Kriterium 03 ikke oppfylt:** agenten kjørte `klass.py grupper 6 --nivaa 1 --dato 2019-11-16`, men
  byttet etterpå ut reglene med divisjonsintervaller skrevet for hånd (`replace naring = 'C' if divisjonsnr >= 10
  & divisjonsnr <= 33` osv.). Intervallene er riktige for SN2007, men ikke laget med verktøyet.
- **Uheldig valg:** populasjonen er de sysselsatte i november 2024 (`ARBSTATUS_PERS_STATUS8`), mens næringen
  er hentet fra 2019. Det står i skriptet, men tabellen blandes med personer som har byttet næring, og alle
  som ikke var sysselsatt i 2019, havner i «uoppgitt». Codex valgte heller hele 2019-fordelingen.

## Samlet

Skillen virker i Codex og Copilot CLI. Begge fant den via `~/.agents/skills` uten oppsett utover lenken,
lastet den på oppgaven, brukte `variabler.csv` og `fallgruver.md` og kjørte verktøyene. Svarene er av samme
type som i Claude. Den eneste svikten (7.7 i Copilot) var at agenten skrev om verktøyets regler for hånd. Det
skjedde med den minste modellen (MAI Code 2 Flash). Cursor er ikke kjørt.
