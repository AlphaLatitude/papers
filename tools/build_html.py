#!/usr/bin/env python3
# AlphaLatitude Inc. © 2026
#
# Generates the phone-reading HTML renderings.
#
# These are the only files on the site that are not byte-identical copies of
# a Zenodo record. They are derivatives, generated here from the mirrored
# LaTeX source, and every page says so. The rules, and why:
#
#   - Mirror only, NEVER uploaded to Zenodo. Zenodo holds the citable object:
#     one PDF and one source per version, each checksummed. A third artifact
#     would have to stay identical to the other two at every version, and any
#     divergence would become a discrepancy in the record of citation rather
#     than a cosmetic glitch on a website.
#   - Every mirrored version gets a rendering, and none is ever deleted: a URL
#     that once worked keeps working.
#   - A page always names the version it shows. When that is not the newest it
#     says so and links forward, rather than quietly serving a different paper
#     than its URL promises.
#   - latest.html is a stable, version-less address per paper holding the
#     current rendering, for the index to link.
#
# Usage: python3 tools/build_html.py     (after build_mirror.py fetch)

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
WORK = '/tmp/papers-latexml'
CORP = 'https://alphalatitude.com'
API_VERSIONS = 'https://zenodo.org/api/records/{}/versions'  # size= is rejected (400)

FOLDERS = {1: '1-gravitation', 2: '2-vacuum', 3: '3-register', 4: '4-dimension'}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'papers-mirror/1.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def pretty(iso):
    y, m, d = iso.split('-')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    return f'{int(d)} {months[int(m) - 1]} {y}'


TABLE_OPEN = re.compile(r'<table[^>]*class="(?:ltx_equation|ltx_tabular)[^"]*"[^>]*>')


def wrap_wide_blocks(doc):
    """Wrap each equation/tabular table in a scrolling div, so a wide formula
    scrolls in its own box instead of dragging the page sideways. A
    display:table box is not a scroll container and forcing display:block
    breaks the row layout, so the wrapper has to be a real div. These tables
    never nest another table; asserts rather than guesses if that changes."""
    out, pos = [], 0
    for m in TABLE_OPEN.finditer(doc):
        if m.start() < pos:
            continue
        end = doc.find('</table>', m.end())
        if end == -1:
            sys.exit('unclosed table in LaTeXML output')
        if '<table' in doc[m.end():end]:
            sys.exit('nested table found; the wrapper needs a real parser')
        end += len('</table>')
        out.append(doc[pos:m.start()])
        out.append('<div class="scrollbox">' + doc[m.start():end] + '</div>')
        pos = end
    out.append(doc[pos:])
    return ''.join(out)


def footer_bar(pdf, doi):
    """The same links at the end. A rendering is a long scroll on a phone; a
    reader who reaches the bibliography should not have to scroll back up."""
    return (
        '<div class="mirror-note mirror-foot">'
        'The PDF is authoritative. '
        f'<a href="{pdf}">Read the PDF</a> <span class="sep">&middot;</span> '
        f'<a href="https://doi.org/{doi}">Zenodo record</a> <span class="sep">&middot;</span> '
        '<a href="../../">All papers</a> <span class="sep">&middot;</span> '
        f'<a href="{CORP}">AlphaLatitude Inc.</a>'
        '<br>Copyright &copy; 2026 Andrew Korytko.'
        '</div>'
    )


def banner(pdf, version, doi, current=None, withdrawn=False):
    head = (
        '<strong>HTML rendering; the PDF is authoritative.</strong><br>'
        f'Generated from the LaTeX source of version {html.escape(version)} for reading on a phone. '
        'Equations are converted automatically and may differ in presentation from the paper. '
    )
    if withdrawn:
        # No version number is asserted: the record that carried these files
        # now carries different ones, so any label would be our guess.
        cur_v, cur_href, cur_date = current or ('', 'latest.html', '')
        fwd = (f'The current version is {html.escape(cur_v)} ({html.escape(cur_date)}): '
               f'<a href="{cur_href}">read it</a>. ' if cur_v else '')
        head = (
            '<strong>Superseded; these files are no longer published on Zenodo.</strong><br>'
            'The Zenodo record this copy came from now carries different files. This page is '
            'kept so that links already pointing at it still work, and it shows what was '
            f'published at the time it was mirrored. {fwd}'
        )
    elif current:
        cur_v, cur_href, cur_date = current
        head = (
            f'<strong>Superseded version {html.escape(version)}.</strong><br>'
            f'Version {html.escape(cur_v)} ({html.escape(cur_date)}) is current: '
            f'<a href="{cur_href}">read it</a>. This page shows {html.escape(version)}, '
            'rendered from its LaTeX source; the PDF of this version is authoritative for it. '
        )
    links = (
        f'<a href="{pdf}">Read the PDF</a> <span class="sep">&middot;</span> '
        f'<a href="https://doi.org/{doi}">Zenodo record</a> <span class="sep">&middot;</span> '
        '<a href="../../">All papers</a> <span class="sep">&middot;</span> '
        f'<a href="{CORP}">AlphaLatitude Inc.</a>'
    )
    cls = 'mirror-note' + (' mirror-old' if (current or withdrawn) else '')
    return f'<div class="{cls}">{head}{links}</div>'


def convert(tex_path, stem):
    """LaTeXML, then its HTML5 post-processor. Run here rather than by hand so
    a new Zenodo version cannot leave a rendering describing the old one."""
    os.makedirs(WORK, exist_ok=True)
    xml = os.path.join(WORK, stem + '.xml')
    out = os.path.join(WORK, stem + '.html')
    r = subprocess.run(['latexml', '--dest=' + xml, tex_path], capture_output=True, text=True)
    errs = [l for l in r.stderr.splitlines() if l.startswith('Error') and 'orcidlink' not in l]
    if errs:
        sys.exit('latexml errors in %s:\n  %s' % (stem, '\n  '.join(errs[:5])))
    subprocess.run(['latexmlpost', '--dest=' + out, '--format=html5', '--pmml',
                    '--nomathtex', '--novalidate', xml], capture_output=True, text=True)
    if not os.path.exists(out):
        sys.exit('latexmlpost produced nothing for ' + stem)
    return out


def versions_for(record_id, n):
    """{filename: (version, date, doi)} across every published version."""
    j = json.loads(get(API_VERSIONS.format(record_id)))
    with open(f'{CACHE}/paper{n}_versions.json', 'w') as f:
        json.dump(j, f)
    by_file = {}
    for rec in j.get('hits', {}).get('hits', []):
        v = str(rec['metadata'].get('version') or '?')
        d = rec['metadata']['publication_date']
        for fl in rec.get('files', []):
            by_file[fl['key']] = (v, d, rec['doi'])
    return by_file


def main():
    css = ''
    for f in ('LaTeXML.css', 'ltx-article.css', 'overrides.css'):
        css += open(os.path.join(HERE, f)).read() + '\n'

    for n, folder in FOLDERS.items():
        j = json.load(open(f'{CACHE}/paper{n}.json'))
        cur_names = [f['key'] for f in j['files']]
        cur_tex = next((x for x in cur_names if x.endswith('.tex')), None)
        cur_pdf = next((x for x in cur_names if x.endswith('.pdf')), None)
        cur_version = str(j['metadata'].get('version') or '')
        cur_date = pretty(j['metadata']['publication_date'])
        by_file = versions_for(j['id'], n)

        dirpath = os.path.join(REPO, 'papers', folder)
        texes = sorted(x for x in os.listdir(dirpath) if x.endswith('.tex'))
        print(f'\npaper {n} ({folder}): current {cur_version}, {len(texes)} version(s)')

        for tex in texes:
            stem = tex[:-4]
            is_current = tex == cur_tex
            meta = by_file.get(tex)
            if meta:
                version, _date, doi = meta
                withdrawn = False
            else:
                version, doi, withdrawn = stem, j['doi'], True
            pdf = next((x for x in os.listdir(dirpath)
                        if x.endswith('.pdf') and x[:-4] == stem), cur_pdf)

            doc = open(convert(os.path.join(dirpath, tex), stem), encoding='utf-8').read()
            # \orcidlink has no LaTeXML binding and leaves a red error marker
            # in the byline; the ORCID number itself is in the text.
            doc = doc.replace('<span class="ltx_ERROR undefined">\\orcidlink</span>', '')
            doc = re.sub(r'(Andrew Korytko\s*)(0009-0005-4569-2228)',
                         r'\1<a href="https://orcid.org/\2">\2</a>', doc, count=1)
            doc = wrap_wide_blocks(doc)
            doc = re.sub(r'<link rel="stylesheet"[^>]*>', '', doc)
            doc = doc.replace('</head>', f'<style>{css}</style>\n</head>')
            doc = doc.replace('</head>',
                              '<link rel="icon" type="image/svg+xml" href="../../favicon.svg">'
                              '<link rel="icon" type="image/png" sizes="32x32" href="../../favicon-32x32.png">'
                              '\n</head>')
            current = None if is_current else (cur_version, 'latest.html', cur_date)
            doc = doc.replace('<body>', '<body>\n' + banner(pdf, version, doi, current, withdrawn), 1)
            doc = doc.replace('</body>', footer_bar(pdf, doi) + '\n</body>', 1)

            dest = os.path.join(dirpath, stem + '.html')
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(doc)
            state = 'CURRENT' if is_current else ('withdrawn from Zenodo' if withdrawn else 'superseded')
            print(f'  {stem + ".html":34} {os.path.getsize(dest)//1024:>4}kb  {state}')

            if is_current:
                with open(os.path.join(dirpath, 'latest.html'), 'w', encoding='utf-8') as f:
                    f.write(doc)
                print(f'  {"latest.html":34} {os.path.getsize(dest)//1024:>4}kb  stable link -> {cur_version}')


if __name__ == '__main__':
    main()
