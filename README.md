# Stolway Analytics website

The static website for stolwayanalytics.com: 21 pages of plain HTML, CSS and a little JavaScript. It shares its design, build script and components with the stolway.com website, so the two sites look like one company.

## What's in here

- `site/`: the finished website. This folder is what Cloudflare publishes.
- `src/`: the source.
  - `src/content/products.json`: every product (text, key figures, specification table, certificates, pictures).
  - `src/build.py`: everything else (menu, product groups, home page banners, technologies, resources, offices, page titles).
  - `src/templates/`: page layouts. `src/static/`: styles, scripts, fonts, logos.
  - `src/sources/img/`: original product pictures. `src/images.py` turns them into the WebP files the site uses.

## Changing the site

1. Edit the content, then run `python3 src/build.py` (needs Python with `jinja2`; add `--images` after changing pictures, which needs `Pillow`).
2. Preview with `python3 src/preview.py` and open http://localhost:8000.
3. Commit to the `preview` branch and push. Cloudflare builds a private preview link.
4. When it looks right, merge `preview` into `main`. Cloudflare publishes `main` to the live site.

## Design language (shared with the other Stolway site)

stolway.com and stolwayanalytics.com use one stylesheet, `src/static/assets/css/site.css`, and it is **identical in both repositories**. Change it in one, copy it to the other, and rebuild both. The same goes for `src/static/assets/js/site.js` and `globe.js`. The last block in the stylesheet (v21) sets the rules both sites follow:

- **Media cards** are links with a picture (systems, products, applications, product groups, projects): the picture sits on a light grey ground, then a small-caps navy label, a navy title, a short line of text and a small-caps red link such as "Explore". They lift slightly on hover.
- **Info tiles** are not links (services, use cases, industries, values, steps, reasons): white, with a navy rule along the top and a red "01" number or an icon above the title. They don't move on hover.
- **Dark tiles** sit on navy sections (timeline, technologies, mission and vision, certificates): a faint white panel with a coral number.
- **Headings:** section and split headings are Title Case with the last part in red (coral on navy), for example `Factory Testing, Installation <span class="accent">& Commissioning</span>`. Callouts, forms and calls to action are sentence-case questions or statements in one colour.
- **Eyebrows** (small caps above a heading) are red on white and grey backgrounds, and coral on navy.
- **Text links** are small caps with an arrow, red on light backgrounds and coral on navy.
- **Corners:** 12px for cards, tiles and pictures; 16px for large panels; buttons and tags are pills.
- **Page endings:** every page ends with the full-width call-to-action band (`cta.html`), with its own wording where it helps.

## Spelling

The site uses "analyser". Page descriptions mention "analyzer" once so both spellings are found in search. To switch the whole site to "analyzer", change `SPELLING` at the top of `src/build.py` and rebuild.

## Still to be supplied (shown as "TBD" on the site)

| Product | What is missing |
|---|---|
| Liquid Analyser STL800 | Everything: description, specification, photo |
| Liquid Analyser STC800 | Everything: description, specification, photo |
| Water Cut Meter | Everything: description, specification, photo |
| ST CEMS-5000C | Full description and specification table |
| ST DMS-300 | Specification table |
| AP5-TFS | Product photo |
| Level Profiler | Product photo. The text came from the old website: confirm it is still current |

To fill one in, edit its entry in `src/content/products.json`, set `"tbd": false`, drop the photo into `src/sources/img/` and list it under `"images"`, then run `python3 src/build.py --images`.

## Before go-live checklist

1. **Connect the enquiry form.** Until then, "Send enquiry" opens the visitor's email app with the enquiry written out. To connect it, create a form at formspree.io (or similar) and rebuild with `python3 src/build.py --endpoint https://formspree.io/f/YOUR_ID`.
2. **Keep the offices in step with stolway.com.** `OFFICES` and the top-bar phone and email in `src/build.py` match the stolway.com website; change both sites together.
3. **Have the privacy policy approved.** It is adapted from the stolway.com policy.
4. **Point the domain at Cloudflare.** Old WordPress addresses (`/index.php/...`) redirect to the new pages through `site/_redirects`.

## Do not commit the hosting backup

The cPanel backup of the old site contains SSL private keys, mailboxes and password files. Only this source belongs in the repository.
