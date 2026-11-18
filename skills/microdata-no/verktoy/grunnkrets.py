"""Lager recode-linjer fra BEFOLKNING_GRUNNKRETS (et valgt år) til delområde, levekårssone, bydel eller egne områder.

Grunnkretskoden er kommune (4) + delområde (2) + grunnkrets (2) og skifter når kommunen skifter nummer
(over 10 000 koder i 2020, 6 000 i 2024). Verktøyet følger hver kode i dataåret gjennom endringene i
SSB Klass (klassifikasjon 1) til gjeldende inndeling, og koder den rett til målinndelingen.

Inndelinger (--til):
  delomrade   6 sifre (kommune + delområde), om lag 1 900 i landet
  lks         levekårssoner fra Klass, 10 sifre (66 kommuner, om lag 1 100 soner)
  bydel       bydeler i Oslo, Bergen, Trondheim og Stavanger, 6 sifre
  delbydel    delbydeler i Oslo, 4 sifre
  grunnkrets  gjeldende grunnkretskode, 8 sifre (se advarselen under)
  FIL.csv     egne områder: kolonnene grunnkrets;kode;navn, med gjeldende grunnkretskoder

Eksempler (fra prosjektmappen):
  python verktoy/grunnkrets.py --til lks --aar 2019 --var gk --kommune 0301
  python verktoy/grunnkrets.py --til delomrade --aar 2015 --kommune 4601,5001
  python verktoy/grunnkrets.py --til mine_omrader.csv --aar 2026

Hvorfor rett til målet: hver regel tar med ALLE grunnkretsene i målenheten, også de som ikke har endret
kode, så ingen verdi går via en mellomkode. Det gir kortere skript, og hver regel treffer hele enheten.
(Med versjon 1 av anonymiseringstiltakene ble regler som traff 1–9 personer stoppet. Grunnkrets kan ikke
brukes med configure confidentiality v1, så det gjelder ikke her.) --til grunnkrets omkoder bare endrede
koder til gjeldende grunnkrets. Tabeller på grunnkrets får mange celler under 5, som vises som 0.

Grunnkretser som er delt mellom flere målenheter, står uendret (--splitt behold) eller får målenheten til
den første av de nye grunnkretsene (--splitt forste). Grunnkretser utenfor inndelingen og «uoppgitt»
(kkkk9999) står også uendret. Omkodede og uendrede verdier kan skilles på lengden (8 tegn = uendret).

Bygger på metadata/grunnkrets/ (python verktoy/hent_grunnkrets.py) og kodelisten for hvert år i
metadata/variabler/BEFOLKNING_GRUNNKRETS.json.
"""

import argparse
import csv
import datetime as dt
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recode_regler import q, recode_linjer  # noqa: E402

METADATA = Path(__file__).resolve().parent.parent / "metadata"
DIR = METADATA / "grunnkrets"
VARIABEL = "BEFOLKNING_GRUNNKRETS"
INNEBYGD = {"lks", "bydel", "delbydel"}


def kodelister():
    """[(fra-dato, {kode: navn}), ...] for hver periode i variabelens kodelistehistorikk."""
    fil = METADATA / "variabler" / f"{VARIABEL}.json"
    if not fil.exists():
        sys.exit(f"Mangler {fil}. Kjør python verktoy/hent_variabler.py.")
    ut, koder = [], []
    for rv in json.loads(fil.read_text(encoding="utf-8"))["measureVariable"]["representedVariables"]:
        vd = rv["valueDomain"]
        if "codeList" in vd:
            koder = list(vd["codeList"])
        else:  # samme rekkefølge som gjeldende_kodeliste() i hent_variabler.py
            d = vd.get("delta", {})
            fjern = set(d.get("remove", []))
            koder = [k for i, k in enumerate(koder) if i not in fjern]
            for i, k in (d.get("replace") or {}).items():
                koder[int(i)] = k
            for i in sorted(d.get("insert", {}), key=int):
                koder.insert(int(i), d["insert"][i])
        start = (dt.date(1970, 1, 1) + dt.timedelta(days=rv["validPeriod"]["start"])).isoformat()
        ut.append((start, {k["code"]: k["category"] for k in koder}))
    return ut


def kodeliste_aar(lister, aar):
    dato = f"{aar}-01-01"
    gyldige = [k for start, k in lister if start <= dato]
    if not gyldige:
        sys.exit(f"{VARIABEL} starter {lister[0][0]}. --aar {aar} er for tidlig.")
    return gyldige[-1]


def les_endringer():
    per_dato = defaultdict(lambda: defaultdict(list))
    with open(DIR / "endringer.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            per_dato[r["dato"]][r["gammel"]].append(r["ny"])
    return per_dato


def folg(kode, fra, per_dato):
    """Gjeldende grunnkretskoder for en kode som var gyldig på datoen fra (flere ved deling)."""
    naa = {kode}
    for dato in sorted(d for d in per_dato if d > fra):
        naa = {n for k in naa for n in (per_dato[dato].get(k) or [k])}
    return naa


def les_inndeling(til):
    """{grunnkrets: kode} og {kode: navn} for en innebygd inndeling eller en egen fil."""
    kart, navn = {}, {}
    if til in INNEBYGD:
        fil, filter_ = DIR / "inndelinger.csv", til
    else:
        fil, filter_ = Path(til), None
        if not fil.exists():
            sys.exit(f"Fant ikke {fil}. --til er delomrade, lks, bydel, delbydel, grunnkrets eller en CSV-fil.")
    with open(fil, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if filter_ and r["inndeling"] != filter_:
                continue
            kart[r["grunnkrets"].strip()] = r["kode"].strip()
            if r.get("navn"):
                navn[r["kode"].strip()] = r["navn"].strip()
    if not kart:
        sys.exit(f"Ingen rader i {fil}" + (f" for {til}" if filter_ else "") + ".")
    return kart, navn


def bygg(aar, til, kommuner=(), splitt="behold", utelat=()):
    lister = kodelister()
    gjeldende_dato, gjeldende = lister[-1]
    fra_koder = kodeliste_aar(lister, aar)
    per_dato = les_endringer()
    fra = f"{aar}-01-01"

    if til == "delomrade":
        mal_for = lambda g: g[:6]  # noqa: E731
        navn = {k: v for k, v in gjeldende.items() if len(k) == 6}
    elif til == "grunnkrets":
        mal_for = lambda g: g  # noqa: E731
        navn = {k: v for k, v in gjeldende.items() if len(k) == 8}
    else:
        inndeling, navn = les_inndeling(til)
        mal_for = inndeling.get

    kart, delt, utenfor, antall = {}, {}, 0, 0
    for kode in sorted(k for k in fra_koder if len(k) == 8 and not k.endswith("9999")):
        nye = sorted(folg(kode, fra, per_dato))
        if kommuner and not any(g[:4] in kommuner for g in nye):
            continue
        antall += 1
        mal = sorted({m for m in map(mal_for, nye) if m})
        if not mal:
            utenfor += 1
            continue
        if len(mal) > 1:
            delt[kode] = mal
            if splitt == "behold":
                continue
            mal = [mal_for(nye[0]) or mal[0]]
        if mal[0] in utelat:
            continue
        kart[kode] = mal[0]
    if til == "grunnkrets":
        kart = {k: m for k, m in kart.items() if k != m}
    kort = False
    if til == "delomrade" and not kommuner:
        # Delområder der ingen grunnkrets har skiftet kode, tas med substr() etterpå (gir mye kortere skript
        # for nyere år). Delområder med minst én endret kode omkodes med alle sine grunnkretser.
        berort = {m for k, m in kart.items() if k[:6] != m}
        kart = {k: m for k, m in kart.items() if m in berort}
        kort = True
    return {"kart": kart, "navn": navn, "delt": delt, "utenfor": utenfor, "gjeldende": gjeldende_dato[:4],
            "antall_fra": antall, "substr": kort}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--til", required=True, help="delomrade, lks, bydel, delbydel, grunnkrets eller FIL.csv")
    ap.add_argument("--aar", type=int, required=True, help="året dataene er fra (import ... ÅÅÅÅ-01-01)")
    ap.add_argument("--var", default="grunnkrets", help="variabelen med grunnkretskoden i skriptet")
    ap.add_argument("--navn", help="ny variabel (standard: navnet på inndelingen)")
    ap.add_argument("--kommune", default="", help="bare disse kommunene (gjeldende nummer), kommaseparert")
    ap.add_argument("--splitt", choices=["behold", "forste"], default="behold",
                    help="delte grunnkretser: la stå (standard) eller bruk den første nye grunnkretsen")
    ap.add_argument("--utelat", default="", help="målkoder som ikke skal omkodes (fra feilmeldingen), kommaseparert")
    a = ap.parse_args()
    kommuner = {k.strip() for k in a.kommune.split(",") if k.strip()}
    utelat = {k.strip() for k in a.utelat.split(",") if k.strip()}
    navn_var = a.navn or (Path(a.til).stem if a.til.endswith(".csv") else a.til)

    r = bygg(a.aar, a.til, kommuner, a.splitt, utelat)
    kart, delt = r["kart"], r["delt"]
    hentet = (DIR / "HENTET").read_text(encoding="utf-8").splitlines()[0]
    print(f"// {VARIABEL} {a.aar} -> {a.til} ({r['gjeldende']}-inndelingen). Klass 1, hentet {hentet}."
          + (f" Kommuner: {', '.join(sorted(kommuner))}." if kommuner else ""))
    hvor = "i kommunene" if kommuner else "i kodelisten"
    print(f"// {len(kart)} av {r['antall_fra']} grunnkretser {hvor} (uten uoppgitt) omkodes til "
          f"{len(set(kart.values()))} enheter."
          + (f" {r['utenfor']} ligger utenfor inndelingen og står uendret (8 tegn)." if r["utenfor"] else ""))
    if delt:
        hva = "står uendret" if a.splitt == "behold" else "får første nye grunnkrets"
        eks = " ".join(f"{k}->{'/'.join(v)}" for k, v in list(delt.items())[:8])
        print(f"// {len(delt)} grunnkretser er delt mellom flere enheter og {hva}: {eks}" + (" ..." if len(delt) > 8 else ""))
    if utelat:
        print(f"// Utelatt (står uendret): {', '.join(sorted(utelat))}")
    if a.til == "grunnkrets":
        print("// Merk: mange grunnkretser har under 5 beboere. De vises som 0 i tabeller (anonymiseringstiltak 11).")
    print(f"generate {navn_var} = {a.var}")
    for linje in recode_linjer(navn_var, kart, r["navn"]):
        print(linje)
    if r["substr"]:
        # Gjenværende 8-tegnskoder er grunnkretser i uendrede delområder. Uoppgitt (kkkk9999) og delte står igjen.
        unntak = sorted(delt) if a.splitt == "behold" else []
        print("// Resten av grunnkretsene ligger i delområder som ikke er endret: de seks første sifrene er delområdet.")
        print(f"replace {navn_var} = substr({navn_var}, 1, 6) if length({navn_var}) == 8 & substr({navn_var}, 5, 4) != '9999'"
              + (f" & !inlist({navn_var}, {', '.join(q(k) for k in unntak)})" if unntak else ""))


if __name__ == "__main__":
    main()
