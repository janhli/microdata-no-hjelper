"""Laster ned variabelkatalogen fra microdata.no til metadata/.

Henter listesidene (20 variabler per side) og deretter detaljsiden for hver
variabel. Metadata ligger som JSON i <script id="__NEXT_DATA__"> på sidene.

Resultat:
  metadata/variabler.csv          oversikt, én linje per variabel
  metadata/kodelister.csv         gjeldende kodeliste for alle variabler (navn;kode;kategori)
  metadata/variabler/<NAVN>.json  full metadata inkl. kodelistehistorikk og måletidspunkter
  metadata/datalager.json         datalagerets versjonshistorikk

Kjøres fra prosjektmappen:  python verktoy/hent_variabler.py [--alle] [--tving] [--versjon N]
Uten --alle hoppes variabler som allerede ligger i metadata/variabler/ over, så lenge datalagerversjonen
er den samme som sist. Er versjonen ny, hentes alle variabler på nytt.

Datalagerversjonen leses fra listesiden (dataStores -> no.ssb.fdb -> version) og brukes i
detalj-URL-ene (/discovery/variable/no.ssb.fdb/<versjon>/<NAVN>). --versjon N overstyrer den.
Hentet versjon står øverst i metadata/datalager.json (versions[0]).

Alt hentes og kontrolleres i minnet før noe skrives. Ved feil avsluttes skriptet med feilkode 1 uten å
endre noen filer. Kontrollene er: ingen nedlastingsfeil, antall variabler lik totalCount fra listesiden,
ikke mer enn 10 % færre variabler enn sist, ikke mer enn 20 % færre kodelinjer enn sist, og at
datalager.json gjelder samme versjon som ble hentet. --tving skriver likevel (for manuell kjøring etter at
du har sett på feilene). JSON-filer for variabler som ikke lenger står i katalogen, slettes.
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://microdata.no/discovery"
UT = Path(__file__).resolve().parent.parent / "metadata"
PAUSE = 0.3  # sekunder mellom forespørsler
MIN_ANDEL_VARIABLER = 0.9  # minst så stor andel av forrige antall variabler
MIN_ANDEL_KODELINJER = 0.8  # minst så stor andel av forrige antall kodelinjer

NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def hent(url, forsok=4):
    req = urllib.request.Request(url, headers={"User-Agent": "microdata-metadata/1.0"})
    for i in range(forsok):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                html = r.read().decode("utf-8")
            break
        except OSError:
            if i == forsok - 1:
                raise
            time.sleep(5 * (i + 1))
    time.sleep(PAUSE)
    return json.loads(NEXT_DATA.search(html).group(1))["props"]["pageProps"]


def gjeldende_kodeliste(ds):
    """Kodelisten for siste periode: full liste i første periode, deretter delta-endringer."""
    koder = []
    for rv in ds["measureVariable"]["representedVariables"]:
        vd = rv.get("valueDomain", {})
        if "codeList" in vd:
            koder = list(vd["codeList"])
        elif "delta" in vd:
            d = vd["delta"]
            fjern = set(d.get("remove", []))
            # Rekkefølgen fjern -> erstatt -> sett inn er den eneste som gir kodelister uten
            # duplikater for alle variablene (testet nov. 2026)
            koder = [k for i, k in enumerate(koder) if i not in fjern]
            for i, k in d.get("replace", {}).items():
                koder[int(i)] = k
            for i in sorted(d.get("insert", {}), key=int):
                koder.insert(int(i), d["insert"][i])
    return koder


def dato(dager):
    if dager is None:
        return ""
    return (dt.date(1970, 1, 1) + dt.timedelta(days=dager)).isoformat()


def bygg_rad(n, ds):
    """Oversiktsrad og kodelinjer for én variabel."""
    koder = gjeldende_kodeliste(ds)
    mv = ds["measureVariable"]
    siste = mv["representedVariables"][-1]
    dekning = ds.get("temporalCoverage", {})
    rad = {
        "navn": n,
        "label": mv.get("label", "").strip(),
        "temporalitet": ds.get("temporality", ""),
        "datatype": mv.get("dataType", ""),
        "enhet": ", ".join(v["keyType"]["label"] for v in ds.get("identifierVariables", [])),
        "fra": dato(dekning.get("start")),
        "til": dato(dekning.get("stop")),
        "antall_koder": len(koder),
        "emner": "; ".join(ds.get("subjectFields", [])),
        "beskrivelse": " ".join(siste.get("description", "").split()),
        "populasjon": " ".join((ds.get("populationDescription") or "").split()),
    }
    return rad, [{"navn": n, "kode": k["code"], "kategori": k["category"].strip()} for k in koder]


def antall_linjer(sti):
    """Antall datalinjer i en CSV-fil (uten overskrift), 0 hvis filen ikke finnes."""
    if not sti.exists():
        return 0
    with open(sti, encoding="utf-8-sig") as f:
        return max(sum(1 for _ in f) - 1, 0)


def hovedversjon(versjon):
    """'59.0.0.0' -> '59' (formen som brukes i URL-er og i require no.ssb.fdb:59)."""
    return str(versjon).split(".")[0] if versjon else ""


def forrige_versjon():
    """Hovedversjonen i metadata/datalager.json fra forrige kjøring, eller '' hvis den mangler."""
    fil = UT / "datalager.json"
    try:
        return hovedversjon(json.loads(fil.read_text(encoding="utf-8"))["versions"][0]["version"])
    except (OSError, ValueError, KeyError, IndexError):
        return ""


def kontroller(feil, navn, totalt, rader, kodelinjer, versjon="", datalager=None):
    """Returnerer en liste med problemer. Tom liste betyr at uttrekket kan skrives."""
    problemer = []
    if versjon and datalager:
        hentet = hovedversjon((datalager.get("versions") or [{}])[0].get("version"))
        if hentet != versjon:
            problemer.append(f"datalager.json gjelder versjon {hentet or '?'}, men variablene er hentet fra versjon {versjon}")
    if feil:
        vis = "; ".join(feil[:5]) + (" ..." if len(feil) > 5 else "")
        problemer.append(f"{len(feil)} variabler feilet: {vis}")
    if len(set(navn)) != totalt:
        problemer.append(f"fant {len(set(navn))} unike variabelnavn, men listesiden oppgir totalCount={totalt}")
    if not rader:
        problemer.append("ingen variabler hentet")
    sist_var = antall_linjer(UT / "variabler.csv")
    if sist_var and len(rader) < MIN_ANDEL_VARIABLER * sist_var:
        problemer.append(f"{len(rader)} variabler, mot {sist_var} sist (grense {MIN_ANDEL_VARIABLER:.0%})")
    sist_koder = antall_linjer(UT / "kodelister.csv")
    if sist_koder and len(kodelinjer) < MIN_ANDEL_KODELINJER * sist_koder:
        problemer.append(f"{len(kodelinjer)} kodelinjer, mot {sist_koder} sist (grense {MIN_ANDEL_KODELINJER:.0%})")
    return problemer


def skriv_csv(sti, felter, rader):
    """Skriver til en midlertidig fil og bytter den inn, så en avbrutt kjøring ikke gir halv fil."""
    tmp = sti.with_name(sti.name + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=felter, delimiter=";")
        w.writeheader()
        w.writerows(rader)
    os.replace(tmp, sti)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--alle", action="store_true", help="hent alle variabler på nytt")
    ap.add_argument("--tving", action="store_true", help="skriv selv om kontrollene feiler")
    ap.add_argument("--versjon", help="datalagerversjon (hovedversjon, f.eks. 59). Standard: lest fra listesiden")
    a = ap.parse_args()
    alle, tving = a.alle, a.tving
    (UT / "variabler").mkdir(parents=True, exist_ok=True)

    navn, side, totalt, versjon = [], 0, 0, a.versjon
    while True:
        data = hent(f"{BASE}/variables?pageIndex={side}")["data"]
        if not versjon:
            versjon = hovedversjon(data.get("dataStores", {}).get("no.ssb.fdb", {}).get("version"))
            if not versjon:
                sys.exit("AVBRUTT: fant ikke datalagerversjonen på listesiden. Bruk --versjon N.")
        navn += [d["name"] for d in data["dataStructures"]]
        totalt = data["totalCount"]
        print(f"liste side {side}: {len(navn)}/{totalt}", file=sys.stderr)
        if len(navn) >= totalt or not data["dataStructures"]:
            break
        side += 1

    forrige = forrige_versjon()
    print(f"datalagerversjon {versjon} (forrige: {forrige or 'ukjent'})", file=sys.stderr)
    if forrige != versjon and not alle:
        print("Ny versjon: henter alle variabler på nytt.", file=sys.stderr)
        alle = True

    rader, kodelinjer, datalager = [], [], None
    nye_json, feil = {}, []
    for i, n in enumerate(navn, 1):
        fil = UT / "variabler" / f"{n}.json"
        try:
            if fil.exists() and not alle:
                ds = json.loads(fil.read_text(encoding="utf-8"))
            else:
                pp = hent(f"{BASE}/variable/no.ssb.fdb/{versjon}/{n}")
                ds = pp["ds"]
                datalager = datalager or pp.get("dataStore")
                nye_json[n] = ds
            rad, kodelinjer_n = bygg_rad(n, ds)
        except Exception as e:  # noqa: BLE001 - samle feil og avbryt før noe skrives
            print(f"FEIL {n}: {e!r}", file=sys.stderr)
            feil.append(f"{n} ({e.__class__.__name__})")
            continue
        rader.append(rad)
        kodelinjer += kodelinjer_n
        if i % 50 == 0:
            print(f"detaljer: {i}/{len(navn)}", file=sys.stderr)

    # Med eksplisitt --versjon kan detaljsidene vise en nyere datalagerhistorikk, så da sjekkes ikke versjonen.
    problemer = kontroller(feil, navn, totalt, rader, kodelinjer, "" if a.versjon else versjon, datalager)
    if problemer:
        for p in problemer:
            print(f"PROBLEM: {p}", file=sys.stderr)
        if not tving:
            print("AVBRUTT: ingen filer er endret. Bruk --tving for å skrive likevel.", file=sys.stderr)
            sys.exit(1)
        print("--tving: skriver likevel.", file=sys.stderr)

    for n, ds in nye_json.items():
        (UT / "variabler" / f"{n}.json").write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    if rader:
        skriv_csv(UT / "variabler.csv", list(rader[0]), rader)
        skriv_csv(UT / "kodelister.csv", ["navn", "kode", "kategori"], kodelinjer)
    if datalager:
        (UT / "datalager.json").write_text(
            json.dumps(datalager, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    # Slett bare når listen er komplett, ellers kan --tving med en avkortet liste slette gyldige filer.
    komplett = len(set(navn)) == totalt
    utgaatt = sorted(p for p in (UT / "variabler").glob("*.json") if komplett and p.stem not in set(navn))
    for p in utgaatt:
        p.unlink()
    if utgaatt:
        print(f"slettet {len(utgaatt)} variabler som ikke lenger står i katalogen: "
              + " ".join(p.stem for p in utgaatt[:10]) + (" ..." if len(utgaatt) > 10 else ""), file=sys.stderr)
    print(f"ferdig: {len(rader)} variabler fra versjon {versjon}", file=sys.stderr)


if __name__ == "__main__":
    main()
