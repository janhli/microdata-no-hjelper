"""Sjekker et microdata.no-skript for feil som kan finnes uten å kjøre det. Kjør det før du leverer.

  python verktoy/sjekk_skript.py skript.txt
  python verktoy/sjekk_skript.py - < skript.txt      (eller uten filnavn: leser fra stdin)
  python verktoy/sjekk_skript.py --snutt kodesnutter/alder.txt

Feil (avslutter med kode 1):
  - require uten heltallsversjon, eller med et datalager som ikke finnes
  - import av variabel som ikke finnes, ligger i et annet datalager enn aliaset, eller har alias uten require
  - fast variabel (FIXED) med dato, andre variabler uten dato, dato utenfor dekningen (fra/til)
  - importlinje som ikke kan tolkes
  - pseudonymvariabel (f.eks. BEFOLKNING_MOR_FNR) i et uttrykk: if, generate, replace
  - median eller sd i tabulate ..., summarize() (gyldig: mean std sum p25 p50 p75 gini iqr)
  - andregradsledd c.x#c.x (utelates fra modellen uten melding)
  - $i limt inn i et navn (t$i), og navn som er funksjonsnavn (t, year, date)
  - uten --snutt: mangler ansvarslinjen øverst eller citation
Advarsler (endrer ikke avslutningskoden):
  - gruppering som starter med en fast verdi og endres med replace ... if x < / > ..., uten sysmiss()
  - citation er ikke siste kommando

Skriver også ut hvilke temafiler (referanser/fallgruver_*.md) som gjelder det skriptet bruker, og hvorfor.

Sjekken finner bare feil som kan sees i teksten. Les referanser/fallgruver.md og temafilene den skriver ut likevel.
--snutt slår av kravene til levering (ansvarslinje og citation), slik testene bruker den på kodesnuttene.
"""

import argparse
import csv
import json
import re
import sys
from collections import namedtuple
from functools import lru_cache
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
METADATA = SKILL / "metadata"
FUNKSJONER_MD = METADATA / "manual" / "kommandoer_og_funksjoner" / "funksjoner.md"
KOMMANDOER_MD = METADATA / "manual" / "kommandoer_og_funksjoner" / "kommandoer.md"

ANSVARSLINJE = ("// Laget med hjelp fra en KI-agent (microdata-no-hjelper). Kontroller variabler, populasjon og "
                "resultater selv: du er ansvarlig for skriptet.")

Funn = namedtuple("Funn", "linje niva melding")  # niva er "feil" eller "advarsel"

DATO = r"\d{4}-\d{2}-\d{2}"
# Valg etter aliaset, f.eks. `, values("2")`, og kommentar.
SLUTT = r"(?:\s*,.*)?(?:\s*//.*)?\s*$"
REQUIRE = re.compile(r"^\s*require\s+([\w.]+):(\d+)\s+as\s+(\w+)\s*(?://.*)?$")
IMPORTLINJE = re.compile(r"^\s*import(?:-event|-panel)?\s")
IMPORT = re.compile(rf"^\s*import\s+(\w+)/(\w+)(?:\s+({DATO}|\$\w+))?\s+as\s+(\$?\w+){SLUTT}")
EVENT = re.compile(rf"^\s*import-event\s+(\w+)/(\w+)\s+({DATO}|\$\w+)\s+to\s+({DATO}|\$\w+)\s+as\s+(\$?\w+){SLUTT}")
PANEL = re.compile(rf"^\s*import-panel((?:\s+\w+/\w+)+)((?:\s+(?:{DATO}|\$\w+))+){SLUTT}")
TILORDNING = re.compile(r"^\s*(generate|replace)\s+(\$?\w+)\s*=\s*(.*)$")
NAVN = [  # (?![\w$]): `t$i` er ikke navnet `t`, den feilen meldes for seg
    (re.compile(r"^\s*let\s+(\w+)\s*="), "bindingen"),
    (re.compile(r"^\s*generate\s+(\w+)(?![\w$])"), "variabelen"),
    (re.compile(r"\bas\s+(\w+)(?![\w$])"), "variabelen"),
    (re.compile(r"->\s*(\w+)(?![\w$])"), "variabelen"),
    (re.compile(r"^\s*(?:create-dataset|clone-dataset\s+\w+)\s+(\w+)(?![\w$])"), "datasettet"),
]
# Temafilene i referanser/, og hva de gjelder. Testes mot filene som finnes.
TEMAFILER = {"fallgruver_analyse.md": "statistisk analyse", "fallgruver_geografi.md": "geografi",
             "fallgruver_klass.md": "Klass og næring", "fallgruver_fhi.md": "FHI-data"}
NARING = re.compile(r"_NARING_SN|_NACE1?_SN")
KLASSVARIABEL = re.compile(r"STYRK08|_NUS(?:2000)?(?:_|$)|^NUDB_BU$|LANDBAK|FODELAND")


@lru_cache(maxsize=None)
def les_variabler():
    with open(METADATA / "variabler.csv", encoding="utf-8-sig", newline="") as f:
        return {r["navn"]: r for r in csv.DictReader(f, delimiter=";")}


@lru_cache(maxsize=None)
def les_datalagre():
    return set(json.loads((METADATA / "datalagre.json").read_text(encoding="utf-8")))


@lru_cache(maxsize=None)
def les_funksjoner():
    return frozenset(re.findall(r"^### (\w+)\s*$", FUNKSJONER_MD.read_text(encoding="utf-8"), re.MULTILINE))


@lru_cache(maxsize=None)
def er_pseudonym(navn):
    """Pseudonymiserte ID-er (RandomUInt48) kan bare brukes i by(), merge ... on og values_from()."""
    fil = METADATA / "variabler" / f"{navn}.json"
    if not fil.exists():
        return False
    return json.loads(fil.read_text(encoding="utf-8"))["measureVariable"].get("format") == "RandomUInt48"


def kodelinjer(tekst):
    """(linjenummer, linje uten kommentar) for linjene som er kode: ikke kommentarer og ikke textblock."""
    i_blokk = False
    for nr, linje in enumerate(tekst.splitlines(), 1):
        s = linje.strip()
        if i_blokk:
            i_blokk = s != "endblock"
            continue
        if s == "textblock":
            i_blokk = True
            continue
        if not s or s.startswith("//"):
            continue
        yield nr, re.sub(r"\s+//.*$", "", linje)


def uten_tekst(s):
    """Fjerner tekstkonstanter, så navn inne i '...' og "..." ikke tas for variabler."""
    return re.sub(r"'[^']*'|\"[^\"]*\"", "''", s)


def er_dato(verdi):
    return re.fullmatch(DATO, verdi) is not None


@lru_cache(maxsize=None)
def geografivariabler():
    """Variabler med Oslo som kommune, fylke eller bydel i kodelisten, og grunnkrets (kodene har ikke navn på Oslo)."""
    with open(METADATA / "kodelister.csv", encoding="utf-8-sig", newline="") as f:
        navn = {r["navn"] for r in csv.DictReader(f, delimiter=";")
                if (r["kode"], r["kategori"]) in {("0301", "Oslo"), ("03", "Oslo"), ("030101", "Gamle Oslo")}}
    return frozenset(navn | {"BEFOLKNING_GRUNNKRETS"})


@lru_cache(maxsize=None)
def analysekommandoer():
    """Kommandoene under Analyse, Regresjon og Overlevelsesanalyse i manualen, pluss paneldata og coefplot."""
    ut = {"import-panel", "summarize-panel", "tabulate-panel", "coefplot"}
    for del_ in re.split(r"(?m)^(?=## )", KOMMANDOER_MD.read_text(encoding="utf-8")):
        if del_.split("\n", 1)[0] in ("## Analyse", "## Regresjon", "## Overlevelsesanalyse"):
            ut |= set(re.findall(r"^### ([\w-]+)\s*$", del_, re.MULTILINE))
    return frozenset(ut)


def temafiler(tekst):
    """{temafil: [hva i skriptet som gjør at den gjelder]}, i rekkefølgen fra TEMAFILER."""
    grunner = {fil: [] for fil in TEMAFILER}
    klass, recode = [], bool(re.search(r"(?mi)^\s*//.*\bklass\b", tekst))
    kode = [uten_tekst(linje) for _, linje in kodelinjer(tekst)]

    def brukt(alias):
        """Om variabelen brukes til mer enn å avgrense populasjonen med sysmiss(), eller å fjernes."""
        navn = re.escape(alias)
        for s in kode:
            if IMPORTLINJE.match(s) or re.match(rf"^\s*drop\s+{navn}\s*$", s):
                continue
            if re.search(rf"(?<![\w$]){navn}(?!\w)", re.sub(rf"sysmiss\(\s*{navn}\s*\)", "", s)):
                return True
        return False

    for s in kode:
        kommando = s.split()[0]
        if kommando in analysekommandoer():
            grunner["fallgruver_analyse.md"].append(kommando)
        recode = recode or kommando == "recode"
        if m := REQUIRE.match(s):
            if m.group(1).startswith("no.fhi."):
                grunner["fallgruver_fhi.md"].append(m.group(1))
        elif IMPORTLINJE.match(s):
            m = IMPORT.match(s)
            for navn in re.findall(r"\b\w+/(\w+)", s):
                if navn in geografivariabler() and (not m or m.group(4).startswith("$") or brukt(m.group(4))):
                    grunner["fallgruver_geografi.md"].append(navn)
                if NARING.search(navn):
                    grunner["fallgruver_klass.md"].append(navn)
                elif KLASSVARIABEL.search(navn):
                    klass.append(navn)
    if recode:  # yrke, utdanning og land bare når kodene grupperes
        grunner["fallgruver_klass.md"] += klass
    return {fil: list(dict.fromkeys(g)) for fil, g in grunner.items() if g}


def sjekk(tekst, variabler=None, levering=True, datalagre=None, funksjoner=None, pseudonym=None):
    """Returnerer en liste med Funn. Argumentene etter `tekst` er til testene; standard er metadataene."""
    variabler = les_variabler() if variabler is None else variabler
    datalagre = les_datalagre() if datalagre is None else datalagre
    funksjoner = les_funksjoner() if funksjoner is None else funksjoner
    pseudonym = er_pseudonym if pseudonym is None else pseudonym
    funn = []

    def feil(nr, melding):
        funn.append(Funn(nr, "feil", melding))

    def advarsel(nr, melding):
        funn.append(Funn(nr, "advarsel", melding))

    linjer = list(kodelinjer(tekst))
    datalager = {}
    for nr, linje in linjer:
        if re.match(r"^\s*require\b", linje):
            m = REQUIRE.match(linje)
            if not m:
                feil(nr, "require må ha formen `require <datalager>:<hovedversjon> as <alias>`, "
                         "f.eks. `require no.ssb.fdb:60 as fdb`")
            elif m.group(1) not in datalagre:
                feil(nr, f"datalageret {m.group(1)} finnes ikke (se metadata/datalagre.json)")
            else:
                datalager[m.group(3)] = m.group(1)

    pseudonymer = {}

    def variabel(nr, alias, navn):
        if alias not in datalager:
            feil(nr, f"aliaset {alias} har ingen require")
            return None
        v = variabler.get(navn)
        if v is None:
            feil(nr, f"{navn} finnes ikke i variabler.csv")
            return None
        if v["datalager"] != datalager[alias]:
            feil(nr, f"{navn} ligger i {v['datalager']}, ikke i {datalager[alias]} ({alias})")
            return None
        return v

    def innenfor(nr, v, dato):
        if er_dato(dato) and not v["fra"] <= dato <= v["til"]:
            feil(nr, f"{v['navn']} {dato} er utenfor dekningen {v['fra']}–{v['til']}")

    for nr, linje in linjer:
        if not IMPORTLINJE.match(linje):
            continue
        if m := IMPORT.match(linje):
            alias, navn, dato, som = m.groups()
            v = variabel(nr, alias, navn)
            if v is None:
                continue
            if pseudonym(navn) and not som.startswith("$"):
                pseudonymer[som] = navn
            if v["temporalitet"] == "FIXED":
                if dato:
                    feil(nr, f"{navn} er FIXED og skal importeres uten dato")
            elif not dato:
                feil(nr, f"{navn} er {v['temporalitet']} og må ha dato")
            else:
                innenfor(nr, v, dato)
        elif m := EVENT.match(linje):
            alias, navn, start, slutt, _ = m.groups()
            v = variabel(nr, alias, navn)
            if v and er_dato(start) and er_dato(slutt) and (slutt < v["fra"] or start > v["til"]):
                feil(nr, f"{navn} {start} to {slutt} overlapper ikke dekningen {v['fra']}–{v['til']}")
        elif m := PANEL.match(linje):
            datoer = m.group(2).split()
            for ref in m.group(1).split():
                v = variabel(nr, *ref.split("/"))
                if v and v["temporalitet"] != "FIXED":
                    for dato in datoer:
                        innenfor(nr, v, dato)
        else:
            feil(nr, f"kan ikke tolke importlinjen: {linje.strip()}")

    grupper = {}  # variabel -> [linje for generate, antall replace med < eller >, har sysmiss]
    siste_kommando = None
    for nr, linje in linjer:
        s = uten_tekst(linje)
        siste_kommando = s.split()[0]

        # Navn som er funksjonsnavn
        for monster, hva in NAVN:
            for m in monster.finditer(s):
                if m.group(1) in funksjoner:
                    feil(nr, f"{hva} {m.group(1)} har samme navn som en funksjon. Velg et annet navn")

        if IMPORTLINJE.match(s) or re.match(r"^\s*require\b", s):
            continue

        # Pseudonymer i uttrykk
        uttrykk = []
        if m := re.search(r"\bif\b(.*)$", s):
            uttrykk.append(m.group(1))
        if m := TILORDNING.match(s):
            uttrykk += [m.group(2), re.sub(r"\bif\b.*$", "", m.group(3))]
        for alias, navn in pseudonymer.items():
            if any(re.search(rf"(?<![\w$.]){re.escape(alias)}(?!\w)", u) for u in uttrykk):
                feil(nr, f"{alias} ({navn}) er en pseudonymisert ID og kan bare brukes i by(), merge ... on og "
                         "values_from(), ikke i uttrykk («Ulovlig bruk av pseudonymvariabel»)")

        # Statistikk i tabulate ..., summarize()
        if re.match(r"^\s*tabulate\b", s) and "summarize(" in s and "," in s:
            valg = re.sub(r"summarize\([^)]*\)", " ", s.split(",", 1)[1])
            for ord_ in re.findall(r"\b(median|sd)\b", valg):
                riktig = "p50" if ord_ == "median" else "std"
                feil(nr, f"`{ord_}` er ikke gyldig i tabulate ..., summarize(). Bruk `{riktig}`")

        # Andregradsledd
        for a, b in re.findall(r"\bc\.(\w+)##?c\.(\w+)", s):
            if a == b:
                feil(nr, f"c.{a}#c.{a} utelates fra modellen uten melding. Lag `generate {a}2 = {a} * {a}` "
                         f"og bruk {a}2")

        # $i limt inn i et navn
        for m in re.finditer(r"[A-Za-z0-9_]\$(\w+)", s):
            feil(nr, f"`{m.group(0)}`: ${m.group(1)} kan ikke limes inn i et navn. "
                     f"Bruk `let v = navn_ ++ ${m.group(1)}` og så `$v`")

        # Grupperinger uten kategori for manglende verdi
        if m := re.match(r"^\s*generate\s+(\w+)\s*=\s*(''|-?\d+(?:\.\d+)?)\s*$", s):
            grupper[m.group(1)] = [nr, 0, False]
        elif (m := re.match(r"^\s*replace\s+(\w+)\s*=.*\bif\b(.*)$", s)) and m.group(1) in grupper:
            g = grupper[m.group(1)]
            g[1] += bool(re.search(r"[<>]", m.group(2)))
            g[2] = g[2] or "sysmiss(" in m.group(2)
    for navn, (nr, sammenligninger, har_sysmiss) in grupper.items():
        if sammenligninger and not har_sysmiss:
            advarsel(nr, f"{navn} får en startverdi og endres med replace ... if x < / > ..., uten sysmiss(). Der x "
                         "mangler, blir startverdien stående uten melding (en sammenligning med manglende verdi er "
                         f"usann). Legg til `replace {navn} = <ukjent> if sysmiss(x)`, eller si fra til brukeren "
                         "hvis startverdien er ment for dem (f.eks. 0 = ikke registrert)")

    if levering:
        if ANSVARSLINJE not in (l.strip() for l in tekst.splitlines()):
            feil(1, f"mangler ansvarslinjen i kommentarblokken øverst: {ANSVARSLINJE}")
        if not any(re.match(r"^\s*citation\b", l) for _, l in linjer):
            feil(len(tekst.splitlines()), "mangler `citation` til slutt i skriptet")
        elif siste_kommando != "citation":
            advarsel(len(tekst.splitlines()), "`citation` bør være siste kommando i skriptet")

    return sorted(funn, key=lambda f: (f.linje, f.niva))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("fil", nargs="?", default="-", help="skriptet som skal sjekkes, eller - for stdin")
    ap.add_argument("--snutt", action="store_true", help="uten krav til ansvarslinje og citation")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.fil == "-":
        sys.stdin.reconfigure(encoding="utf-8")
        tekst = sys.stdin.read()
    else:
        sti = Path(a.fil)
        if not sti.exists():
            ap.error(f"finner ikke {a.fil}")
        tekst = sti.read_text(encoding="utf-8")

    funn = sjekk(tekst, levering=not a.snutt)
    for f in funn:
        print(f"linje {f.linje}: {f.niva.upper()}: {f.melding}")
    antall_feil = sum(f.niva == "feil" for f in funn)
    antall_adv = len(funn) - antall_feil
    if antall_feil:
        print(f"\n{antall_feil} feil og {antall_adv} advarsler. Rett feilene før skriptet leveres.")
    else:
        print(f"Ingen feil funnet ({antall_adv} advarsler). Sjekken finner ikke alt: les referanser/fallgruver.md.")
    if tema := temafiler(tekst):
        print("Les også temafilene for det skriptet bruker:")
        for fil, grunner in tema.items():
            print(f"  referanser/{fil} ({', '.join(grunner)})")
    sys.exit(1 if antall_feil else 0)


if __name__ == "__main__":
    main()
