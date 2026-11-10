"""Tester kontrollene i hent_variabler.py med simulerte svar fra microdata.no (uten nett).

Testene kjøres på en kopi av metadata/ i en midlertidig mappe. Svarene bygges fra JSON-filene i repoet.
"""

import contextlib
import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from hjelp import METADATA

import hent_variabler as hv

NAVN = sorted(p.stem for p in (METADATA / "variabler").glob("*.json"))
DATALAGER = json.loads((METADATA / "datalager.json").read_text(encoding="utf-8"))
VERSJON = DATALAGER["versions"][0]["version"].split(".")[0]


def datalager_med_versjon(versjon):
    d = copy.deepcopy(DATALAGER)
    d["versions"].insert(0, {**d["versions"][0], "version": f"{versjon}.0.0.0"})
    return d


class Stub:
    """Erstatter hv.hent. Teller detaljforespørsler og husker URL-ene."""

    def __init__(self, navn=None, feil_paa=(), totalt=None, versjon=VERSJON, datalager=None):
        self.navn = NAVN if navn is None else navn
        self.totalt = len(self.navn) if totalt is None else totalt
        self.feil_paa, self.versjon = set(feil_paa), versjon
        self.datalager = DATALAGER if datalager is None else datalager
        self.detaljer = []

    def __call__(self, url, forsok=4):
        if "/variables?pageIndex=" in url:
            side = int(url.rsplit("=", 1)[1])
            data = {"dataStructures": [{"name": n} for n in self.navn[side * 20:(side + 1) * 20]],
                    "totalCount": self.totalt}
            if self.versjon:
                data["dataStores"] = {"no.ssb.fdb": {"version": f"{self.versjon}.0.0.0"}}
            return {"data": data}
        self.detaljer.append(url)
        n = url.rsplit("/", 1)[1]
        if n in self.feil_paa:
            raise OSError("simulert nedlastingsfeil")
        ds = json.loads((METADATA / "variabler" / f"{n}.json").read_text(encoding="utf-8"))
        return {"ds": ds, "dataStore": self.datalager}


class TestHentVariabler(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ut = Path(self._tmp.name)
        for f in ("variabler.csv", "kodelister.csv", "datalager.json"):
            shutil.copy(METADATA / f, self.ut / f)
        shutil.copytree(METADATA / "variabler", self.ut / "variabler")
        self._orig = hv.UT, hv.hent, sys.argv
        hv.UT = self.ut

    def tearDown(self):
        hv.UT, hv.hent, sys.argv = self._orig
        self._tmp.cleanup()

    def kjor(self, argv, stub):
        hv.hent, sys.argv = stub, ["hent_variabler.py", *argv]
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                hv.main()
                kode = 0
            except SystemExit as e:
                kode = e.code
        return kode, err.getvalue()

    def hash(self):
        h = hashlib.sha256()
        for f in sorted(self.ut.rglob("*")):
            if f.is_file():
                h.update(f.name.encode())
                h.update(f.read_bytes())
        return h.hexdigest()

    def test_vellykket_kjoring_gir_identiske_filer(self):
        kode, err = self.kjor(["--alle"], Stub())
        self.assertEqual(kode, 0, err[-500:])
        for f in ("variabler.csv", "kodelister.csv"):
            self.assertEqual((self.ut / f).read_bytes(), (METADATA / f).read_bytes(), f)
        self.assertFalse(list(self.ut.glob("*.tmp")))

    def test_versjon_fra_listesiden_brukes_i_url(self):
        stub = Stub()
        self.kjor(["--alle"], stub)
        self.assertTrue(all(f"/no.ssb.fdb/{VERSJON}/" in u for u in stub.detaljer))

    def test_versjon_kan_overstyres(self):
        stub = Stub()
        kode, _ = self.kjor(["--alle", "--versjon", "57"], stub)
        self.assertEqual(kode, 0)
        self.assertTrue(all("/no.ssb.fdb/57/" in u for u in stub.detaljer))

    def test_mangler_versjon_paa_listesiden(self):
        h = self.hash()
        kode, err = self.kjor(["--alle"], Stub(versjon=""))
        self.assertNotEqual(kode, 0)
        self.assertIn("--versjon", str(kode) + err)
        self.assertEqual(self.hash(), h)

    def test_ny_versjon_henter_alt_paa_nytt(self):
        ny = str(int(VERSJON) + 1)
        stub = Stub(versjon=ny, datalager=datalager_med_versjon(ny))
        kode, err = self.kjor([], stub)
        self.assertEqual(kode, 0, err[-500:])
        self.assertEqual(len(stub.detaljer), len(NAVN))
        lagret = json.loads((self.ut / "datalager.json").read_text(encoding="utf-8"))
        self.assertEqual(lagret["versions"][0]["version"], f"{ny}.0.0.0")

    def test_samme_versjon_bruker_lokale_filer(self):
        stub = Stub(feil_paa=NAVN)
        kode, _ = self.kjor([], stub)
        self.assertEqual(kode, 0)
        self.assertEqual(stub.detaljer, [])

    def test_datalager_med_annen_versjon_stoppes(self):
        h = self.hash()
        ny = str(int(VERSJON) + 1)
        kode, err = self.kjor(["--alle"], Stub(versjon=ny))  # detaljsidene gir fortsatt gammel datalager.json
        self.assertEqual(kode, 1)
        self.assertIn("datalager.json gjelder versjon", err)
        self.assertEqual(self.hash(), h)

    def test_nedlastingsfeil_stopper_uten_endringer(self):
        h = self.hash()
        kode, err = self.kjor(["--alle"], Stub(feil_paa=NAVN[:5]))
        self.assertEqual(kode, 1)
        self.assertIn("5 variabler feilet", err)
        self.assertEqual(self.hash(), h)

    def test_halvert_katalog_stoppes(self):
        h = self.hash()
        kode, _ = self.kjor(["--alle"], Stub(navn=NAVN[: len(NAVN) // 2]))
        self.assertEqual(kode, 1)
        self.assertEqual(self.hash(), h)

    def test_totalcount_avvik_stoppes(self):
        h = self.hash()
        kode, err = self.kjor(["--alle"], Stub(navn=NAVN[:-10], totalt=len(NAVN)))
        self.assertEqual(kode, 1)
        self.assertIn("totalCount", err)
        self.assertEqual(self.hash(), h)

    def test_tving_skriver_likevel(self):
        kode, err = self.kjor(["--alle", "--tving"], Stub(feil_paa=NAVN[:5]))
        self.assertEqual(kode, 0)
        self.assertIn("--tving", err)
        linjer = (self.ut / "variabler.csv").read_text(encoding="utf-8-sig").splitlines()
        self.assertEqual(len(linjer) - 1, len(NAVN) - 5)
        # Feilede variabler står fortsatt i listen, så JSON-filene deres slettes ikke
        self.assertTrue(all((self.ut / "variabler" / f"{n}.json").exists() for n in NAVN[:5]))

    def test_fjernet_variabel_slettes(self):
        kode, err = self.kjor(["--alle"], Stub(navn=NAVN[1:]))
        self.assertEqual(kode, 0, err[-500:])
        self.assertFalse((self.ut / "variabler" / f"{NAVN[0]}.json").exists())
        self.assertIn("slettet 1 variabler", err)

    def test_ingen_sletting_med_avkortet_liste_og_tving(self):
        kode, _ = self.kjor(["--alle", "--tving"], Stub(navn=NAVN[:-10], totalt=len(NAVN)))
        self.assertEqual(kode, 0)
        self.assertTrue(all((self.ut / "variabler" / f"{n}.json").exists() for n in NAVN[-10:]))


if __name__ == "__main__":
    unittest.main()
