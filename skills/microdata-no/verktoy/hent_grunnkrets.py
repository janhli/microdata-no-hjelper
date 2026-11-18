"""Laster ned grunnkretsendringer og inndelinger bygd på grunnkrets fra SSB Klass (klassifikasjon 1).

Lagrer til metadata/grunnkrets/:
  endringer.csv    dato;gammel;ny, alle endringer i grunnkretskoder (8 sifre) siden 1990
  inndelinger.csv  inndeling;grunnkrets;kode;navn, fra koblingstabellene til gjeldende grunnkretsversjon:
                   lks (levekårssoner), bydel (Oslo, Bergen, Trondheim, Stavanger), delbydel (Oslo)
  HENTET           dato for nedlasting og hvilken versjon og hvilke tabeller som ble brukt

Brukes av verktoy/grunnkrets.py. Kjøres fra prosjektmappen:  python verktoy/hent_grunnkrets.py

Klass bryter ofte forbindelsen midt i store svar (over ca. 150 kB). Nedlastingen fortsetter da med
Range-forespørsler. Ved problemer (for få rader, manglende tabell) skrives ingenting.
"""

import csv
import io
import json
import os
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

KLASS = "https://data.ssb.no/api/klass/v1"
FRA = "1990-01-01"  # BEFOLKNING_GRUNNKRETS starter her
UT = Path(__file__).resolve().parent.parent / "metadata" / "grunnkrets"
# inndeling -> starten på tabellnavnet i Klass, og minste antall rader
TABELLER = {
    "lks": ("Levekårssoner", 3000),
    "bydel": ("Bydelsinndeling", 1000),
    "delbydel": ("Delbydeler i Oslo", 400),
}
MIN_ENDRINGER = 15000


def hent(url, forsok=40):
    data = b""
    for i in range(forsok):
        hd = {"Accept": "application/json"}
        if data:
            hd["Range"] = f"bytes={len(data)}-"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hd), timeout=180) as r:
                if data and r.status != 206:
                    data = b""
                data += r.read()
            return json.loads(data)
        except Exception as e:  # noqa: BLE001 - IncompleteRead og nettfeil: fortsett fra der vi kom
            data += getattr(e, "partial", b"") or b""
            time.sleep(1 + i % 5)
    raise RuntimeError(f"ga opp etter {forsok} forsøk: {url}")


def csv_tekst(felter, rader):
    f = io.StringIO()
    w = csv.writer(f, delimiter=";", lineterminator="\n")
    w.writerow(felter)
    w.writerows(rader)
    return f.getvalue()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    problemer = []
    endr = hent(f"{KLASS}/classifications/1/changes?from={FRA}&language=nb")["codeChanges"]
    endringer = sorted({(e["changeOccurred"], e["oldCode"], e["newCode"]) for e in endr
                        if len(e["oldCode"]) == 8 and len(e["newCode"]) == 8})
    if len(endringer) < MIN_ENDRINGER:
        problemer.append(f"bare {len(endringer)} endringer (minst {MIN_ENDRINGER})")

    kl = hent(f"{KLASS}/classifications/1")
    idag = date.today().isoformat()
    gjeldende = [v for v in kl["versions"] if v["validFrom"] <= idag and (not v.get("validTo") or idag < v["validTo"])]
    if len(gjeldende) != 1:
        sys.exit(f"PROBLEM: fant {len(gjeldende)} gjeldende versjoner av Klass 1")
    versjon = hent(gjeldende[0]["_links"]["self"]["href"])
    rader, brukt = [], []
    for inndeling, (start, minst) in TABELLER.items():
        treff = [t for t in versjon["correspondenceTables"] if t["name"].strip().startswith(start)]
        if len(treff) != 1:
            problemer.append(f"{inndeling}: {len(treff)} tabeller begynner med «{start}»")
            continue
        tab = hent(treff[0]["_links"]["self"]["href"])
        n = 0
        for m in tab["correspondenceMaps"]:
            if len(m["targetCode"]) == 8:  # grunnkrets er målet i alle tre tabellene
                rader.append((inndeling, m["targetCode"], m["sourceCode"], m["sourceName"].strip()))
                n += 1
        if n < minst:
            problemer.append(f"{inndeling}: bare {n} grunnkretser (minst {minst})")
        brukt.append(f"{inndeling}: {tab['name'].strip()} ({n} grunnkretser)")
    dobbel = len(rader) - len({(r[0], r[1]) for r in rader})
    if dobbel:
        problemer.append(f"{dobbel} grunnkretser står i flere enheter i samme inndeling")
    if problemer:
        print("PROBLEM: " + "; ".join(problemer), file=sys.stderr)
        sys.exit(1)

    UT.mkdir(parents=True, exist_ok=True)
    data = {"endringer.csv": csv_tekst(["dato", "gammel", "ny"], endringer),
            "inndelinger.csv": csv_tekst(["inndeling", "grunnkrets", "kode", "navn"], sorted(rader))}
    if all((UT / n).exists() and (UT / n).read_text(encoding="utf-8") == t for n, t in data.items()):
        print("Ingen endringer i grunnkretsene (HENTET står urørt, så den ukentlige jobben åpner ingen PR).")
        return
    filer = {
        **data,
        "HENTET": f"{idag}\nKlass 1: {versjon['name'].strip()}\n" + "\n".join(brukt) + "\n",
    }
    for navn, tekst in filer.items():  # skriv alt til .tmp først, så bytt inn
        (UT / f"{navn}.tmp").write_text(tekst, encoding="utf-8", newline="\n")
    for navn in filer:
        os.replace(UT / f"{navn}.tmp", UT / navn)
    print(f"Skrev {UT}: {len(endringer)} endringer, " + ", ".join(brukt))


if __name__ == "__main__":
    main()
