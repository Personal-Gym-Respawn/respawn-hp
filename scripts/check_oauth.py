"""Offline HTML, links, metadata, passive-content and package boundary checks."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
from build_oauth import FILES, OUTPUT, check_source

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
EXTERNAL = {'https://myaccount.google.com/connections', 'mailto:respawn.personalgym@gmail.com'}
SECRET = re.compile(r'ya29\.[\w-]+|1//[\w-]{20,}|AIza[\w-]{30,}|gh[pousr]_[\w]{20,}|github_pat_[\w]+|-----BEGIN [A-Z ]*PRIVATE KEY-----|accounts/\d+/locations/\d+|[A-Za-z0-9_-]+\.apps\.googleusercontent\.com|(?:client_secret|refresh_token)\s*[=:]\s*["\']?[^\s<]+', re.I)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack, self.nodes, self.links, self.ids, self.refs = [], [], [], set(), []
        self.doctype = False
        self.feed(text)
        self.close()
        assert not self.stack, 'UNCLOSED_TAGS'

    def handle_decl(self, decl):
        assert decl.lower() == 'doctype html', 'DOCTYPE'
        self.doctype = True

    def handle_starttag(self, tag, attrs):
        assert len(dict(attrs)) == len(attrs), 'DUPLICATE_ATTRIBUTE'
        a = dict(attrs)
        self.nodes.append((tag, a))
        assert tag not in {'script','form','input','button','textarea','select','iframe','img','object','embed','base','svg'}, 'ACTIVE_OR_UNREVIEWED_CONTENT'
        assert not any(k.startswith('on') or k == 'style' for k in a), 'INLINE_ACTIVE_CONTENT'
        if 'id' in a:
            assert a['id'] not in self.ids, 'DUPLICATE_ID'
            self.ids.add(a['id'])
        if 'aria-labelledby' in a:
            self.refs.extend(a['aria-labelledby'].split())
        if 'href' in a:
            self.links.append((tag, a['href']))
        if tag == 'a':
            assert a.get('href') not in {None, '', '#'}, 'EMPTY_LINK'
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack and self.stack.pop() == tag, 'MISMATCHED_TAG: ' + tag


def check(directory=OUTPUT):
    check_source(directory)
    pages = {}
    for name in sorted(FILES):
        text = (directory / name).read_text(encoding='utf-8')
        assert not SECRET.search(text), 'CREDENTIAL_OR_PRIVATE_ID_PATTERN: ' + name
        if not name.endswith('.html'):
            continue
        p = pages[name] = Page(text)
        assert p.doctype, 'MISSING_DOCTYPE'
        assert ('html', {'lang':'ja'}) in p.nodes, 'LANG'
        for tag, count in [('html',1),('head',1),('body',1),('main',1),('h1',1),('title',1)]:
            assert sum(t == tag for t,a in p.nodes) == count, tag + '_COUNT'
        meta = {a.get('name') or a.get('property'): a.get('content') for t,a in p.nodes if t == 'meta'}
        assert any(t == 'meta' and a.get('charset') == 'utf-8' for t,a in p.nodes), 'CHARSET'
        assert meta.get('viewport') == 'width=device-width, initial-scale=1', 'VIEWPORT'
        assert meta.get('description') and meta.get('og:title') and meta.get('og:description'), 'META'
        assert meta.get('robots') == 'noindex, nofollow', 'DRAFT_ROBOTS'
        route = '/' if name == 'index.html' else '/' + name.removesuffix('index.html')
        canon = [a.get('href') for t,a in p.nodes if t == 'link' and a.get('rel') == 'canonical']
        assert canon == ['https://respawn-gym.com' + route], 'CANONICAL'
        assert meta.get('og:url') == canon[0], 'OG_URL'
        assert set(p.refs) <= p.ids, 'ARIA_REFERENCE'
        assert any(t == 'a' and a.get('class') == 'skip-link' and a.get('href') == '#main' for t,a in p.nodes), 'SKIP_LINK'
    for name, p in pages.items():
        for tag, href in p.links:
            if tag == 'link' and href.startswith('https://respawn-gym.com'):
                continue  # canonical metadata is not a browser request
            if href in EXTERNAL:
                continue
            url = urlsplit(href)
            assert not url.scheme and not url.netloc and not url.query, 'UNREVIEWED_EXTERNAL_LINK'
            assert href.startswith(('/', '#')) and '..' not in unquote(url.path).split('/'), 'LINK_PATH'
            target = name if not url.path else url.path.lstrip('/')
            if url.path.endswith('/'):
                target += 'index.html'
            assert target in FILES, 'BROKEN_LINK: ' + href
            if url.fragment:
                assert target in pages and unquote(url.fragment) in pages[target].ids, 'BROKEN_FRAGMENT'
    css = (directory/'assets/site.css').read_text()
    assert not re.search(r'url\s*\(|@import', css, re.I), 'CSS_NETWORK'
    assert ':focus-visible' in css and '@media' in css, 'FOCUS_OR_RESPONSIVE_RULES'
    headers = (directory/'_headers').read_text()
    assert "default-src 'none'" in headers and "form-action 'none'" in headers and "frame-ancestors 'none'" in headers, 'CSP'
    assert 'X-Robots-Tag: noindex, nofollow' in headers, 'DRAFT_HEADER'
    assert (directory/'robots.txt').read_text() == 'User-agent: *\nDisallow: /\n', 'ROBOTS'
    print('PASS: 4 HTML documents; internal links/fragments, metadata, basic accessibility, passive assets, credential patterns and 7-file boundary.')


if __name__ == '__main__':
    check()
