"""Sjekker importlinjene i kodesnuttene og testskriptene mot metadataene.

- Variabelen må finnes i `variabler.csv`, i datalageret som aliaset i `require` peker på.
- Faste variabler (temporalitet FIXED) tar ikke dato ved `import`, de andre må ha dato. Feilen stopper skriptet
  i microdata.no («tar ikke et datoargument siden den har temporalitet: 'Fast'»).
- Datoene må ligge innenfor dekningen (`fra`/`til`). For `import-event` må perioden overlappe dekningen.
- En importlinje som ikke kan tolkes, er en feil, slik at linjer ikke hoppes over uten at det merkes.

Datoer som er makroer (`$dato`) teller som dato, men dekningen sjekkes ikke. Snutter med status UTGÅTT
hoppes over, fordi variablene deres kan være slettet.
"""

import csv
import re
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
VARIABLER = ROT / "skills" / "microdata-no" / "metadata" / "variabler.csv"
SKRIPT = sorted(
    list((ROT / "skills" / "microdata-no" / "kodesnutter").glob("*.txt"))
    + list((ROT / ".claude" / "skills" / "vedlikehold" / "testskript").glob("*.txt"))
)
DATO = r"\d{4}-\d{2}-\d{2}"
# Valg etter aliaset, f.eks. `, values("2")`, og kommentar.
SLUTT = r"(?:\s*,.*)?(?:\s*//.*)?\s*$"
REQUIRE = re.compile(r"^\s*require\s+([\w.]+):\d+\s+as\s+(\w+)", re.MULTILINE)
IMPORTLINJE = re.compile(r"^\s*import(?:-event|-panel)?\s")
IMPORT = re.compile(rf"^\s*import\s+(\w+)/(\w+)(?:\s+({DATO}|\$\w+))?\s+as\s+\$?\w+{SLUTT}")
EVENT = re.compile(rf"^\s*import-event\s+(\w+)/(\w+)\s+({DATO}|\$\w+)\s+to\s+({DATO}|\$\w+)\s+as\s+\$?\w+{SLUTT}")
PANEL = re.compile(rf"^\s*import-panel((?:\s+\w+/\w+)+)((?:\s+(?:{DATO}|\$\w+))+){SLUTT}")


def les_variabler():
    with open(VARIABLER, encoding="utf-8-sig", newline="") as f:
        return {r["navn"]: r for r in csv.DictReader(f, delimiter=";")}


def utgatt(tekst):
    return re.search(r"^// Status:\s*UTGÅTT", tekst, re.MULTILINE) is not None


def er_dato(verdi):
    return re.fullmatch(DATO, verdi) is not None


def feil_i(tekst, variabler):
    """Returnerer (linjenummer, melding) for hver feil i importlinjene i et skript."""
    datalager = {alias: lager for lager, alias in REQUIRE.findall(tekst)}
    feil = []

    def variabel(nr, alias, navn):
        if alias not in datalager:
            feil.append((nr, f"aliaset {alias} har ingen require"))
            return None
        v = variabler.get(navn)
        if v is None:
            feil.append((nr, f"{navn} finnes ikke i variabler.csv"))
            return None
        if v["datalager"] != datalager[alias]:
            feil.append((nr, f"{navn} ligger i {v['datalager']}, ikke i {datalager[alias]} ({alias})"))
            return None
        return v

    def innenfor(nr, v, dato):
        if er_dato(dato) and not v["fra"] <= dato <= v["til"]:
            feil.append((nr, f"{v['navn']} {dato} er utenfor dekningen {v['fra']}–{v['til']}"))

    for nr, linje in enumerate(tekst.splitlines(), 1):
        if not IMPORTLINJE.match(linje):
            continue
        if m := IMPORT.match(linje):
            alias, navn, dato = m.groups()
            v = variabel(nr, alias, navn)
            if v is None:
                continue
            if v["temporalitet"] == "FIXED":
                if dato:
                    feil.append((nr, f"{navn} er FIXED og skal importeres uten dato"))
            elif not dato:
                feil.append((nr, f"{navn} er {v['temporalitet']} og må ha dato"))
            else:
                innenfor(nr, v, dato)
        elif m := EVENT.match(linje):
            alias, navn, start, slutt = m.groups()
            v = variabel(nr, alias, navn)
            if v and er_dato(start) and er_dato(slutt) and (slutt < v["fra"] or start > v["til"]):
                feil.append((nr, f"{navn} {start} to {slutt} overlapper ikke dekningen {v['fra']}–{v['til']}"))
        elif m := PANEL.match(linje):
            datoer = m.group(2).split()
            for ref in m.group(1).split():
                v = variabel(nr, *ref.split("/"))
                if v and v["temporalitet"] != "FIXED":
                    for dato in datoer:
                        innenfor(nr, v, dato)
        else:
            feil.append((nr, f"kan ikke tolke importlinjen: {linje.strip()}"))
    return feil


class TestImportlinjer(unittest.TestCase):
    def test_importlinjer_mot_metadata(self):
        variabler = les_variabler()
        feil = []
        for fil in SKRIPT:
            tekst = fil.read_text(encoding="utf-8")
            if utgatt(tekst):
                continue
            feil += [f"{fil.relative_to(ROT)}:{nr}: {melding}" for nr, melding in feil_i(tekst, variabler)]
        self.assertEqual(feil, [], "\n".join(feil))

    def test_finner_skript(self):
        self.assertTrue(any(f.parent.name == "kodesnutter" for f in SKRIPT))
        self.assertTrue(any(f.parent.name == "testskript" for f in SKRIPT))


class TestSjekken(unittest.TestCase):
    """Sjekken må finne feilene den skal finne, ellers består testen over uansett."""

    VARIABLER = {
        "FAST": {"navn": "FAST", "temporalitet": "FIXED", "fra": "1900-01-01", "til": "2025-12-31",
                 "datalager": "no.ssb.fdb"},
        "STATUS": {"navn": "STATUS", "temporalitet": "STATUS", "fra": "2015-01-01", "til": "2024-01-01",
                   "datalager": "no.ssb.fdb"},
        "KREFT": {"navn": "KREFT", "temporalitet": "FIXED", "fra": "1953-01-01", "til": "2024-12-31",
                  "datalager": "no.fhi.kreftregisteret"},
    }

    def meldinger(self, *linjer):
        tekst = "require no.ssb.fdb:60 as fdb\nrequire no.fhi.kreftregisteret:1 as krg\n" + "\n".join(linjer)
        return [melding for _, melding in feil_i(tekst, self.VARIABLER)]

    def test_riktige_linjer_gir_ingen_feil(self):
        self.assertEqual(self.meldinger(
            "import fdb/FAST as f",
            "import fdb/STATUS 2020-01-01 as s",
            "  import fdb/STATUS $dato as $var",
            "import krg/KREFT as k",
            'import fdb/FAST as f, values("2")',
            "import-event fdb/STATUS 2010-01-01 to 2016-01-01 as e",
            "import-panel fdb/STATUS fdb/FAST 2016-01-01 2017-01-01",
        ), [])

    def test_finner_feil(self):
        for linje, forventet in [
            ("import fdb/FINNESIKKE 2020-01-01 as x", "finnes ikke"),
            ("import fdb/FAST 2020-01-01 as f", "skal importeres uten dato"),
            ("import fdb/STATUS as s", "må ha dato"),
            ("import fdb/STATUS 2025-01-01 as s", "utenfor dekningen"),
            ("import fdb/KREFT as k", "ligger i no.fhi.kreftregisteret"),
            ("import npr/STATUS 2020-01-01 as s", "ingen require"),
            ("import-event fdb/STATUS 2000-01-01 to 2010-01-01 as e", "overlapper ikke"),
            ("import-panel fdb/STATUS 2016-01-01 2026-01-01", "utenfor dekningen"),
            ("import fdb/STATUS 2020-01-01", "kan ikke tolke"),
        ]:
            with self.subTest(linje=linje):
                meldinger = self.meldinger(linje)
                self.assertEqual(len(meldinger), 1, meldinger)
                self.assertIn(forventet, meldinger[0])


if __name__ == "__main__":
    unittest.main()
