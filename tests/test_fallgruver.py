"""Sjekker at fallgruvefilene henger sammen.

`referanser/fallgruver.md` leses i sin helhet før hvert skript og må være kort. Temafilene
(`referanser/fallgruver_<tema>.md`) leses bare når skriptet bruker temaet. Henvisninger til avsnitt («Navn») må
treffe en overskrift i filen de peker på, ellers leter agenten forgjeves.
"""

import re
import unittest

from hjelp import SKILL

ROT = SKILL.parent.parent
REF = SKILL / "referanser"
KJERNE = REF / "fallgruver.md"
MAKS_KJERNE = 30_000  # byte. Var 57 kB før delingen i november 2026.
FILNAVN = r"`?(?:[\w./-]*/)?(fallgruver(?:_\w+)?\.md)"
# «Navn» i `fallgruver_x.md`, og fallgruver.md, «Navn». Linjeskift kan stå inne i henvisningen.
NAVN_SA_FIL = re.compile(r"«([^«»]+)»\s+i\s+\[?" + FILNAVN)
FIL_SA_NAVN = re.compile(FILNAVN + r"`?,\s+«([^«»]+)»")
UTEN_FIL = re.compile(r"\b[Ss]e(?:\s+også)?\s+«([^«»]+)»(?!\s+i\s+(?:\[|`|manualen))")


def les(fil):
    return fil.read_text(encoding="utf-8")


def flat(tekst):
    """Uten backticks og med enkle mellomrom, så linjeskift inne i en henvisning ikke betyr noe."""
    return " ".join(tekst.replace("`", "").split())


def overskrifter(fil):
    return [flat(o) for o in re.findall(r"^#+ (.+)$", les(fil), re.MULTILINE)]


def treffer(navn, fil):
    return any(o.startswith(flat(navn)) for o in overskrifter(fil))


def fallgruvefiler():
    return sorted(REF.glob("fallgruver*.md"))


def tekstfiler():
    """Filene som viser til fallgruvene. Ikke evals (historikk) og metadata (hentet)."""
    monstre = ["*.md", "skills/microdata-no/*.md", "skills/microdata-no/referanser/*.md",
               "skills/microdata-no/kodesnutter/*", "skills/microdata-no/verktoy/*.py", "arkiv/**/*",
               ".claude/skills/**/*.md", ".claude/skills/**/*.txt"]
    return sorted({f for m in monstre for f in ROT.glob(m) if f.is_file()})


class TestFallgruver(unittest.TestCase):
    def test_kjernen_er_kort(self):
        self.assertLessEqual(len(KJERNE.read_bytes()), MAKS_KJERNE)

    def test_temafilene_star_i_indeksen_og_i_skill_md(self):
        tema = [f.name for f in fallgruvefiler() if f != KJERNE]
        self.assertGreaterEqual(len(tema), 4)
        for navn in tema:
            with self.subTest(fil=navn):
                self.assertIn(f"`{navn}`", les(KJERNE))
                self.assertIn(f"`referanser/{navn}`", les(SKILL / "SKILL.md"))

    def test_avsnitt_med_filnavn_finnes(self):
        feil, antall = [], 0
        for f in tekstfiler():
            tekst = re.sub(r"\n\s*//\s*", "\n", les(f))  # kommentarer i snutter og testskript
            par = [(n, fil) for n, fil in NAVN_SA_FIL.findall(tekst)]
            par += [(n, fil) for fil, n in FIL_SA_NAVN.findall(tekst)]
            for navn, fil in par:
                antall += 1
                if not (REF / fil).exists() or not treffer(navn, REF / fil):
                    feil.append(f"{f.relative_to(ROT)}: «{navn}» finnes ikke i {fil}")
        self.assertEqual(feil, [], "\n".join(feil))
        self.assertGreater(antall, 5)

    def test_avsnitt_uten_filnavn_finnes_i_samme_fil(self):
        feil = [f"{f.name}: «{navn}»" for f in fallgruvefiler() for navn in UTEN_FIL.findall(les(f))
                if not treffer(navn, f)]
        self.assertEqual(feil, [], "\n".join(feil))

    def test_versjon_1_av_tiltakene_staar_bare_i_ett_avsnitt(self):
        # Avsnittet slettes når overgangsordningen er over (etter planen 30. april 2027).
        monster = re.compile(r"confidentiality v1|\*\*Versjon 1|bare versjon 1|(?i:i|med|fra) versjon 1\b")
        feil = []
        for f in fallgruvefiler():
            for avsnitt in re.split(r"(?m)^(?=#{2,3} )", les(f)):
                tittel = avsnitt.split("\n", 1)[0]
                if tittel.startswith("### Versjon 1 av anonymiseringstiltakene"):
                    self.assertIn("30. april 2027", avsnitt)
                    self.assertEqual(f, KJERNE)
                    continue
                feil += [f"{f.name}, {tittel}: {m}" for m in monster.findall(avsnitt)]
        self.assertEqual(feil, [], "\n".join(feil))
        self.assertTrue(treffer("Versjon 1 av anonymiseringstiltakene", KJERNE))

    def test_stata_tabellen_viser_til_avsnitt_som_finnes(self):
        tabell = les(SKILL / "SKILL.md").split("### Vaner fra Stata som ikke virker")[1].split("\n## ")[0]
        navn = [n for linje in tabell.splitlines() if linje.startswith("|")
                for n in re.findall(r"«([^«»]+)»", linje.rsplit("|", 2)[1])]
        self.assertGreater(len(navn), 5)
        for n in navn:
            with self.subTest(avsnitt=n):
                self.assertTrue(any(treffer(n, f) for f in fallgruvefiler()), n)


if __name__ == "__main__":
    unittest.main()
