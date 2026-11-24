"""Tester kontrollene i hent_variabler.py med simulerte svar fra microdata.no (uten nett).

Testene kjøres på en kopi av metadata/ i en midlertidig mappe. Svarene bygges fra JSON-filene i repoet.
"""

import contextlib
import csv
import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from hjelp import METADATA

import hent_variabler as hv

NAVN = sorted(p.stem for p in (METADATA / "variabler").glob("*.json"))


def lager_i_metadata():
    """{navn: datalager} fra variabler.csv (kolonnen finnes fra 2026-11). Ellers er alt no.ssb.fdb."""
    with open(METADATA / "variabler.csv", encoding="utf-8-sig") as f:
        return {r["navn"]: r.get("datalager") or "no.ssb.fdb" for r in csv.DictReader(f, delimiter=";")}


LAGER = lager_i_metadata()
DATALAGER = json.loads((METADATA / "datalager.json").read_text(encoding="utf-8"))
VERSJON = DATALAGER["versions"][0]["version"].split(".")[0]


def datalager_med_versjon(versjon):
    d = copy.deepcopy(DATALAGER)
    d["versions"].insert(0, {**d["versions"][0], "version": f"{versjon}.0.0.0"})
    return d


class Stub:
    """Erstatter hv.hent. Teller detaljforespørsler og husker URL-ene."""

    def __init__(self, navn=None, feil_paa=(), totalt=None, versjon=VERSJON, datalager=None, andre=()):
        self.navn = NAVN if navn is None else navn
        # andre: (datalager, navn) for variabler som ikke ligger i metadata/ (nye FHI-variabler)
        self.liste = ([{"name": n, "dataStore": LAGER.get(n, "no.ssb.fdb")} for n in self.navn]
                      + [{"name": n, "dataStore": s} for s, n in andre])
        self.lagre = {d["dataStore"] for d in self.liste} - {"no.ssb.fdb"}
        self.totalt = len(self.liste) if totalt is None else totalt
        self.feil_paa, self.versjon = set(feil_paa), versjon
        self.datalager = DATALAGER if datalager is None else datalager
        self.detaljer = []

    def __call__(self, url, forsok=4):
        if "/variables?pageIndex=" in url:
            side = int(url.rsplit("=", 1)[1])
            data = {"dataStructures": self.liste[side * 20:(side + 1) * 20],
                    "totalCount": self.totalt}
            data["dataStores"] = {s: {"label": s, "version": "1.0.0.0"} for s in self.lagre}
            if self.versjon:
                data["dataStores"]["no.ssb.fdb"] = {"version": f"{self.versjon}.0.0.0"}
            return {"data": data}
        self.detaljer.append(url)
        n = url.rsplit("/", 1)[1]
        if n in self.feil_paa:
            raise OSError("simulert nedlastingsfeil")
        fil = METADATA / "variabler" / f"{n}.json"
        if not fil.exists():  # ny variabel: lån innholdet til en annen
            fil = METADATA / "variabler" / f"{NAVN[0]}.json"
        ds = json.loads(fil.read_text(encoding="utf-8"))
        return {"ds": ds, "dataStore": self.datalager}


class TestHentVariabler(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ut = Path(self._tmp.name)
        for f in ("variabler.csv", "kodelister.csv", "datalager.json", "VERSJON"):
            if (METADATA / f).exists():
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
        # Linjeskift sammenlignes ikke: en lokal utsjekking kan ha \r\n (git normaliserer til \n, .gitattributes).
        for f in ("variabler.csv", "kodelister.csv"):
            self.assertEqual((self.ut / f).read_bytes().replace(b"\r\n", b"\n"),
                             (METADATA / f).read_bytes().replace(b"\r\n", b"\n"), f)
        self.assertFalse(list(self.ut.glob("*.tmp")))

    def test_versjon_fra_listesiden_brukes_i_url(self):
        stub = Stub()
        self.kjor(["--alle"], stub)
        ssb = [u for u in stub.detaljer if "/no.ssb.fdb/" in u]
        self.assertTrue(ssb)
        self.assertTrue(all(f"/no.ssb.fdb/{VERSJON}/" in u for u in ssb))

    def test_versjon_kan_overstyres(self):
        stub = Stub()
        kode, _ = self.kjor(["--alle", "--versjon", "57"], stub)
        self.assertEqual(kode, 0)
        ssb = [u for u in stub.detaljer if "/no.ssb.fdb/" in u]
        self.assertTrue(ssb)
        self.assertTrue(all("/no.ssb.fdb/57/" in u for u in ssb))

    def test_andre_datalagre_hentes_med_egen_versjon(self):
        # Listesiden fikk FHI-variabler i 2026-11. Under no.ssb.fdb ga de 404 (workflowen gikk ut på tid).
        stub = Stub(andre=[("no.fhi.npr", "TEST_NPR_X"), ("no.fhi.kreftregisteret", "TEST_KRG_X")])
        kode, err = self.kjor([], stub)
        self.assertEqual(kode, 0, err[-500:])
        self.assertIn(f"{hv.BASE}/variable/no.fhi.npr/1/TEST_NPR_X", stub.detaljer)
        self.assertIn(f"{hv.BASE}/variable/no.fhi.kreftregisteret/1/TEST_KRG_X", stub.detaljer)
        rader = {r["navn"]: r for r in csv.DictReader(
            (self.ut / "variabler.csv").read_text(encoding="utf-8-sig").splitlines(), delimiter=";")}
        self.assertEqual(rader["TEST_NPR_X"]["datalager"], "no.fhi.npr")
        self.assertEqual(hv.forrige_versjoner()["no.fhi.npr"], "1")
        self.assertIn("no.fhi.npr", json.loads((self.ut / "datalagre.json").read_text(encoding="utf-8")))

    def test_ny_versjon_i_ett_datalager_henter_bare_det(self):
        stub = Stub(andre=[("no.fhi.npr", "TEST_NPR_X")])
        self.kjor([], stub)
        stub = Stub(andre=[("no.fhi.npr", "TEST_NPR_X")])
        orig = stub.__call__

        def med_ny_npr(url, forsok=4):
            svar = orig(url, forsok)
            if "/variables?pageIndex=" in url:
                svar["data"]["dataStores"]["no.fhi.npr"]["version"] = "2.0.0.0"
            return svar
        kode, err = self.kjor([], med_ny_npr)
        self.assertEqual(kode, 0, err[-500:])
        npr = {n for n in NAVN if LAGER.get(n) == "no.fhi.npr"} | {"TEST_NPR_X"}
        self.assertEqual({u.rsplit("/", 1)[1] for u in stub.detaljer}, npr)  # bare NPR, men alle i NPR

    def test_lenker_i_beskrivelsen(self):
        tekst = ("Se Kreftregisterets [metadatabase](https://metadata.kreftregisteret.no/variables/detail/12). "
                 "Mer på [helsedata](https://helsedata.no/). Kode: (https://finnkode.helsedirektoratet.no/icd10/chapter/).")
        self.assertEqual(hv.lenker(tekst), ["https://metadata.kreftregisteret.no/variables/detail/12",
                                            "https://helsedata.no/",
                                            "https://finnkode.helsedirektoratet.no/icd10/chapter/"])

    def test_404_proves_ikke_paa_nytt(self):
        kall = []

        def svar(req, timeout):
            kall.append(req.full_url)
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", None, None)
        orig = urllib.request.urlopen, hv.time.sleep
        urllib.request.urlopen, hv.time.sleep = svar, lambda s: None
        try:
            with self.assertRaises(urllib.error.HTTPError):
                hv.hent("https://example.invalid/x")
        finally:
            urllib.request.urlopen, hv.time.sleep = orig
        self.assertEqual(len(kall), 1)

    def test_csv_skrives_med_lf(self):
        self.kjor(["--alle"], Stub())
        for f in ("variabler.csv", "kodelister.csv"):
            self.assertNotIn(b"\r\n", (self.ut / f).read_bytes(), f)

    def med_dekning(self, stop):
        """Stub der katalogen har fått ny dato i globalTemporalCoverage, som er lik for alle variablene."""
        stub = Stub()

        def svar(url, forsok=4):
            s = stub(url, forsok)
            if "ds" in s:
                s["ds"]["globalTemporalCoverage"] = {"start": -1096, "stop": stop}
            return s
        return svar

    def test_ny_dato_for_katalogen_endrer_ingen_filer(self):
        # stop flytter seg mellom hentingene. PR #15 hadde 772 endrede filer uten at noen variabel var endret.
        kode, err = self.kjor(["--alle"], self.med_dekning(20778))
        self.assertEqual(kode, 0, err[-500:])
        forste = self.hash()
        kode, err = self.kjor(["--alle"], self.med_dekning(20785))
        self.assertEqual(kode, 0, err[-500:])
        self.assertEqual(self.hash(), forste)

    def test_bare_globalTemporalCoverage_utelates(self):
        kode, err = self.kjor(["--alle"], self.med_dekning(20778))
        self.assertEqual(kode, 0, err[-500:])
        for n in NAVN:
            ventet = json.loads((METADATA / "variabler" / f"{n}.json").read_text(encoding="utf-8"))
            ventet.pop("globalTemporalCoverage", None)
            lagret = json.loads((self.ut / "variabler" / f"{n}.json").read_text(encoding="utf-8"))
            self.assertEqual(lagret, ventet, n)

    def test_overstyrt_versjon_huskes_til_neste_kjoring(self):
        # Med --versjon 57 viser datalager.json likevel nyeste versjon øverst. Neste vanlige kjøring skal
        # da hente alt på nytt, ikke gjenbruke filene fra 57.
        self.kjor(["--alle", "--versjon", "57"], Stub())
        self.assertEqual(hv.forrige_versjoner()["no.ssb.fdb"], "57")
        stub = Stub()
        kode, err = self.kjor([], stub)
        self.assertEqual(kode, 0, err[-500:])
        ssb = sum(1 for n in NAVN if LAGER.get(n, "no.ssb.fdb") == "no.ssb.fdb")
        self.assertEqual(len([u for u in stub.detaljer if "/no.ssb.fdb/" in u]), ssb)
        self.assertEqual(hv.forrige_versjoner()["no.ssb.fdb"], VERSJON)

    def test_versjon_i_gammelt_format_gjelder_ssb(self):
        (self.ut / "VERSJON").write_text("59\n", encoding="utf-8")
        self.assertEqual(hv.forrige_versjoner(), {"no.ssb.fdb": "59"})

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
        ssb = {n for n in NAVN if LAGER.get(n, "no.ssb.fdb") == "no.ssb.fdb"}
        self.assertEqual({u.rsplit("/", 1)[1] for u in stub.detaljer}, ssb)  # FHI-lagrene har samme versjon
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
