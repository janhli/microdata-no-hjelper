"""Sjekker importlinjene i kodesnuttene og testskriptene mot metadataene.

Faste variabler (temporalitet FIXED) tar ikke dato ved import, de andre må ha dato. Feilen stopper skriptet
i microdata.no («tar ikke et datoargument siden den har temporalitet: 'Fast'»). Snutter med status UTGÅTT
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
# Bare `import`, ikke `import-event` eller `import-panel`.
IMPORT = re.compile(r"^\s*import\s+\w+/(\w+)(\s+\d{4}-\d{2}-\d{2})?\s+as\s+\w+")


def temporalitet():
    with open(VARIABLER, encoding="utf-8-sig", newline="") as f:
        return {r["navn"]: r["temporalitet"] for r in csv.DictReader(f, delimiter=";")}


def utgatt(tekst):
    return re.search(r"^// Status:\s*UTGÅTT", tekst, re.MULTILINE) is not None


class TestImportlinjer(unittest.TestCase):
    def test_dato_etter_temporalitet(self):
        temp = temporalitet()
        feil = []
        for fil in SKRIPT:
            tekst = fil.read_text(encoding="utf-8")
            if utgatt(tekst):
                continue
            for nr, linje in enumerate(tekst.splitlines(), 1):
                m = IMPORT.match(linje)
                if not m or m.group(1) not in temp:
                    continue
                navn, har_dato = m.group(1), m.group(2) is not None
                fast = temp[navn] == "FIXED"
                if fast and har_dato:
                    feil.append(f"{fil.relative_to(ROT)}:{nr}: {navn} er FIXED og skal importeres uten dato")
                elif not fast and not har_dato:
                    feil.append(f"{fil.relative_to(ROT)}:{nr}: {navn} er {temp[navn]} og må ha dato")
        self.assertEqual(feil, [], "\n".join(feil))

    def test_finner_skript(self):
        self.assertTrue(any(f.parent.name == "kodesnutter" for f in SKRIPT))
        self.assertTrue(any(f.parent.name == "testskript" for f in SKRIPT))


if __name__ == "__main__":
    unittest.main()
