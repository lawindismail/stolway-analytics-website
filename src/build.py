#!/usr/bin/env python3
"""Build the Stolway Analytics static website.

Usage:  python3 src/build.py [--endpoint https://formspree.io/f/xxxx] [--images]
Writes the finished website into ./site.
--images also re-creates the WebP pictures from src/sources/img (needs Pillow).

Where the content lives:
  src/content/products.json   every product: text, key figures, specification table, certificates, pictures
  this file                   everything else: menu, product groups, home page banners, technologies,
                              resources (Ex marking guide, standards, glossary), offices, page titles
Pages are written as about.html etc. but every link and the sitemap use clean addresses
(/about, /products/st-line-laser). Preview locally with src/preview.py.
"""
import json, os, re, sys, datetime
import seo
from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "site")

# Spelling used across the whole site: "analyser" (Australian, matches stolway.com) or "analyzer" (American).
# Change this one word and rebuild to switch every page. Page descriptions always mention the other spelling
# once, so people searching either way can find the site.
SPELLING = "analyser"

# Form handler. Leave empty until a form service is connected (see README).
FORM_ENDPOINT = ""
if "--endpoint" in sys.argv:
    FORM_ENDPOINT = sys.argv[sys.argv.index("--endpoint") + 1]

TODAY = datetime.date.today()
SITE = {
    "url": "https://stolwayanalytics.com",
    "name": "Stolway Analytics",
    "parent_url": "https://stolway.com/",
    "careers_url": "https://stolway.com/careers",   # Careers in the top bar goes to the main Stolway website
    "phone": "+61 2 4262 3000",           # shown in the top bar, menu and footer
    "email": "info@stolway.com.au",       # shown in the top bar, menu and footer; enquiries go here until a form service is connected
    "year": TODAY.year,
    "version": "",   # set in build(): a fingerprint of the CSS and JS, so browsers fetch new copies whenever either changes
    "updated": TODAY.strftime("%-d %B %Y"),
    "form_endpoint": FORM_ENDPOINT,
}

# Top navigation. Order = order on screen. The logo is the Home link, and "Request a Quote" is the button at the end.
# "mega": the wide panel listing every product by group. "mobile_only": shown in the phone menu only. "external": a link to another website.
NAV = [
    {"label": "Home", "href": "index.html", "mobile_only": True},
    {"label": "Products", "href": "products.html", "section": "products", "mega": True},
    {"label": "Technology", "href": "technology.html"},
    {"label": "Resources", "href": "resources.html"},
    {"label": "About Us", "href": "about.html"},
    {"label": "Careers", "href": SITE["careers_url"], "mobile_only": True, "external": True},   # opens the Careers page on stolway.com
    {"label": "Contact Us", "href": "contact.html", "mobile_only": True},
]
CERTS = ["Engineered in Australia", "IECEx certified equipment", "Ex p pressurised enclosures", "Ex d flameproof enclosures", "Zone 1 and Zone 2 designs"]

# Product groups, in menu order. "image" is the picture on the group tile (a name from src/images.json).
GROUPS = [
    {"id": "process", "name": "Process Analysers", "title": "Process|Analysers", "image": "stll-exp",
     "intro": "Laser and spectroscopy analysers for gas composition and trace measurement in process streams."},
    {"id": "emissions", "name": "Emissions Monitoring", "title": "Emissions|Monitoring", "image": "sss-probe",
     "intro": "Continuous emission monitoring, heated stack sampling and dust monitoring for flue gas."},
    {"id": "ambient", "name": "Ambient Air & Calibration", "title": "Ambient Air|& Calibration", "image": "co-5300",
     "intro": "Ambient gas analysers, converters and calibration equipment."},
    {"id": "liquid", "name": "Liquid & Level", "title": "Liquid|& Level", "image": "placeholder",
     "intro": "Online analysers and level profiling for liquid process streams and separators."},
]

PRODUCTS = json.load(open(os.path.join(HERE, "content", "products.json"), encoding="utf-8"))
PLACEHOLDER = {"file": "placeholder", "alt": "Image coming soon"}
TBD_TEXT = "Details for this product are being finalised. Contact us for a datasheet or to talk through your application."
for p in PRODUCTS:
    p["group_name"] = next(g["name"] for g in GROUPS if g["id"] == p["group"])
    p["no_image"] = not p["images"]
    if p["no_image"]:
        p["images"] = [PLACEHOLDER]
    p["card"] = p["summary"] or TBD_TEXT
for g in GROUPS:
    g["products"] = [p for p in PRODUCTS if p["group"] == g["id"]]
for p in PRODUCTS:
    same = [o for o in PRODUCTS if o["group"] == p["group"] and o is not p and not o["tbd"]]
    rest = [o for o in PRODUCTS if o["group"] != p["group"] and o["featured"]]
    p["related"] = (same + rest)[:3]
BY_SLUG = {p["slug"]: p for p in PRODUCTS}
FEATURED = [p for p in PRODUCTS if p["featured"]]

# Home page hero: text banners that rotate over the animated spectrum background. Add, remove or reorder freely.
SLIDES = [
    {"eyebrow": "Stolway Analytics", "title": "Precision In Every Spectrum", "accent": "Process Analysers & Sampling Systems",
     "text": "High-end liquid and gas online analysers built on spectroscopy, with IECEx certified designs for hazardous areas.",
     "cta": "Explore Our Products", "href": "products.html"},
    {"eyebrow": "Emissions monitoring", "title": "Smart Sampling System", "accent": "For CEMS Stack Gas",
     "text": "A heated probe, filter and sample line with programmable blowback, keeping CEMS sample paths free of plugging.",
     "cta": "Explore The SSS", "href": "products/smart-sampling-system.html"},
    {"eyebrow": "Process analysers", "title": "ST Line Laser", "accent": "ppb-Level H₂O, H₂S & SO₂",
     "text": "OF-CEAS laser spectroscopy with a response time under 10 seconds, in Ex p and Ex d versions.",
     "cta": "Explore ST Line Laser", "href": "products/st-line-laser.html"},
    {"eyebrow": "Hazardous areas", "title": "IECEx Certified", "accent": "For Zone 1 & Zone 2",
     "text": "Pressurised and flameproof designs, with certificates you can verify on the IECEx register.",
     "cta": "View Certificates", "href": "resources.html#certificates"},
]

WHY = [
    {"icon": "spectrum", "title": "Spectroscopy-based analysers", "text": "High-end liquid and gas online analysers built on spectroscopy technology."},
    {"icon": "cert", "title": "Certified for hazardous areas", "text": "IECEx certified Ex p and Ex d designs for Zone 1 and Zone 2 installations."},
    {"icon": "tailored", "title": "Tailored solutions", "text": "We diagnose your requirements first, then provide solutions tailored to them."},
    {"icon": "global", "title": "Engineered in Australia", "text": "Head office in Melbourne, with engineering and manufacturing in Australia and regional manufacturing in the Middle East."},
]
# Line icons (24x24 SVG path data)
ICONS = {
    "spectrum": '<path d="M3 6h3.500c1.200 0 1.300 11 2.500 11s1.300-11 2.500-11H13c1 0 1.100 6 2 6s1-6 2-6h4"/><path d="M3 20h18"/>',
    "cert": '<path d="M12 3 5 6v5.500c0 4.300 2.900 7.700 7 9 4.100-1.300 7-4.700 7-9V6l-7-3Z"/><path d="m9 12 2.200 2.200L15.200 10"/>',
    "tailored": '<path d="M4 7h8M18 7h2M4 17h2M12 17h8"/><circle cx="15" cy="7" r="2.500"/><circle cx="9" cy="17" r="2.500"/>',
    "global": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.200 3 14.800 0 18M12 3c-3 3.200-3 14.800 0 18"/>',
}

# Measurement principles (home page and Technology page). "product" is the slug of the product that uses it.
TECH = [
    {"id": "of-ceas", "name": "OF-CEAS", "long": "Optical Feedback Cavity-Enhanced Absorption Spectroscopy", "product": "st-line-laser",
     "text": "A laser locked to a high-finesse optical cavity multiplies the effective path length for ppb-level H₂O and H₂S detection.",
     "detail": "Process gas is drawn at low pressure through a resonant optical cell. A frequency-stabilised infrared laser couples with the cavity through optical feedback, and the many passes of light through the gas greatly increase the effective path length. The target gases absorb specific wavelengths, and the absorption spectra are fitted to reference data to give the concentration.",
     "points": ["ppb-level detection with molecular specificity", "No cross-interference, even in complex gas matrices", "No consumables such as electrochemical cells or drying cartridges"]},
    {"id": "tdlas", "name": "TDLAS", "long": "Tunable Diode Laser Absorption Spectroscopy", "product": "st-lle-9680",
     "text": "Single-line laser scanning of the target gas absorption peak, free of background-gas interference, for up to five gases at once.",
     "detail": "A low-noise semiconductor laser scans a single absorption line of the gas being measured, clear of absorption by background gases. The concentration is calculated from the second harmonic and line-broadening information.",
     "points": ["1 to 5 gases measured simultaneously", "High accuracy, small drift and high stability", "No moving parts"]},
    {"id": "tfs", "name": "TFS", "long": "Tunable Filter Spectroscopy", "product": "ap5-tfs",
     "text": "Broadband light sliced into wavelength components to resolve hydrocarbon composition in real time, with BTU and Wobbe index outputs.",
     "detail": "The sensor platform has a light source, a sample cell, a wavelength-separating element and a photo-detector. The wavelength-separating element slices the broadband light into components that interact with the sample molecules. Some are absorbed and others pass through, and the absorption pattern gives the hydrocarbon composition in real time.",
     "points": ["One-second response", "No carrier gas, fuel gas or instrument air", "No periodic on-site calibration"]},
    {"id": "ndir", "name": "NDIR", "long": "Non-Dispersive Infrared", "product": "st-co-5300",
     "text": "Filter-wheel infrared absorption over a 14 m effective optical path for ppm-level carbon monoxide.",
     "detail": "High-energy infrared light passes alternately through a chamber filled with CO and one without, by way of a filter wheel, then through a sample absorption cell with a 14 m effective optical path. The concentration is calculated by comparing absorption in the sample with absorption in the reference gas, following the Beer–Lambert law.",
     "points": ["ppm-level CO for atmospheric monitoring", "Temperature and pressure compensation", "Auto zero and span calibration"]},
    {"id": "laser-scattering", "name": "Laser scattering", "long": "Laser forward scattering", "product": "st-dms-300",
     "text": "Isokinetic extraction into a fully heated chamber for dust measurement in wet, low-temperature flue gas.",
     "detail": "Particulates are extracted isokinetically from the flue into a fully heated gas chamber. The forward-scattered laser light is measured and converted into an output signal proportional to the dust concentration.",
     "points": ["Suited to ultra-low emission monitoring", "Built for low-temperature, high-humidity flue gas", "Positive pressure explosion-proof version"]},
    {"id": "heated-sampling", "name": "Heated sampling", "long": "Smart heated sample conditioning", "product": "smart-sampling-system",
     "text": "Heated probe, filter and 200 °C sample line with programmable blowback, keeping CEMS sample paths free of plugging.",
     "detail": "The controller manages the temperature of the heated probe, filter and sample line, and runs configurable instrument-air blowback sequences that clean the probe, filter and sample line tube.",
     "points": ["Works with any CEMS analyser", "Programmable sampling, blowback and validation sequences", "Dual HMI at the probe and the controller"]},
]
for t in TECH:
    t["p"] = BY_SLUG[t["product"]]

INDUSTRIES = [
    {"name": "Oil & gas", "text": "Natural gas processing, sour gas treatment and custody transfer."},
    {"name": "Gas processing & LNG", "text": "Gas quality, dryers, BTU and Wobbe index."},
    {"name": "Refineries & chemical plants", "text": "Trace H₂O and H₂S, and process gas analysis."},
    {"name": "Petrochemicals", "text": "Multi-gas analysis in corrosive environments."},
    {"name": "Power plants", "text": "CEMS stack sampling and ultra-low dust emissions."},
    {"name": "Environmental monitoring", "text": "Ambient CO and NH₃, and analyser calibration."},
    {"name": "Industrial safety", "text": "Confined space and occupational health monitoring."},
    {"name": "Manufacturing", "text": "Online analysers for industrial processes."},
]

# ---- Resources page ----
CERT_ROWS = [dict(c, product=p) for p in PRODUCTS for c in p["certs"]]
EX_MARKINGS = [
    {"product": "ST Line Laser, Ex p", "slug": "st-line-laser", "marking": "Ex pxb IIC T4 Gb", "parts": [
        ("Ex", "Explosion protected", "Equipment designed for use in explosive atmospheres."),
        ("pxb", "Pressurised enclosure, type px", "Protective gas keeps the enclosure at overpressure; level \"b\" suits Zone 1."),
        ("IIC", "Gas group IIC", "The most demanding gas group, including hydrogen and acetylene. Also covers IIA and IIB."),
        ("T4", "Temperature class T4", "Maximum surface temperature 135 °C."),
        ("Gb", "Equipment protection level Gb", "High protection: suitable for Zone 1 and Zone 2.")]},
    {"product": "ST Line Laser, Ex d", "slug": "st-line-laser", "marking": "Ex db IIB+H2 T6 Gb", "parts": [
        ("Ex", "Explosion protected", "Equipment designed for use in explosive atmospheres."),
        ("db", "Flameproof enclosure", "The enclosure contains any internal explosion and prevents it spreading; level \"b\" suits Zone 1."),
        ("IIB+H2", "Gas group IIB plus hydrogen", "Suitable for IIA and IIB gases, and additionally hydrogen."),
        ("T6", "Temperature class T6", "Maximum surface temperature 85 °C."),
        ("Gb", "Equipment protection level Gb", "High protection: suitable for Zone 1 and Zone 2.")]},
    {"product": "Smart Sampling System", "slug": "smart-sampling-system", "marking": "Ex pzc IIC T4 Gc", "parts": [
        ("Ex", "Explosion protected", "Equipment designed for use in explosive atmospheres."),
        ("pzc", "Pressurised enclosure, type pz", "Pressurisation for Zone 2 locations; level \"c\"."),
        ("IIC", "Gas group IIC", "The most demanding gas group, including hydrogen and acetylene."),
        ("T4", "Temperature class T4", "Maximum surface temperature 135 °C."),
        ("Gc", "Equipment protection level Gc", "Enhanced protection: suitable for Zone 2.")]},
]
ZONES = [("Zone 0", "Ga", "Explosive gas atmosphere present continuously or for long periods."),
         ("Zone 1", "Gb (or Ga)", "Explosive gas atmosphere likely to occur in normal operation."),
         ("Zone 2", "Gc (or Ga, Gb)", "Explosive gas atmosphere not likely in normal operation, and only briefly if it does occur.")]
TCLASSES = [("T1", "450 °C"), ("T2", "300 °C"), ("T3", "200 °C"), ("T4", "135 °C"), ("T5", "100 °C"), ("T6", "85 °C")]
STANDARDS = [
    ("IEC 60079-0", "Explosive atmospheres: Equipment, general requirements", "All certified products"),
    ("IEC 60079-1", "Equipment protection by flameproof enclosures \"d\"", "ST Line Laser (Ex d), AP5-TFS"),
    ("IEC 60079-2", "Equipment protection by pressurized enclosure \"p\"", "Smart Sampling System, ST Line Laser (Ex p)"),
]
LINKS = [
    ("IECEx certificate register", "Search and verify IECEx Certificates of Conformity, test reports and quality assessment reports.", "https://www.iecex-certs.com/#/search"),
    ("IECEx System", "The IEC System for Certification to Standards Relating to Equipment for Use in Explosive Atmospheres.", "https://www.iecex.com/"),
    ("IEC Webstore: IEC 60079 series", "Official source for the explosive-atmospheres standards referenced on our certificates.", "https://webstore.iec.ch/en/search?q=60079"),
]
GLOSSARY = [
    ("CEMS", "Continuous Emission Monitoring System. Measures pollutants in stack (flue) gas continuously."),
    ("OF-CEAS", "Optical Feedback Cavity-Enhanced Absorption Spectroscopy. Laser absorption in a high-finesse cavity for ppb-level detection."),
    ("TDLAS", "Tunable Diode Laser Absorption Spectroscopy. Scans a single absorption line of the target gas."),
    ("NDIR", "Non-Dispersive Infrared. Infrared absorption measurement using optical filters rather than a spectrometer."),
    ("TFS", "Tunable Filter Spectroscopy. Broadband light separated into wavelength components to resolve gas composition."),
    ("LOD", "Limit of detection. The lowest concentration an analyser can reliably distinguish from zero."),
    ("F.S.", "Full scale. The upper end of the measuring range; accuracy is often stated as a percentage of it."),
    ("T90", "Response time to reach 90% of a step change in concentration."),
    ("ppm / ppb", "Parts per million / parts per billion by volume (µmol/mol and nmol/mol)."),
    ("Wobbe index", "Indicator of the interchangeability of fuel gases, from heating value and specific gravity."),
    ("Isokinetic sampling", "Extracting a sample at the same velocity as the gas stream, so particulate measurements are representative."),
    ("HMI", "Human–machine interface. The local touchscreen used to monitor and configure the system."),
]

# ---- About page ----
ABOUT = {
    "summary": "Stolway Analytics is a process analytics company that designs, manufactures and commercialises high-end liquid and gas online analysers based on spectroscopy technology.",
    "expertise": "Our team of seasoned metrology professionals brings knowledge across design and manufacturing.",
    "pillars": [("Spectroscopy technology", "Liquid and gas online analysers based on spectroscopy."),
                ("Metrology expertise", "A team of seasoned metrology professionals."),
                ("Design & manufacturing", "Analysers designed, manufactured and commercialised in-house.")],
    "mission": "Empower industries with cutting-edge process analysers built on spectroscopy.",
    "vision": "Become a global leader in process analytics, known for accuracy and efficiency.",
    "vision_points": ["Invest in R&D", "Maintain a commitment to quality", "Focus on the future of metrology"],
    "values": ["Precision", "Reliability", "Innovation", "Expertise", "Customer-centric approach"],
    "approach": [("Understand your needs", "We diagnose your requirements first."), ("Provide tailored solutions", "Solutions are then tailored to what you need.")],
}

# Same offices as stolway.com. Keep the two lists in step.
OFFICES = [
    {"role": "Head office, engineering & manufacturing", "geo": (-37.65, 145.03), "city": "Melbourne, VIC", "entity": "Stolway Pty Ltd, Melbourne", "country": "AU", "street": "71 Trafalgar Road", "locality": "Epping", "region": "VIC", "postcode": "3076",
     "lines": ["71 Trafalgar Road", "Epping VIC 3076", "Australia"], "phone": "+61 414 144 684", "email": "info@stolway.com.au"},
    {"role": "Engineering & manufacturing", "geo": (-34.42, 150.89), "city": "Wollongong, NSW", "entity": "Stolway Pty Ltd, Wollongong", "country": "AU", "street": "W/2 91-95 Montague Street", "locality": "Wollongong", "region": "NSW", "postcode": "2500",
     "lines": ["W/2 91–95 Montague Street", "Wollongong NSW 2500", "Australia"], "phone": "+61 2 4262 3000", "email": "info@stolway.com.au"},
    {"role": "Middle East manufacturing", "geo": (24.35, 54.5), "city": "Abu Dhabi, UAE", "entity": "Stolway Manufacturing Sole Proprietorship LLC", "country": "AE", "street": "Store B1303, Plot 29, ICAD 3, Musaffah South", "locality": "Abu Dhabi",
     "lines": ["Store B1303, Plot 29, ICAD 3", "Musaffah South, PO Box 26647", "Abu Dhabi, United Arab Emirates"], "phone": "+971 2 55 909 31", "email": "info@stolwayuae.com"},
    {"role": "Middle East manufacturing", "geo": (26.39, 50.14), "city": "Dammam, KSA", "entity": "BR Stolway Manufacturing Co LLC", "country": "SA", "street": "Unit 75, Street 166, Dammam 2nd Industrial Area", "locality": "Dammam",
     "lines": ["Unit 75, Street 166", "Dammam 2nd Industrial Area, PO Box 34324", "Kingdom of Saudi Arabia"], "phone": "", "email": "info.ksa@stolway.com.au"},
]

# Structured data for search engines (schema.org), built by src/seo.py
ORG = seo.organization(
    SITE["url"], "Stolway Analytics", ABOUT["summary"], "/assets/img/icon-512.png", SITE["email"], SITE["phone"], OFFICES,
    parent=("Stolway", "https://stolway.com/"),
    knows_about=["Process analysers", "Gas analysers", "Laser gas analysers", "TDLAS", "OF-CEAS", "NDIR", "Tunable filter spectroscopy",
                 "Continuous emission monitoring (CEMS)", "IECEx", "Hazardous area analysers"])
WEBSITE = seo.website(SITE["url"], "Stolway Analytics", "Spectroscopy-based process analysers and sampling systems")

# Data for the globe on the About and Contact pages: one marker per office above
GLOBE = json.dumps([{"name": o["city"], "role": o["role"], "lat": o["geo"][0], "lon": o["geo"][1]} for o in OFFICES], ensure_ascii=False)


def page(path, template, title, description, **kw):
    d = {"path": path, "template": template, "title": title, "description": description}
    d.update(kw)
    return d


# [[analyzers]] in a title or description is swapped for the *other* spelling (see SPELLING above).
PAGES = [
    page("/index.html", "index.html", "Stolway Analytics | Process Analysers & Sampling Systems",
         "Spectroscopy-based online process analysers ([[analyzers]]) and sampling systems for gases and liquids, with IECEx certified designs for hazardous areas.",
         ),
    page("/products.html", "products.html", "Process Analysers & Sampling Systems | Stolway Analytics",
         "Laser and spectroscopy gas analysers ([[analyzers]]), CEMS stack sampling, dust monitoring, ambient air analysers and liquid measurement from Stolway Analytics.",
         section="products", h1="Analysers & Sampling Systems|For Process, Stack & Ambient Applications",
         intro="Four product groups covering process gas composition, emissions monitoring, ambient air and liquid measurement.",
         crumbs=[{"label": "Products"}]),
    page("/technology.html", "technology.html", "Measurement Technology | Stolway Analytics",
         "The measurement principles behind Stolway Analytics analysers ([[analyzers]]): OF-CEAS, TDLAS, tunable filter spectroscopy, NDIR, laser scattering and heated sampling.",
         h1="Measurement Principles|Behind Our Range",
         intro="Each analyser is built on a proven measurement principle, matched to the application.", crumbs=[{"label": "Technology"}]),
    page("/resources.html", "resources.html", "Resources: IECEx Certificates, Ex Markings & Glossary | Stolway Analytics",
         "IECEx certificates, a guide to reading Ex markings, IEC 60079 standards and a glossary for Stolway Analytics analysers ([[analyzers]]) and sampling systems.",
         h1="Certificates, Standards|& Technical References",
         intro="Everything you need to check a certificate or read an Ex marking, in one place.", crumbs=[{"label": "Resources"}]),
    page("/about.html", "about.html", "About Stolway Analytics",
         "Stolway Analytics designs, manufactures and commercialises spectroscopy-based liquid and gas online analysers ([[analyzers]]), engineered in Australia with offices in Australia and the Middle East.",
         h1="Precision Process Analytics|Built On Spectroscopy",
         intro="Engineered in Australia and part of the Stolway group, with head office in Melbourne.", crumbs=[{"label": "About"}]),
    page("/contact.html", "contact.html", "Contact Stolway Analytics",
         "Contact Stolway Analytics for quotes, datasheets and technical support. Head office in Melbourne, with offices in Wollongong, Abu Dhabi and Dammam.",
         h1="Let's Talk About|Your Application",
         intro="Tell us what you need to measure and one of our team will get back to you.", crumbs=[{"label": "Contact"}]),
    page("/privacy.html", "privacy.html", "Privacy Policy | Stolway Analytics", "How Stolway Analytics handles personal information collected through this website."),
    page("/404.html", "404.html", "Page Not Found | Stolway Analytics", "The page you were looking for could not be found."),
]
for p in PRODUCTS:
    PAGES.append(page(f"/products/{p['slug']}.html", "product.html", f"{p['name']} | Stolway Analytics",
                      p["summary"] or f"{p['name']} from Stolway Analytics. Contact us for a datasheet.", section="products", product=p))

# ---- Search results: page titles (keep under 60 characters) and descriptions (120 to 155 characters) ----
SEO = {
    "/index.html": ("Process Gas Analysers & Sampling Systems | Stolway Analytics",
                    "Spectroscopy-based online process analysers (analyzers) and sampling systems for gases and liquids, with IECEx certified designs for hazardous areas."),
    "/products.html": ("Gas Analysers, CEMS & Sampling Systems | Stolway Analytics",
                       "Laser and spectroscopy gas analysers (analyzers), CEMS stack sampling, dust monitors, ambient air analysers and calibrators from Stolway Analytics."),
    "/technology.html": ("TDLAS, OF-CEAS, NDIR & TFS Technology | Stolway Analytics",
                         "How our analysers (analyzers) measure: OF-CEAS, TDLAS, tunable filter spectroscopy, NDIR, laser scattering and heated sample conditioning."),
    "/resources.html": ("IECEx Certificates & Ex Marking Guide | Stolway Analytics",
                        "IECEx certificates for Stolway Analytics analysers (analyzers) and sampling systems, a guide to reading Ex markings, IEC 60079 standards and a glossary."),
    "/about.html": ("About Stolway Analytics | Spectroscopy Process Analysers",
                    "Stolway Analytics designs and manufactures spectroscopy-based liquid and gas online analysers (analyzers). Engineered in Australia, part of the Stolway group."),
    "/contact.html": ("Contact Stolway Analytics | Quotes, Datasheets & Support",
                      "Contact Stolway Analytics for analyser quotes, datasheets and technical support. Head office in Melbourne, with offices in Wollongong, Abu Dhabi and Dammam."),
    "/privacy.html": ("Privacy Policy | Stolway Analytics", "How Stolway Analytics collects, uses, stores and protects personal information sent through this website, and how to contact us about it."),
    "/404.html": ("Page Not Found | Stolway Analytics", "The page you were looking for could not be found. Try our process analysers, measurement technology, resources or contact page."),
    "/products/ap5-tfs.html": ("AP5-TFS Tunable Filter Gas Analyser | Stolway Analytics",
                               "Tunable filter spectroscopy analyser for real-time hydrocarbon composition of natural gas, LNG, LPG and biogas, with BTU and Wobbe index outputs."),
    "/products/smart-sampling-system.html": ("Smart Sampling System for CEMS | Stolway Analytics",
                                             "Heated CEMS sampling system that stops sample-line plugging and delivers stack gas to any CEMS analyser, IECEx certified for hazardous areas."),
    "/products/st-cems-5000c.html": ("ST CEMS-5000C Emission Monitoring System | Stolway Analytics",
                                     "Continuous emission monitoring system covering flue gas analysis and pre-treatment, flue gas sampling and direct reading, and moisture measurement."),
    "/products/st-dms-300.html": ("ST DMS-300 Dust Monitor | Stolway Analytics",
                                  "Explosion-proof extractive dust monitor for low-temperature, high-humidity flue gas, suited to ultra-low emission monitoring in power plants."),
    "/products/st-line-laser.html": ("ST Line Laser H2O, H2S & SO2 Analyser | Stolway Analytics",
                                     "OF-CEAS line laser analysers for ppb-level H2O, H2S and SO2 in process gas, IECEx certified in Ex p and Ex d versions for hazardous areas."),
    "/products/st-mgc-5800.html": ("ST MGC-5800 Multi Gas Calibrator | Stolway Analytics",
                                   "Dynamic dilution calibrator using high-precision mass flow controllers to supply zero and span gas to analysers, with an optional ozone generator."),
    "/products/st-c-nh3-5302.html": ("ST C NH3-5302 Ammonia Converter | Stolway Analytics",
                                     "Thermal converter used with a NOx analyser to measure ammonia (NH3), oxidising NH3 to NOx over precious-metal catalysts at high temperature."),
    "/products/level-profiler.html": ("Level Profiler for Separators | Stolway Analytics",
                                      "A virtual window into separators and vessels: locates water, emulsion, oil, foam and gas layers without nuclear sources. Ex ia intrinsically safe."),
}
_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
for pg in PAGES:
    if pg["path"] in SEO:
        pg["title"], pg["description"] = SEO[pg["path"]]
    pg["title"], pg["description"] = pg["title"].translate(_SUB), pg["description"].translate(_SUB)   # people search "H2S", not "H₂S"
    pr = pg.get("product")
    if pr:
        if pr["tbd"]:
            pg["description"] = f"{pr['name']} from Stolway Analytics. Details are being finalised: contact us for a datasheet or to talk through your application."
            pg["noindex"] = True   # no details yet: kept out of search results and the sitemap until the page has real content
        if not pr["no_image"]:
            pg["og_image"], pg["og_alt"], pg["og_contain"] = pr["images"][0]["file"], pr["images"][0]["alt"], True
PAGE = {pg["path"]: pg for pg in PAGES}
PAGE["/index.html"]["ld"] = [WEBSITE, ORG]
PAGE["/about.html"]["ld"] = [ORG]
PAGE["/contact.html"]["ld"] = [ORG]

# Old stolwayanalytics.com (WordPress) addresses -> new pages, so existing links and search results keep working
REDIRECTS = [
    ("/index.php", "/"),
    ("/index.php/about1", "/about"), ("/index.php/contactus", "/contact"),
    ("/index.php/service", "/products"), ("/index.php/portfolio", "/products"), ("/index.php/blog", "/"),
    ("/index.php/service/water-cut-meter", "/products/water-cut-meter"),
]
for p in PRODUCTS:
    REDIRECTS.append((f"/index.php/{p['old_slug']}", f"/products/{p['slug']}"))
    REDIRECTS.append((f"/products/{p['old_slug']}", f"/products/{p['slug']}"))   # addresses used by the 2026 rebuild that was never finished
REDIRECTS = list(dict.fromkeys((a, b) for a, b in REDIRECTS if a != b))


def clean_url(path):
    """/index.html -> /, /about.html -> /about, /products/ap5-tfs.html -> /products/ap5-tfs"""
    if path == "/index.html":
        return "/"
    return path[:-5] if path.endswith(".html") else path


_HREF = re.compile(r'href="(?!https?:|mailto:|tel:|#)([^"#?]*?)\.html(?=["#?])')


def clean_links(html):
    """Rewrite local links in a rendered page so nothing points at a .html address."""
    def fix(m):
        p = m.group(1)
        if p == "index" or p.endswith("/index"):
            return 'href="' + (p[:-5] or "./")
        return 'href="' + p
    return _HREF.sub(fix, html)


def spell(html):
    """Apply the SPELLING switch to a finished page."""
    other = "analyzer" if SPELLING == "analyser" else "analyser"
    if SPELLING == "analyzer":
        html = re.sub(r"nalys(?=e[rd]|ing)", "nalyz", html)
    html = html.replace("[[analyzers]]", other + "s").replace("[[Analyzers]]", other.capitalize() + "s")
    return html


def breadcrumb_jsonld(pg):
    trail = [("Home", "/")]
    if pg.get("product"):
        trail += [("Products", "/products"), (pg["product"]["name"], clean_url(pg["path"]))]
    else:
        trail += [(c["label"], clean_url(pg["path"])) for c in pg.get("crumbs", [])]
    if len(trail) < 2:
        return ""
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE["url"] + u} for i, (n, u) in enumerate(trail)]}, ensure_ascii=False)


def write_server_files():
    # Cloudflare / Netlify: /about is already answered from about.html, so only the old addresses need rules
    lines = ["# 301 redirects from the old stolwayanalytics.com addresses"]
    for a, b in REDIRECTS:
        lines.append(f"{a}  {b}  301")
        if a != "/index.php":
            lines.append(f"{a}/  {b}  301")
    lines.append("/index.php/*  /  301")
    open(os.path.join(OUT, "_redirects"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(OUT, "_headers"), "w").write(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "  Strict-Transport-Security: max-age=31536000\n\n"
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n")


def build():
    import shutil, subprocess, hashlib
    if "--images" in sys.argv:
        subprocess.run([sys.executable, os.path.join(HERE, "images.py")], check=True)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    images = json.load(open(os.path.join(HERE, "images.json")))
    for pg in PAGES:   # link-preview pictures (1200 x 630 JPEG) in static/assets/og, made once per picture
        if pg.get("og_image") and seo.og_image(pg["og_image"], os.path.join(HERE, "static", "assets", "img"), images,
                                               os.path.join(HERE, "static", "assets", "og"), pg.get("og_contain", False)):
            pg["og_url"] = f'{SITE["url"]}/assets/og/{pg["og_image"]}.jpg'
        else:
            pg["og_url"] = SITE["url"] + "/assets/img/og-image.jpg"
        pg["robots"] = seo.robots_meta(pg)
        pg["ld_blocks"] = [seo.ld(*pg["ld"])] if pg.get("ld") else []
    shutil.copytree(os.path.join(HERE, "static"), OUT)
    h = hashlib.md5()
    for f in ("assets/css/site.css", "assets/js/site.js", "assets/js/globe.js", "assets/js/spectrum.js"):
        h.update(open(os.path.join(HERE, "static", f), "rb").read())
    SITE["version"] = h.hexdigest()[:10]
    env = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.globals["IMAGES"] = json.load(open(os.path.join(HERE, "images.json")))
    for pg in PAGES:
        depth = pg["path"].count("/") - 1
        root = "/" if pg["path"] == "/404.html" else "../" * depth
        pg["url"] = SITE["url"] + clean_url(pg["path"])
        pg["breadcrumbs"] = breadcrumb_jsonld(pg)
        html = env.get_template(pg["template"]).render(
            page=pg, site=SITE, nav=NAV, products=PRODUCTS, groups=GROUPS, featured=FEATURED, industries=INDUSTRIES,
            offices=OFFICES, certs=CERTS, slides=SLIDES, globe=GLOBE, why=WHY, icons=ICONS, tech=TECH, about=ABOUT,
            cert_rows=CERT_ROWS, ex_markings=EX_MARKINGS, zones=ZONES, tclasses=TCLASSES, standards=STANDARDS,
            links=LINKS, glossary=GLOSSARY, tbd_text=TBD_TEXT, root=root, p=pg.get("product"))
        out = os.path.join(OUT, pg["path"].lstrip("/"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(spell(clean_links(html)))
    open(os.path.join(OUT, "sitemap.xml"), "w").write(seo.sitemap(SITE["url"], PAGES, TODAY.isoformat(), clean_url))
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    open(os.path.join(OUT, "site.webmanifest"), "w").write(json.dumps({
        "name": "Stolway Analytics", "short_name": "Stolway Analytics", "start_url": "/", "display": "browser",
        "background_color": "#FFFFFF", "theme_color": "#10164E",
        "icons": [{"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2))
    write_server_files()
    print(f"Built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    build()
