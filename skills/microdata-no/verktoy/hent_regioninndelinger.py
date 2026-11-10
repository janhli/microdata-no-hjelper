"""Lager koblingstabeller fra kommune til regioninndelinger (politidistrikt, helseregion osv.).

Kilder:
  * SSB Klass: nyeste koblingstabell mellom hver regionklassifikasjon og Kommuneinndeling (eller
    Fylkesinndeling for landsdeler), som tilsvarer det repoet norge-administrative-grenser gjør i
    data-pipeline/scripts/05-add-distrikter.mjs. Er tabellen eldre enn ønsket kommuneinndeling
    (helseregionene har bare tabell mot Kommuneinndeling 2020), oversettes kommunekodene fram med
    metadata/kommuneendringer.json (kjør verktoy/hent_kommuneendringer.py først).
  * Manuelt lastet inn: metadata/regioner/manuelt/ (bo- og arbeidsmarkedsregioner, TØI), som ikke
    finnes i Klass.

Skriver metadata/regioner/<inndeling>.csv (kolonner: kommunenr;regionkode;regionnavn) og INDEX.csv.
Hver tabell må dekke nøyaktig kommunene i den valgte kommuneinndelingen, en region per kommune.

Kjøres fra prosjektmappen:  python verktoy/hent_regioninndelinger.py [--aar 2024]
"""

import argparse
import csv
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
UT = SKILL / "metadata" / "regioner"
MANUELT = UT / "manuelt"
ENDRINGER = SKILL / "metadata" / "kommuneendringer.json"
KLASS = "https://data.ssb.no/api/klass/v1"
KOMMUNEINNDELING = 131

# slug, Klass-id, mot hva (Kommuneinndeling/Fylkesinndeling), beskrivelse
INNDELINGER = [
    ("politidistrikt", 109, "Kommuneinndeling", "Politidistrikt"),
    ("valgdistrikt", 543, "Kommuneinndeling", "Valgdistrikt (stortingsvalg)"),
    ("okonomiske_regioner", 108, "Kommuneinndeling", "Økonomiske regioner"),
    ("helseregioner", 105, "Kommuneinndeling", "Helseregioner"),
    ("familievernregioner", 557, "Kommuneinndeling", "Familievernregioner"),
    ("barnevernsregioner", 563, "Kommuneinndeling", "Barnevernsregioner"),
    ("reiselivsregioner", 527, "Kommuneinndeling", "Reiselivsregioner"),
    ("samiske_valgkretser", 581, "Kommuneinndeling", "Samiske valgkretser"),
    ("sentralitet", 128, "Kommuneinndeling", "Sentralitet (SSBs indeks, ikke sammenhengende regioner)"),
    ("landsdeler", 106, "Fylkesinndeling", "Landsdeler (via fylke)"),
]


def hent(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def kommuner_ved(aar):
    koder = hent(f"{KLASS}/classifications/{KOMMUNEINNDELING}/codesAt?date={aar}-01-01&language=nb")["codes"]
    # 99xx er «uoppgitt», ikke en kommune
    return {c["code"]: c["name"].strip() for c in koder if re.fullmatch(r"\d{4}", c["code"]) and not c["code"].startswith("99")}


def nyeste_tabell(klassid, mot, aar):
    """Nyeste koblingstabell mot <mot> <år> med år <= aar. Returnerer (tabellnavn, tabellår, koblinger)."""
    kl = hent(f"{KLASS}/classifications/{klassid}")
    gjeldende = [v for v in kl["versions"] if not v.get("validTo")]
    if not gjeldende:
        sys.exit(f"Ingen gjeldende versjon av klassifikasjon {klassid}")
    v = hent(gjeldende[0]["_links"]["self"]["href"])
    kandidater = []
    for t in v["correspondenceTables"]:
        m = re.search(rf"^{re.escape(v['name'])} - {mot} (\d{{4}})$", t["name"])
        # Fylkestabeller kan ha nyere år enn kommuneinndelingen. Dekningssjekken under fanger avvik.
        if m and (int(m.group(1)) <= aar or mot == "Fylkesinndeling"):
            kandidater.append((int(m.group(1)), t))
    if not kandidater:
        sys.exit(f"Ingen koblingstabell mot {mot} for {v['name']} (år <= {aar})")
    ar, t = max(kandidater, key=lambda x: x[0])
    tab = hent(t["_links"]["self"]["href"])
    kobl = [(m["sourceCode"], m["sourceName"].strip(), m["targetCode"]) for m in tab["correspondenceMaps"]]
    return t["name"], ar, kobl


def kommune_til_aar(kode, fra_aar, til_aar, endr):
    """Følger en kommunekode fra kommuneinndeling <fra_aar> til <til_aar>. Gir liste med nye koder."""
    tilstand = {kode}
    datoer = sorted({e["dato"] for e in endr if f"{fra_aar}-01-01" < e["dato"] <= f"{til_aar}-12-31"})
    for dato in datoer:
        ny = set()
        for s in tilstand:
            mal = [e["ny"] for e in endr if e["dato"] == dato and e["gammel"] == s]
            ny |= set(mal) if mal else {s}
        tilstand = ny
    return sorted(tilstand)


def slutt_pa_tom(kommuner, kobl, slug, kilde):
    """Sjekker at hver kommune har nøyaktig en region."""
    mangler = sorted(set(kommuner) - set(kobl))
    ekstra = sorted(set(kobl) - set(kommuner))
    return mangler, ekstra


def skriv_csv(slug, kobl, kommuner):
    with open(UT / f"{slug}.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["kommunenr", "regionkode", "regionnavn"])
        for k in sorted(kobl):
            kode, navn = kobl[k]
            w.writerow([k, kode, navn])


def fra_klass(slug, klassid, mot, aar, kommuner, endr):
    tabell, tabellaar, kobl = nyeste_tabell(klassid, mot, aar)
    ut = {}
    if mot == "Fylkesinndeling":
        fylke = {}
        for kode, navn, maal in kobl:
            if maal in fylke and fylke[maal][0] != kode:
                sys.exit(f"{slug}: fylke {maal} i flere regioner")
            fylke[maal] = (kode, navn)
        for k in kommuner:
            if k[:2] in fylke:
                ut[k] = fylke[k[:2]]
        oversatt = False
    else:
        oversatt = tabellaar < aar
        for kode, navn, maal in kobl:
            if not re.fullmatch(r"\d{4}", maal):
                continue
            mal = kommune_til_aar(maal, tabellaar, aar, endr) if oversatt else [maal]
            for k in mal:
                if k in ut and ut[k][0] != kode:
                    sys.exit(f"{slug}: kommune {k} er både i {ut[k][0]} og {kode} ({tabell})")
                ut[k] = (kode, navn)
    return tabell, oversatt, ut


def fra_ba_regioner(kommuner):
    """TØIs bo- og arbeidsmarkedsregioner, lastet inn manuelt (kommunenr_2024, BA-region)."""
    fil = MANUELT / "bo_og_arbeidsmarkedsregioner_2024.csv"
    ut, navn = {}, {}
    linjer = fil.read_text(encoding="utf-8-sig").splitlines()
    for rad in csv.DictReader(linjer):
        k = rad["kommunenr_2024"].strip()
        m = re.fullmatch(r"0*(\d+)\s+(.+)", rad["BA-region"].strip())
        if not m:
            sys.exit(f"Ugyldig BA-region «{rad['BA-region']}» for {k}")
        kode, nav = f"{int(m.group(1)):03d}", m.group(2).strip()
        if navn.setdefault(kode, nav) != nav:
            sys.exit(f"Regionnummer {kode} har to navn: {navn[kode]} og {nav}")
        if k in ut and ut[k][0] != kode:
            sys.exit(f"Kommune {k} er i to BA-regioner: {ut[k][0]} og {kode}")
        ut[k] = (kode, nav)
    return fil.name, ut


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--aar", type=int, default=2024, help="kommuneinndelingen tabellene skal gjelde for (standard 2024)")
    a = ap.parse_args()
    if not ENDRINGER.exists():
        sys.exit("Mangler metadata/kommuneendringer.json. Kjør først: python verktoy/hent_kommuneendringer.py")
    endr = json.loads(ENDRINGER.read_text(encoding="utf-8"))["endringer"]

    kommuner = kommuner_ved(a.aar)
    UT.mkdir(parents=True, exist_ok=True)
    indeks = []
    problemer = []
    kilder = [(s, k, m, b) for s, k, m, b in INNDELINGER]
    for slug, klassid, mot, beskr in kilder:
        tabell, oversatt, kobl = fra_klass(slug, klassid, mot, a.aar, kommuner, endr)
        mangler, ekstra = slutt_pa_tom(kommuner, kobl, slug, tabell)
        # Svalbard (21xx) og «uoppgitt» ligger ofte utenfor regioninndelingene
        mangler_u = [k for k in mangler if not k.startswith("21")]
        if mangler_u:
            problemer.append(f"{slug}: {len(mangler_u)} kommuner uten region: {' '.join(mangler_u[:12])}")
        kobl = {k: v for k, v in kobl.items() if k in kommuner}
        skriv_csv(slug, kobl, kommuner)
        indeks.append([slug, beskr, f"Klass {klassid}", tabell, "ja" if oversatt else "nei", len({v[0] for v in kobl.values()}), len(kobl)])

    fil, ba = fra_ba_regioner(kommuner)
    mangler_ba = [k for k in sorted(set(kommuner) - set(ba)) if not k.startswith("21")]
    if mangler_ba:
        problemer.append(f"bo_og_arbeidsmarkedsregioner: {len(mangler_ba)} kommuner uten region: {' '.join(mangler_ba[:12])}")
    ba = {k: v for k, v in ba.items() if k in kommuner}
    skriv_csv("bo_og_arbeidsmarkedsregioner", ba, kommuner)
    indeks.append(["bo_og_arbeidsmarkedsregioner", "Bo- og arbeidsmarkedsregioner (TØI 2019, omkodet til 2024)",
                   "Manuelt (TØI)", fil, "nei", len({v[0] for v in ba.values()}), len(ba)])

    with open(UT / "INDEX.csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["inndeling", "beskrivelse", "kilde", "tabell", "oversatt_fra_eldre_kommuneinndeling",
                    "antall_regioner", "antall_kommuner"])
        w.writerows(indeks)
    (UT / "HENTET").write_text(f"{date.today().isoformat()} (kommuneinndeling {a.aar})\n", encoding="utf-8", newline="\n")

    for r in indeks:
        print(f"{r[0]:32} {r[5]:>4} regioner {r[6]:>4} kommuner  {r[3]}" + ("  [oversatt]" if r[4] == "ja" else ""))
    for p in problemer:
        print("ADVARSEL:", p)
    print(f"Kommuner i Kommuneinndeling {a.aar}: {len(kommuner)}")


if __name__ == "__main__":
    main()
