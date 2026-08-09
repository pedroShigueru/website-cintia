"""Inspetor de HTML sobre html.parser, para nao depender de bs4."""
from html.parser import HTMLParser

NIVEIS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class InfoPagina(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.meta: dict[str, str] = {}      # name/property -> content
        self.links: list[dict[str, str]] = []
        self.imgs: list[dict[str, str]] = []
        self.headings: list[tuple[int, str]] = []
        self.html_lang: str | None = None
        self.jsonld: list[str] = []
        self._coletando: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "title":
            self._iniciar("title")
        elif tag == "meta":
            chave = a.get("name") or a.get("property")
            if chave:
                self.meta[chave] = a.get("content", "")
        elif tag == "link":
            self.links.append(a)
        elif tag == "a" and "href" in a:
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._iniciar("jsonld")
        elif tag in NIVEIS:
            self._iniciar(tag)

    def handle_endtag(self, tag):
        if self._coletando is None:
            return
        texto = "".join(self._buffer).strip()
        if self._coletando == "title" and tag == "title":
            self.title = texto
        elif self._coletando == "jsonld" and tag == "script":
            self.jsonld.append(texto)
        elif self._coletando == tag and tag in NIVEIS:
            self.headings.append((int(tag[1]), texto))
        else:
            return
        self._coletando = None
        self._buffer = []

    def handle_data(self, data):
        if self._coletando is not None:
            self._buffer.append(data)

    def _iniciar(self, nome: str) -> None:
        self._coletando = nome
        self._buffer = []

    @property
    def h1(self) -> list[str]:
        return [texto for nivel, texto in self.headings if nivel == 1]

    def link(self, rel: str) -> dict[str, str] | None:
        for item in self.links:
            if item.get("rel") == rel:
                return item
        return None


def analisar(html: str) -> InfoPagina:
    info = InfoPagina()
    info.feed(html)
    info.close()
    return info
