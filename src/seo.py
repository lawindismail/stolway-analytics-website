"""Search-engine helpers shared by stolway.com and stolwayanalytics.com.

THIS FILE IS IDENTICAL IN BOTH REPOSITORIES (stolway-website and stolway-analytics-website),
like assets/css/site.css. Change it in one, copy it to the other, rebuild both.

What it does:
  organization()  schema.org Organization for the company, with every office as a location
  website()       schema.org WebSite for the home page
  video()         schema.org VideoObject for a product film
  og_image()      makes the 1200 x 630 JPEG shown when a page is shared (LinkedIn, Teams, WhatsApp...)
  sitemap()       sitemap.xml with the main picture of each page, leaving out pages marked noindex
  robots_meta()   the robots tag for a page
"""
import json, os
from xml.sax.saxutils import escape

ROBOTS_INDEX = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"


def robots_meta(page):
    """noindex for the 404 page and anything marked noindex (e.g. products with no details yet)."""
    return "noindex, follow" if page.get("noindex") or page["path"] == "/404.html" else ROBOTS_INDEX


def _address(lines, country):
    return {"@type": "PostalAddress", "streetAddress": ", ".join(lines[:-1]), "addressCountry": country}


def organization(site_url, name, description, logo, email, telephone, offices, founding=None, legal_name=None,
                 parent=None, sub=None, knows_about=None):
    """offices: dicts with city, entity, lines, phone, email, geo (lat, lon), country (2 letters), street, locality, region, postcode."""
    org = {
        "@type": "Organization", "@id": site_url + "/#organization", "name": name, "url": site_url + "/",
        "logo": {"@type": "ImageObject", "url": site_url + logo, "width": 512, "height": 512},
        "description": description, "email": email, "telephone": telephone,
        "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "telephone": telephone, "email": email,
                          "availableLanguage": ["en"], "areaServed": "Worldwide"}],
    }
    if legal_name: org["legalName"] = legal_name
    if founding: org["foundingDate"] = founding
    if knows_about: org["knowsAbout"] = knows_about
    hq = offices[0]
    org["address"] = {"@type": "PostalAddress", "streetAddress": hq["street"], "addressLocality": hq["locality"],
                      "addressRegion": hq.get("region", ""), "postalCode": hq.get("postcode", ""), "addressCountry": hq["country"]}
    org["location"] = []
    for o in offices:
        place = {"@type": "Place", "name": f'{o["entity"]} ({o["city"]})',
                 "address": {"@type": "PostalAddress", "streetAddress": o["street"], "addressLocality": o["locality"],
                             "addressCountry": o["country"]},
                 "geo": {"@type": "GeoCoordinates", "latitude": o["geo"][0], "longitude": o["geo"][1]}}
        if o.get("region"): place["address"]["addressRegion"] = o["region"]
        if o.get("postcode"): place["address"]["postalCode"] = o["postcode"]
        if o.get("phone"): place["telephone"] = o["phone"]
        org["location"].append(place)
    if parent: org["parentOrganization"] = {"@type": "Organization", "@id": parent[1] + "#organization", "name": parent[0], "url": parent[1]}
    if sub: org["subOrganization"] = {"@type": "Organization", "@id": sub[1] + "#organization", "name": sub[0], "url": sub[1]}
    return org


def website(site_url, name, description):
    return {"@type": "WebSite", "@id": site_url + "/#website", "url": site_url + "/", "name": name,
            "description": description, "inLanguage": "en-AU", "publisher": {"@id": site_url + "/#organization"}}


def video(site_url, name, description, file, upload_date, seconds):
    return {"@type": "VideoObject", "name": name, "description": description,
            "thumbnailUrl": f"{site_url}/assets/video/{file}-poster.webp",
            "contentUrl": f"{site_url}/assets/video/{file}.mp4", "uploadDate": upload_date,
            "duration": f"PT{seconds // 60}M{seconds % 60}S", "publisher": {"@id": site_url + "/#organization"}}


def ld(*objs):
    """One JSON-LD block (a @graph) from any number of schema.org objects."""
    return json.dumps({"@context": "https://schema.org", "@graph": list(objs)}, ensure_ascii=False)


def og_image(name, img_dir, images, out_dir, contain=False):
    """Make out_dir/<name>.jpg (1200 x 630) from the largest WebP of picture `name` in img_dir.
    contain=True keeps the whole picture (product cut-outs) on its own background colour; otherwise it fills the frame.
    Skips the work if the file already exists. Returns False if the picture can't be found."""
    out = os.path.join(out_dir, name + ".jpg")
    if os.path.exists(out):
        return True
    info = images.get(name)
    if not info:
        return False
    src = os.path.join(img_dir, f"{name}-{info['widths'][-1]}.webp")
    if not os.path.exists(src):
        return False
    from PIL import Image
    im = Image.open(src).convert("RGB")
    W, H = 1200, 630
    if contain:
        ground = im.getpixel((2, 2))
        from PIL import ImageChops   # trim the empty margin around the product first
        box = ImageChops.difference(im, Image.new("RGB", im.size, ground)).convert("L").point(lambda v: 255 if v > 18 else 0).getbbox()
        if box:
            pad = 24
            im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
        k = min(W * 0.9 / im.width, H * 0.9 / im.height)
        r = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        canvas = Image.new("RGB", (W, H), ground)
        canvas.paste(r, ((W - r.width) // 2, (H - r.height) // 2))
    else:
        k = max(W / im.width, H / im.height)
        r = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        x, y = (r.width - W) // 2, (r.height - H) // 2
        canvas = r.crop((x, y, x + W, y + H))
    os.makedirs(out_dir, exist_ok=True)
    canvas.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    return True


def sitemap(site_url, pages, lastmod, clean_url):
    """pages: the PAGES list. Each page may carry 'og_url' (its main picture) and 'og_alt'."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for pg in pages:
        if pg["path"] == "/404.html" or pg.get("noindex"):
            continue
        out.append(f"  <url><loc>{site_url + clean_url(pg['path'])}</loc><lastmod>{lastmod}</lastmod>")
        if pg.get("og_image") and pg.get("og_url"):   # only a page's own picture, not the generic brand image
            out.append(f"    <image:image><image:loc>{escape(pg['og_url'])}</image:loc></image:image>")
        out.append("  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"
