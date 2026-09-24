#!/usr/bin/env python3
# AlphaLatitude Inc. © 2026
#
# Builds index.html and LICENSE.md from the Zenodo records, and downloads the
# mirrored files.
#
# These tools used to live in a session scratchpad, on the reasoning that the
# repository should contain only the site. A cleared scratchpad took them with
# it. They live here now: the site is still static with no build step (the
# HTML is committed and served as-is), and the only way to keep a generator
# recoverable is to version it.
#
#   python3 tools/build_mirror.py latest   what each concept DOI resolves to
#   python3 tools/build_mirror.py fetch    download current files, verify md5
#   python3 tools/build_mirror.py sync     download EVERY version's files
#   python3 tools/build_mirror.py build    write index.html + LICENSE.md
#
# Papers are pinned to their CONCEPT DOIs, the all-versions address, so the
# mirror follows whatever Zenodo currently publishes rather than a record id
# that goes stale on the next upload.

import html
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CACHE = os.path.join(HERE, 'cache')
SITE = 'https://papers.alphalatitude.com'
GH = 'https://github.com/AlphaLatitude/papers'
CORP = 'https://alphalatitude.com'
ORCID = '0009-0005-4569-2228'

API = 'https://zenodo.org/api/records/{}'
API_VERSIONS = 'https://zenodo.org/api/records/{}/versions'  # size= is rejected (400)

PAPERS = [
    {'n': 1, 'concept': '22255461', 'folder': '1-gravitation', 'leg': 'Gravitation'},
    {'n': 2, 'concept': '22683543', 'folder': '2-vacuum', 'leg': 'Vacuum'},
    {'n': 3, 'concept': '22669416', 'folder': '3-register', 'leg': 'Register'},
    {'n': 4, 'concept': '22678537', 'folder': '4-dimension', 'leg': 'Dimension'},
]


def get(url, dest=None):
    req = urllib.request.Request(url, headers={'User-Agent': 'papers-mirror/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    if dest:
        with open(dest, 'wb') as f:
            f.write(data)
    return data


def md5(path):
    out = subprocess.run(['md5', '-q', path], capture_output=True, text=True)
    if out.returncode == 0:
        return out.stdout.strip()
    return subprocess.run(['md5sum', path], capture_output=True, text=True).stdout.split()[0]


# A trailing paragraph opening "v8:" or "Version 7 (5 Sep 2026):" is a
# changelog entry, not part of the abstract. Never applied to the first
# paragraph, which is the abstract itself.
VERSION_NOTE = re.compile(r'^(v\d+|Version\s+\d+)\s*[:(]', re.I)


def abstract_text(desc_html):
    """Zenodo stores the abstract as HTML, with the Greek written as entities
    (&rho;, &Lambda;). Reduce it to the plain text the record shows."""
    s = desc_html
    s = re.sub(r'(?i)<\s*br\s*/?\s*>', '\n', s)
    s = re.sub(r'(?i)</\s*(p|div|li)\s*>', '\n\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    paras = [x for x in s.strip().split('\n\n') if x.strip()]
    kept = [paras[0]] if paras else []
    kept += [x for x in paras[1:] if not VERSION_NOTE.match(x)]
    return '\n\n'.join(kept)


# Exponents and subscripts are written with ^ and _ in the plain text; set
# them properly. Applied AFTER html.escape, so these tags are the only markup
# in an otherwise escaped paragraph. The character classes exclude a trailing
# full stop: "10^61." is not 10 to the 61-point-something.
CARET_PAREN = re.compile(r'\^\(([^)]{1,20})\)')
CARET_PLAIN = re.compile(r'\^(-?[0-9A-Za-z]{1,8}(?:\.[0-9]{1,4})?)')
UNDER_PAREN = re.compile(r'_\(([^)]{1,20})\)')
UNDER_PLAIN = re.compile(r'_([0-9A-Za-zͰ-Ͽ]{1,12})')


def mathify(escaped):
    s = CARET_PAREN.sub(r'<sup>\1</sup>', escaped)
    s = CARET_PLAIN.sub(r'<sup>\1</sup>', s)
    s = UNDER_PAREN.sub(r'<sub>\1</sub>', s)
    return UNDER_PLAIN.sub(r'<sub>\1</sub>', s)


DATE_ON_PAGE = re.compile(
    r'\b(January|February|March|April|May|June|July|August|September|October|'
    r'November|December)\s+(\d{1,2}),\s+(20\d\d)\b')


def paper_date(pdf_path):
    """The date the paper states on its own title page.

    Zenodo's publication_date is the moment of deposit in CERN's timezone, so
    an evening upload from California is stamped the next day - the record
    says 24 September for a paper whose title page says 23. The page should
    show what the paper says. Read from the PDF because the source usually
    writes \\date{\\today}, which resolves when the document is compiled and
    tells us nothing afterwards. Returns None if no date is found, and the
    caller falls back to the record."""
    if not os.path.exists(pdf_path):
        return None
    try:
        txt = subprocess.run(['pdftotext', '-f', '1', '-l', '1', pdf_path, '-'],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return None
    m = DATE_ON_PAGE.search(txt)
    if not m:
        return None
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    return f'{m.group(3)}-{months.index(m.group(1)) + 1:02d}-{int(m.group(2)):02d}'


def pretty_date(iso):
    y, mo, d = iso.split('-')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    return f'{int(d)} {months[int(mo) - 1]} {y}'


def fetch():
    os.makedirs(CACHE, exist_ok=True)
    for p in PAPERS:
        if not p['concept']:
            continue
        # The concept id redirects to the latest published version.
        j = json.loads(get(API.format(p['concept']), f"{CACHE}/paper{p['n']}.json"))
        folder = os.path.join(REPO, 'papers', p['folder'])
        os.makedirs(folder, exist_ok=True)
        print(f"\npaper {p['n']} -> record {j['id']} {j['metadata'].get('version') or '?'} "
              f"({j['metadata']['publication_date']}): {j['metadata']['title'][:52]}")
        for f in j.get('files', []):
            name = f['key']
            dest = os.path.join(folder, name)
            want = f['checksum'].split(':', 1)[1]
            if os.path.exists(dest) and md5(dest) == want:
                print(f'  {name}: present, md5 OK')
                continue
            get(f['links']['self'], dest)
            got = md5(dest)
            if got != want:
                sys.exit(f'checksum mismatch on {name}: want {want} got {got}')
            print(f'  {name}: downloaded, md5 {got} OK')


def sync_all():
    """Download the files of EVERY published version. A version whose files
    are only in git history still 404s on the live site, and a record can
    change after we mirror it (two did, on 10 September 2026)."""
    os.makedirs(CACHE, exist_ok=True)
    for p in PAPERS:
        cur = json.loads(get(API.format(p['concept'])))
        vers = json.loads(get(API_VERSIONS.format(cur['id'])))
        folder = os.path.join(REPO, 'papers', p['folder'])
        os.makedirs(folder, exist_ok=True)
        known = set()
        print(f"\npaper {p['n']}:")
        for rec in vers.get('hits', {}).get('hits', []):
            v = str(rec['metadata'].get('version') or '?')
            for f in rec.get('files', []):
                name = f['key']
                known.add(name)
                dest = os.path.join(folder, name)
                want = f['checksum'].split(':', 1)[1]
                if os.path.exists(dest) and md5(dest) == want:
                    print(f'  {v:5} {name:28} present, md5 OK')
                    continue
                get(f['links']['self'], dest)
                got = md5(dest)
                if got != want:
                    sys.exit(f'checksum mismatch on {name}: want {want} got {got}')
                print(f'  {v:5} {name:28} downloaded, md5 OK')
        for f in sorted(os.listdir(folder)):
            if f.endswith('.html') or f in known:
                continue
            print(f'  ORPHAN {f}: not in any published version of this record')


def check_latest():
    for p in PAPERS:
        j = json.loads(get(API.format(p['concept'])))
        print(f"paper {p['n']}: concept {p['concept']} -> record {j['id']} "
              f"{j['metadata'].get('version') or '?'} ({j['metadata']['publication_date']})")


def load(p):
    j = json.load(open(f"{CACHE}/paper{p['n']}.json"))
    m = j['metadata']
    return {
        'title': m['title'],
        'abstract': abstract_text(m.get('description', '')),
        'version': str(m.get('version') or '').lstrip('vV'),
        'date': m['publication_date'],          # Zenodo deposit, CET
        'paper_date': None,                     # filled in by build()
        'doi': j['doi'],
        'concept': j.get('conceptdoi'),
        'files': sorted(f['key'] for f in j.get('files', [])),
        'license': (m.get('license') or {}).get('id', ''),
    }


def build():
    data = {p['n']: load(p) for p in PAPERS if p['concept']}
    # Prefer the date printed on the paper over the deposit date.
    for p in PAPERS:
        d = data.get(p['n'])
        if not d:
            continue
        pdf = next((f for f in d['files'] if f.endswith('.pdf')), None)
        if pdf:
            d['paper_date'] = paper_date(os.path.join(REPO, 'papers', p['folder'], pdf))
        shown = d['paper_date'] or d['date']
        src = 'title page' if d['paper_date'] else 'Zenodo deposit (no date found on page 1)'
        print(f"  paper {p['n']}: showing {shown} from {src}"
              + (f" (record says {d['date']})" if d['paper_date'] and d['paper_date'] != d['date'] else ''))
    licenses = {d['license'] for d in data.values() if d['license']}
    if len(licenses) > 1:
        sys.exit(f'Records carry different licenses: {licenses} - ask Andrew.')
    for n, d in data.items():
        if not d['version']:
            sys.exit(f"paper {n}: record has no Version field on Zenodo; the status line "
                     f"and tag need it. Set it on the record.")

    p1_concept = data[1]['concept']
    lede = ('Preprints on the granularity of Hilbert space and its consequences for gravity, '
            'the cosmological constant, and the dimension of space. The citable versions are on '
            'Zenodo; this page mirrors them.')
    css = open(os.path.join(HERE, 'index.css')).read()

    head = [
        '<!doctype html>', '<html lang="en">', '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Papers from Andrew Korytko</title>',
        f'<meta name="description" content="{html.escape(lede)}">',
        f'<link rel="canonical" href="{SITE}/">',
        '<link rel="icon" type="image/svg+xml" href="/favicon.svg">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
        '<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">',
        '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700'
        '&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">',
    ]
    # Highwire Press tags, one set per paper, so Google Scholar can index them.
    for p in PAPERS:
        d = data.get(p['n'])
        if not d:
            continue
        pdf = next((f for f in d['files'] if f.endswith('.pdf')), None)
        head += [
            '',
            f'<meta name="citation_title" content="{html.escape(d["title"])}">',
            '<meta name="citation_author" content="Korytko, Andrew">',
            f'<meta name="citation_publication_date" content="{d["date"].replace("-", "/")}">',
        ]
        if pdf:
            head.append(f'<meta name="citation_pdf_url" content="{SITE}/papers/{p["folder"]}/{pdf}">')
        head.append(f'<meta name="citation_doi" content="{d["doi"]}">')
    head += ['', f'<style>{css}</style>', '</head>', '<body>']

    zenodo_link = '<a href="https://doi.org/' + p1_concept + '">Zenodo</a>;'
    lede_html = html.escape(lede).replace('Zenodo;', zenodo_link, 1)
    updated = subprocess.run(
        ['git', '-C', REPO, 'log', '-1', '--format=%cd', '--date=format:%-d %B %Y'],
        capture_output=True, text=True).stdout.strip()

    body = [
        '<div class="chart">', '<div class="graticule"></div>', '<div class="course"></div>',
        '<div class="inner">', '<header class="hero">',
        f'<p class="hero__meta mono">Preprints &middot; <a href="{CORP}">AlphaLatitude Inc.</a>'
        ' &middot; Sunnyvale, California</p>',
        '<h1 class="display">Papers from <span class="lat">Andrew Korytko</span></h1>',
        f'<p class="lede">{lede_html}</p>',
        f'<p class="orcid mono">ORCID <a href="https://orcid.org/{ORCID}">{ORCID}</a></p>',
        '</header>',
    ]

    for p in PAPERS:
        d = data.get(p['n'])
        body += [
            '<section class="leg">', '<div class="fix"></div>',
            f'<div class="leghead mono"><span class="num">{p["n"]:02d}</span>'
            f'<span class="ttl">{html.escape(p["leg"])}</span></div>',
        ]
        if not d:
            body += [f'<h2 class="display">{html.escape(p["title"])}</h2>',
                     '<p class="prep">In preparation.</p>', '</section>']
            continue
        body.append(f'<h2 class="display">{html.escape(d["title"])}</h2>')
        body.append(f'<p class="status mono">Version v{d["version"]} &middot; '
                    f'{pretty_date(d["paper_date"] or d["date"])}</p>')
        for para in d['abstract'].split('\n\n'):
            body.append(f'<p>{mathify(html.escape(para))}</p>')

        links = []
        pdf = next((f for f in d['files'] if f.endswith('.pdf')), None)
        tex = next((f for f in d['files'] if f.endswith('.tex')), None)
        if pdf:
            links.append(f'<a href="papers/{p["folder"]}/{pdf}">PDF</a>')
        # The stable, version-less address; the page it serves names its own
        # version inside, so the URL claims nothing the page does not repeat.
        if os.path.exists(os.path.join(REPO, 'papers', p['folder'], 'latest.html')):
            links.append(f'<a href="papers/{p["folder"]}/latest.html">HTML rendering</a>')
        if tex:
            links.append(f'<a href="papers/{p["folder"]}/{tex}">LaTeX source</a>')
        else:
            links.append('<span class="prep">source on Zenodo</span>')
        links.append(f'<a href="https://doi.org/{d["doi"]}">Zenodo record</a>')
        links.append(f'<a href="https://doi.org/{d["concept"]}">Zenodo latest</a>')
        body.append('<p class="links">' + ' '.join(links) + '</p>')
        body.append(f'<pre class="mono">{html.escape(f"A. Korytko, {d['title']}, Zenodo (2026). doi:{d['concept']}")}</pre>')
        body.append('</section>')

    # Footer follows alphalatitude.com. Its analytics sentence is deliberately
    # NOT copied: this page runs none, so repeating it would describe software
    # that is not here.
    body += [
        '<footer class="mono">',
        '<p class="arrival">Registered position</p>',
        '<div class="footer-block">',
        f'<a href="{CORP}">AlphaLatitude Inc.</a> &copy; 2026 &middot; Sunnyvale, California '
        '&middot; Registered in California (C-corp)<br>',
        'OptionsAhoy&trade; is a trademark of AlphaLatitude Inc.',
        '</div>', '<div class="footer-block">',
        'Mirror of Zenodo records; the DOIs above are the citations of record. '
        f'Source for this page: <a href="{GH}">{GH.replace("https://", "")}</a>.'
        + (f' Updated {updated}.' if updated else ''),
        '</div>', '<div class="footer-block">',
        'This page sets no cookies, runs no scripts, and collects no personal data.',
        '</div>', '</footer>', '</div>', '</div>', '</body>', '</html>', '',
    ]

    with open(os.path.join(REPO, 'index.html'), 'w') as f:
        f.write('\n'.join(head + body))
    print(f'index.html written ({len(data)} published papers, license {licenses or "unknown"})')

    lic = (licenses or {''}).pop()
    if lic.lower().startswith('cc-by-4'):
        with open(os.path.join(REPO, 'LICENSE.md'), 'w') as f:
            f.write('# License\n\n'
                    'The papers mirrored here are distributed under the Creative Commons '
                    'Attribution 4.0 International license (CC BY 4.0), matching their Zenodo '
                    'records: https://creativecommons.org/licenses/by/4.0/\n\n'
                    'Copyright Andrew Korytko.\n')
        print('LICENSE.md written (CC BY 4.0)')
    else:
        print(f'LICENSE.md NOT written: unrecognised license id {lic!r} - check the records.')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    {'fetch': fetch, 'build': build, 'latest': check_latest, 'sync': sync_all}[cmd]()
