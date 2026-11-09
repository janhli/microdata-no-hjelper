"""Laster ned variabelkatalogen fra microdata.no til metadata/.

Henter listesidene (20 variabler per side) og deretter detaljsiden for hver
variabel. Metadata ligger som JSON i <script id="__NEXT_DATA__"> på sidene.

Resultat:
  metadata/variabler.csv          oversikt, én linje per variabel
  metadata/kodelister.csv         gjeldende kodeliste for alle variabler (navn;kode;kategori)
  metadata/variabler/<NAVN>.json  full metadata inkl. kodelistehistorikk og måletidspunkter
  metadata/datalager.json         datalagerets versjonshistorikk

Kjøres fra prosjektmappen:  python verktoy/hent_variabler.py [--alle]
Uten --alle hoppes variabler som allerede ligger i metadata/variabler/ over.
"""

import csv
import datetime as dt
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://microdata.no/discovery"
UT = Path(__file__).resolve().parent.parent / "metadata"
PAUSE = 0.3  # sekunder mellom forespørsler

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


def main():
    (UT / "variabler").mkdir(parents=True, exist_ok=True)

    navn, side = [], 0
    while True:
        data = hent(f"{BASE}/variables?pageIndex={side}")["data"]
        navn += [d["name"] for d in data["dataStructures"]]
        print(f"liste side {side}: {len(navn)}/{data['totalCount']}", file=sys.stderr)
        if len(navn) >= data["totalCount"] or not data["dataStructures"]:
            break
        side += 1

    alle = "--alle" in sys.argv
    rader, kodelinjer, datalager = [], [], None
    for i, n in enumerate(navn, 1):
        fil = UT / "variabler" / f"{n}.json"
        if fil.exists() and not alle:
            ds = json.loads(fil.read_text(encoding="utf-8"))
        else:
            try:
                pp = hent(f"{BASE}/variable/no.ssb.fdb/58/{n}")
            except Exception as e:  # noqa: BLE001 - logg og fortsett
                print(f"FEIL {n}: {e}", file=sys.stderr)
                continue
            ds = pp["ds"]
            datalager = datalager or pp.get("dataStore")
            fil.write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")

        koder = gjeldende_kodeliste(ds)
        kodelinjer += [{"navn": n, "kode": k["code"], "kategori": k["category"].strip()} for k in koder]
        mv = ds["measureVariable"]
        siste = mv["representedVariables"][-1]
        dekning = ds.get("temporalCoverage", {})
        rader.append({
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
        })
        if i % 50 == 0:
            print(f"detaljer: {i}/{len(navn)}", file=sys.stderr)

    with open(UT / "variabler.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rader[0]), delimiter=";")
        w.writeheader()
        w.writerows(rader)
    with open(UT / "kodelister.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["navn", "kode", "kategori"], delimiter=";")
        w.writeheader()
        w.writerows(kodelinjer)
    if datalager:
        (UT / "datalager.json").write_text(
            json.dumps(datalager, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ferdig: {len(rader)} variabler", file=sys.stderr)


if __name__ == "__main__":
    main()
