# Figurer i Vega-editoren

Microdata.no lager figurene (`barchart`, `histogram`, `boxplot` osv.) som **Vega-Lite**-spesifikasjoner,
med de aggregerte tallene inne i spesifikasjonen. Brukeren trenger ikke kunne Vega-Lite. Brukeren limer
inn spesifikasjonen og sier hva som skal endres med vanlige ord. Du gir tilbake en hel, endret
spesifikasjon som limes inn igjen.

Avklart med `barchart (count) fylke`, versjon 60, november 2026 (TESTLOGG 9.1–9.3). Endringsmønstrene
under er prøvd i editoren (fylkesnavn, sortering, liggende søyler, tittel, norsk tallformat,
farge etter gruppe, stablede søyler i prosent og figur fra eksportert tabell, TESTLOGG 9.4–9.5).
Tall på søylene er ikke prøvd.

## Slik gjør brukeren det (forklar det slik)

1. Hold musepekeren over figuren i resultatvinduet og klikk eksportknappen. Velg Vega-editoren.
2. Editoren åpnes på **vega.github.io/editor**, utenfor microdata.no. Spesifikasjonen står til venstre.
3. Merk alt i venstre vindu (Ctrl+A), kopier (Ctrl+C) og lim det inn i samtalen sammen med hva som skal
   endres.
4. Lim den nye spesifikasjonen inn i venstre vindu i stedet for den gamle, og klikk **Run** øverst.
5. Lagre med **Export** (.png, .svg, .pdf, .html eller .json). Ta vare på .json for å endre figuren igjen.

## Hva spesifikasjonen fra microdata.no inneholder

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"values": [
    {"bar": "fylke", "title": "03", "bar_order": 0, "cat_order": ["03"], "category": ["03"], "value": 724295},
    ...
  ]},
  "mark": {"type": "bar", "size": 20, "orient": "vertical"},
  "encoding": {
    "x": {"field": "title", "sort": ["03", "11", ...], "axis": {"format": "c"}, "title": "fylke"},
    "y": {"type": "quantitative", "title": "count", "field": "value"},
    "tooltip": [{"field": "category", "title": "fylke"}, {"field": "value", "title": "count", "format": "~"}]
  },
  "width": {"step": 25}, "height": 200,
  "params": [{"name": "Highlight", "select": {"type": "point", "toggle": "datum", "fields": ["bar"]}, "bind": "legend"}],
  "config": {"concat": {"spacing": 8, "columns": 2}},
  "usermeta": {"preamble": "This chart was created by https://microdata.no. ..."}
}
```

- **`title`** i hver rad er kategorien (koden, f.eks. fylkesnummer), **`value`** er tallet, og
  `category`/`cat_order` er lister med kategorien (for `over()` og `by()`). Aksetitlene er
  variabelnavnet og statistikken (`fylke`, `count`).
- **Tallene er de samme støylagte, aggregerte tallene som i figuren.** Manualens «man får ikke de
  underliggende tallene» gjelder bare .png/.svg. Celler med 1–4 er 0. Ikke presenter tallene som
  eksakte, og ikke regn ut nye tall fra dem som microdata.no ikke viste.
- `x` har ingen `type`. Sett `"type": "nominal"` når du endrer `x` eller legger til felt.
- Behold `$schema`, `data` og `params`. Endre resten fritt.

## Stilen i Config-fanen

Microdata.no legger en mørk stil i editorens **Config**-fane. Den gjelder i tillegg til spesifikasjonen,
og `axisX`/`axisY` der går foran `axis` i spesifikasjonen (TESTLOGG 9.5, 2026-11-19):

| I Config-fanen | Virkning |
|---|---|
| `"axisX"`/`"axisY": {"format": "~s"}` | Tallformat på begge akser: navn på en akse blir «NaN» (f.eks. liggende søyler) |
| `"legend": {"format": "~s"}` | Det samme i forklaringen (farge etter gruppe) |
| `"axisX": {"labelAngle": 45}` | Skrå aksetekster |
| `style` med `"font": "IBM Plex Sans"` | Fonten finnes sjelden lokalt, så aksene faller tilbake til Times |
| `"background": "#002b36"`, `"bar": {"fill": "#859900"}`, `range` | Mørk bakgrunn, grønne søyler, egne fargeskalaer |

Brukeren trenger ikke røre Config-fanen når du setter alt i spesifikasjonen: `labelExpr` på navneakser og
navneforklaringer, `axisX`/`axisY` i `config`, og bakgrunn, farger og fonter (prøvd: riktig figur med
fanen urørt). Vil brukeren tømme den, må det stå `{}`. En helt tom fane gir «ValueExpected at Ln 1,
Col 1». Ta alltid med denne blokken (bytt ut `config` fra microdata.no):

```json
"background": "white",
"config": {
  "font": "Arial, Helvetica, sans-serif",
  "locale": {"number": {"decimal": ",", "thousands": " ", "grouping": [3], "currency": ["", " kr"]}},
  "title": {"font": "Arial, Helvetica, sans-serif", "subtitleFont": "Arial, Helvetica, sans-serif",
            "fontSize": 14, "subtitleFontSize": 11, "color": "#222", "subtitleColor": "#555", "anchor": "start"},
  "axis": {"labelFont": "Arial, Helvetica, sans-serif", "titleFont": "Arial, Helvetica, sans-serif",
           "labelFontSize": 11, "titleFontSize": 11, "titleFontWeight": "normal", "labelAngle": 0,
           "labelColor": "#222", "titleColor": "#222", "gridColor": "#ddd", "domainColor": "#888", "tickColor": "#888"},
  "axisX": {"labelAngle": 0}, "axisY": {"labelAngle": 0},
  "legend": {"labelFont": "Arial, Helvetica, sans-serif", "titleFont": "Arial, Helvetica, sans-serif",
             "labelColor": "#222", "titleColor": "#222"},
  "style": {"guide-label": {"font": "Arial, Helvetica, sans-serif"}, "guide-title": {"font": "Arial, Helvetica, sans-serif", "fill": "#222"}},
  "range": {"category": ["#2b5c8a", "#e07b39", "#5a9e6f", "#c44e52", "#8172b2", "#937860", "#da8bc3", "#8c8c8c"]}
}
```

På hver akse eller forklaring med navn (ikke tall): `"axis": {"labelExpr": "datum.value"}` eller
`"legend": {"labelExpr": "datum.value"}`. Det hopper over tallformatet `~s`.

## Vanlige endringer

**Koder til navn.** Legg til et oppslag og bruk det nye feltet på aksen. Hent navnene fra
`metadata/kodelister.csv` (variabelen), `metadata/regioner/` eller Klass, ikke fra hukommelsen.

```json
"transform": [{"lookup": "title", "from": {"data": {"values": [
  {"kode": "03", "navn": "Oslo"}, {"kode": "11", "navn": "Rogaland"}]}, "key": "kode", "fields": ["navn"]}}],
"encoding": {"x": {"field": "navn", "type": "nominal", "sort": "-y", "title": null}, ...}
```

**Sortering:** `"sort": "-y"` (størst først), `"sort": "y"` eller en liste med kategoriene i ønsket
rekkefølge. Med liggende søyler: `"-x"`.

**Tittel og kilde:**

```json
"title": {"text": "Bosatte etter fylke, 1.1.2025",
          "subtitle": "Kilde: microdata.no (SSB, no.ssb.fdb:60). Tallene er støylagt."}
```

**Aksetitler:** `"title": "Antall personer"` i `y`, `"title": null` for å fjerne.

**Liggende søyler** (lange navn): bytt `x` og `y`, sett `"orient": "horizontal"` i `mark`.

**Farge:** én farge med `"mark": {"type": "bar", "color": "#2b5c8a"}`. Farge etter gruppe:
`"color": {"field": "<felt>", "type": "nominal", "title": null}` i `encoding`.

**Størrelse:** fjern `"size"` i `mark` og bruk `"width": 500` (fast bredde) i stedet for `{"step": 25}`.

**Norsk tallformat** (mellomrom som tusenskille, komma som desimaltegn): `locale` i `config`-blokken over,
og `"axis": {"format": ",d"}` på tallaksen (`",.1f"` for én desimal, `".0%"` for prosent av andeler).

**Tall på søylene:** gjør `mark` og `encoding` om til et lag med søyler og et lag med tekst:

```json
"layer": [
  {"mark": "bar"},
  {"mark": {"type": "text", "dy": -6}, "encoding": {"text": {"field": "value", "format": ",d"}}}
]
```

(Felles `encoding` står utenfor `layer`. Ikke vis tall som ser mer presise ut enn de er.)

## Figur fra en tabell (når figurkommandoen ikke holder)

Brukeren eksporterer tabellen: musepekeren over tabellen, eksportknappen, «semikolonseparert» på og
«norsk kommategnsetting» av, Ctrl+C. Utskriften ser slik ut (prøvd 2026-11-19, TESTLOGG 9.4):

```
fylke; 1 - 0–19 år; 2 - 20–66 år; 3 - 67 år og over; 9 - Ukjent; Total
03; 20.238356576689267; 68.02109091210325; 11.722465908133863; 0.017396274712029525; 100
...
Total; 22.211586466814566; 61.01639926232546; 16.7602881270828; 0.011744018996352919; 100
```

- Semikolon og et mellomrom mellom feltene. Overskriftene er «kode - navn», så navnene følger med.
- **Ta ut raden og kolonnen `Total`**, og små restgrupper som «Ukjent» når de ikke skal vises.
- Alle desimaler følger med. **Avrund** (én desimal for prosent), så tallene ikke ser presise ut.
- `flatten` endrer ingenting for to dimensjoner. Den trengs ved tre eller flere.

Behold tabellen bred (én rad per rad i tabellen) og bruk `fold` til én rad per kategori. Mønster for
stablede søyler i prosent med farge etter gruppe (prøvd, riktig rekkefølge på farger og rader):

```json
"data": {"values": [{"fylke": "03", "0–19 år": 20.2, "20–66 år": 68.0, "67 år og over": 11.7}, ...]},
"transform": [
  {"lookup": "fylke", "from": {"data": {"values": [{"kode": "03", "navn": "Oslo"}, ...]}, "key": "kode", "fields": ["navn"]}},
  {"calculate": "datum['67 år og over']", "as": "eldre"},
  {"fold": ["0–19 år", "20–66 år", "67 år og over"], "as": ["aldersgruppe", "prosent"]},
  {"calculate": "indexof(['0–19 år', '20–66 år', '67 år og over'], datum.aldersgruppe)", "as": "rekkefolge"}
],
"mark": {"type": "bar", "orient": "horizontal"},
"encoding": {
  "y": {"field": "navn", "type": "nominal", "title": null,
        "sort": {"field": "eldre", "op": "max", "order": "descending"}, "axis": {"labelExpr": "datum.value"}},
  "x": {"field": "prosent", "type": "quantitative", "stack": "normalize", "title": null, "axis": {"format": ".0%"}},
  "color": {"field": "aldersgruppe", "type": "nominal", "title": null, "sort": ["0–19 år", "20–66 år", "67 år og over"],
            "legend": {"orient": "top", "labelExpr": "datum.value"}},
  "order": {"field": "rekkefolge"}
}
```

`eldre` lagres før `fold`, så radene kan sorteres etter én av gruppene. `order` og `sort` på `color`
holder fargene i samme rekkefølge i søylene og i forklaringen. For søyler ved siden av hverandre: fjern
`stack` og legg til `"yOffset": {"field": "aldersgruppe"}`.

## Personvern

Spesifikasjonen inneholder bare tallene som allerede vises i figuren, og de er laget for å kunne tas ut.
Editoren ligger på vega.github.io, utenfor microdata.no. Si fra om det, og om at deling fra editoren
(lenke eller gist) gjør figuren og tallene offentlige.
