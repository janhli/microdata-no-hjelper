"""Felles hjelpefunksjoner for testene. Kjør alle tester fra repoets rot:

    python -m unittest discover -s tests

Testene for klass.py trenger nett (SSB Klass). De hoppes over hvis Klass ikke svarer, eller hvis
miljøvariabelen UTEN_NETT er satt.
"""

import os
import re
import subprocess
import sys
import urllib.request
from functools import lru_cache
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "microdata-no"
VERKTOY = SKILL / "verktoy"
METADATA = SKILL / "metadata"
if str(VERKTOY) not in sys.path:
    sys.path.insert(0, str(VERKTOY))

from recode_regler import REGEL, simuler  # noqa: E402

EKSTRA_VERDIER = ("9999", "-1", "xxxx", "UKJENT", "0000")


def kjor(skript, *args):
    """Kjører et verktøy slik brukeren gjør (python -I) og returnerer stdout. Feiler testen ved feilkode."""
    r = subprocess.run([sys.executable, "-I", str(VERKTOY / skript), *args], capture_output=True,
                       encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        raise AssertionError(f"{skript} {' '.join(args)} feilet ({r.returncode}): {r.stderr.strip()[-800:]}")
    return r.stdout


def recode_linjer_i(tekst):
    return [l for l in tekst.splitlines() if l.startswith("recode ")]


def tiltenkt(linjer):
    """kilde -> mål slik reglene er skrevet (første regel som nevner kilden), og eventuell sluttregel."""
    kart, slutt = {}, None
    for linje in linjer:
        for venstre, mal in REGEL.findall(linje):
            if venstre.strip() == "*":
                slutt = mal
                continue
            for k in re.findall(r"'([^']*)'", venstre):
                kart.setdefault(k, mal)
    return kart, slutt


def avvik(tekst, ekstra=EKSTRA_VERDIER):
    """Kjører recode-linjene i tekst med simulatoren og returnerer verdier som ikke ender der reglene sier.

    Hver kilde skal ende på målet i sin egen regel. Alle andre verdier (også målene) skal stå uendret, eller
    få sluttregelens verdi. Et avvik betyr at en verdi er omkodet to ganger, eller at sluttregelen overskriver.
    """
    linjer = recode_linjer_i(tekst)
    kart, slutt = tiltenkt(linjer)
    verdier = sorted(set(kart) | set(kart.values()) | set(ekstra))
    ut = dict(zip(verdier, simuler(linjer, verdier)))
    feil = []
    for v in verdier:
        forventet = kart.get(v, slutt if slutt is not None else v)
        if ut[v] != forventet:
            feil.append(f"{v}: {ut[v]} (skulle vært {forventet})")
    return feil


@lru_cache(maxsize=None)
def har_nett(url="https://data.ssb.no/api/klass/v1/classifications/7"):
    if os.environ.get("UTEN_NETT"):
        return False
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=20):
            return True
    except OSError:
        return False
