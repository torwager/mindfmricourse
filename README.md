# fMRI Acquisition and Analysis Course — website

Static site for the 3-day live-online fMRI course taught by Vince Calhoun, Kent Kiehl, and Tor Wager.
Published with GitHub Pages from the `main` branch: **https://torwager.github.io/mindfmricourse/**

## Structure

| File | Purpose |
| --- | --- |
| `index.html` | Home — interactive neuron-network hero, three feature tiles, attendee links |
| `instructors.html` | Instructor profiles |
| `content.html` | Audience, format, topics, sample three-day agenda |
| `enroll.html` | Registration tiers with PayPal pay-links, post-registration questionnaire |
| `materials.html` | Background readings (books, review articles, chapters), online courses, software |
| `assets/css/style.css` | All styles (design tokens at the top) |
| `assets/js/neurons.js` | Canvas animation for the home hero |
| `assets/js/main.js` | Header, mobile nav, scroll-reveal, parallax drift |
| `assets/img/` | Photos, book covers, generated SVG artwork |

No build step. Edit the HTML and push to `main`; GitHub Pages redeploys within a minute or two.

## Common edits

* **Dates / price / links** — search for `September 9` and `paypal.com/ncp/payment` across the HTML files.
  The PayPal pay-links live in `enroll.html` (one per tier) and in the header/hero buttons.
* **Attendee-only links** (calendar, Dropbox, Zoom) — `index.html`, section `#attendees`.
* **Agenda** — `content.html`, the `<details>` blocks inside `.agenda`.
* **Readings / software** — `materials.html`.

## PayPal registration

Each "Register" button is a PayPal *No-Code Checkout pay-link* (`https://www.paypal.com/ncp/payment/<ID>`).
Clicking it opens a PayPal-hosted checkout page for that product; buyers pay with PayPal or a card, and the
payment lands in the course's PayPal business account. Product name, price, and quantity are managed in
PayPal (Business → Pay Links and Buttons) — changing them there updates the checkout without touching this site.
