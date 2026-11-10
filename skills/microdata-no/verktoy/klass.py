"""Slår opp i SSB Klass og lager recode-linjer for microdata.no.

Underkommandoer (fra prosjektmappen, python verktoy/klass.py <kommando> --help):

  sok <tekst>                      Finn klassifikasjoner og ID-er.
  koder <id> [--dato D] [--nivaa N]
                                   List koder gyldige på datoen (standard i dag).
  grupper <id> --nivaa N [--dato D] [--variabel V] [--navn X]
                                   recode fra detaljerte koder til overordnet kode på nivå N
                                   (STYRK 4-siffer -> hovedgruppe, SN 5-siffer -> divisjon/seksjon,
                                   NUS -> utdanningsnivå, land -> verdensdel).
  kobling <id> [--dato D] [--tabell TEKST] [--navn X] [--nivaa N] [--utelat KODER]
                                   Uten --tabell: list koblingstabellene til versjonen som gjelder
                                   på datoen. Med --tabell: recode fra kodene i <id> til kodene i
                                   den andre klassifikasjonen.

Eksempler:
  python verktoy/klass.py sok yrke
  python verktoy/klass.py grupper 545 --nivaa 3 --variabel BEFOLKNING_LANDBAK3GEN --navn landbak
  python verktoy/klass.py grupper 7 --nivaa 1 --variabel REGSYS_ARB_YRKE_STYRK08 --navn yrke
  python verktoy/klass.py grupper 6 --nivaa 2 --dato 2024-01-01 --variabel REGSYS_NARING_SN2007 --navn naring
  python verktoy/klass.py kobling 36 --tabell "ISCED 2011 Attainment" --navn nus

Utskriften er `generate`/`recode` for en strengvariabel, laget av verktoy/recode_regler.py. Er en kode både
kilde og mål (vanlig i koblinger mellom versjoner, f.eks. SN2007 og SN2025), samles de reglene i én kommando,
så ingen verdi omkodes to ganger. Med --variabel tas bare koder med som finnes i variabelens
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
UTELAT_HJELP = ("kommaseparerte målkoder som tas ut, f.eks. 17.240 fra microdata.no-feilen «Omkodingen til "
                "17.240 påvirker for få enheter». Legg til én kode per runde og kjør på nytt")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recode_regler import konflikter, recode_linjer  # noqa: E402


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


def skriv_recode(variabel, kart, merkelapper, utelat=""):
    """Skriver recode-linjene, og sier fra hvis noen regler måtte samles i én kommando.

    utelat: kommaseparerte målkoder som tas ut. microdata.no stopper en recode der én målverdi treffer
    1–9 enheter («Omkodingen til X påvirker for få enheter»). Kildekodene til X står da uendret.
    """
    ut = {m.strip() for m in utelat.split(",") if m.strip()}
    if ut:
        fjernet = sorted(k for k, m in kart.items() if m in ut)
        ukjent = sorted(ut - set(kart.values()))
        kart = {k: m for k, m in kart.items() if m not in ut}
        print(f"// --utelat: {len(ut)} målkoder tatt ut ({' '.join(sorted(ut))}). Kildekoder som står uendret: "
              + (" ".join(fjernet) or "ingen"))
        if ukjent:
            print(f"// --utelat: {' '.join(ukjent)} er ikke målkode i utskriften (sjekk koden fra feilmeldingen)")
    konf = konflikter({k: m for k, m in kart.items() if k != m})
    if konf:
        print(f"// {len(konf)} koder er både kilde og mål i ulike regler. De står samlet i første recode-kommando,")
        print("// så ingen verdi omkodes to ganger. Ikke del den linjen.")
    for linje in recode_linjer(variabel, kart, merkelapper):
        print(linje)


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

    # Er hierarkiet bygd på prefiks (forelderkoden er starten av koden, som i SN, STYRK og NUS)?
    # Da kan en kode som mangler i Klass (f.eks. 43.220) plasseres via nærmeste kode som finnes (43.22).
    med_forelder = [c for c in koder.values() if c["parentCode"]]
    prefiks = bool(med_forelder) and sum(c["code"].startswith(c["parentCode"]) for c in med_forelder) >= 0.8 * len(med_forelder)

    def naermeste(kode):
        k = kode
        while len(k) > 1:
            k = k[:-1].rstrip(".")
            if k in koder:
                return k
        return None

    onsket = kodeliste(a.variabel) if a.variabel else sorted(koder)
    kart, merkelapper = {}, {}
    mangler, via, hoyt = [], [], 0
    for k in onsket:
        oppslag = k
        if k not in koder:
            oppslag = naermeste(k) if prefiks else None
            if oppslag is None:
                mangler.append(k)
                continue
            via.append(f"{k}→{oppslag}")
        mal = forelder(oppslag)
        if mal is None:
            hoyt += 1  # koden ligger over omkodingsnivået, står uendret
            continue
        if mal == k:
            continue  # kilden er allerede på målnivå
        kart[k] = mal
        merkelapper[mal] = koder[mal]["name"]

    print(f"// Klass {a.id} ({a.dato}): koder omkodet til nivå {a.nivaa}. Hentet {date.today().isoformat()}.")
    if a.variabel:
        print(f"// Begrenset til koder i kodelisten til {a.variabel}.")
        if via:
            vis = " ".join(via[:30]) + (" ..." if len(via) > 30 else "")
            print(f"// {len(via)} koder finnes ikke i Klass på {a.dato}, men er gruppert via nærmeste overordnede kode: {vis}")
        if mangler:
            vis = " ".join(mangler[:30]) + (" ..." if len(mangler) > 30 else "")
            print(f"// {len(mangler)} koder i variabelen finnes ikke i Klass på {a.dato} og står uendret: {vis}")
    if hoyt:
        print(f"// {hoyt} koder ligger over nivå {a.nivaa} og står uendret.")
    print(f"generate {a.navn}_nivaa{a.nivaa} = {a.navn}")
    skriv_recode(f"{a.navn}_nivaa{a.nivaa}", kart, merkelapper, a.utelat)


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
    # Med --nivaa løftes hvert mål til overordnet kode på nivå N i den andre klassifikasjonen. En kilde
    # med flere detaljerte mål blir da entydig hvis alle målene ligger under samme overordnede kode.
    opp, nivaanavn = (lambda kode: kode), {}
    if a.nivaa:
        lenke = tab["_links"]["target" if forste else "source"]["href"].split("{")[0]
        items = {i["code"]: i for i in hent(f"{lenke}?language=nb")["classificationItems"]}
        nivaaer = sorted({int(i["level"]) for i in items.values()})
        if a.nivaa not in nivaaer:
            sys.exit(f"Nivå {a.nivaa} finnes ikke i målklassifikasjonen. Nivåer: {nivaaer}")
        nivaanavn = {k: i["name"] for k, i in items.items() if int(i["level"]) == a.nivaa}

        def opp(kode):
            i = items.get(kode)
            while i is not None and int(i["level"]) > a.nivaa:
                i = items.get(i["parentCode"])
            return i["code"] if i is not None and int(i["level"]) == a.nivaa else None
    # Alle mål per kilde. Klass kan ha rader uten mål (targetCode er null): koden har ingen motpart.
    maal_per_kilde, navn_paa_maal = defaultdict(set), {}
    for m in tab["correspondenceMaps"]:
        kilde, mal, mnavn = (m["sourceCode"], m["targetCode"], m["targetName"]) if forste else (m["targetCode"], m["sourceCode"], m["sourceName"])
        if kilde is None:
            continue
        if mal is not None and a.nivaa:
            mal, mnavn = opp(mal), None
        maal_per_kilde[kilde].add(mal)
        if mal is not None:
            navn_paa_maal[mal] = (mnavn or nivaanavn.get(mal, "")).strip()
    kart, delt, uten_maal = {}, [], []
    for kilde, maal in maal_per_kilde.items():
        if maal == {None}:
            uten_maal.append(kilde)
        elif len(maal) > 1:
            delt.append(kilde)  # flere mål, eller bare delvis motpart
        else:
            kart[kilde] = next(iter(maal))
    print(f"// {t['name'].strip()}. Hentet {date.today().isoformat()}.")
    print(f"// Retning: koder i {v['name'].strip()} -> den andre klassifikasjonen (velg versjon med --dato).")
    if a.nivaa:
        print(f"// Målene er løftet til nivå {a.nivaa} i den andre klassifikasjonen. {len(kart)} kildekoder får entydig mål.")
    if delt:
        print(f"// {len(delt)} koder kobles til flere mål og er utelatt (står uendret): " + " ".join(sorted(delt)[:30])
              + (" ..." if len(delt) > 30 else ""))
        print("// NB: Uendrede koder er fortsatt i den gamle klassifikasjonen, så resultatet blander to kodeverk.")
        print("//     SN2002 -> SN2007 lot 42 % av sysselsatte stå uendret (2006). Ikke grupper på kodens sifre")
        print("//     uten å skille dem ut." + ("" if a.nivaa else " --nivaa 1 eller 2 gir langt færre uendrede koder."))
    if uten_maal:
        print(f"// {len(uten_maal)} koder har ingen motpart i tabellen og står uendret: " + " ".join(sorted(uten_maal)))
    print(f"generate {a.navn}_kobl = {a.navn}")
    skriv_recode(f"{a.navn}_kobl", kart, navn_paa_maal, a.utelat)


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
    s.add_argument("--utelat", default="", help=UTELAT_HJELP)
    s.set_defaults(f=kommando_grupper)

    s = sub.add_parser("kobling", help="recode via koblingstabell")
    s.add_argument("id", type=int)
    s.add_argument("--dato", default=idag)
    s.add_argument("--tabell", help="del av tabellnavnet")
    s.add_argument("--navn", default="kode")
    s.add_argument("--nivaa", type=int, help="omkod til overordnet kode på dette nivået i den andre klassifikasjonen "
                   "(f.eks. 1 seksjon, 2 divisjon i SN). Gir færre koder med flere mål og færre små målkoder")
    s.add_argument("--utelat", default="", help=UTELAT_HJELP)
    s.set_defaults(f=kommando_kobling)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
