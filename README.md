# fMRI Acquisition and Analysis Course — website

Static site for the 3-day live-online fMRI course taught by Vince Calhoun, Kent Kiehl, and Tor Wager.
Published with GitHub Pages from the `main` branch: **https://torwager.github.io/mindfmricourse/**

## How the site is built

The HTML pages are **generated** by `tools/build_site.py` from the content folder. Edit the sources, run the
build, commit, push:

```bash
python3 tools/build_site.py      # regenerates index/instructors/content/enroll/materials + lectures/*.html
git add -A && git commit -m "..." && git push
```

| Path | What it is |
| --- | --- |
| `tools/build_site.py` | The generator. Page copy (home, instructors bios, enroll, materials lists), the 2026 agenda table, and the cheat-sheet ↔ session mapping live at the top of this file. |
| `content/lectures/day1.json` … `day3.json` | One entry per session: title, instructor, duration, overview, outline sections, key terms, take-aways, hands-on steps. Distilled from the lecture slides. Edit these to change a lecture page. |
| `content/images/slides.json`, `papers.json` | Figure index: file, caption, source/citation, which session (slides) or concept tags (papers). Images live in `assets/img/figures/`. |
| `content/guides/*.html` | Cheat sheets converted from the course .docx files (pandoc); embedded in the hands-on sessions. |
| `assets/pdf/` | Chapters, review papers, the agenda, and the GIFT walk-through, linked from Materials and lecture pages. |
| `assets/css/style.css` | All styles; design tokens at the top. `.glow` gives any card the running-light border. |
| `assets/js/neurons.js` | The interactive neuron network on the home page. |
| `assets/js/main.js` | Header, mobile nav, scroll reveal, parallax bands, scroll cue, and the session quick-view popup. |

No build tools other than Python 3 are required. Do not hand-edit the generated `*.html` files — changes will be overwritten on the next build.

## Common edits

* **Dates / prices / PayPal links** — constants at the top of `tools/build_site.py` (`DATES`, `PAYPAL`, `QUESTIONNAIRE`).
* **Agenda** — the `AGENDA` table in `tools/build_site.py`.
* **A lecture's outline** — the matching entry in `content/lectures/dayN.json`.
* **Add or swap a figure** — drop the JPEG in `assets/img/figures/` and add an entry to `content/images/slides.json` (with `"lecture": "2.3"`) or `papers.json` (with concept tags).
* **Readings / software** — `materials_page()` in `tools/build_site.py`.

## PayPal registration

Each "Register" button is a PayPal *No-Code Checkout pay-link* (`https://www.paypal.com/ncp/payment/<ID>`).
Clicking it opens a PayPal-hosted checkout page for that product; buyers pay with PayPal or a card, and the
payment lands in the course's PayPal business account. Product name, price, and quantity are managed in
PayPal (Business → Pay Links and Buttons) — changing them there updates the checkout without touching this site.
