"""Slår opp i SSB Klass og lager recode-linjer for microdata.no.

Underkommandoer (fra prosjektmappen, python verktoy/klass.py <kommando> --help):

  sok <tekst>                      Finn klassifikasjoner og ID-er.
  koder <id> [--dato D] [--nivaa N]
                                   List koder gyldige på datoen (standard i dag).
  grupper <id> --nivaa N [--dato D] [--variabel V] [--navn X]
                                   recode fra detaljerte koder til overordnet kode på nivå N
                                   (STYRK 4-siffer -> hovedgruppe, SN 5-siffer -> divisjon/seksjon,
                                   NUS -> utdanningsnivå, land -> verdensdel).
  kobling <id> [--dato D] [--tabell TEKST] [--navn X]
                                   Uten --tabell: list koblingstabellene til versjonen som gjelder
                                   på datoen. Med --tabell: recode fra kodene i <id> til kodene i
                                   den andre klassifikasjonen.

Eksempler:
  python verktoy/klass.py sok yrke
  python verktoy/klass.py grupper 545 --nivaa 3 --variabel BEFOLKNING_LANDBAK3GEN --navn landbak
  python verktoy/klass.py grupper 7 --nivaa 1 --variabel REGSYS_ARB_YRKE_STYRK08 --navn yrke
  python verktoy/klass.py grupper 6 --nivaa 2 --dato 2024-01-01 --variabel REGSYS_NARING_SN2007 --navn naring
  python verktoy/klass.py kobling 36 --tabell "ISCED 2011 Attainment" --navn nus

Utskriften er `generate`/`recode` for en strengvariabel. Reglene kjører i rekkefølge, og verdier som allerede
er omkodet påvirkes ikke av senere regler. Med --variabel tas bare koder med som finnes i variabelens
kodeliste (metadata/kodelister.csv), og koder som mangler i Klass på datoen listes i en kommentar.
"""

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

KLASS = "https://data.ssb.no/api/klass/v1"
KODELISTER = Path(__file__).resolve().parent.parent / "metadata" / "kodelister.csv"
MAKS_KODER = 25  # koder per regel
MAKS_TEGN = 600  # omtrentlig makslengde på en recode-linje


def hent(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"Klass svarte {e.code} for {url}")
    except urllib.error.URLError as e:
        sys.exit(f"Får ikke kontakt med Klass ({e.reason}). Verktøyet krever nettilgang.")


def koder_ved(klassid, dato):
    return hent(f"{KLASS}/classifications/{klassid}/codesAt?date={dato}&language=nb")["codes"]


def kodeliste(variabel):
    """Koder i variabelens gjeldende kodeliste, fra metadata/kodelister.csv."""
    with open(KODELISTER, encoding="utf-8-sig", newline="") as f:
        koder = [r[1] for r in csv.reader(f, delimiter=";") if r and r[0] == variabel]
    if not koder:
        sys.exit(f"Fant ikke kodeliste for {variabel} i metadata/kodelister.csv")
    return koder


def q(tekst):
    return "'" + tekst.replace("'", "’") + "'"


def regler_fra(mapping, navn):
    """mapping: {mål: (merkelapp, [kilder])} -> recode-linjer (store regioner deles i biter)."""
    regler = []
    for mal in sorted(mapping):
        merke, kilder = mapping[mal]
        kilder = sorted(set(kilder))
        for i in range(0, len(kilder), MAKS_KODER):
            bit = " ".join(q(k) for k in kilder[i : i + MAKS_KODER])
            lab = f" {q(merke)}" if i == 0 and merke else ""
            regler.append(f"({bit} = {q(mal)}{lab})")
    linjer, naa = [], ""
    for regel in regler:
        if naa and len(naa) + len(regel) > MAKS_TEGN:
            linjer.append(naa)
            naa = ""
        naa = f"{naa} {regel}" if naa else regel
    if naa:
        linjer.append(naa)
    return [f"recode {navn} {l}" for l in linjer]


def kommando_sok(a):
    r = hent(f"{KLASS}/classifications/search?query={urllib.parse.quote(a.tekst)}")
    sett = set()
    for c in r["_embedded"]["searchResults"]:
        if c["language"] == "nb" and c["id"] not in sett:
            sett.add(c["id"])
            print(f"{c['id']:>5}  {c['name']}")


def kommando_koder(a):
    for c in koder_ved(a.id, a.dato):
        if a.nivaa and c["level"] != str(a.nivaa):
            continue
        print(f"{c['code']};{c['parentCode'] or ''};{c['level']};{c['name']}")


def kommando_grupper(a):
    koder = {c["code"]: c for c in koder_ved(a.id, a.dato)}
    if not koder:
        sys.exit(f"Ingen koder i klassifikasjon {a.id} på {a.dato}")
    nivaaer = sorted({int(c["level"]) for c in koder.values()})
    if a.nivaa not in nivaaer:
        sys.exit(f"Nivå {a.nivaa} finnes ikke. Nivåer: {nivaaer}")

    def forelder(kode):
        """Overordnet kode på nivå a.nivaa, eller None hvis koden ligger over det nivået."""
        c = koder[kode]
        while int(c["level"]) > a.nivaa:
            c = koder.get(c["parentCode"])
            if c is None:
                return None
        return c["code"] if int(c["level"]) == a.nivaa else None

    onsket = kodeliste(a.variabel) if a.variabel else sorted(koder)
    mapping = defaultdict(lambda: ("", []))
    mangler, hoyt = [], 0
    for k in onsket:
        if k not in koder:
            mangler.append(k)
            continue
        mal = forelder(k)
        if mal is None:
            hoyt += 1  # koden ligger over omkodingsnivået, står uendret
            continue
        if mal == k:
            continue  # kilden er allerede på målnivå
        mapping[mal] = (koder[mal]["name"], mapping[mal][1] + [k])

    print(f"// Klass {a.id} ({a.dato}): koder omkodet til nivå {a.nivaa}. Hentet {date.today().isoformat()}.")
    if a.variabel:
        print(f"// Begrenset til koder i kodelisten til {a.variabel}.")
        if mangler:
            vis = " ".join(mangler[:30]) + (" ..." if len(mangler) > 30 else "")
            print(f"// {len(mangler)} koder i variabelen finnes ikke i Klass på {a.dato} og står uendret: {vis}")
    if hoyt:
        print(f"// {hoyt} koder ligger over nivå {a.nivaa} og står uendret.")
    print(f"generate {a.navn}_nivaa{a.nivaa} = {a.navn}")
    for linje in regler_fra(mapping, f"{a.navn}_nivaa{a.nivaa}"):
        print(linje)


def kommando_kobling(a):
    kl = hent(f"{KLASS}/classifications/{a.id}")
    ver = [v for v in kl["versions"] if (v.get("validFrom") or "") <= a.dato and (not v.get("validTo") or a.dato < v["validTo"])]
    if not ver:
        sys.exit(f"Ingen versjon av {a.id} er gyldig {a.dato}")
    v = hent(ver[0]["_links"]["self"]["href"])
    tabeller = v["correspondenceTables"]
    if not a.tabell:
        print(f"// Koblingstabeller for {v['name'].strip()} (gyldig {a.dato}):")
        for t in tabeller:
            print(t["name"].strip())
        return
    treff = [t for t in tabeller if a.tabell.lower() in t["name"].lower()]
    if len(treff) != 1:
        sys.exit(f"--tabell «{a.tabell}» traff {len(treff)} tabeller. Bruk uten --tabell for å se listen.")
    t = treff[0]
    tab = hent(t["_links"]["self"]["href"])
    forste = t["name"].strip().startswith(v["name"].strip())
    mapping, delt = defaultdict(lambda: ("", [])), defaultdict(set)
    kobl = {}
    for m in tab["correspondenceMaps"]:
        kilde, mal, mnavn = (m["sourceCode"], m["targetCode"], m["targetName"]) if forste else (m["targetCode"], m["sourceCode"], m["sourceName"])
        if kilde in kobl and kobl[kilde][0] != mal:
            delt[kilde] |= {kobl[kilde][0], mal}
        kobl.setdefault(kilde, (mal, mnavn))
    for kilde, (mal, mnavn) in kobl.items():
        if kilde in delt:
            continue
        mapping[mal] = (mnavn.strip(), mapping[mal][1] + [kilde])
    print(f"// {t['name'].strip()}. Hentet {date.today().isoformat()}.")
    if delt:
        print(f"// {len(delt)} koder kobles til flere mål og er utelatt (står uendret): " + " ".join(sorted(delt)[:30]))
    print(f"generate {a.navn}_kobl = {a.navn}")
    for linje in regler_fra(mapping, f"{a.navn}_kobl"):
        print(linje)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="kommando", required=True)
    idag = date.today().isoformat()

    s = sub.add_parser("sok", help="finn klassifikasjoner")
    s.add_argument("tekst")
    s.set_defaults(f=kommando_sok)

    s = sub.add_parser("koder", help="list koder")
    s.add_argument("id", type=int)
    s.add_argument("--dato", default=idag)
    s.add_argument("--nivaa", type=int)
    s.set_defaults(f=kommando_koder)

    s = sub.add_parser("grupper", help="recode til overordnet nivå")
    s.add_argument("id", type=int)
    s.add_argument("--nivaa", type=int, required=True)
    s.add_argument("--dato", default=idag)
    s.add_argument("--variabel", help="microdata-variabel; begrenser til koder i kodelisten")
    s.add_argument("--navn", default="kode", help="variabelnavn i skriptet (standard kode)")
    s.set_defaults(f=kommando_grupper)

    s = sub.add_parser("kobling", help="recode via koblingstabell")
    s.add_argument("id", type=int)
    s.add_argument("--dato", default=idag)
    s.add_argument("--tabell", help="del av tabellnavnet")
    s.add_argument("--navn", default="kode")
    s.set_defaults(f=kommando_kobling)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
