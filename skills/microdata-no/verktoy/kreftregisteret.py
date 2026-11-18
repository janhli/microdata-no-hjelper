"""Kreftformer og verdier fra Kreftregisterets metadatabase (ELVIS), og recode til kreftformer.

Underkommandoer (fra skill-mappen, python verktoy/kreftregisteret.py <kommando> --help):

  hent                             Henter kreftformene og verdiene for Kreftregisterets variabler i
                                   microdata.no fra ELVIS til metadata/fhi/kreftregisteret/.
  grupper --variabel V --nivaa N [--navn X] [--ukjent] [--utelat KODER]
                                   generate/recode fra en ICD-10-variabel (f.eks. S_TOPOGRAFIICD10,
                                   SOM_EP_HOVEDTILSTAND1) til kreftform. Nivå 1: 14 hovedgrupper
                                   (C15-C26 Fordøyelsesorganer ...). Nivå 2: tresifret kode (C18 Tykktarm).
  verdier --variabel V [--kreftform ICD]
                                   Verdiene i ELVIS for en variabel, med kreftformene hver verdi gjelder for
                                   (TNM-verdiene er ulike for ulike kreftformer).

Eksempler:
  python verktoy/kreftregisteret.py hent
  python verktoy/kreftregisteret.py grupper --variabel S_TOPOGRAFIICD10 --nivaa 1 --navn kreftform
  python verktoy/kreftregisteret.py grupper --variabel SOM_EP_HOVEDTILSTAND1 --nivaa 2 --navn kreft3 --ukjent
  python verktoy/kreftregisteret.py verdier --variabel S_PT --kreftform C50

Kilde: https://metadata.kreftregisteret.no (ELVIS). Hjelpesiden sier at variabler og verdier kan eksporteres
eller hentes via API av alle, uten registrering. API-et (/rest/v1/) er det nettsiden selv bruker, og det er
ikke dokumentert. hent kontrollerer derfor svarene og avslutter med feilkode uten å skrive filer hvis
formatet ser endret ut. Koblingen mellom variabel i microdata.no og ELVIS står i kolonnen ekstern_metadata i
metadata/variabler.csv (lenken til detaljsiden).

Kodene i microdata.no er uten punktum, med tre eller fire tegn (C18, C187). grupper bruker de tre første
tegnene. Kreftformene i ELVIS dekker C00-C96 (ikke C77-C79 spredning og C97 flere svulster) og D45-D47.
Koder som ikke er kreftform, står uendret, eller blir 'annet' med --ukjent.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recode_regler import q, recode_linjer  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
UT = SKILL / "metadata" / "fhi" / "kreftregisteret"
VARIABLER = SKILL / "metadata" / "variabler.csv"
KODELISTER = SKILL / "metadata" / "kodelister.csv"
ELVIS = "https://metadata.kreftregisteret.no"
DATALAGER = "no.fhi.kreftregisteret"
PAUSE = 0.5  # sekunder mellom forespørsler, av hensyn til tjenesten
DETALJ = re.compile(r"metadata\.kreftregisteret\.no/variables/detail/(\d+)")
MIN_KREFTFORMER = 80  # 102 i 2026-11


def hent_json(sti):
    req = urllib.request.Request(ELVIS + sti, headers={
        "User-Agent": "microdata-no-hjelper (https://github.com/janhli/microdata-no-hjelper)",
        "Accept": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except OSError:
            if i == 2:
                raise
            time.sleep(5 * (i + 1))
    time.sleep(PAUSE)
    return data


def elvis_variabler():
    """{microdata-navn: ELVIS-id} for Kreftregisterets variabler, fra lenkene i variabler.csv."""
    ut = {}
    with open(VARIABLER, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r.get("datalager") != DATALAGER:
                continue
            m = DETALJ.search(r.get("ekstern_metadata", ""))
            if m:
                ut[r["navn"]] = m.group(1)
    if not ut:
        sys.exit(f"Fant ingen {DATALAGER}-variabler med ELVIS-lenke i {VARIABLER.name}. Kjør hent_variabler.py først.")
    return ut


def skriv_csv(sti, felter, rader):
    with open(sti, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(felter)
        w.writerows(rader)


def kommando_hent(a):
    variabler = elvis_variabler()
    problemer = []

    sites = hent_json("/rest/v1/metadata/cancer-sites")
    former = []
    for s in sites:
        try:
            p = s.get("parent")
            former.append([2 if p else 1, s["icdCode"], s["name"].strip(), (s.get("nameEn") or "").strip(),
                           p["icdCode"] if p else "", p["name"].strip() if p else ""])
        except (KeyError, TypeError, AttributeError) as e:
            problemer.append(f"kreftform med uventet format ({e!r}): {str(s)[:120]}")
    if len(former) < MIN_KREFTFORMER:
        problemer.append(f"bare {len(former)} kreftformer (venter minst {MIN_KREFTFORMER})")
    topp = {f[1] for f in former if f[0] == 1}
    if any(f[0] == 2 and f[4] not in topp for f in former):
        problemer.append("kreftformer med overordnet gruppe som ikke finnes")

    verdier = []
    for navn, vid in sorted(variabler.items()):
        try:
            liste = hent_json(f"/rest/v1/variables/variable-values/:variable/{vid}")
        except OSError as e:
            problemer.append(f"{navn} (ELVIS {vid}): {e!r}")
            continue
        if not isinstance(liste, list):
            problemer.append(f"{navn} (ELVIS {vid}): svaret er ikke en liste")
            continue
        for v in liste:
            if "value" not in v:
                problemer.append(f"{navn} (ELVIS {vid}): verdi uten «value»")
                break
            gjelder = sorted({c["cancerSite"]["icdCode"] for c in v.get("valueCancerSites") or []
                              if not c.get("validTo")})
            verdier.append([navn, vid, v["value"], " ".join((v.get("description") or "").split()), " ".join(gjelder)])
        print(f"{navn:26} ELVIS {vid:>5}: {len(liste)} verdier", file=sys.stderr)

    if problemer:
        for p in problemer:
            print("PROBLEM:", p, file=sys.stderr)
        sys.exit("AVBRUTT: ingen filer er endret.")
    UT.mkdir(parents=True, exist_ok=True)
    skriv_csv(UT / "kreftformer.csv", ["nivaa", "icd", "navn", "navn_en", "gruppe_icd", "gruppe_navn"], former)
    skriv_csv(UT / "verdier.csv", ["variabel", "elvis_id", "verdi", "beskrivelse", "kreftformer"], verdier)
    (UT / "HENTET").write_text(f"{date.today().isoformat()} ({ELVIS})\n", encoding="utf-8", newline="\n")
    print(f"ferdig: {len(former)} kreftformer, {len(verdier)} verdier for {len(variabler)} variabler", file=sys.stderr)


def les_kreftformer():
    fil = UT / "kreftformer.csv"
    if not fil.exists():
        sys.exit(f"Mangler {fil}. Kjør først: python verktoy/kreftregisteret.py hent")
    with open(fil, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def kodeliste(variabel):
    with open(KODELISTER, encoding="utf-8-sig", newline="") as f:
        koder = [r[1] for r in csv.reader(f, delimiter=";") if r and r[0] == variabel]
    if not koder:
        sys.exit(f"Fant ikke kodeliste for {variabel} i metadata/kodelister.csv")
    return koder


def kommando_grupper(a):
    former = les_kreftformer()
    tresifret = {f["icd"]: f for f in former if f["nivaa"] == "2"}
    grupper = {f["icd"]: f["navn"] for f in former if f["nivaa"] == "1"}
    koder = kodeliste(a.variabel)
    prefiks = sorted({k[:3] for k in koder})
    # Alle kreftformer i ELVIS tas med, også de som mangler i kodelisten: S_TOPOGRAFIICD10 har D45 og D46 i
    # dataene (302 ondartede i 2023), men ikke i kodelisten (versjon 1, TESTLISTE 10.2). Regler som treffer 0
    # enheter er ufarlige (TESTLISTE 1.7).
    med = sorted(tresifret)
    ikke_i_kodelisten = [p for p in med if p not in prefiks]
    uten_c = [p for p in prefiks if p not in tresifret and (p.startswith("C") or p in ("D45", "D46", "D47"))]
    andre = [p for p in prefiks if p not in tresifret and p not in uten_c]
    if not med:
        sys.exit(f"Ingen av kodene i {a.variabel} er kreftformer i ELVIS (tre første tegn, f.eks. C18).")
    navn = a.navn

    print(f"// {a.variabel} -> kreftform nivå {a.nivaa} (Kreftregisterets metadatabase ELVIS, "
          f"hentet {(UT / 'HENTET').read_text(encoding='utf-8').split()[0]})")
    print(f"// {len(koder)} koder i kodelisten, {len(med)} tresifrede kreftformer i ELVIS.")
    if ikke_i_kodelisten:
        print(f"// Kreftformer som ikke står i kodelisten, men tas med (dataene kan ha dem): {' '.join(ikke_i_kodelisten)}")
    if uten_c:
        print(f"// Ikke kreftform i ELVIS, står {'som annet' if a.ukjent else 'uendret'}: {' '.join(uten_c)}"
              " (C77-C79 er spredning, C97 flere svulster)")
    if andre:
        print(f"// {len(andre)} andre tresifrede koder (ikke kreft), står {'som annet' if a.ukjent else 'uendret'}"
              + (f": {' '.join(andre[:15])}{' ...' if len(andre) > 15 else ''}" if andre else ""))
    var = a.var or a.variabel.lower()
    if a.ukjent:
        # Ikke recode med sluttregel (*): uavklart om den også treffer manglende verdier, og en recode med nesten
        # 20 000 koder blir svært lang. Kreftkodene velges heller med en betingelse: C-koder unntatt dem som ikke er
        # kreftform i ELVIS, pluss D-kodene som er det.
        tre = f"substr({var}, 1, 3)"
        c_ut = [p for p in uten_c if p.startswith("C")]
        d_inn = [p for p in med if not p.startswith("C")]
        vilkar = f"substr({var}, 1, 1) == 'C'"
        if c_ut:
            vilkar += f" & !inlist({tre}, {', '.join(q(p) for p in c_ut)})"
        if d_inn:
            vilkar = f"({vilkar}) | inlist({tre}, {', '.join(q(p) for p in d_inn)})"
        print(f"generate {navn} = 'annet' if !sysmiss({var})")
        print(f"replace {navn} = {tre} if {vilkar}")
    else:
        print(f"generate {navn} = substr({var}, 1, 3)")

    if a.nivaa == 2:
        etiketter = " ".join(f"{q(p)} {q(tresifret[p]['navn'])}" for p in med)
        if a.ukjent:
            etiketter += " 'annet' 'Ikke kreftform'"
        print(f"define-labels {navn}txt {etiketter}")
        print(f"assign-labels {navn} {navn}txt")
        return

    kart = {p: tresifret[p]["gruppe_icd"] for p in med}
    ut = {m.strip() for m in (a.utelat or "").split(",") if m.strip()}
    if ut:
        fjernet = sorted(k for k, m in kart.items() if m in ut)
        kart = {k: m for k, m in kart.items() if m not in ut}
        print(f"// --utelat: {' '.join(sorted(ut))} tatt ut. Står uendret (tresifret): {' '.join(fjernet) or 'ingen'}")
    for linje in recode_linjer(navn, kart, grupper):
        print(linje)
    # Hovedgrupper med samme kode som den tresifrede (C50 Bryst) blir ikke med i recode_linjer (k == m), og
    # ville stått uten merkelapp. En regel til samme verdi setter merkelappen (testet versjon 60, TESTLISTE 10.8).
    like = sorted(m for k, m in kart.items() if k == m)
    if like:
        print(f"recode {navn} " + " ".join(f"({q(m)} = {q(m)} {q(grupper[m])})" for m in like))


def kommando_verdier(a):
    fil = UT / "verdier.csv"
    if not fil.exists():
        sys.exit(f"Mangler {fil}. Kjør først: python verktoy/kreftregisteret.py hent")
    with open(fil, encoding="utf-8") as f:
        rader = [r for r in csv.DictReader(f, delimiter=";") if r["variabel"] == a.variabel]
    if not rader:
        sys.exit(f"Ingen verdier for {a.variabel} i {fil.name}.")
    if a.kreftform:
        rader = [r for r in rader if a.kreftform in r["kreftformer"].split() or not r["kreftformer"]]
    print(f"{a.variabel}: {len(rader)} verdier" + (f" for {a.kreftform} (og verdier uten kreftform)" if a.kreftform else ""))
    for r in rader:
        gjelder = r["kreftformer"].split()
        vis = " ".join(gjelder[:8]) + (f" (+{len(gjelder) - 8})" if len(gjelder) > 8 else "")
        print(f"  {r['verdi']:10} {r['beskrivelse'][:60]:60} {vis}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(required=True)
    p = sub.add_parser("hent", help="hent kreftformer og verdier fra ELVIS")
    p.set_defaults(f=kommando_hent)
    p = sub.add_parser("grupper", help="recode fra ICD-10-kode til kreftform")
    p.add_argument("--variabel", required=True, help="variabel med ICD-10-koder (kodelisten brukes)")
    p.add_argument("--var", help="navnet på variabelen i skriptet (standard: variabelnavnet med små bokstaver)")
    p.add_argument("--nivaa", type=int, choices=[1, 2], required=True,
                   help="1: 14 hovedgrupper, 2: tresifret kode med navn")
    p.add_argument("--navn", default="kreftform", help="navn på den nye variabelen (standard kreftform)")
    p.add_argument("--ukjent", action="store_true", help="koder som ikke er kreftform, blir 'annet'")
    p.add_argument("--utelat", help="nivå 1: grupper som tas ut, f.eks. C40-C41 (trengs bare med configure confidentiality v1)")
    p.set_defaults(f=kommando_grupper)
    p = sub.add_parser("verdier", help="verdier for en variabel, med kreftformene de gjelder for")
    p.add_argument("--variabel", required=True)
    p.add_argument("--kreftform", help="bare verdier som gjelder denne kreftformen (tresifret ICD-10, f.eks. C50)")
    p.set_defaults(f=kommando_verdier)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
