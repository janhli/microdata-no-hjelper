"""Tester kontrollene i hent_manual.py med en liten syntetisk manual (uten nett)."""

import contextlib
import hashlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

import hjelp  # noqa: F401 - legger verktoy/ i sys.path
import hent_manual as hm

ANTALL = 20


def url(i):
    return f"https://microdata.no/manual/side{i:02d}/"


def html(i, tekst=None):
    tekst = f"Innhold på side {i}. " * 30 if tekst is None else tekst
    return f'<html><body><div class="theme-doc-markdown markdown"><h1>Side {i}</h1><p>{tekst}</p></div></body></html>'


class Stub:
    def __init__(self, sider=range(ANTALL), feil_paa=(), tomme=()):
        self.sider, self.feil_paa, self.tomme = list(sider), set(feil_paa), set(tomme)

    def __call__(self, u):
        if u == hm.SITEMAP:
            # Sitemap oppgir vertsnavnet uten .no, som på microdata.no
            return "<urlset>" + "".join(f"<url><loc>https://microdata/manual/side{i:02d}/</loc></url>"
                                        for i in self.sider) + "</urlset>"
        i = int(re.search(r"side(\d+)", u).group(1))
        if i in self.feil_paa:
            raise OSError("simulert nedlastingsfeil")
        return html(i, "") if i in self.tomme else html(i)


class TestHentManual(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ut = Path(self._tmp.name)
        self._orig = hm.UT, hm.hent, sys.argv
        hm.UT = self.ut
        kode, err = self.kjor([], Stub())  # første kjøring lager 20 sider
        self.assertEqual(kode, 0, err)

    def tearDown(self):
        hm.UT, hm.hent, sys.argv = self._orig
        self._tmp.cleanup()

    def kjor(self, argv, stub):
        hm.hent, sys.argv = stub, ["hent_manual.py", *argv]
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            try:
                hm.main()
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

    def test_forste_kjoring(self):
        filer = sorted(p.name for p in self.ut.glob("*.md"))
        self.assertEqual(len(filer), ANTALL)
        tekst = (self.ut / "side00.md").read_text(encoding="utf-8")
        self.assertTrue(tekst.startswith("<!-- Kilde: https://microdata.no/manual/side00/ -->"))
        self.assertIn("Innhold på side 0", tekst)

    def test_skriver_bare_lf(self):
        # Løse \r fikk git til å regne manualsider som binære, så linjeskift ikke ble normalisert
        stub = Stub()
        stub_html = stub.__call__
        kode, err = self.kjor([], lambda u: stub_html(u).replace("<p>", "<pre>a\r\nb\rc</pre><p>"))
        self.assertEqual(kode, 0, err)
        for f in self.ut.glob("*.md"):
            self.assertNotIn(b"\r", f.read_bytes(), f.name)

    def test_nedlastingsfeil_stopper_uten_endringer(self):
        h = self.hash()
        kode, err = self.kjor([], Stub(feil_paa={3, 4, 5}))
        self.assertEqual(kode, 1)
        self.assertIn("3 sider feilet", err)
        self.assertEqual(self.hash(), h)

    def test_mange_tomme_sider_stoppes(self):
        h = self.hash()
        kode, err = self.kjor([], Stub(tomme=range(ANTALL)))
        self.assertEqual(kode, 1)
        self.assertIn("mye kortere", err)
        self.assertEqual(self.hash(), h)

    def test_faa_tomme_sider_gir_advarsel(self):
        kode, err = self.kjor([], Stub(tomme={1, 2, 3}))
        self.assertEqual(kode, 0)
        self.assertIn("ADVARSEL", err)

    def test_halvert_sitemap_stoppes(self):
        h = self.hash()
        kode, err = self.kjor([], Stub(sider=range(ANTALL // 2)))
        self.assertEqual(kode, 1)
        self.assertIn("sist (grense", err)
        self.assertEqual(self.hash(), h)

    def test_fjernet_side_slettes(self):
        kode, err = self.kjor([], Stub(sider=range(1, ANTALL)))
        self.assertEqual(kode, 0, err)
        self.assertFalse((self.ut / "side00.md").exists())
        self.assertEqual(len(list(self.ut.glob("*.md"))), ANTALL - 1)

    def test_tving_skriver_men_sletter_ikke(self):
        kode, err = self.kjor(["--tving"], Stub(feil_paa={3, 4, 5}))
        self.assertEqual(kode, 0)
        self.assertIn("--tving", err)
        self.assertEqual(len(list(self.ut.glob("*.md"))), ANTALL)


if __name__ == "__main__":
    unittest.main()
