"""Laster ned manualen på microdata.no/manual som Markdown til metadata/manual/.

Sidelisten hentes fra sitemap.xml. Innholdet i <div class="theme-doc-markdown">
(Docusaurus) gjøres om til enkel Markdown: overskrifter, avsnitt, lister,
kodeblokker og tabeller.

Kjøres fra prosjektmappen:  python verktoy/hent_manual.py
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


def main():
    sider = re.findall(r"<loc>([^<]+)</loc>", hent(SITEMAP))
    # Sitemap oppgir vertsnavnet som "microdata" uten .no
    sider = [re.sub(r"^https?://[^/]+", "https://microdata.no", s) for s in sider]
    sider = [s for s in sider if "/manual/test/" not in s]

    for i, url in enumerate(sider, 1):
        sti = urllib.parse.unquote(url.split("/manual/", 1)[1]).strip("/") or "index"
        fil = UT / (re.sub(r'[<>:"|?*]', "_", sti) + ".md")
        try:
            html = hent(url if url.endswith("/") else url + "/")
        except Exception as e:  # noqa: BLE001 - logg og fortsett
            print(f"FEIL {url}: {e}", file=sys.stderr)
            continue
        p = TilMarkdown()
        p.feed(html)
        fil.parent.mkdir(parents=True, exist_ok=True)
        fil.write_text(f"<!-- Kilde: {url} -->\n\n" + p.markdown(), encoding="utf-8")
        if i % 25 == 0:
            print(f"manual: {i}/{len(sider)}", file=sys.stderr)
    print(f"ferdig: {len(sider)} sider", file=sys.stderr)


if __name__ == "__main__":
    main()
