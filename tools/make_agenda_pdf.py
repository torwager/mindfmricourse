#!/usr/bin/env python3
"""Build the downloadable agenda PDF (AGENDA_PDF) from the AGENDA table in build_site.py.

Needs Playwright with Chromium:  python3 tools/make_agenda_pdf.py
Re-run whenever the dates or the agenda change, so the PDF and the site stay in step.
"""
import html, os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_site as B   # also changes directory to the repo root

CSS = """
@page { size: Letter; margin: 0.7in 0.75in; }
body { font: 10.5pt/1.4 Georgia, 'Liberation Serif', serif; color: #1c2026; }
.cover { text-align: center; padding-top: 1.6in; page-break-after: always; }
.cover h1 { font-size: 24pt; font-weight: normal; margin: 0 0 .1in; }
.cover .dates { font-size: 16pt; color: #a87a12; margin: .25in 0 .6in; }
.cover p { margin: .12in 0; }
.cover .who { font-size: 12pt; margin-top: .3in; }
.cover .who small { display: block; font-size: 10pt; color: #646b75; }
h2 { font-size: 15pt; font-weight: normal; border-bottom: 2px solid #e9b949; padding-bottom: 4pt; margin: 0 0 10pt; }
section { page-break-after: always; } section:last-child { page-break-after: auto; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font: bold 8.5pt Helvetica, Arial, sans-serif; text-transform: uppercase; letter-spacing: .06em;
     color: #646b75; border-bottom: 1px solid #1c2026; padding: 4pt 6pt; }
td { padding: 5.5pt 6pt; border-bottom: 1px solid #e3dfd6; vertical-align: top; }
td.n, td.t { white-space: nowrap; } td.n { width: 8%; } td.t { width: 13%; } td.i { width: 24%; }
tr.brk td { color: #646b75; font-style: italic; background: #f6f3ec; }
"""

FACULTY = [
    ('Vince D. Calhoun, Ph.D.', 'TReNDS Center, Georgia State / Georgia Tech / Emory'),
    ('Kent A. Kiehl, Ph.D.', 'The Mind Research Network (MRN) and The University of New Mexico'),
    ('Tor Wager, Ph.D.', 'Dartmouth College'),
]


def page():
    out = [f'<!doctype html><meta charset="utf-8"><style>{CSS}</style>',
           '<div class="cover"><h1>fMRI Image Acquisition and Analyses Course<br>with SPM and ICA</h1>',
           f'<div class="dates">{B.DATES}</div><p><strong>Course faculty</strong></p>']
    out += [f'<p class="who">{n}<small>{a}</small></p>' for n, a in FACULTY]
    out.append('<p style="margin-top:.6in">Location: virtual, live online via Zoom (Eastern Time Zone; New York)</p>'
               f'<p>Course website: {B.SITE_URL}</p></div>')
    for day in (1, 2, 3):
        label, rows = B.AGENDA[day]
        out.append(f'<section><h2>Day {day}: {label}, {B.DATES[-4:]}</h2><table>'
                   '<tr><th>Lecture</th><th>Start</th><th>Description</th><th>Instructor(s)</th></tr>')
        for r in rows:
            if len(r) == 2:
                out.append(f'<tr class="brk"><td class="n"></td><td class="t">{r[0]}</td><td colspan="2">{r[1]}</td></tr>')
            else:
                start, sid, desc, who = r
                sid = '' if sid in (None, '0.0') else sid
                out.append(f'<tr><td class="n">{sid}</td><td class="t">{start}</td><td>{desc}</td><td class="i">{html.escape(who)}</td></tr>')
        out.append('</table></section>')
    return ''.join(out)


def main():
    from playwright.sync_api import sync_playwright
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(page())
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto('file://' + f.name)
        pg.pdf(path=B.AGENDA_PDF, format='Letter', print_background=True)
        b.close()
    os.unlink(f.name)
    print('wrote', B.AGENDA_PDF)


if __name__ == '__main__':
    main()
