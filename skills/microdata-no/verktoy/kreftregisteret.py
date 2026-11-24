"""Kreftformer og verdier fra Kreftregisterets metadatabase (ELVIS), og recode til kreftformer.

Underkommandoer (fra skill-mappen, python verktoy/kreftregisteret.py <kommando> --help):

  hent                             Henter kreftformene og verdiene for Kreftregisterets variabler i
                                   microdata.no fra ELVIS til metadata/fhi/kreftregisteret/.
  grupper --variabel V --nivaa N [--navn X] [--ukjent] [--utelat KODER] [--kjonn K] [--topografi T] [--morfologi M]
                                   generate/recode fra en ICD-10-variabel (f.eks. S_TOPOGRAFIICD10,
                                   SOM_EP_HOVEDTILSTAND1) til kreftform. Nivå 1: 14 hovedgrupper
                                   (C15-C26 Fordøyelsesorganer ...). Nivå 2: tresifret kode (C18 Tykktarm).
                                   Nivå cin: de 48 kreftformene i Cancer in Norway (C19-20 Endetarm og
                                   rektosigmoid, C33-34 Lunge og luftrør ...).
  verdier --variabel V [--kreftform ICD]
                                   Verdiene i ELVIS for en variabel, med kreftformene hver verdi gjelder for
                                   (TNM-verdiene er ulike for ulike kreftformer).

Eksempler:
  python verktoy/kreftregisteret.py hent
  python verktoy/kreftregisteret.py grupper --variabel S_TOPOGRAFIICD10 --nivaa 1 --navn kreftform
  python verktoy/kreftregisteret.py grupper --variabel SOM_EP_HOVEDTILSTAND1 --nivaa 2 --navn kreft3 --ukjent
  python verktoy/kreftregisteret.py grupper --variabel S_TOPOGRAFIICD10 --nivaa cin --var topo --kjonn kjonn --topografi topo3
  python verktoy/kreftregisteret.py verdier --variabel S_PT --kreftform C50

Kilde: https://metadata.kreftregisteret.no (ELVIS). Hjelpesiden sier at variabler og verdier kan eksporteres
eller hentes via API av alle, uten registrering. API-et (/rest/v1/) er det nettsiden selv bruker, og det er
ikke dokumentert. hent kontrollerer derfor svarene og avslutter med feilkode uten å skrive filer hvis
formatet ser endret ut. Koblingen mellom variabel i microdata.no og ELVIS står i kolonnen ekstern_metadata i
metadata/variabler.csv (lenken til detaljsiden).

Kodene i microdata.no er uten punktum, med tre eller fire tegn (C18, C187). grupper bruker de tre første
tegnene. Kreftformene i ELVIS dekker C00-C96 (ikke C77-C79 spredning og C97 flere svulster) og D45-D47.
Koder som ikke er kreftform, står uendret, eller blir 'annet' med --ukjent.

Nivå cin bygger på metadata/fhi/kreftregisteret/cancer_in_norway.csv: tabell 2.3 i Cancer in Norway 2025, slik
FHI gjengir den på https://fhi.no/is/ncd/dodelighet-sykelighet/kreft (tabell 2, skrevet av 2026-11-23).
Fasit for insidens: Kreftregisterets statistikkbank, https://sb.kreftregisteret.no/. Noen kreftformer avgjøres
av fire tegn (C00.3-5 og C00.8 er munnhule, C05.1-2 oropharynx, C57.0-4 eggstokk, D35.2-4 og D44.3-5 endokrine
kjertler). Tre regler trenger andre variabler:
  * Leppekreft: i Kreftregisterets data er kreft i leppens vermilionkant kodet C44.0 (hud på leppe) eller C43.0
    med ICD-10, men leppen står i ICD-O-3-topografien (S_TOPOGRAFIICDO3, uten C: 000-002, 006, 009). Rapporten
    regner dem som leppe (--topografi). Testet: 91 tilfeller i 2023, rapporten 89 (TESTLOGG 10.11).
  * C48.2 hos kvinner er eggstokk m.m. (--kjonn, BEFOLKNING_KJOENN, '2' = kvinne).
  * Basalcellekarsinom (morfologi 809x i ICD-O-3) er ikke med (--morfologi, S_MORFOLOGIICDO3). Datalageret i
    microdata.no har ingen basalcellekarsinomer (2023), så det trengs bare om de kommer med senere.
Pagets sykdom i bryst og papillomer i urinveier er heller ikke med i rapporten, men skilles ikke ut her.
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
    if a.nivaa == "cin":
        return kommando_grupper_cin(a)
    if a.kjonn or a.morfologi or a.topografi:
        sys.exit("--kjonn, --topografi og --morfologi gjelder bare --nivaa cin.")
    a.nivaa = int(a.nivaa)
    former = les_kreftformer()
    tresifret = {f["icd"]: f for f in former if f["nivaa"] == "2"}
    grupper = {f["icd"]: f["navn"] for f in former if f["nivaa"] == "1"}
    koder = kodeliste(a.variabel)
    prefiks = sorted({k[:3] for k in koder})
    # Alle kreftformer i ELVIS tas med, også de som mangler i kodelisten: S_TOPOGRAFIICD10 har D45 og D46 i
    # dataene (302 ondartede i 2023), men ikke i kodelisten (versjon 1, TESTLOGG 10.2). Regler som treffer 0
    # enheter er ufarlige (TESTLOGG 1.7).
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
    # ville stått uten merkelapp. En regel til samme verdi setter merkelappen (testet versjon 60, TESTLOGG 10.8).
    like = sorted(m for k, m in kart.items() if k == m)
    if like:
        print(f"recode {navn} " + " ".join(f"({q(m)} = {q(m)} {q(grupper[m])})" for m in like))


def les_cin():
    fil = UT / "cancer_in_norway.csv"
    with open(fil, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


CIN_KVINNE = "C56,C57.0-4,C48.2"


def cin_kart(koder):
    """{kode i dataene: kreftform}. Fire tegn går foran tre. Koder som ikke er kreftform, er ikke med."""
    prefiks = {}
    for g in les_cin():
        for k in g["koder"].split():
            prefiks[k] = g["gruppe"]
    kart = {}
    for k in koder:
        m = prefiks.get(k[:4]) if k[:4] in prefiks else prefiks.get(k[:3])
        if m:
            kart[k] = m
    return kart


def kommando_grupper_cin(a):
    cin = les_cin()
    navn_for = {g["gruppe"]: g["navn"] for g in cin}
    alle = [k for g in cin for k in g["koder"].split()]
    tre, fire = sorted(k for k in alle if len(k) == 3), sorted(k for k in alle if len(k) == 4)
    koder = kodeliste(a.variabel)
    dekket = cin_kart(koder)
    c_uten = sorted({k[:3] for k in koder if k.startswith("C") and k not in dekket})
    var = a.var or a.variabel.lower()
    navn = a.navn
    t3, t4 = f"substr({var}, 1, 3)", f"substr({var}, 1, 4)"

    print(f"// {a.variabel} -> kreftform som i Cancer in Norway ({len(cin)} kreftformer, tabell 2.3 i Cancer in "
          "Norway 2025, gjengitt på fhi.no).")
    print(f"// {len(dekket)} av {len(koder)} koder i kodelisten er kreftform. Fire tegn avgjør: {' '.join(fire)}.")
    if c_uten:
        print(f"// C-koder som ikke er kreftform i rapporten, står {'som annet' if a.ukjent else 'uendret'}: "
              f"{' '.join(c_uten)} (C46 Kaposi er ført under organet, C77-C79 er spredning, C97 flere svulster)")
    if a.ukjent:
        print(f"generate {navn} = 'annet' if !sysmiss({var})")
        print(f"replace {navn} = {t3} if inlist({t3}, {', '.join(q(k) for k in tre)})")
    else:
        print(f"generate {navn} = {t3}")
    print(f"replace {navn} = {t4} if inlist({t4}, {', '.join(q(k) for k in fire)})")
    if a.topografi:
        o3 = f"substr({a.topografi}, 1, 3)"
        hud = f"inlist({t3}, 'C43', 'C44')"
        print(f"// Leppekreft er kodet som hud på leppe (C43.0/C44.0) i ICD-10. ICD-O-3-topografien ({a.topografi}, uten C) "
              "viser leppen, som rapporten regner som leppe eller munnhule.")
        print(f"replace {navn} = 'C00' if {hud} & inlist({o3}, '000', '001', '002', '006', '009')")
        print(f"replace {navn} = 'C02-06' if {hud} & inlist({o3}, '003', '004', '005', '008')")
    else:
        print("// Leppekreft (om lag 90 i året) er kodet som hud på leppe (C44.0) og havner i C44 Hud, ikke C00 Leppe. Legg til "
              "--topografi <variabel> (S_TOPOGRAFIICDO3) for å få den som i rapporten.")

    kart = {k: g["gruppe"] for g in cin for k in g["koder"].split()}
    for linje in recode_linjer(navn, kart, navn_for):
        print(linje)
    # Kreftformer der koden er lik gruppen (C18 Tykktarm) får navnet med en regel til samme verdi (TESTLOGG 10.8).
    like = sorted({m for k, m in kart.items() if k == m})
    if like:
        print(f"recode {navn} " + " ".join(f"({q(m)} = {q(m)} {q(navn_for[m])})" for m in like))

    if a.kjonn:
        print(f"// C48.2 (bukhinnen) hos kvinner er eggstokk m.m. ({a.kjonn} == '2' er kvinne, som i BEFOLKNING_KJOENN).")
        print(f"replace {navn} = {q(CIN_KVINNE)} if {t4} == 'C482' & {a.kjonn} == '2'")
    else:
        print("// C48.2 (bukhinnen) står i bløtvev for alle. I rapporten er den eggstokk m.m. for kvinner: legg til "
              "--kjonn <variabel> (BEFOLKNING_KJOENN).")
    if a.morfologi:
        print(f"// Basalcellekarsinom (morfologi 809x) er ikke med i noen kreftform i rapporten.")
        print(f"replace {navn} = 'basal' if substr({a.morfologi}, 1, 3) == '809' & !sysmiss({navn})")
        print(f"recode {navn} ('basal' = 'basal' 'Basalcellekarsinom (ikke med i Cancer in Norway)')")
    else:
        print("// Basalcellekarsinom er ikke med i rapporten, men står her i sin kreftform (mest C44). Legg til "
              "--morfologi <variabel> (S_MORFOLOGIICDO3) for å skille dem ut som 'basal'.")


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
    p.add_argument("--nivaa", choices=["1", "2", "cin"], required=True,
                   help="1: 14 hovedgrupper, 2: tresifret kode med navn, cin: kreftformene i Cancer in Norway")
    p.add_argument("--navn", default="kreftform", help="navn på den nye variabelen (standard kreftform)")
    p.add_argument("--ukjent", action="store_true", help="koder som ikke er kreftform, blir 'annet'")
    p.add_argument("--utelat", help="nivå 1: grupper som tas ut, f.eks. C40-C41 (trengs bare med configure confidentiality v1)")
    p.add_argument("--kjonn", help="nivå cin: kjønnsvariabelen ('2' = kvinne), for C48.2 hos kvinner")
    p.add_argument("--topografi", help="nivå cin: ICD-O-3-topografien (S_TOPOGRAFIICDO3), for leppekreft kodet som hud")
    p.add_argument("--morfologi", help="nivå cin: morfologivariabelen (S_MORFOLOGIICDO3), for å skille ut basalcellekarsinom")
    p.set_defaults(f=kommando_grupper)
    p = sub.add_parser("verdier", help="verdier for en variabel, med kreftformene de gjelder for")
    p.add_argument("--variabel", required=True)
    p.add_argument("--kreftform", help="bare verdier som gjelder denne kreftformen (tresifret ICD-10, f.eks. C50)")
    p.set_defaults(f=kommando_verdier)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
