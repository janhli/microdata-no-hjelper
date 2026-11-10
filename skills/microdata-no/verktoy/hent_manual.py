"""Laster ned manualen på microdata.no/manual som Markdown til metadata/manual/.

Sidelisten hentes fra sitemap.xml. Innholdet i <div class="theme-doc-markdown">
(Docusaurus) gjøres om til enkel Markdown: overskrifter, avsnitt, lister,
kodeblokker og tabeller.

Kjøres fra prosjektmappen:  python verktoy/hent_manual.py [--tving]

Alle sider hentes og kontrolleres i minnet før noe skrives. Ved feil avsluttes skriptet med feilkode 1
uten å endre noen filer. Kontrollene er: ingen nedlastingsfeil, minst 90 % av forrige antall sider, og
ikke mer enn 5 sider som er blitt under 20 % så lange som før (en endret nettside gir ofte tomme sider).
--tving skriver likevel (for manuell kjøring etter at du har sett på feilene). Sider som ikke lenger står
i sitemap, slettes (ikke når noen sider feilet).
"""

import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SITEMAP = "https://microdata.no/manual/sitemap.xml"
UT = Path(__file__).resolve().parent.parent / "metadata" / "manual"
PAUSE = 0.3
MIN_ANDEL_SIDER = 0.9  # minst så stor andel av forrige antall sider
KRYMP_MIN_TEGN = 200  # bare sider som var minst så lange sist vurderes for krymping
KRYMP_ANDEL = 0.2  # en side regnes som krympet hvis den er under så stor andel av forrige lengde
KRYMP_MAKS_SIDER = 5  # flere krympede sider enn dette stopper oppdateringen

BLOKK = {"p", "div", "ul", "ol", "table", "blockquote", "details", "summary"}


class TilMarkdown(HTMLParser):
    """Henter innholdet i theme-doc-markdown og skriver det som Markdown."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.dybde = 0  # div-nivå inne i innholdet; 0 = utenfor
        self.ut = []
        self.pre = False
        self.lister = []
        self.celler = None
        self.tabellrader = 0
        self.hopp = 0  # inne i <button>/<svg> o.l. som ikke skal med
        self.spans = []  # True for <span class="rosecodeblock"> (kodeeksempel)

    def skriv(self, tekst):
        if self.celler is not None:
            self.celler[-1] += tekst
        else:
            self.ut.append(tekst)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.dybde == 0:
            if tag == "div" and "theme-doc-markdown" in (a.get("class") or ""):
                self.dybde = 1
            return
        if tag == "div":
            self.dybde += 1
        if tag in ("button", "svg", "style", "script"):
            self.hopp += 1
        if self.hopp:
            return
        if tag == "span":
            kode = "rosecodeblock" in (a.get("class") or "")
            self.spans.append(kode)
            if kode:
                self.pre = True
                self.skriv("\n\n```\n")
        elif re.fullmatch(r"h[1-6]", tag):
            self.skriv("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "pre":
            self.pre = True
            self.skriv("\n\n```\n")
        elif tag == "code" and not self.pre:
            self.skriv("`")
        elif tag == "br":
            self.skriv("\n")
        elif tag in ("ul", "ol"):
            self.lister.append(tag)
        elif tag == "li":
            self.skriv("\n" + "  " * (len(self.lister) - 1) + ("1. " if self.lister[-1:] == ["ol"] else "- "))
        elif tag == "tr":
            self.celler = []
        elif tag in ("td", "th") and self.celler is not None:
            self.celler.append("")
        elif tag in ("strong", "b"):
            self.skriv("**")
        elif tag == "a" and a.get("href", "").startswith("http"):
            self.skriv("[")
            self.lenke = a["href"]
        elif tag in BLOKK:
            self.skriv("\n\n")

    def handle_endtag(self, tag):
        if self.dybde == 0:
            return
        if tag == "div":
            self.dybde -= 1
            if self.dybde == 0:
                return
        if tag in ("button", "svg", "style", "script"):
            self.hopp = max(0, self.hopp - 1)
            return
        if self.hopp:
            return
        if tag == "span":
            if self.spans and self.spans.pop():
                self.pre = False
                self.skriv("\n```\n")
        elif tag == "pre":
            self.pre = False
            self.skriv("\n```\n\n")
        elif tag == "code" and not self.pre:
            self.skriv("`")
        elif tag in ("ul", "ol") and self.lister:
            self.lister.pop()
            self.skriv("\n")
        elif tag == "tr" and self.celler is not None:
            rad = "| " + " | ".join(" ".join(c.split()) for c in self.celler) + " |"
            self.celler = None
            self.ut.append(("\n" if self.tabellrader else "\n\n") + rad)
            if self.tabellrader == 0:
                self.ut.append("\n|" + "---|" * rad.count(" | ") + "---|")
            self.tabellrader += 1
        elif tag == "table":
            self.tabellrader = 0
            self.skriv("\n\n")
        elif tag in ("strong", "b"):
            self.skriv("**")
        elif tag == "a" and getattr(self, "lenke", None):
            self.skriv(f"]({self.lenke})")
            self.lenke = None
        elif re.fullmatch(r"h[1-6]", tag) or tag in BLOKK:
            self.skriv("\n\n")

    def handle_data(self, data):
        if self.dybde == 0 or self.hopp:
            return
        if self.pre:
            self.skriv(data)
        else:
            self.skriv(re.sub(r"\s+", " ", data))

    def markdown(self):
        tekst = "".join(self.ut).replace("​", "")
        tekst = re.sub(r"[ \t]+\n", "\n", tekst)
        return re.sub(r"\n{3,}", "\n\n", tekst).strip() + "\n"


def hent(url):
    req = urllib.request.Request(url, headers={"User-Agent": "microdata-manual/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        tekst = r.read().decode("utf-8")
    time.sleep(PAUSE)
    return tekst


def kropp(tekst):
    """Sideinnholdet uten kildekommentaren øverst."""
    return (tekst.split("-->", 1)[1] if tekst.startswith("<!--") else tekst).strip()


def kontroller(feil, nye):
    """Returnerer (problemer, advarsler). Tom problemliste betyr at uttrekket kan skrives.

    «Tom side» måles mot forrige versjon, siden noen indekssider med rette er tomme.
    """
    problemer, advarsler = [], []
    if feil:
        vis = "; ".join(feil[:5]) + (" ..." if len(feil) > 5 else "")
        problemer.append(f"{len(feil)} sider feilet: {vis}")
    sist = list(UT.rglob("*.md"))
    if sist and len(nye) < MIN_ANDEL_SIDER * len(sist):
        problemer.append(f"{len(nye)} sider, mot {len(sist)} sist (grense {MIN_ANDEL_SIDER:.0%})")
    krympet = []
    for fil, tekst in nye.items():
        if fil.exists():
            gammel, ny = kropp(fil.read_text(encoding="utf-8")), kropp(tekst)
            if len(gammel) >= KRYMP_MIN_TEGN and len(ny) < KRYMP_ANDEL * len(gammel):
                krympet.append(f"{fil.relative_to(UT).as_posix()} ({len(gammel)} -> {len(ny)} tegn)")
    if len(krympet) > KRYMP_MAKS_SIDER:
        problemer.append(f"{len(krympet)} sider er blitt mye kortere (kan bety at nettsiden er endret): "
                         + "; ".join(krympet[:5]) + " ...")
    elif krympet:
        advarsler.append("sider som er blitt mye kortere: " + "; ".join(krympet))
    return problemer, advarsler


def main():
    sider = re.findall(r"<loc>([^<]+)</loc>", hent(SITEMAP))
    # Sitemap oppgir vertsnavnet som "microdata" uten .no
    sider = [re.sub(r"^https?://[^/]+", "https://microdata.no", s) for s in sider]
    sider = [s for s in sider if "/manual/test/" not in s]

    tving = "--tving" in sys.argv
    nye, feil = {}, []
    for i, url in enumerate(sider, 1):
        sti = urllib.parse.unquote(url.split("/manual/", 1)[1]).strip("/") or "index"
        fil = UT / (re.sub(r'[<>:"|?*]', "_", sti) + ".md")
        try:
            html = hent(url if url.endswith("/") else url + "/")
            p = TilMarkdown()
            p.feed(html)
            nye[fil] = f"<!-- Kilde: {url} -->\n\n" + p.markdown()
        except Exception as e:  # noqa: BLE001 - samle feil og avbryt før noe skrives
            print(f"FEIL {url}: {e!r}", file=sys.stderr)
            feil.append(f"{url} ({e.__class__.__name__})")
        if i % 25 == 0:
            print(f"manual: {i}/{len(sider)}", file=sys.stderr)

    problemer, advarsler = kontroller(feil, nye)
    for a in advarsler:
        print(f"ADVARSEL: {a}", file=sys.stderr)
    if problemer:
        for p in problemer:
            print(f"PROBLEM: {p}", file=sys.stderr)
        if not tving:
            print("AVBRUTT: ingen filer er endret. Bruk --tving for å skrive likevel.", file=sys.stderr)
            sys.exit(1)
        print("--tving: skriver likevel.", file=sys.stderr)

    for fil, tekst in nye.items():
        fil.parent.mkdir(parents=True, exist_ok=True)
        # Alltid \n: på Windows gir ellers write_text \r\n, og løse \r får git til å regne filen som binær
        fil.write_text(tekst.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")
    # Sider som ikke lenger står i sitemap, slettes. Ikke ved feil (--tving), da kan gyldige sider mangle i nye.
    utgaatt = [] if feil else sorted(set(UT.rglob("*.md")) - set(nye))
    for fil in utgaatt:
        fil.unlink()
        print(f"slettet {fil.relative_to(UT).as_posix()} (ikke lenger i sitemap)", file=sys.stderr)
    print(f"ferdig: {len(nye)} sider", file=sys.stderr)


if __name__ == "__main__":
    main()
