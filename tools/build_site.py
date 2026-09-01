#!/usr/bin/env python3
"""Build the fMRI course site.

Reads content/lectures/day*.json (session outlines), content/images/*.json (figures),
content/guides/*.html (cheat sheets) and writes all HTML pages in the repo root and
lectures/. Run from the repo root:  python3 tools/build_site.py
"""
import json, os, re, glob, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ----------------------------------------------------------------------------- data
PAYPAL = {
    'trainee': 'https://www.paypal.com/ncp/payment/9UY83YQR8RG6A',
    'faculty': 'https://www.paypal.com/ncp/payment/322ZKGJEC7XDG',
    'industry': 'https://www.paypal.com/ncp/payment/2YWQU3FT5QFKQ',
}
QUESTIONNAIRE = 'https://docs.google.com/a/mrn.org/forms/d/12QP5TnkLdwx9zxKfD1hYAXfNOcP3GqJGMv4vOxn8ff0/viewform'
AGENDA_PDF = 'assets/pdf/fMRI_Course_Agenda_Sep_9-11_2026.pdf'
DATES = 'September 9–11, 2026'
SITE_URL = 'https://torwager.github.io/mindfmricourse/'
SOCIAL_CARD = 'assets/img/social-card.jpg'   # 1200x630, built by tools/make_social_card.py
SOCIAL_ALT = 'fMRI Acquisition and Analysis — September 9–11, 2026, live online. Vince Calhoun, Kent Kiehl, and Tor Wager.'

ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
EXT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>'
CHEV = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>'
DOWN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M6 13l6 6 6-6"/></svg>'
PDF_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></svg>'

def load_json(p, default=None):
    return json.load(open(p)) if os.path.exists(p) else (default if default is not None else [])

LECTURES = []
for d in (1, 2, 3):
    for s in load_json(f'content/lectures/day{d}.json'):
        s['day'] = d
        LECTURES.append(s)
BY_ID = {s['id']: s for s in LECTURES}

IMAGES = load_json('content/images/slides.json') + load_json('content/images/papers.json')
for im in IMAGES:
    im.setdefault('origin', 'papers')
    im.setdefault('concepts', [])

# Agenda (2026) — rows: (start, id or None, description, instructors) ; 2-tuples are breaks
AGENDA = {
    1: ('Wednesday, September 9', [
        ('8:00 am', '0.0', 'Course introduction', 'Kiehl, Calhoun, Wager'),
        ('8:30 am', '1.1', 'Virtual tours of MRI and acquisition of data, stimulus presentation, behavioral monitoring', 'Kiehl'),
        ('9:30 am', 'Break'),
        ('9:45 am', None, 'Check download and tools install: Dropbox folder with data', 'All'),
        ('10:00 am', '1.2', 'fMRI physics, pulse sequences, and reconstruction', 'Calhoun'),
        ('11:00 am', '1.2b', 'Install: SPM and toolboxes', 'Wager'),
        ('11:20 am', '1.3', 'MATLAB basics and orientation', 'Wager'),
        ('11:30 am', '1.4', 'Reproducible analysis: coding and data-management practices; CANlab tools install check', 'Wager'),
        ('12:00 pm', 'Lunch break'),
        ('12:30 pm', '1.5', 'Intro to SPM: data checking, reorienting data', 'Kiehl'),
        ('1:30 pm', '1.6', 'Spatial preprocessing: realignment, slice timing, unwarp', 'Kiehl'),
        ('2:30 pm', 'Break'),
        ('3:00 pm', '1.7', 'Preprocessing: coregistration, normalization, smoothing', 'Kiehl'),
        ('4:00 pm', '1.8', 'General Linear Model I: principles and fMRI', 'Wager'),
        ('5:00 pm', '1.9', 'CANlab interactive tools: basic analysis and visualization', 'Wager'),
        ('5:30 pm', None, 'Question and answer session', 'Kiehl, Wager, Calhoun'),
        ('6:00 pm', 'Adjourn'),
    ]),
    2: ('Thursday, September 10', [
        ('8:00 am', None, 'Review from Day 1: question and answer', 'Kiehl, Calhoun, Wager'),
        ('8:30 am', '2.1', 'GLM model building: predictors and contrasts', 'Wager'),
        ('9:00 am', '2.2', 'GLM filtering and nuisance regressors', 'Wager'),
        ('9:30 am', '2.3', 'GLM multicollinearity and diagnostics', 'Wager'),
        ('10:15 am', 'Break'),
        ('10:30 am', '2.4', 'SPM GUI for single subjects: explore design, scaling, results', 'Kiehl'),
        ('12:00 pm', 'Lunch break'),
        ('12:30 pm', '2.5', 'Basis sets: flexible hemodynamic modeling', 'Wager'),
        ('1:15 pm', '2.6', 'Derivative boost', 'Calhoun'),
        ('1:30 pm', '2.7', 'Parametric modulators', 'Wager'),
        ('1:45 pm', '2.8', 'Autocorrelation and generalized linear models', 'Wager'),
        ('2:30 pm', 'Break'),
        ('3:00 pm', '2.9', 'Intro to connectivity and mediation; mediation demo and walkthrough', 'Wager'),
        ('4:00 pm', '2.10', 'Introduction to ICA: Independent Component Analysis', 'Calhoun'),
        ('5:30 pm', None, 'Question and answer session', 'Kiehl, Calhoun, Wager'),
        ('6:00 pm', 'Adjourn'),
    ]),
    3: ('Friday, September 11', [
        ('8:00 am', None, 'Review of Days 1–2', 'Kiehl, Calhoun, Wager'),
        ('8:15 am', '3.1', 'Experimental design: psychological and statistical principles', 'Wager'),
        ('9:45 am', 'Coffee break'),
        ('10:00 am', '3.2', 'Group analysis: fixed, random, and mixed effects', 'Wager'),
        ('10:45 am', '3.3', 'Group analysis: thresholding and inference', 'Wager'),
        ('11:30 am', '3.4', 'SPM results: group subjects, plotting, display, small-volume correction', 'Kiehl'),
        ('12:30 pm', 'Lunch'),
        ('1:00 pm', '3.5', 'ICA II: fMRI', 'Calhoun'),
        ('2:00 pm', 'Break'),
        ('2:15 pm', '3.6', 'ICA of fMRI: implementation', 'Calhoun, Kiehl'),
        ('3:45 pm', None, 'Final Q&amp;A and farewell', 'Kiehl, Calhoun, Wager'),
        ('4:00 pm', 'Adjourn'),
    ]),
}
DAY_TITLES = {1: 'Acquisition, preprocessing, and the GLM', 2: 'Modeling, connectivity, and ICA', 3: 'Design, group inference, and ICA in practice'}

# Cheat sheets per session: (label, content/guides file or None, external link or None)
GUIDES = {
    '1.1': [('Sample fMRI slice protocol', 'Sample_fMRI_slice_protocol_v1.0', None)],
    '1.2b': [('Install steps for the course toolboxes', 'fMRI_analysis_course_install_steps', None)],
    '1.5': [('Cheat sheet: re-orientation', 'cheat_sheet_reorientation_2022', None), ('Cheat sheet: ArtRepair', 'cheat_sheet_art_repair_2022', None)],
    '1.6': [('Cheat sheet: realignment (INRIAlign)', 'cheat_sheet_realignment_2022', None)],
    '1.7': [('Cheat sheet: normalization', 'cheat_sheet_normalization_2022', None), ('Cheat sheet: spatial smoothing', 'cheat_sheet_spatial_smoothing', None)],
    '1.9': [('Basic t-test demo with CANlab tools (MATLAB live script)', None, 'assets/guides/Basic_t_test_demo_CANlab_tools.html')],
    '2.4': [('Cheat sheet: fMRI model specification', 'cheat_sheet_fMRImodelspecification_2022', None)],
    '3.4': [('Cheat sheet: second-level t-test', 'cheat_sheet_second_level_t-test_2021', None)],
    '3.6': [('GIFT walk-through (PDF)', None, 'assets/pdf/GIFT_Walk_Through.pdf'), ('GIFT documentation', None, 'https://trendscenter.org/software/gift/')],
}

# Keywords (matched as substrings of the paper-figure concept tags) used to pull research figures into lecture pages
CONCEPTS = {
    '0.0': ['brain signatures', 'meta-analysis'], '1.1': ['psychopathy', 'physics'], '1.2': ['physics', 'k-space'],
    '1.2b': ['reproducibility'], '1.3': ['reproducibility'], '1.4': ['reproducibility', 'preprocessing'], '1.5': ['preprocessing', 'psychopathy'],
    '1.6': ['preprocessing', 'registration'], '1.7': ['preprocessing', 'registration'],
    '1.8': ['hrf', 'glm'], '1.9': ['multivariate', 'brain signatures'],
    '2.1': ['glm', 'hrf'], '2.2': ['preprocessing', 'glm'], '2.3': ['glm', 'design'],
    '2.4': ['psychopathy', 'group analysis'], '2.5': ['hrf'], '2.6': ['hrf'], '2.7': ['glm', 'multivariate'],
    '2.8': ['hrf', 'glm'], '2.9': ['mediation', 'connectivity'], '2.10': ['ica', 'resting-state'],
    '3.1': ['design', 'efficiency'], '3.2': ['group analysis', 'meta-analysis'], '3.3': ['thresholding', 'multiple comparisons'],
    '3.4': ['psychopathy', 'thresholding'], '3.5': ['dynamic connectivity', 'ica'], '3.6': ['ica', 'resting-state'],
}

# ----------------------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s, quote=True)

def slug(sid):
    return 'session-' + sid.replace('.', '-')

def lecture_url(sid, root=''):
    return f'{root}lectures/{slug(sid)}.html'

def head(title, desc, root='', page='index.html'):
    url = SITE_URL + page
    card = SITE_URL + SOCIAL_CARD
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="fMRI Acquisition and Analysis Course">
<meta property="og:image" content="{card}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(SOCIAL_ALT)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{card}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="{root}assets/img/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..600,0..100;1,9..144,300..600,0..100&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html"><img class="mark" src="{root}assets/img/mark.svg" alt=""><span><b>fMRI</b> Course</span></a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span></button>
    <nav class="nav" id="nav">
      <a href="{root}index.html">Home</a>
      <a href="{root}instructors.html">Instructors</a>
      <a href="{root}content.html">Content</a>
      <a href="{root}materials.html">Materials</a>
      <a class="cta" href="{root}enroll.html">Enroll</a>
    </nav>
  </div>
</header>
'''

def crumbs(trail, root=''):
    """Breadcrumb bar. trail: list of (label, href or None); the last item is the current page."""
    items = []
    for i, (label, href) in enumerate(trail):
        if href is None or i == len(trail) - 1:
            items.append(f'<span aria-current="page">{label}</span>')
        else:
            h = href if href.startswith(('http', '#')) else root + href
            items.append(f'<a href="{h}">{label}</a>')
    return '<nav class="crumbs" aria-label="Breadcrumb"><div class="wrap">' + '<i>/</i>'.join(items) + '</div></nav>'


def sessions_of(day):
    return [s for s in LECTURES if s['day'] == day]


def sessions_by_instructor(surname):
    return [s for s in LECTURES if surname in s['instructor']]


def session_chips(day, current=None, root=''):
    """Chip row linking every session of a day — the same-day sibling links."""
    out = []
    for s in sessions_of(day):
        cls = ' here' if s['id'] == current else ''
        title = esc(s['title'])
        if s['id'] == current:
            out.append(f'<span class="chip here" title="{title}">{esc(s["id"])} {title}</span>')
        else:
            out.append(f'<a class="chip{cls}" href="{lecture_url(s["id"], root)}" title="{title}">{esc(s["id"])} {title}</a>')
    return '<div class="chip-row">' + ''.join(out) + '</div>'


def more_links(links, root='', eyebrow='Keep exploring', heading='Where to next'):
    """A block of internal links closing a page."""
    lis = ''.join(f'<a class="more-link glow" href="{root + h if not h.startswith("http") else h}"><strong>{t}</strong><span>{d}</span>{ARROW}</a>' for t, d, h in links)
    return f'''
<section class="section-tight related">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h2 class="related-h">{heading}</h2>
    <div class="more-grid">{lis}</div>
  </div>
</section>'''


def foot(root=''):
    return f'''
<footer class="site-footer">
  <div class="wrap">
    <div>
      <strong>fMRI Acquisition and Analysis Course</strong>
      A three-day live-online course on the design, acquisition, and analysis of fMRI data with SPM, ICA, and CANlab tools.<br>
      Taught by Vince Calhoun, Kent Kiehl, and Tor Wager.
    </div>
    <div>
      <strong>Site</strong>
      <ul>
        <li><a href="{root}index.html">Home</a></li>
        <li><a href="{root}instructors.html">Instructors</a></li>
        <li><a href="{root}content.html">Content and schedule</a></li>
        <li><a href="{root}materials.html">Readings and software</a></li>
        <li><a href="{root}enroll.html">Enroll</a></li>
      </ul>
    </div>
    <div>
      <strong>The three days</strong>
      <ul>
        <li><a href="{root}content.html#day1">Day 1 — {DAY_TITLES[1]}</a></li>
        <li><a href="{root}content.html#day2">Day 2 — {DAY_TITLES[2]}</a></li>
        <li><a href="{root}content.html#day3">Day 3 — {DAY_TITLES[3]}</a></li>
        <li><a href="{root}content.html#schedule">Full three-day agenda</a></li>
      </ul>
    </div>
    <div>
      <strong>Questions</strong>
      <ul>
        <li><a href="mailto:kkiehl@mrn.org">kkiehl@mrn.org</a></li>
        <li><a href="https://sites.dartmouth.edu/canlab/training-courses/">CANlab training courses</a></li>
        <li><a href="https://github.com/torwager/mindfmricourse">Site source on GitHub</a></li>
      </ul>
    </div>
  </div>
  <div class="credits"><span>Design notes: the interactive neuron network on the home page was inspired by the node-network and particle sites showcased on <a href="https://www.awwwards.com/sites/brainit">Awwwards</a>; the pinned-image “curtain” parallax follows the pattern collected in Awwwards’ <a href="https://www.awwwards.com/websites/parallax/">parallax showcase</a>. Type: Fraunces and Inter. Built with Claude Code.</span></div>
</footer>
<script src="{root}assets/js/main.js"></script>
'''

def scroll_cue(target='#start'):
    return f'<div class="scroll-cue"><a href="{target}">Scroll down {DOWN}</a></div>'

def curtain_hero(img, eyebrow, title, lede, extra='', root='', photo=False, meta='', crumb=''):
    cls = ' photo' if photo else ''
    return f'''
<section class="curtain">
  <div class="curtain-media{cls}" data-parallax style="background-image:url('{root}{img}')">
    <div class="hero-copy page-hero">
      <div class="wrap">
        <p class="eyebrow">{eyebrow}</p>
        {meta}
        <h1>{title}</h1>
        <p class="lede">{lede}</p>
        {extra}
      </div>
    </div>
    {scroll_cue()}
  </div>
  <div class="curtain-body" id="start">
{crumb}
'''

CURTAIN_END = '\n  </div>\n</section>\n'

def figure(im, root=''):
    cap = esc(im.get('caption', ''))
    src = esc(im.get('source') or im.get('citation') or '')
    return f'<figure class="figure glow"><img src="{root}assets/img/figures/{im["file"]}" alt="{cap}" loading="lazy" width="{im.get("width","")}" height="{im.get("height","")}"><figcaption><b>{cap}.</b> {src}</figcaption></figure>'

def band(im, root=''):
    cap = esc(im.get('caption', '')); src = esc(im.get('source') or im.get('citation') or '')
    return f'<div class="band"><div class="band-img" style="background-image:url(\'{root}assets/img/figures/{im["file"]}\')"></div><div class="band-cap">{cap} — {src}</div></div>'

paper_use = {}
def pick_figures(sid, n=4):
    """Slide figures for this lecture (largest first)."""
    out = [im for im in IMAGES if im.get('lecture') == sid and im.get('role') == 'figure']
    out.sort(key=lambda im: -(im.get('width', 0) * im.get('height', 0)))
    return out[:n]

def pick_research(sid, n=2):
    """Paper figures whose concept tags contain any of this session's keywords; each figure used on at most 2 pages."""
    keys = [k.lower() for k in CONCEPTS.get(sid, [])]
    scored = []
    for im in IMAGES:
        if im['origin'] != 'papers' or im.get('role') != 'figure': continue
        tags = ' | '.join(im.get('concepts', [])).lower()
        score = sum(1 for k in keys if k in tags)
        if score and paper_use.get(im['file'], 0) < 2:
            scored.append((-score, paper_use.get(im['file'], 0), im['file'], im))
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    out = [t[3] for t in scored[:n]]
    for im in out: paper_use[im['file']] = paper_use.get(im['file'], 0) + 1
    return out

def pick_panel(day, sid):
    cands = [im for im in IMAGES if im.get('role') == 'panel' and im['file'].startswith(f'panel_day{day}')]
    cands += [im for im in IMAGES if im.get('role') == 'panel' and im['origin'] == 'papers']
    if not cands:
        cands = [im for im in IMAGES if im.get('role') == 'panel']
    if not cands: return None
    idx = sum(ord(c) for c in sid) % len(cands)
    return cands[idx]

def img_by_file(name):
    for im in IMAGES:
        if im['file'] == name: return im
    return None

def band_named(name, root=''):
    im = img_by_file(name)
    return band(im, root) if im else ''

def guide_fragment(name):
    p = f'content/guides/{name}.html'
    if not os.path.exists(p): return ''
    h = open(p).read()
    h = h.replace('../assets/img/guides/', '../assets/img/guides/')  # lecture pages live one level down
    return h

# ----------------------------------------------------------------------------- lecture pages
def lecture_page(s, prev_s, next_s):
    root = '../'
    sid = s['id']; day = s['day']
    panel = pick_panel(day, sid)
    figs = pick_figures(sid)
    hero_img = f'assets/img/figures/{panel["file"]}' if panel else {1: 'assets/img/bold-waves.svg', 2: 'assets/img/brain-dots.svg', 3: 'assets/img/lattice.svg'}[day]
    meta = f'<div class="lec-meta"><span><b><a href="{root}content.html#day{day}">Day {day}</a></b></span><span><b>Session {esc(sid)}</b></span><span><a href="{root}instructors.html">{esc(s["instructor"])}</a></span><span>{esc(s["duration"])} h</span><span>{"Hands-on session" if s["type"]=="hands-on" else "Lecture"}</span></div>'
    body = head(f'{sid} {s["title"]} — fMRI Course', s['overview'][:155], root, f'lectures/{slug(sid)}.html')
    crumb = crumbs([('Home', 'index.html'), ('Content and schedule', 'content.html'),
                    (f'Day {day}', f'content.html#day{day}'), (f'Session {esc(sid)}', None)], root)
    body += '<main>' + curtain_hero(hero_img, f'Day {day} · {DAY_TITLES[day]}', esc(s['title']), esc(s['overview']),
                                    root=root, photo=bool(panel), meta=meta, crumb=crumb)

    # At a glance
    body += '<section class="section"><div class="wrap glance">'
    body += '<div class="rv"><p class="eyebrow">Take-aways</p><ul class="takeaways">' + ''.join(f'<li>{esc(t)}</li>' for t in s.get('takeaways', [])) + '</ul></div>'
    body += '<div class="rv rv-d1"><p class="eyebrow">Key terms</p><ul class="terms">' + ''.join(f'<li>{esc(t)}</li>' for t in s.get('key_terms', [])) + '</ul>'
    if figs:
        body += '<div style="margin-top:1.4rem">' + figure(figs[0], root) + '</div>'
    body += '</div></div></section>'

    # Outline with figures / band interleaved
    secs = s.get('sections', [])
    body += '<section class="section" style="background:var(--bg-2)"><div class="wrap"><div class="section-head"><div class="rv"><p class="eyebrow">Outline</p><h2>What the session covers</h2></div></div><div class="outline">'
    fig_i = 1
    for i, sec in enumerate(secs, 1):
        body += f'<article class="osec glow rv"><h3><span class="n">{i:02d}</span><span>{esc(sec["heading"])}</span></h3><ul>' + ''.join(f'<li>{esc(p)}</li>' for p in sec['points']) + '</ul></article>'
        # after the 2nd section: a figure row; after the 4th: another
        if i in (2, 4) and fig_i < len(figs):
            row = figs[fig_i:fig_i + 2]; fig_i += len(row)
            body += f'<div class="fig-row {"two" if len(row) == 2 else ""}">' + ''.join(figure(f, root) for f in row) + '</div>'
    body += '</div></div></section>'

    # Parallax band mid-page
    if panel:
        body += band(panel, root)

    # Hands-on
    if s['type'] == 'hands-on' or s.get('hands_on') or GUIDES.get(sid):
        body += '<section class="section"><div class="wrap"><div class="section-head"><div class="rv"><p class="eyebrow">Hands-on</p><h2>Step by step</h2></div><p class="lede rv rv-d1">The walk-through below is distilled from the course cheat sheets. Data paths refer to the course Dropbox folder (e.g. <code>data/auditory_oddball</code>).</p></div>'
        if s.get('hands_on'):
            body += '<ol class="steps-list rv">' + ''.join(f'<li><span>{esc(st)}</span></li>' for st in s['hands_on']) + '</ol>'
        for label, frag, link in GUIDES.get(sid, []):
            if frag:
                body += f'<details class="cheat rv"><summary><span>{esc(label)} — full cheat sheet</span>{CHEV}</summary><div class="cheat-body">{guide_fragment(frag)}</div></details>'
            elif link:
                href = link if link.startswith('http') else root + link
                body += f'<p class="rv" style="margin-top:1.2rem"><a class="btn btn-ghost" href="{href}" target="_blank" rel="noopener">{esc(label)} {EXT}</a></p>'
        body += '</div></section>'

    # Remaining slide figures + related research figures
    rest = figs[fig_i:]
    research = pick_research(sid)
    if rest or research:
        body += '<section class="section"><div class="wrap">'
        if rest:
            body += '<div class="fig-row two">' + ''.join(figure(f, root) for f in rest[:2]) + '</div>'
        if research:
            body += '<div class="section-head" style="margin-top:2rem"><div class="rv"><p class="eyebrow">From the instructors\' research</p><h2>Related figures</h2></div><p class="lede rv rv-d1">Examples of these concepts in published work by the course instructors.</p></div>'
            body += f'<div class="fig-row {"two" if len(research) == 2 else ""}">' + ''.join(figure(f, root) for f in research) + '</div>'
        body += '</div></section>'

    # Prev / next
    body += '<section class="section-tight"><div class="wrap"><div class="lec-nav">'
    body += (f'<a href="{lecture_url(prev_s["id"])}"><small>Previous · {esc(prev_s["id"])}</small><strong>{esc(prev_s["title"])}</strong></a>' if prev_s else '<span></span>')
    body += (f'<a class="next" href="{lecture_url(next_s["id"])}"><small>Next · {esc(next_s["id"])}</small><strong>{esc(next_s["title"])}</strong></a>' if next_s else f'<a class="next" href="{root}content.html#sessions"><small>Back</small><strong>All sessions</strong></a>')
    body += '</div>'
    body += f'<div class="sibling"><p class="eyebrow">Day {day} · {DAY_TITLES[day]}</p>{session_chips(day, sid, root)}</div>'
    body += '</div></section>'
    other_days = [d for d in (1, 2, 3) if d != day]
    body += more_links([
        ('All sessions and the three-day agenda', 'Every session card, plus the hour-by-hour schedule.', 'content.html#sessions'),
        (f'Day {other_days[0]} — {DAY_TITLES[other_days[0]]}', 'The other sessions in the course.', f'content.html#day{other_days[0]}'),
        (f'Day {other_days[1]} — {DAY_TITLES[other_days[1]]}', 'The other sessions in the course.', f'content.html#day{other_days[1]}'),
        ('Readings and software', 'Background chapters, review papers, and the toolboxes used here.', 'materials.html'),
        ('Instructors', 'Vince Calhoun, Kent Kiehl, and Tor Wager.', 'instructors.html'),
        ('Enroll', f'{DATES} · live online. Reserve a space.', 'enroll.html'),
    ], root)
    body += CURTAIN_END + '</main>' + foot(root) + '</body>\n</html>\n'
    return body

# ----------------------------------------------------------------------------- content page
def session_card(s):
    kind = 'hands-on' if s['type'] == 'hands-on' else 'lecture'
    short = s['overview'].split('. ')[0].rstrip('.') + '.'
    return f'''<a class="session glow rv" href="{lecture_url(s['id'])}" data-quickview>
  <div class="meta"><b>Session {esc(s['id'])}</b><span>{esc(s['instructor'])} · {esc(s['duration'])} h</span></div>
  <h4>{esc(s['title'])}</h4>
  <p>{esc(short)}</p>
  <div class="foot"><span class="tag {kind}">{kind}</span>{ARROW}</div>
</a>'''

def agenda_day(day):
    date, rows = AGENDA[day]
    trs = ''
    for r in rows:
        if len(r) == 2:
            trs += f'<tr class="break"><td class="time">{r[0]}</td><td colspan="3">{r[1]}</td></tr>'
        else:
            t, sid, desc, who = r
            cell = f'<a href="{lecture_url(sid)}" data-quickview>{desc}</a>' if sid and sid in BY_ID else desc
            trs += f'<tr><td class="time">{t}</td><td>{sid or "—"}</td><td>{cell}</td><td class="who">{who}</td></tr>'
    return f'''
<details{" open" if day == 1 else ""}>
  <summary><span>Day {day} — {DAY_TITLES[day]} <small>· {date}</small></span>{CHEV}</summary>
  <div class="table-scroll"><table>
    <thead><tr><th>Start</th><th>Session</th><th>Topic</th><th>Instructor</th></tr></thead>
    <tbody>{trs}</tbody>
  </table></div>
</details>'''

def content_page():
    body = head('Content and Schedule — fMRI Acquisition and Analysis Course', 'Topics, sessions, and the three-day schedule for the fMRI Acquisition and Analysis Course. Click any session for a detailed outline.', '', 'content.html') + '<main>'
    daynav = ('<ul class="subnav">'
              + ''.join(f'<li><a href="#day{d}">Day {d} — {DAY_TITLES[d]}</a></li>' for d in (1, 2, 3))
              + '<li><a href="#schedule">Full agenda</a></li></ul>')
    body += curtain_hero('assets/img/bold-waves.svg', 'Content', 'Topics and schedule', 'Interactive lectures with hands-on demonstrations and work-through sessions, from MRI physics to machine learning, over three full days. Click any session for a detailed outline.',
                         daynav, crumb=crumbs([('Home', 'index.html'), ('Content and schedule', None)]))
    body += f'''
    <section class="section">
      <div class="wrap grid-2">
        <div class="rv">
          <p class="eyebrow">Audience and format</p>
          <h2>Learn by doing, on your own laptop.</h2>
        </div>
        <div class="stack rv rv-d1">
          <p>This course is designed for fMRI researchers with beginning to intermediate skill levels. For newcomers, it provides a comprehensive set of foundational tools for acquiring and analyzing fMRI data. For experienced researchers, it offers advanced training in Independent Component Analysis and optimizing the validity of your studies.</p>
          <p>The format is interactive lectures with hands-on demonstrations and work-through sessions. Participants work through examples on their own laptops. Registration is first-come, first-served, and enrollment is limited by the interactive nature of the course.</p>
          <p class="muted">Software used in the course (install instructions and a MATLAB trial are provided to attendees):</p>
          <ul class="software-chips">
            <li>MATLAB</li><li>SPM25</li><li>GIFT</li><li>CANlab Core Tools</li><li>SnPM</li><li>Mediation (M3) toolbox</li>
          </ul>
        </div>
      </div>
    </section>
    <hr class="rule">
    <section class="section" id="sessions">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Sessions</p><h2>What we cover, session by session</h2></div>
          <p class="lede rv rv-d1">Each card opens a detailed outline of the session: main concepts, key terms, take-aways, figures from the lectures, and — for hands-on sessions — step-by-step cheat sheets.</p>
        </div>'''
    day_bands = {1: 'panel_day1_a.jpg', 2: 'chang2015_pines_maps.jpg', 3: 'rashid2014_states.jpg'}
    for day in (1, 2, 3):
        cards = ''.join(session_card(s) for s in LECTURES if s['day'] == day)
        body += (f'<div class="day-block" id="day{day}"><div class="day-head"><h3>Day {day} — {DAY_TITLES[day]}</h3>'
                 f'<span>{AGENDA[day][0]} · <a href="#schedule">hour-by-hour agenda</a></span></div><div class="sessions">{cards}</div></div>')
        if day < 3:
            body += '</div></section>' + band_named(day_bands[day]) + '<section class="section"><div class="wrap">'
    body += f'''
      </div>
    </section>
    <section class="section" style="background:var(--bg-2)" id="schedule">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Schedule</p><h2>Three-day agenda</h2></div>
          <p class="lede rv rv-d1">Each day runs 8:00 am – 6:00 pm Eastern Time with breaks (Day 3 ends at 4:00 pm). <a href="{AGENDA_PDF}">Download the agenda (PDF)</a>.</p>
        </div>
        <div class="agenda rv rv-d1">{agenda_day(1)}{agenda_day(2)}{agenda_day(3)}</div>
        <p class="rv rv-d1" style="margin-top:1.4rem"><a href="#sessions">Back to the session cards {ARROW}</a></p>
      </div>
    </section>
    <section class="section">
      <div class="wrap grid-2">
        <div class="rv"><p class="eyebrow">Next step</p><h2>Ready to join us?</h2></div>
        <div class="rv rv-d1">
          <p>Spaces are limited. Reserve yours now, then browse the <a href="materials.html">background readings and software</a> to prepare. The sessions are taught by <a href="instructors.html">Vince Calhoun, Kent Kiehl, and Tor Wager</a>.</p>
          <p><a class="btn btn-amber" href="enroll.html">Reserve a space {ARROW}</a></p>
        </div>
      </div>
    </section>''' + more_links([
        ('Instructors', 'Who teaches which sessions.', 'instructors.html'),
        ('Readings and software', 'Books, chapters, review papers, and the toolboxes to install.', 'materials.html'),
        ('Enroll', f'{DATES} · live online. Trainee, faculty, and industry rates.', 'enroll.html'),
        ('Home', 'Back to the course overview.', 'index.html'),
    ])
    body += CURTAIN_END + '</main>' + foot() + '</body>\n</html>\n'
    return body

# ----------------------------------------------------------------------------- index
def index_page():
    tile_img = {}
    for key, cands in {'instructors': ['lec1-1_a.jpg'], 'content': ['panel_day2_a.jpg', 'lec2-10_a.jpg'], 'enroll': ['panel_day3_a.jpg', 'lec3-5_a.jpg']}.items():
        for c in cands:
            if os.path.exists('assets/img/figures/' + c): tile_img[key] = c; break
    def tile_media(key):
        return f'<div class="tile-media" style="background-image:url(\'assets/img/figures/{tile_img[key]}\')"></div>' if key in tile_img else ''
    body = head(f'fMRI Acquisition and Analysis Course — {DATES}, Live Online', 'A three-day live-online course on fMRI acquisition and analysis with Statistical Parametric Mapping, Independent Component Analysis, and more. Taught by Vince Calhoun, Kent Kiehl, and Tor Wager.', '', 'index.html')
    body += f'''
<main>
<section class="curtain">
  <div class="curtain-media" id="hero" style="background:linear-gradient(160deg,#faf8f4 0%,#f1f2f0 60%,#e9edf0 100%)">
    <canvas id="neurons" aria-label="Interactive network of neurons. Move your cursor over a neuron to fire it." role="img"></canvas>
    <div class="hero-copy">
      <div class="wrap">
        <div class="date-pill"><span class="dot"></span> {DATES} &nbsp;·&nbsp; Live online via Zoom</div>
        <h1>fMRI Acquisition and Analysis</h1>
        <p class="lede">A three-day, hands-on course on the design, acquisition, and analysis of neuroimaging data with Statistical Parametric Mapping, Independent Component Analysis, and more.</p>
        <div class="hero-actions">
          <a class="btn btn-amber" href="enroll.html">Reserve a space {ARROW}</a>
          <a class="btn btn-ghost" href="content.html">Topics and schedule</a>
        </div>
      </div>
    </div>
    <div class="hero-hint"><span class="pulse"></span> Hover over a neuron to fire it</div>
    {scroll_cue()}
  </div>
  <div class="curtain-body" id="start">

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <div class="rv">
            <p class="eyebrow">The course</p>
            <h2>From raw scanner signal to publishable inference, in three days.</h2>
          </div>
          <p class="lede rv rv-d1">Interactive lectures paired with hands-on demonstrations and work-through sessions on your own laptop. Built for researchers with beginning to intermediate fMRI skills, and detailed enough to challenge experienced analysts with ICA and study-validity optimization.</p>
        </div>
        <dl class="facts rv rv-d1">
          <div><dt>Dates</dt><dd>Sept 9–11, 2026</dd></div>
          <div><dt>Hours</dt><dd>8:00 am – 6:00 pm ET</dd></div>
          <div><dt>Format</dt><dd>Live online, Zoom</dd></div>
          <div><dt>Instructors</dt><dd><a href="instructors.html">Calhoun · Kiehl · Wager</a></dd></div>
        </dl>
        <ul class="subnav rv rv-d1" style="margin-top:1.8rem">
          <li><a href="content.html#day1">Day 1 — {DAY_TITLES[1]}</a></li>
          <li><a href="content.html#day2">Day 2 — {DAY_TITLES[2]}</a></li>
          <li><a href="content.html#day3">Day 3 — {DAY_TITLES[3]}</a></li>
          <li><a href="content.html#schedule">Full agenda</a></li>
        </ul>
      </div>
    </section>

    <section class="section-tight" id="explore">
      <div class="wrap">
        <div class="tiles">
          <a class="tile glow rv" href="instructors.html">
            <div>{tile_media('instructors')}<span class="num">01</span><h3>Instructors</h3><p>Vince Calhoun, Kent Kiehl, and Tor Wager — researchers who develop the methods and toolboxes used in the course and have taught fMRI methods for over 25 years.</p></div>
            <span class="go">Meet the instructors {ARROW}</span>
          </a>
          <a class="tile glow rv rv-d1" href="content.html">
            <div>{tile_media('content')}<span class="num">02</span><h3>Content</h3><p>MRI physics, study design, preprocessing, the general linear model, thresholding, connectivity and mediation, ICA with GIFT, and machine learning. Detailed outlines for every session.</p></div>
            <span class="go">Topics and schedule {ARROW}</span>
          </a>
          <a class="tile tile-enroll glow rv rv-d2" href="enroll.html">
            <div>{tile_media('enroll')}<span class="num">03</span><h3>Enroll</h3><p>Reserve a space. Enrollment is first-come, first-served and limited by the interactive nature of the course. Trainee, faculty, and industry rates.</p></div>
            <span class="go">Reserve a space {ARROW}</span>
          </a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap grid-2">
        <div class="rv">
          <p class="eyebrow">Who it's for</p>
          <h2>Foundations for beginners, depth for experienced analysts.</h2>
        </div>
        <div class="stack rv rv-d1">
          <p>This course is designed for fMRI researchers with beginning to intermediate skill levels. For newcomers, it provides a comprehensive set of foundational tools for acquiring and analyzing fMRI data. For experienced researchers, it offers advanced training in Independent Component Analysis and in optimizing the validity of your studies.</p>
          <p>You will work through examples on your own laptop with SPM, GIFT, CANlab Core Tools, SnPM, and the Mediation toolbox. No specific preparation is required — see the <a href="materials.html">background readings</a> if you would like a head start.</p>
          <p><a class="btn btn-primary" href="materials.html">Readings and software {ARROW}</a></p>
        </div>
      </div>
    </section>

    {band_named('panel_day2_a.jpg')}
    <section class="section attendee" id="attendees">
      <div class="wrap">
        <p class="eyebrow">For registered attendees</p>
        <h2>Course-day materials</h2>
        <p class="muted">Registered attendees receive everything needed for the course days by email before the course. Not registered yet? <a href="enroll.html">Reserve a space</a>, or browse the <a href="content.html#sessions">session outlines</a> and <a href="materials.html">readings and software</a>.</p>
        <div class="attendee-note rv">Before the course you will receive: a calendar invitation for the three course days, the Zoom meeting link and passcode, the link to the shared Dropbox folder with data and tools, and a MATLAB trial license. If you have registered and have not received these a week before the course, contact <a href="mailto:kkiehl@mrn.org">kkiehl@mrn.org</a>.</div>
      </div>
    </section>

  </div>
</section>
</main>
''' + foot() + '<script src="assets/js/neurons.js"></script>\n</body>\n</html>\n'
    return body

# ----------------------------------------------------------------------------- instructors
def person(img, name, role, paras, links, surname=None):
    lis = ''.join(f'<li><a href="{u}">{t} {EXT}</a></li>' for t, u in links)
    ps = ''.join(f'<p>{p}</p>' for p in paras)
    teaches = ''
    if surname:
        mine = sessions_by_instructor(surname)
        chips = ''.join(f'<a class="chip" href="{lecture_url(s["id"])}" title="{esc(s["title"])}">{esc(s["id"])} {esc(s["title"])}</a>' for s in mine)
        teaches = (f'<div class="teaches"><p class="eyebrow">Teaches {len(mine)} sessions</p><div class="chip-row">{chips}</div>'
                   f'<p class="muted" style="margin:.9rem 0 0;font-size:.9rem"><a href="content.html#sessions">See all sessions and the three-day agenda {ARROW}</a></p></div>')
    return f'''
<article class="person rv">
  <div class="portrait"><img src="assets/img/{img}" alt="{esc(name)}"></div>
  <div>
    <h3>{name}</h3>
    <p class="role">{role}</p>
    {ps}
    <ul class="links">{lis}</ul>
    {teaches}
  </div>
</article>'''

def instructors_page():
    body = head('Instructors — fMRI Acquisition and Analysis Course', 'Meet the instructors: Vince Calhoun, Kent Kiehl, and Tor Wager.', '', 'instructors.html') + '<main>'
    body += curtain_hero('assets/img/topo.svg', 'Instructors', 'Instructors', 'Vince Calhoun, Kent Kiehl, and Tor Wager.',
                         crumb=crumbs([('Home', 'index.html'), ('Instructors', None)]))
    body += f'''
    <section class="section">
      <div class="wrap group">
        <div class="group-photo rv"><img src="assets/img/instructors-group.jpg" alt="Vince Calhoun, Kent Kiehl, and Tor Wager"></div>
        <div class="rv rv-d1">
          <p class="statement">We have been doing neuroimaging research and teaching fMRI methods for over 25 years. We love interacting with students from around the world, and from different career tracks and stages.</p>
          <p class="muted">Vince Calhoun, Kent Kiehl, and Tor Wager</p>
        </div>
      </div>
    </section>
    {band_named('panel_day2_b.jpg')}
    <section class="section">
      <div class="wrap">
        {person('calhoun.jpg', 'Vince Calhoun, Ph.D.', 'Georgia State University · Georgia Institute of Technology · Emory University',
          ['Dr. Calhoun develops techniques for making sense of complex brain imaging data. His work includes algorithms that map dynamic brain networks and how they are altered by tasks and by mental illness, and he is the lead developer of the GIFT toolbox for group Independent Component Analysis.',
           'He is the founding director of the Center for Translational Research in Neuroimaging and Data Science (TReNDS), a tri-institutional center of Georgia State, Georgia Tech, and Emory.'],
          [('TReNDS Center', 'http://trendscenter.org/'), ('Publications', 'https://scholar.google.com/citations?user=WNOoGKIAAAAJ&hl=en'), ('GIFT toolbox', 'https://github.com/trendscenter/gift'), ('vcalhoun@gsu.edu', 'mailto:vcalhoun@gsu.edu')], 'Calhoun')}
        {person('kiehl.jpg', 'Kent Kiehl, Ph.D.', 'The Mind Research Network · The University of New Mexico',
          ['Dr. Kiehl is an author and neuroscientist who specializes in the use of clinical brain imaging techniques to understand major mental illnesses, with special focus on criminal psychopathy, psychotic disorders (schizophrenia, bipolar disorder, affective disorders), traumatic brain injury, substance abuse, and paraphilias.',
           'He designed the Mind Mobile MRI System for forensic research, which has collected data from over 3,000 offenders across eight facilities. He lectures widely on neuroscience and law, co-edited the <em>Handbook on Psychopathy and Law</em> (Oxford University Press, 2013), and founded the MINDSET consulting group.'],
          [('Lectures', 'https://kentkiehl.com/lectures/'), ('MINDSET consulting group', 'http://www.mindsetconsultinggroup.com/'), ('Handbook on Psychopathy and Law', 'http://www.amazon.com/Handbook-Psychopathy-Oxford-Neuroscience-Philosophy/dp/0199841381'), ('kkiehl@mrn.org', 'mailto:kkiehl@mrn.org')], 'Kiehl')}
        {person('wager.jpg', 'Tor Wager, Ph.D.', 'Diana L. Taylor Distinguished Professor in Neuroscience · Department of Psychological and Brain Sciences, Dartmouth College',
          ['Dr. Wager received his Ph.D. from the University of Michigan in 2003 and has since taught at Columbia University and the University of Colorado, Boulder. He directs the Cognitive and Affective Neuroscience laboratory, a research lab devoted to work on the neurophysiology of affective processes — pain, emotion, stress, and empathy.',
           'With Martin Lindquist he is the author of <em>Elements of Functional Magnetic Resonance Imaging</em> (MIT Press) and <em>Principles of fMRI</em>, and the lead developer of the open-source CANlab neuroimaging tools.'],
          [('CANlab', 'https://sites.dartmouth.edu/canlab/'), ('Code and tools', 'http://canlab.github.io'), ('Elements of fMRI (MIT Press)', 'https://mitpress.mit.edu/9780262045049/elements-of-functional-magnetic-resonance-imaging/'), ('torwager@gmail.com', 'mailto:torwager@gmail.com')], 'Wager')}
      </div>
    </section>''' + more_links([
        ('Content and schedule', 'The 27 sessions and the hour-by-hour agenda.', 'content.html#sessions'),
        ('Readings and software', 'Books and chapters by the instructors, plus GIFT, SPM, and CANlab tools.', 'materials.html'),
        ('Enroll', f'{DATES} · live online. Reserve a space.', 'enroll.html'),
        ('Home', 'Back to the course overview.', 'index.html'),
    ])
    body += CURTAIN_END + '</main>' + foot() + '</body>\n</html>\n'
    return body

# ----------------------------------------------------------------------------- enroll
def tier(name, price, who, url, featured=False):
    return f'''
<div class="tier glow{' featured' if featured else ''} rv">
  <h3>{name}</h3>
  <div class="price"><sup>$</sup>{price}</div>
  <p class="who">{who}</p>
  <a class="btn btn-amber" href="{url}" rel="noopener">Register as {name.lower()} {ARROW}</a>
</div>'''

def enroll_page():
    body = head('Enroll — fMRI Acquisition and Analysis Course', f'Reserve a space in the {DATES} live-online fMRI course. Trainee, faculty, and industry rates.', '', 'enroll.html') + '<main>'
    body += curtain_hero('assets/img/lattice.svg', 'Enroll', 'Reserve a space', f'{DATES} · Live online. Three days of lectures and hands-on demonstrations hosted by Dartmouth College.',
                         crumb=crumbs([('Home', 'index.html'), ('Enroll', None)]))
    body += f'''
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Registration</p><h2>Choose your rate</h2></div>
          <p class="lede rv rv-d1">Select the category that describes you. Each button opens secure checkout on PayPal, where you can pay with a PayPal account or a credit or debit card.</p>
        </div>
        <div class="tiers">
          {tier('Trainee', '715', 'Undergraduate and graduate students, post-doctoral fellows, and other trainees.', PAYPAL['trainee'], True)}
          {tier('Faculty', '950', 'K-awardees, research scientists, and assistant (or higher) professors.', PAYPAL['faculty'])}
          {tier('Industry', '1,500', 'Anyone primarily employed in a non-academic setting.', PAYPAL['industry'])}
        </div>
      </div>
    </section>
    <section class="section" style="background:var(--bg-2)">
      <div class="wrap grid-2">
        <div class="rv"><p class="eyebrow">How it works</p><h2>Three steps to enroll</h2></div>
        <ol class="steps rv rv-d1">
          <li><div><strong>Register and pay</strong>Click the button for your category above. You will be taken to a PayPal-hosted checkout page for the course fee. A receipt is emailed to you when payment completes.</div></li>
          <li><div><strong>Complete the short questionnaire</strong>After paying, please fill in the <a href="{QUESTIONNAIRE}">post-registration questionnaire</a> so we can tailor the course to attendees' backgrounds and send you the right materials.</div></li>
          <li><div><strong>Watch for course materials</strong>Before the course you will receive the calendar invitation, the Zoom link and passcode, the Dropbox link for data and tools, and a MATLAB trial license.</div></li>
        </ol>
      </div>
    </section>
    <section class="section">
      <div class="wrap grid-2">
        <div class="rv"><p class="eyebrow">Questions</p><h2>Need help?</h2></div>
        <div class="note rv rv-d1">
          <p>Enrollment is first-come, first-served and is limited by the interactive nature of the course. For questions about registration, eligibility categories, or invoices, contact <a href="mailto:kkiehl@mrn.org">kkiehl@mrn.org</a>.</p>
          <p class="muted" style="font-size:.92rem">If a payment button does not open, please make sure pop-ups are allowed for this site, or copy the link address and open it in a new tab.</p>
        </div>
      </div>
    </section>''' + more_links([
        ('Content and schedule', 'What you get: 27 sessions over three days, with detailed outlines.', 'content.html#sessions'),
        ('Instructors', 'Vince Calhoun, Kent Kiehl, and Tor Wager.', 'instructors.html'),
        ('Readings and software', 'Prepare with the background chapters and install the toolboxes.', 'materials.html'),
        ('Home', 'Back to the course overview.', 'index.html'),
    ], eyebrow='Before you register', heading='Have a look around first')
    body += CURTAIN_END + '</main>' + foot() + '</body>\n</html>\n'
    return body

# ----------------------------------------------------------------------------- materials
def reading(title, cite, links):
    """links: list of (label, url)"""
    a = ''.join(f'<a class="pdf" href="{u}" rel="noopener">{PDF_ICON} {l}</a>' for l, u in links)
    return f'<li><div><div class="title">{title}</div><div class="cite">{cite}</div></div><span class="pdf-links">{a}</span></li>'

def sw(name, tag, desc, links, sessions=()):
    lis = ''.join(f'<li><a href="{u}" rel="noopener">{t} {EXT}</a></li>' for t, u in links)
    used = ''
    if sessions:
        chips = ''.join(f'<a class="chip" href="{lecture_url(sid)}" title="{esc(BY_ID[sid]["title"])}">{esc(sid)} {esc(BY_ID[sid]["title"])}</a>' for sid in sessions if sid in BY_ID)
        used = f'<div class="used-in"><p class="eyebrow">Used in</p><div class="chip-row">{chips}</div></div>'
    return f'<div class="sw glow rv"><h3>{name} <small>{tag}</small></h3><p>{desc}</p><ul>{lis}</ul>{used}</div>'

def materials_page():
    chapters = ''.join([
        reading('Fundamentals of functional neuroimaging', 'Geuter, S., Lindquist, M. A., &amp; Wager, T. D. (2017). In <em>Handbook of Psychophysiology</em> (4th ed.). Cambridge University Press.', [('PDF', 'assets/pdf/Geuter_2017_Fundamentals_of_functional_neuroimaging.pdf')]),
        reading('Principles of functional magnetic resonance imaging', 'Lindquist, M. A., &amp; Wager, T. D. (2014). In <em>Handbook of Neuroimaging Data Analysis</em> (pp. 3–48). Chapman &amp; Hall / CRC.', [('PDF', 'assets/pdf/Lindquist_Wager_2014_Principles_of_fMRI.pdf')]),
        reading('Essentials of functional magnetic resonance imaging', 'Wager, T. D., &amp; Lindquist, M. A. (2011). In <em>The Oxford Handbook of Social Neuroscience</em>. Oxford University Press.', [('PDF', 'assets/pdf/Wager_Lindquist_2011_Essentials_of_fMRI.pdf'), ('Publisher', 'https://doi.org/10.1093/oxfordhb/9780195342161.013.0006')]),
        reading('Essentials of functional neuroimaging', 'Wager, T. D., Lindquist, M. A., &amp; Hernandez, L. (2009). In <em>Handbook of Neuroscience for the Behavioral Sciences</em>. Wiley.', [('PDF', 'assets/pdf/Wager_2009_Essentials_of_functional_neuroimaging.pdf')]),
        reading('Elements of functional neuroimaging', 'Wager, T. D., Hernandez, L., Jonides, J., &amp; Lindquist, M. A. (2007). In <em>Handbook of Psychophysiology</em> (3rd ed., pp. 19–55). Cambridge University Press.', [('PDF', 'assets/pdf/Wager_2007_Elements_of_functional_neuroimaging.pdf')]),
    ])
    reviews = ''.join([
        reading('Multisubject independent component analysis of fMRI: a decade of intrinsic networks, default mode, and neurodiagnostic discovery', 'Calhoun, V. D., &amp; Adalı, T. (2012). <em>IEEE Reviews in Biomedical Engineering</em>, 5, 60–73.', [('Full text', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4433055/')]),
        reading('Comparison of multi-subject ICA methods for analysis of fMRI data', 'Erhardt, E. B., Rachakonda, S., Bedrick, E. J., Allen, E. A., Adalı, T., &amp; Calhoun, V. D. (2011). <em>Human Brain Mapping</em>, 32, 2075–2095.', [('PDF', 'assets/pdf/Erhardt_2011_Comparison_of_multisubject_ICA.pdf'), ('PMC', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3117074/')]),
        reading('The chronnectome: time-varying connectivity networks as the next frontier in fMRI data discovery', 'Calhoun, V. D., Miller, R., Pearlson, G., &amp; Adalı, T. (2014). <em>Neuron</em>, 84, 262–274.', [('PDF', 'assets/pdf/Calhoun_2014_Chronnectome.pdf'), ('PMC', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4372723/')]),
        reading('A review of group ICA for fMRI data and ICA for joint inference of imaging, genetic, and ERP data', 'Calhoun, V. D., Liu, J., &amp; Adalı, T. (2009). <em>NeuroImage</em>, 45, S163–S172.', [('PDF', 'assets/pdf/Calhoun_2009_Review_of_group_ICA.pdf'), ('PMC', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2651152/')]),
        reading('The statistical analysis of fMRI data', 'Lindquist, M. A. (2008). <em>Statistical Science</em>, 23, 439–464.', [('Full text', 'https://arxiv.org/abs/0906.3662')]),
        reading('Zen and the art of multiple comparisons', 'Lindquist, M. A., &amp; Mejia, A. (2015). <em>Psychosomatic Medicine</em>, 77, 114–125.', [('Full text', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4333023/')]),
        reading('Best practices in data analysis and sharing in neuroimaging using MRI', 'Nichols, T. E., Das, S., Eickhoff, S. B., et al. (2017). <em>Nature Neuroscience</em>, 20, 299–303.', [('Full text', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5685169/')]),
        reading('Building better biomarkers: brain models in translational neuroimaging', 'Woo, C.-W., Chang, L. J., Lindquist, M. A., &amp; Wager, T. D. (2017). <em>Nature Neuroscience</em>, 20, 365–377.', [('PDF', 'assets/pdf/Woo_2017_Building_better_biomarkers.pdf'), ('PMC', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5988350/')]),
        reading('Representation, pattern information, and brain signatures: from neurons to neuroimaging', 'Kragel, P. A., Koban, L., Barrett, L. F., &amp; Wager, T. D. (2018). <em>Neuron</em>, 99, 257–273.', [('PDF', 'assets/pdf/Kragel_2018_Brain_signatures.pdf'), ('PMC', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6296466/')]),
    ])
    software = ''.join([
        sw('SPM25', 'Statistical Parametric Mapping', 'The core package used throughout the course for preprocessing, GLM estimation, and inference. SPM 25 runs in MATLAB; a standalone build that does not need a MATLAB license is also available.',
           [('SPM website', 'https://www.fil.ion.ucl.ac.uk/spm/'), ('Download (GitHub releases)', 'https://github.com/spm/spm/releases/latest'), ('Installation guide', 'https://www.fil.ion.ucl.ac.uk/spm/docs/installation/'), ('Documentation', 'https://www.fil.ion.ucl.ac.uk/spm/docs/'), ('SPM courses', 'https://www.fil.ion.ucl.ac.uk/spm/docs/courses/'), ('SPM 25 paper', 'https://arxiv.org/abs/2501.12081')], ['1.2b', '1.5', '1.6', '1.7', '2.4', '3.4']),
        sw('GIFT', 'Group ICA of fMRI Toolbox', "Vince Calhoun's MATLAB toolbox for group ICA and IVA, including dynamic functional network connectivity, constrained ICA with the NeuroMark template, and source-based morphometry. Requires only base MATLAB.",
           [('GitHub (trendscenter/gift)', 'https://github.com/trendscenter/gift'), ('Releases', 'https://github.com/trendscenter/gift/releases'), ('GIFT at TReNDS', 'https://trendscenter.org/software/gift/'), ('Docker / Nipype build', 'https://github.com/trendscenter/aa-gift')], ['2.10', '3.5', '3.6']),
        sw('CANlab tools', 'Cognitive and Affective Neuroscience Lab', "Tor Wager's object-oriented MATLAB tools for interactive analysis and visualization of neuroimaging data, plus repositories of brain signature patterns and atlases, robust regression, and multilevel mediation. Core Tools and Neuroimaging Pattern Masks are meant to be installed together.",
           [('canlab.github.io', 'https://canlab.github.io/'), ('CanlabCore', 'https://github.com/canlab/CanlabCore'), ('Neuroimaging_Pattern_Masks', 'https://github.com/canlab/Neuroimaging_Pattern_Masks'), ('RobustToolbox (robust regression)', 'https://github.com/canlab/RobustToolbox'), ('MediationToolbox (multilevel mediation)', 'https://github.com/canlab/MediationToolbox'), ('Installing the tools', 'https://canlab.github.io/_pages/canlab_help_1_installing_tools/canlab_help_1_installing_tools.html'), ('Help and examples', 'https://github.com/canlab/CANlab_help_examples')], ['1.4', '1.9', '2.9']),
        sw('SnPM', 'Statistical nonParametric Mapping', 'Permutation-based inference for SPM by Tom Nichols and Andrew Holmes. SnPM13 runs inside the SPM batch system and provides voxel- and cluster-level nonparametric multiple-comparison correction.',
           [('SnPM13 (NISOx)', 'https://www.nisox.org/Software/SnPM13/'), ('Manual', 'https://www.nisox.org/Software/SnPM13/man'), ('GitHub (SnPM-toolbox)', 'https://github.com/SnPM-toolbox/SnPM-devel'), ('NITRC page', 'https://www.nitrc.org/projects/snpm/')], ['3.3']),
        sw('FSL randomise', 'Permutation inference in FSL', "FSL's command-line tool for nonparametric permutation inference, including threshold-free cluster enhancement (TFCE). A useful complement to SnPM if you work in the FSL ecosystem.",
           [('randomise documentation', 'https://fsl.fmrib.ox.ac.uk/fsl/docs/statistics/randomise.html'), ('FSL', 'https://fsl.fmrib.ox.ac.uk/fsl/docs/')], ['3.3']),
        sw('MATLAB', 'Required for SPM, GIFT, CANlab, SnPM', 'The course toolboxes run in MATLAB. Registered attendees receive a trial license before the course; many universities also provide MATLAB through campus-wide licenses.',
           [('MATLAB trial', 'https://www.mathworks.com/campaigns/products/trials.html'), ('Get MATLAB', 'https://www.mathworks.com/products/get-matlab.html')], ['1.3', '1.2b']),
    ])
    websites = ''.join(f'<li><a href="{u}" rel="noopener">{t} {EXT}</a></li>' for t, u in [
        ('Functional MRI 1 (Coursera) — Lindquist and Wager', 'https://www.coursera.org/learn/functional-mri'),
        ('Functional MRI 2 (Coursera) — Lindquist and Wager', 'https://www.coursera.org/learn/functional-mri-2'),
        ('fMRI 1 lectures on YouTube', 'https://www.youtube.com/watch?v=ZL-Tr1KSMKY&list=PLcvMDPDk-dSmTBejANv7kY2mFo1ni_gkA'),
        ('fMRI for Newbies (Culham Lab)', 'http://culhamlab.ssc.uwo.ca/fmri4newbies/'),
        ('SPM documentation', 'http://www.fil.ion.ucl.ac.uk/spm/doc/'),
        ('SPM course materials', 'http://www.fil.ion.ucl.ac.uk/spm/course/'),
        ('MRC CBU: SPM statistics', 'http://www.mrc-cbu.cam.ac.uk/Imaging/Common/spmstats.shtml'),
        ('MRC CBU: design efficiency', 'http://www.mrc-cbu.cam.ac.uk/Imaging/Common/fMRI-efficiency.shtml'),
        ('GIFT publications', 'http://mialab.mrn.org/software/gift/publications.html'),
        ('CANlab training courses and suggested readings', 'https://sites.dartmouth.edu/canlab/training-courses/'),
    ])
    body = head('Materials — Readings and Software — fMRI Acquisition and Analysis Course', 'Background readings (books, chapters, review articles), online courses, and software for the fMRI course: SPM25, GIFT, CANlab tools, SnPM, FSL randomise.', '', 'materials.html') + '<main>'
    body += curtain_hero('assets/img/brain-dots.svg', 'Materials', 'Readings and software',
        'No specific preparation is required — the course is designed as an introduction to fMRI. If you would like a head start, begin with the books and chapters below and install the software before day one.',
        '<ul class="subnav"><li><a href="#books">Books</a></li><li><a href="#chapters">Chapters</a></li><li><a href="#reviews">Review articles</a></li><li><a href="#courses">Online courses and sites</a></li><li><a href="#software">Software</a></li></ul>',
        crumb=crumbs([('Home', 'index.html'), ('Readings and software', None)]))
    body += f'''
    <section class="section" id="books">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Books</p><h2>Start here</h2></div>
          <p class="lede rv rv-d1">Two textbooks by course instructor Tor Wager and Martin Lindquist that cover the concepts taught in the course, from acquisition to inference.</p>
        </div>
        <div class="books">
          <article class="book primary glow rv">
            <a href="https://mitpress.mit.edu/9780262045049/elements-of-functional-magnetic-resonance-imaging/" rel="noopener"><img src="assets/img/elements-of-fmri-cover.jpg" alt="Cover of Elements of Functional Magnetic Resonance Imaging" width="389" height="500"></a>
            <div>
              <span class="badge">New · MIT Press</span>
              <h3>Elements of Functional Magnetic Resonance Imaging</h3>
              <p class="by">Tor D. Wager &amp; Martin A. Lindquist</p>
              <p>A comprehensive, current treatment of fMRI — physics and acquisition, experimental design, preprocessing, the general linear model, group analysis and multiple comparisons, connectivity, and multivariate prediction. The closest companion to what we teach.</p>
              <a class="btn btn-primary" href="https://mitpress.mit.edu/9780262045049/elements-of-functional-magnetic-resonance-imaging/" rel="noopener">View at MIT Press {ARROW}</a>
            </div>
          </article>
          <article class="book glow rv rv-d1">
            <a href="https://leanpub.com/principlesoffmri" rel="noopener"><img src="assets/img/principles-of-fmri-cover.jpg" alt="Cover of Principles of fMRI" width="320" height="427"></a>
            <div>
              <span class="badge">Leanpub</span>
              <h3>Principles of fMRI</h3>
              <p class="by">Tor D. Wager &amp; Martin A. Lindquist</p>
              <p>The earlier e-book that provides comprehensive coverage of the key concepts involved in fMRI acquisition and analysis. Concise and readable — a good first pass before the course.</p>
              <a class="btn btn-ghost" href="https://leanpub.com/principlesoffmri" rel="noopener">Get it on Leanpub {ARROW}</a>
            </div>
          </article>
        </div>
      </div>
    </section>
    <section class="section" id="chapters" style="background:var(--bg-2)">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Methods chapters</p><h2>Handbook chapters</h2></div>
          <p class="lede rv rv-d1">Comprehensive chapters by the instructors that cover many aspects of fMRI analysis. They overlap in their core material, but each has some different sections and topics, so it is worth skimming more than one. The 2017 and 2014 chapters are the most recent starting points.</p>
        </div>
        <ul class="reading-list rv rv-d1">{chapters}</ul>
      </div>
    </section>
    <section class="section" id="reviews">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Review articles</p><h2>Key papers</h2></div>
          <p class="lede rv rv-d1">Peer-reviewed reviews on ICA, statistical inference, reproducibility, and brain signatures. Links go to the full text (PDF, PubMed Central, or arXiv).</p>
        </div>
        <ul class="reading-list rv rv-d1">{reviews}</ul>
      </div>
    </section>
    <section class="section" id="courses" style="background:var(--bg-2)">
      <div class="wrap grid-2">
        <div class="rv"><p class="eyebrow">Online courses and websites</p><h2>Go deeper</h2><p class="muted">Free video courses by Martin Lindquist and Tor Wager, plus reference sites for SPM, GIFT, and study design.</p></div>
        <ul class="links rv rv-d1" style="margin-top:0">{websites}</ul>
      </div>
    </section>
    {band_named('panel_day3_a.jpg')}
    <section class="section" id="software">
      <div class="wrap">
        <div class="section-head">
          <div class="rv"><p class="eyebrow">Software</p><h2>Install before day one</h2></div>
          <p class="lede rv rv-d1">All course toolboxes are free and open source. Registered attendees receive sample datasets, walkthrough cheat sheets, short demonstration videos, and a MATLAB trial license.</p>
        </div>
        <div class="sw-grid">{software}</div>
      </div>
    </section>''' + more_links([
        ('Content and schedule', 'Where each toolbox and topic appears in the three days.', 'content.html#sessions'),
        ('Instructors', 'The authors of several of the readings above.', 'instructors.html'),
        ('Enroll', f'{DATES} · live online. Reserve a space.', 'enroll.html'),
        ('Home', 'Back to the course overview.', 'index.html'),
    ])
    body += CURTAIN_END + '</main>' + foot() + '</body>\n</html>\n'
    return body

# ----------------------------------------------------------------------------- build
def main():
    os.makedirs('lectures', exist_ok=True)
    pages = {'index.html': index_page(), 'instructors.html': instructors_page(), 'content.html': content_page(), 'enroll.html': enroll_page(), 'materials.html': materials_page()}
    for name, htmltext in pages.items():
        open(name, 'w').write(htmltext)
    for i, s in enumerate(LECTURES):
        prev_s = LECTURES[i - 1] if i > 0 else None
        next_s = LECTURES[i + 1] if i + 1 < len(LECTURES) else None
        open(f'lectures/{slug(s["id"])}.html', 'w').write(lecture_page(s, prev_s, next_s))
    print(f'wrote {len(pages)} pages + {len(LECTURES)} lecture pages; {len(IMAGES)} images indexed')

if __name__ == '__main__':
    main()
