"""Builds the static content pages of ilovephoto.in.

The converter (index.html) is hand-written. Everything else — guides, FAQ,
about/legal pages, assets/presets.js and sitemap.xml — is generated here so
that the presets used by the converter and the specs shown in the guides come
from one source of truth.

Run from the repo root:  python scripts/build_site.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ilovephoto.in"
REVIEWED = "November 2026"
LASTMOD = "2026-11-03"
PUBLISHED = "2026-03-27"
INDEXNOW_KEY = "29e78a8aaef5383a7e60445c796c5e12"

# ─────────────────────────────────────────────────────────────────────────────
# PRESETS — only documents where YOU take and upload (or print) the photo.
# Not included on purpose: Aadhaar, Indian passport (captured at the centre),
# JEE Main / SSC (live webcam capture), NREGA (taken by officials).
# Where published limits disagree, the preset uses values that satisfy all of
# them, and the guide says so.
# ─────────────────────────────────────────────────────────────────────────────
PRESETS = [
    # ID & tax
    dict(id="pan_protean", group="ID & tax", kind="photo", name="PAN card photo — Protean (NSDL)",
         w=197, h=276, dpi=200, minKB=0, maxKB=50, guide="pan-card-photo-size.html"),
    dict(id="pan_uti", group="ID & tax", kind="photo", name="PAN card photo — UTIITSL",
         w=213, h=213, dpi=300, minKB=0, maxKB=30, guide="pan-card-photo-size.html#utiitsl"),
    dict(id="voter", group="ID & tax", kind="photo", name="Voter ID (Form 6 / Form 8) photo",
         w=413, h=531, dpi=300, minKB=0, maxKB=100, guide="voter-id-photo-size.html"),
    dict(id="dl", group="ID & tax", kind="photo", name="Learner's / Driving licence (Sarathi) photo",
         w=420, h=525, dpi=300, minKB=10, maxKB=20, guide="driving-licence-photo-size.html"),
    # Exams & jobs
    dict(id="neet", group="Exams & jobs", kind="photo", name="NEET UG passport-size photo",
         w=413, h=531, dpi=300, minKB=10, maxKB=200, guide="neet-photo-size.html"),
    dict(id="neet_pc", group="Exams & jobs", kind="photo", name="NEET UG postcard photo (4×6 in)",
         w=1200, h=1800, dpi=300, minKB=10, maxKB=200, guide="neet-photo-size.html#postcard"),
    dict(id="upsc", group="Exams & jobs", kind="photo", name="UPSC (CSE, ESE, CDS, NDA…) photo",
         w=600, h=750, dpi=300, minKB=20, maxKB=200, stamp=True, guide="upsc-photo-size.html"),
    dict(id="ibps", group="Exams & jobs", kind="photo", name="IBPS / SBI / RBI bank exam photo",
         w=200, h=230, dpi=200, minKB=20, maxKB=50, guide="ibps-bank-exam-photo-size.html"),
    dict(id="cat", group="Exams & jobs", kind="photo", name="CAT (IIM) photo",
         w=1200, h=1200, dpi=300, minKB=0, maxKB=80, guide="cat-exam-photo-size.html"),
    # Travel & visas
    dict(id="oci", group="Travel & visas", kind="photo", name="OCI card photo",
         w=600, h=600, dpi=300, minKB=0, maxKB=200, guide="oci-card-photo-requirements.html"),
    dict(id="evisa", group="Travel & visas", kind="photo", name="India e-Visa photo",
         w=600, h=600, dpi=300, minKB=10, maxKB=300, guide="india-evisa-photo.html"),
    dict(id="us", group="Travel & visas", kind="photo", name="US visa (DS-160) / US passport photo",
         w=600, h=600, dpi=300, minKB=0, maxKB=240, guide="us-visa-photo-requirements.html"),
    dict(id="schengen", group="Travel & visas", kind="photo", name="Schengen visa photo (35×45 mm print)",
         w=827, h=1063, dpi=600, minKB=0, maxKB=500, print=True, guide="schengen-visa-photo-size.html"),
    dict(id="uk", group="Travel & visas", kind="photo", name="UK passport photo (online application)",
         w=900, h=1125, dpi=300, minKB=50, maxKB=2048, guide="uk-passport-photo-size.html"),
    # Signatures
    dict(id="sig_pan", group="Signatures", kind="signature", name="PAN signature — Protean (NSDL)",
         w=354, h=157, dpi=200, minKB=0, maxKB=50, guide="signature-size-guide.html#pan"),
    dict(id="sig_neet", group="Signatures", kind="signature", name="NEET UG signature",
         w=350, h=150, dpi=200, minKB=10, maxKB=30, guide="signature-size-guide.html#neet"),
    dict(id="sig_upsc", group="Signatures", kind="signature", name="UPSC signature",
         w=700, h=350, dpi=300, minKB=20, maxKB=200, guide="signature-size-guide.html#upsc"),
    dict(id="sig_ibps", group="Signatures", kind="signature", name="IBPS / SBI bank exam signature",
         w=140, h=60, dpi=200, minKB=10, maxKB=20, guide="signature-size-guide.html#ibps"),
    dict(id="sig_oci", group="Signatures", kind="signature", name="OCI signature (3:1)",
         w=600, h=200, dpi=300, minKB=0, maxKB=200, guide="signature-size-guide.html#oci"),
    # Profile
    dict(id="linkedin", group="Profile", kind="photo", name="LinkedIn / résumé profile photo",
         w=800, h=800, dpi=72, minKB=0, maxKB=1024, guide="linkedin-profile-photo-size.html"),
]
P = {p["id"]: p for p in PRESETS}


def kb_range(p):
    if p["minKB"] and p["maxKB"]:
        return f'{p["minKB"]}–{p["maxKB"]} KB'
    return f'up to {p["maxKB"]} KB' if p["maxKB"] < 1024 else f'up to {p["maxKB"] // 1024} MB'


def print_size(p):
    w = p["w"] / p["dpi"] * 25.4
    h = p["h"] / p["dpi"] * 25.4
    return f"{w:.0f} × {h:.0f} mm"


def esc(s):
    return html.escape(s, quote=True)


# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────
HEAD_COMMON = """<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JEEC2LBZBG"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-JEEC2LBZBG');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4415395756457608" crossorigin="anonymous"></script>"""

NAV = [("/", "Converter"), ("/blog/", "Guides"), ("/blog/faq.html", "FAQ"), ("/about.html", "About")]


def header(active):
    active_attr = ' class="active"'
    links = "".join(
        f'<a href="{href}"{active_attr if href == active else ""}>{label}</a>' for href, label in NAV
    )
    return f"""<header class="site-header"><div class="wrap">
  <a class="brand" href="/" aria-label="ilovephoto.in home">I <span class="heart">♥</span> Photo <small>ilovephoto.in</small></a>
  <nav class="nav" aria-label="Main">{links}</nav>
</div></header>"""


FOOTER = """<footer class="site-footer"><div class="wrap">
  <div class="footer-grid">
    <div>
      <a class="brand" href="/">I <span class="heart">♥</span> Photo</a>
      <p>Free, private photo and signature resizer for Indian application forms. Your files are processed in your browser and never uploaded.</p>
    </div>
    <div><h3>Popular guides</h3><ul>
      <li><a href="/blog/pan-card-photo-size.html">PAN card photo</a></li>
      <li><a href="/blog/neet-photo-size.html">NEET UG photo</a></li>
      <li><a href="/blog/upsc-photo-size.html">UPSC photo</a></li>
      <li><a href="/blog/signature-size-guide.html">Signature sizes</a></li>
      <li><a href="/blog/us-visa-photo-requirements.html">US visa photo</a></li>
    </ul></div>
    <div><h3>Learn</h3><ul>
      <li><a href="/blog/photo-size-chart.html">Photo size chart</a></li>
      <li><a href="/blog/faq.html">FAQ</a></li>
      <li><a href="/blog/photo-size-dpi-kb-explained.html">Pixels, DPI &amp; KB explained</a></li>
      <li><a href="/blog/take-passport-photo-at-home.html">Take a photo at home</a></li>
      <li><a href="/blog/photo-not-required.html">When you don't upload a photo</a></li>
    </ul></div>
    <div><h3>Site</h3><ul>
      <li><a href="/about.html">About</a></li>
      <li><a href="/contact.html">Contact</a></li>
      <li><a href="/privacy-policy.html">Privacy policy</a></li>
      <li><a href="/terms-of-service.html">Terms of service</a></li>
    </ul></div>
  </div>
  <p class="footer-note">© 2026 ilovephoto.in · Not affiliated with any government body. Requirements change — always check the instructions on the official portal before you submit.</p>
</div></footer>"""


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def og_name(path):
    return path.replace("/", "-").replace(".html", "") + ".png"


def og_url(path):
    return f"{SITE}/assets/og/{og_name(path)}"


def make_og_image(path, heading, sub):
    """1200×630 social/preview card, so links in WhatsApp, X, LinkedIn and AI answers show a real image."""
    from PIL import Image, ImageDraw, ImageFont

    def font(bold, size):
        names = ["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]
        for n in names:
            for d in ["C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/", "/Library/Fonts/", ""]:
                try:
                    return ImageFont.truetype(d + n, size)
                except OSError:
                    pass
        return ImageFont.load_default()

    def wrap(draw, text, f, width):
        lines, cur = [], ""
        for w in text.split():
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= width:
                cur = t
            else:
                lines.append(cur)
                cur = w
        return lines + [cur]

    img = Image.new("RGB", (1200, 630), "#f6f6f3")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1200, 14], fill="#c8244a")
    d.text((80, 70), "I ", font=font(True, 40), fill="#17191e")
    d.text((80 + d.textlength("I ", font=font(True, 40)), 70), "\u2665", font=font(True, 40), fill="#c8244a")
    d.text((80 + d.textlength("I \u2665 ", font=font(True, 40)), 70), "Photo  ·  ilovephoto.in", font=font(True, 40), fill="#17191e")
    y = 190
    for line in wrap(d, heading, font(True, 76), 1040)[:3]:
        d.text((80, y), line, font=font(True, 76), fill="#17191e")
        y += 92
    y += 16
    for line in wrap(d, sub, font(False, 38), 1040)[:3]:
        d.text((80, y), line, font=font(False, 38), fill="#5a6170")
        y += 50
    d.text((80, 548), "Free · private · runs in your browser", font=font(True, 32), fill="#c8244a")
    out = ROOT / "assets" / "og" / og_name(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)


def page(path, title, desc, body, active="", jsonld=None, robots="index, follow", og=None):
    url = SITE + "/" + path.replace("index.html", "")
    make_og_image(path, *(og or (title.split(" | ")[0], desc)))
    image = og_url(path)
    ld = ""
    for block in jsonld or []:
        ld += f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>\n'
    doc = f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:site_name" content="ilovephoto.in">
<meta property="og:locale" content="en_IN">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{image}">
{HEAD_COMMON}
{ld}</head>
<body>
{header(active)}
<main>
{body}
</main>
{FOOTER}
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def faq_html(faqs):
    items = "".join(f"<details><summary>{q}</summary><div><p>{a}</p></div></details>" for q, a in faqs)
    return f'<div class="faq">{items}</div>'


def faq_ld(faqs):
    import re
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": strip(q),
                        "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faqs],
    }


def crumbs_ld(items):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                            for i, (n, u) in enumerate(items)],
    }


def spec_table(pid, stated, anchor=""):
    """Three-column table: requirement / what the portal states / what our preset outputs."""
    p = P[pid]
    ours = {
        "Dimensions": f'{p["w"]} × {p["h"]} px',
        "Resolution": f'{p["dpi"]} DPI <small>({print_size(p)} if printed)</small>',
        "Format": "JPEG (.jpg)",
        "File size": kb_range(p),
    }
    rows = ""
    keys = list(dict.fromkeys([k for k, _ in stated] + list(ours)))
    stated_d = dict(stated)
    for k in keys:
        rows += f'<tr><th>{k}</th><td>{stated_d.get(k, "<small>Not specified</small>")}</td><td>{ours.get(k, "<small>—</small>")}</td></tr>'
    aid = f' id="{anchor}"' if anchor else ""
    return f"""<div class="spec"{aid}>
  <div class="spec-head"><h3>{esc(p["name"])}</h3><a class="btn btn-primary btn-small" href="/?preset={pid}">Use this preset</a></div>
  <div class="table-scroll"><table>
    <thead><tr><th>Requirement</th><td><small>What the portal asks</small></td><td><small>ilovephoto.in preset</small></td></tr></thead>
    {rows}
  </table></div>
</div>"""


def cta(pid, text):
    p = P[pid]
    return f"""<div class="cta"><p>{text}<span>{p["w"]}×{p["h"]} px · {kb_range(p)} · processed in your browser</span></p>
<a class="btn btn-primary" href="/?preset={pid}">Open converter</a></div>"""


def toc(sections):
    li = "".join(f'<li><a href="#{sid}">{t}</a></li>' for sid, t, _ in sections)
    return f'<nav class="toc" aria-label="On this page"><strong>On this page</strong><ol>{li}</ol></nav>'


def related(slugs):
    cards = ""
    for s in slugs:
        g = GUIDES_BY_SLUG[s]
        cards += f'<a class="card-link" href="/blog/{s}"><strong>{g["short"]}</strong><span>{g["card"]}</span></a>'
    return f'<h2>Related guides</h2><div class="cards">{cards}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# Guide content
# ─────────────────────────────────────────────────────────────────────────────
COMMON_PHOTO_RULES = """<ul>
<li><strong>Recent and in colour.</strong> Most portals want a photo taken in the last 6 months (UPSC and NEET are stricter — see their guides).</li>
<li><strong>Plain, light background.</strong> White or off-white with no pattern, shadow or other people.</li>
<li><strong>Face the camera.</strong> Neutral expression, eyes open, mouth closed, head straight — not tilted.</li>
<li><strong>Face fills most of the frame.</strong> Roughly 70–80% of the photo height from chin to top of head.</li>
<li><strong>No caps or dark glasses.</strong> Religious head coverings are fine if the full face is visible.</li>
<li><strong>Even light.</strong> Face a window; avoid overhead bulbs that cast shadows under the eyes.</li>
</ul>"""

GUIDES = []


def guide(**g):
    GUIDES.append(g)


guide(
    slug="pan-card-photo-size.html", category="ID & tax", short="PAN card photo & signature",
    card="Protean (NSDL) and UTIITSL sizes", presets=["pan_protean", "pan_uti", "sig_pan"],
    title="PAN Card Photo Size 2026 — Protean (NSDL) & UTIITSL Specs | ilovephoto.in",
    h1="PAN card photo and signature size (Protean & UTIITSL)",
    desc="Exact PAN card photo and signature size for online applications on Protean (NSDL) and UTIITSL, when you don't need to upload a photo at all, and how to avoid rejection.",
    lede="You only upload a PAN photo when you apply through Protean or UTIITSL and choose to submit scanned documents. If you apply with Aadhaar e-KYC, your photo comes straight from Aadhaar and there's nothing to upload.",
    sections=[
        ("need", "Do you need to upload a photo?", """
<table class="data-table"><thead><tr><th>How you apply</th><th>Photo upload?</th></tr></thead><tbody>
<tr><td>Instant e-PAN on the Income Tax e-filing portal</td><td>No — taken from Aadhaar</td></tr>
<tr><td>Protean / UTIITSL with Aadhaar e-KYC (paperless)</td><td>No — taken from Aadhaar</td></tr>
<tr><td>Protean with “Submit scanned images through e-Sign”</td><td><strong>Yes</strong> — photo, signature and documents</td></tr>
<tr><td>UTIITSL online with document upload</td><td><strong>Yes</strong> — photo and signature</td></tr>
<tr><td>Physical form (Form 49A / 49AA) sent by post</td><td>Paste two printed photos (3.5 × 2.5 cm)</td></tr>
</tbody></table>
<p>If you want a <em>different</em> photo from the one on your Aadhaar, use the scanned-images route — e-KYC will always use the Aadhaar photo.</p>"""),
        ("protean", "Protean (NSDL) photo specifications", "__SPEC_pan_protean__" + """
<p>Protean asks for a colour photo of 3.5 cm (height) × 2.5 cm (width) scanned at 200 DPI. At that resolution, 2.5 × 3.5 cm works out to 197 × 276 pixels, which is exactly what our preset produces. The file is compressed to stay under 50 KB.</p>"""),
        ("utiitsl", "UTIITSL photo specifications", "__SPEC_pan_uti__" + """
<p>UTIITSL's online form uses a small square photo. Most published guidance gives 213 × 213 pixels at 300 DPI with a cap of around 30 KB; the preset uses those values.</p>"""),
        ("signature", "Signature size", "__SPEC_sig_pan__" + """
<p>Sign in black ink on plain white paper, photograph or scan it, then crop tightly around the signature. Use the same signature you'll use for banking and tax work — it is printed on the card. See the <a href="/blog/signature-size-guide.html">signature guide</a> for scanning tips.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES),
        ("rejected", "Why PAN photos get rejected", """
<ul>
<li><strong>Photo and signature swapped</strong> — the most common slip. Check each upload box before submitting.</li>
<li><strong>Old or unclear photo</strong> — a blurry phone shot or a photo of a printed photo.</li>
<li><strong>Signature on lined paper</strong> or with the date written beside it.</li>
<li><strong>File over the limit</strong> — the portal silently refuses files above 50 KB (Protean) or 30 KB (UTIITSL).</li>
</ul>"""),
    ],
    faqs=[
        ("Is the PAN card photo size 2.5 × 3.5 cm or 3.5 × 4.5 cm?", "For PAN it is 2.5 cm wide × 3.5 cm high. 3.5 × 4.5 cm is the general passport-size used by many other forms."),
        ("What is the PAN card photo size in pixels?", "For Protean (NSDL) it is 197 × 276 pixels at 200 DPI, under 50 KB. For UTIITSL it is a square 213 × 213 pixels at 300 DPI."),
        ("Can I change my PAN card photo online?", "Yes. Apply for “Changes or Correction in PAN data” on Protean or UTIITSL and tick the photo mismatch option. Choose the scanned-images route so you can upload a new photo."),
        ("Do I need a photo for instant e-PAN?", "No. Instant e-PAN uses your Aadhaar details, including the Aadhaar photo."),
    ],
    sources=[("Protean (NSDL) PAN services", "https://www.protean-tinpan.com/"),
             ("UTIITSL PAN services", "https://www.pan.utiitsl.com/"),
             ("Income Tax e-filing portal (instant e-PAN)", "https://www.incometax.gov.in/")],
    related=["signature-size-guide.html", "voter-id-photo-size.html", "photo-not-required.html"],
)

guide(
    slug="voter-id-photo-size.html", category="ID & tax", short="Voter ID (EPIC) photo",
    card="Form 6 & Form 8 on the ECI portal", presets=["voter"],
    title="Voter ID Photo Size 2026 — Form 6 & Form 8 Upload Guide | ilovephoto.in",
    h1="Voter ID photo size for Form 6 and Form 8",
    desc="Photo size for a new Voter ID (Form 6) or photo correction (Form 8) on voters.eci.gov.in and the Voter Helpline app — specs, rules and a free converter.",
    lede="When you register as a new voter (Form 6) or correct your details (Form 8) online, you upload your own passport-size photo. It is printed on your EPIC card, so a clear photo matters.",
    sections=[
        ("specs", "Photo specifications", "__SPEC_voter__" + """
<p>The ECI asks for a recent passport-size colour photo (3.5 × 4.5 cm) with a plain white background showing your full face. Published file limits vary between guides, so the preset keeps the file under 100 KB — small enough for every limit we've seen, while still sharp enough to print.</p>"""),
        ("where", "Where you upload it", """
<ul>
<li><strong>Form 6</strong> — new registration, including first-time voters turning 18.</li>
<li><strong>Form 8</strong> — correction of entries, including replacing the photo, or shifting your address.</li>
<li>Both are available on <a href="https://voters.eci.gov.in/" rel="noopener">voters.eci.gov.in</a> and the Voter Helpline app.</li>
</ul>
<p>If you apply offline at your Booth Level Officer, you attach a printed passport-size photo instead — use the converter's <em>Print sheet</em> to get several on one A4 page.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES),
        ("tips", "Getting the photo approved", """
<ul>
<li>Use the same look you'll have at the polling booth — the photo is used to identify you.</li>
<li>Don't upload a photo of your old voter card or another ID — it will be blurry and is often rejected.</li>
<li>Check the preview before submitting: the app doesn't let you replace the photo after submission without filing Form 8.</li>
</ul>"""),
    ],
    faqs=[
        ("What is the voter ID photo size?", "A passport-size colour photo, 3.5 × 4.5 cm, on a white background. Our preset outputs 413 × 531 pixels at 300 DPI, under 100 KB."),
        ("How do I change the photo on my voter ID?", "File Form 8 on voters.eci.gov.in or the Voter Helpline app, choose “Correction of entries”, select photograph and upload the new photo."),
        ("Can I use a selfie?", "Only if it meets the rules: front-facing, plain light background, even light and no filters. Hold the phone at eye level, or ask someone to take it from about 1.5 m away."),
    ],
    sources=[("Voters' Service Portal (ECI)", "https://voters.eci.gov.in/")],
    related=["pan-card-photo-size.html", "take-passport-photo-at-home.html", "photo-size-dpi-kb-explained.html"],
)

guide(
    slug="driving-licence-photo-size.html", category="ID & tax", short="Driving licence photo",
    card="Learner's licence on Sarathi Parivahan", presets=["dl"],
    title="Driving Licence Photo Size 2026 — Sarathi Parivahan Upload | ilovephoto.in",
    h1="Learner's & driving licence photo size (Sarathi)",
    desc="Photo size for the learner's licence and driving licence application on Sarathi Parivahan — 10–20 KB, 420 × 525 px — plus when the RTO takes the photo for you.",
    lede="On Sarathi Parivahan, the photo upload step mostly comes up for the learner's licence. For the permanent driving licence, many RTOs capture your photo at the test — your state's flow decides which.",
    sections=[
        ("specs", "Photo specifications", "__SPEC_dl__" + """
<p>The Sarathi upload step is known for a strict and small size window: the error commonly reported by applicants is that the file must be between 10 KB and 20 KB. The preset targets that range at 420 × 525 pixels. If your state's page shows a different limit, create a custom preset with those numbers.</p>"""),
        ("when", "When you'll be asked for a photo", """
<ul>
<li><strong>Learner's licence (LL)</strong> — usually upload photo and signature online, unless you complete Aadhaar e-KYC, in which case some states use the Aadhaar photo.</li>
<li><strong>Driving licence (DL)</strong> — many RTOs take your photo and signature on a camera at the time of the driving test.</li>
<li><strong>Renewal / duplicate</strong> — depends on the state; some ask for an upload, some reuse the photo on record.</li>
</ul>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES),
        ("errors", "Fixing common upload errors", """
<ul>
<li><strong>“File size should be between 10 KB and 20 KB”</strong> — use the preset; it raises or lowers compression to land inside the window.</li>
<li><strong>Photo looks stretched</strong> — you resized without keeping the 4:5 shape. Crop first, then resize.</li>
<li><strong>Upload button does nothing</strong> — the portal accepts .jpg/.jpeg only, not .png or .heic.</li>
</ul>"""),
    ],
    faqs=[
        ("What size photo is required for a learner's licence?", "Sarathi expects a JPEG between 10 KB and 20 KB. Our preset outputs 420 × 525 pixels inside that range."),
        ("Do I need a photo for a permanent driving licence?", "Often not — many RTOs capture it at the driving test. Check your appointment slip or state transport website."),
        ("What about the signature?", "Sarathi also asks for a signature on the learner's licence form. Limits vary by state; check the on-screen size and use a custom preset. See the signature guide for scanning tips."),
    ],
    sources=[("Sarathi Parivahan (MoRTH)", "https://sarathi.parivahan.gov.in/")],
    related=["signature-size-guide.html", "voter-id-photo-size.html", "photo-size-dpi-kb-explained.html"],
)

guide(
    slug="neet-photo-size.html", category="Exams & jobs", short="NEET UG photo",
    card="Passport, postcard & live photo", presets=["neet", "neet_pc", "sig_neet"],
    title="NEET UG Photo Size 2026 — Passport, Postcard & Signature | ilovephoto.in",
    h1="NEET UG photo, postcard photo and signature size",
    desc="NEET UG photo requirements: passport-size photo and 4×6 postcard photo (10–200 KB each), signature size, the new live photo capture, and how to keep all three consistent.",
    lede="NEET UG asks for three images of you: a live photo captured in the form, a passport-size photo and a 4 × 6 inch postcard photo. The two uploaded photos must be the same recent photo and must match how you look in the live capture.",
    sections=[
        ("live", "The live photo — what changed", """
<p>From the 2026 cycle, NTA added a mandatory <strong>live photo</strong>, taken through your webcam or phone (via a QR code) while filling the form, and matched against your Aadhaar. You can't upload a file for this step, so a converter can't help — just sit facing a window against a plain wall, remove glasses and caps, and look at the camera.</p>
<p>You still upload the passport-size and postcard photos below. Use the same photo session for both, so all three images clearly look like the same person on the same day.</p>"""),
        ("passport", "Passport-size photo", "__SPEC_neet__" + """
<p>NTA specifies a colour photo with a white background, face covering about 80% of the frame, JPEG between 10 KB and 200 KB. It doesn't fix exact pixels, so the preset uses the standard 3.5 × 4.5 cm at 300 DPI.</p>"""),
        ("postcard", "Postcard-size photo (4 × 6 in)", "__SPEC_neet_pc__" + """
<p>The postcard photo is the same kind of photo at a larger 4 × 6 inch size — head and shoulders against white. Keep the file under 200 KB; the preset compresses a 1200 × 1800 pixel image to fit. You'll paste printed copies of both photos on the admit card, so keep the originals.</p>"""),
        ("signature", "Signature", "__SPEC_sig_neet__" + """
<p>Published NEET signature limits have differed between years (4–30 KB, 10–100 KB). The preset targets 10–30 KB, which satisfies both. Thumb and finger impressions are also required — scan them on white paper at good resolution and check the size window shown in the form.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES + """
<p>NEET bulletins in recent years have also required the photo to be taken in the current year — don't reuse your Class 10 or Class 12 photo.</p>"""),
    ],
    faqs=[
        ("What is the NEET photo size in KB?", "Both the passport-size and postcard photos must be JPEG files between 10 KB and 200 KB."),
        ("Is the postcard photo different from the passport photo?", "It should be the same recent photo, just at 4 × 6 inches. Different photos are a common reason for discrepancy notices."),
        ("Can I upload a photo for the live capture step?", "No. The live photo has to be taken through the camera during the application. Use good light and a plain background."),
        ("Does NEET require my name and date on the photo?", "Check the current information bulletin. If it asks for it, the converter's “Name & date strip” option adds it for you."),
        ("Is JEE Main the same?", "JEE Main 2026 also moved to live photo capture. Follow the instructions in the JEE Main bulletin; this converter only helps with photos you upload as files."),
    ],
    sources=[("NEET UG — National Testing Agency", "https://neet.nta.nic.in/")],
    related=["signature-size-guide.html", "upsc-photo-size.html", "photo-not-required.html"],
)

guide(
    slug="upsc-photo-size.html", category="Exams & jobs", short="UPSC photo",
    card="20–200 KB, name & date strip", presets=["upsc", "sig_upsc"],
    title="UPSC Photo Size 2026 — CSE, ESE, CDS, NDA Photo & Signature | ilovephoto.in",
    h1="UPSC photo and signature size",
    desc="UPSC online application photo and signature requirements: 20–200 KB JPEG, 350–1000 px, recent photo with name and date — plus a free converter that adds the strip.",
    lede="UPSC uses the same photo rules across its exams (Civil Services, ESE, CDS, NDA, CAPF and others). You upload the photo once to your One-Time Registration (OTR) profile and reuse it.",
    sections=[
        ("specs", "Photo specifications", "__SPEC_upsc__" + """
<p>UPSC instructions in recent years have given a photo size of 20–300 KB and dimensions between 350 and 1000 pixels per side. Some 2026 guidance quotes a lower 200 KB cap, so the preset stays at 20–200 KB to be safe either way.</p>"""),
        ("stamp", "Name and date on the photo", """
<p>UPSC has asked candidates to submit a photo that is recent (taken shortly before the application window opens) and that shows the <strong>candidate's name and the date the photo was taken</strong> printed below the face. Check whether the current notice still asks for this.</p>
<p>The converter has a <strong>Name &amp; date strip</strong> option. Turn it on, type your name as in your application, and pick the date the photo was taken. The strip is added below the face without squashing it.</p>"""),
        ("signature", "Signature", "__SPEC_sig_upsc__" + """
<p>Same file limits as the photo. Sign in black ink on white paper — UPSC may ask you to reproduce the signature at the exam venue, so use your normal signature.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES + """
<p>Keep the photo consistent with the one you'll carry: UPSC may ask for printed copies of the same photo at the interview or exam.</p>"""),
    ],
    faqs=[
        ("What is the UPSC photo size?", "A JPEG between 20 KB and 200–300 KB depending on the notice, with each side between 350 and 1000 pixels. Our preset outputs 600 × 750 pixels, 20–200 KB."),
        ("How old can my UPSC photo be?", "UPSC has required the photo to be taken very recently — within about 10 days before the application window opened in recent cycles. Take a fresh photo for each cycle."),
        ("How do I add my name and date to the photo?", "Pick the UPSC preset, switch on “Name & date strip”, fill in your name and the date, then download."),
    ],
    sources=[("UPSC online applications", "https://upsconline.gov.in/"), ("Union Public Service Commission", "https://upsc.gov.in/")],
    related=["signature-size-guide.html", "ibps-bank-exam-photo-size.html", "neet-photo-size.html"],
)

guide(
    slug="ibps-bank-exam-photo-size.html", category="Exams & jobs", short="IBPS & SBI bank exam photo",
    card="200 × 230 px, 20–50 KB", presets=["ibps", "sig_ibps"],
    title="IBPS & SBI Photo and Signature Size 2026 — PO, Clerk, RRB, SO | ilovephoto.in",
    h1="IBPS and SBI bank exam photo and signature size",
    desc="Photo and signature specs for IBPS PO, Clerk, RRB, SO and SBI exams: photo 200 × 230 px at 20–50 KB, signature 140 × 60 px at 10–20 KB, plus thumb and declaration.",
    lede="IBPS and SBI recruitment forms use the same scanned-document rules across PO, Clerk, RRB and SO posts. Besides the photo and signature, you upload a left thumb impression and a handwritten declaration, and capture a live photo.",
    sections=[
        ("photo", "Photograph", "__SPEC_ibps__" + """
<p>The photo is small — 200 × 230 pixels is the preferred size — but must be at least 20 KB. Very small images often come out under the minimum; the converter raises quality first and, if needed, pads the file so it reaches 20 KB without changing the picture.</p>"""),
        ("signature", "Signature", "__SPEC_sig_ibps__" + """
<p>Sign in black ink on white paper. Signatures in capital letters are not accepted. The same signature is checked against the one you give at the exam and joining.</p>"""),
        ("other", "Thumb impression, declaration and live photo", """
<ul>
<li><strong>Left thumb impression</strong> — on white paper with blue or black ink. Published sizes differ; check the on-screen limit and make a custom preset if needed.</li>
<li><strong>Handwritten declaration</strong> — copy the given text in English, in your own handwriting (not in capitals). Commonly 800 × 400 pixels, 50–100 KB.</li>
<li><strong>Live photo</strong> — captured through your webcam or phone during registration. It can't be uploaded as a file.</li>
</ul>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES),
    ],
    faqs=[
        ("What is the IBPS photo size?", "200 × 230 pixels (preferred), JPEG, 20–50 KB."),
        ("What is the IBPS signature size?", "140 × 60 pixels (preferred), JPEG, 10–20 KB."),
        ("Is the SBI photo size the same?", "Yes — SBI PO and Clerk notices use the same photo and signature specs as IBPS."),
        ("My file is only 8 KB. How do I increase it to 20 KB?", "Use the preset: it automatically raises quality and, if still under 20 KB, adds padding data so the portal accepts the file."),
    ],
    sources=[("IBPS", "https://www.ibps.in/"), ("SBI careers", "https://sbi.co.in/web/careers")],
    related=["signature-size-guide.html", "upsc-photo-size.html", "photo-size-dpi-kb-explained.html"],
)

guide(
    slug="cat-exam-photo-size.html", category="Exams & jobs", short="CAT (IIM) photo",
    card="Photo & signature for CAT registration", presets=["cat"],
    title="CAT Exam Photo Size 2026 — IIM CAT Registration | ilovephoto.in",
    h1="CAT (IIM) photo and signature size",
    desc="Photo and signature size for CAT registration on iimcat.ac.in, how to keep the photo under the limit, and what to carry on exam day.",
    lede="CAT registration asks for a recent passport-style photo and your signature. The same photo appears on your admit card, which you take to the test centre.",
    sections=[
        ("photo", "Photograph", "__SPEC_cat__" + """
<p>Guides disagree on the CAT photo limit — some quote up to 1 MB, others 80 KB. The preset produces a 1200 × 1200 pixel photo under 80 KB, which passes either limit.</p>"""),
        ("signature", "Signature", """
<p>CAT asks for a signature scan, commonly given as 80 × 35 mm in JPEG. File limits quoted online vary (80–150 KB). Check the size shown on the registration page and use a custom preset with those numbers — for example 945 × 413 px at 300 DPI for 80 × 35 mm.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES),
        ("examday", "On exam day", """
<p>Carry the printed admit card with the photo clearly visible, plus a valid photo ID. If the photo on the admit card is unclear, the candidate may be asked for extra verification — another reason to upload a sharp, well-lit photo.</p>"""),
    ],
    faqs=[
        ("What is the CAT photo size?", "A square JPEG — 1200 × 1200 pixels is commonly specified. Our preset keeps it under 80 KB so it passes every published limit."),
        ("Can I use a photo with a coloured background?", "A plain light background is recommended. Avoid busy or dark backgrounds."),
    ],
    sources=[("CAT — Indian Institutes of Management", "https://iimcat.ac.in/")],
    related=["ibps-bank-exam-photo-size.html", "upsc-photo-size.html", "signature-size-guide.html"],
)

guide(
    slug="oci-card-photo-requirements.html", category="Travel & visas", short="OCI card photo",
    card="Square photo & 3:1 signature", presets=["oci", "sig_oci"],
    title="OCI Card Photo & Signature Requirements 2026 | ilovephoto.in",
    h1="OCI card photo and signature requirements",
    desc="OCI card application photo and signature specs: square JPEG photo, 3:1 signature, size limits and the mistakes that get OCI uploads rejected.",
    lede="The OCI application on ociservices.gov.in asks for a square photo and a wide 3:1 signature, uploaded as JPEG files. You also give printed photos to the embassy or VFS centre in some countries.",
    sections=[
        ("photo", "Photo specifications", "__SPEC_oci__" + """
<p>The OCI photo is square (it corresponds to a 2 × 2 inch print). Published limits range from 200 × 200 up to 900 or 1500 pixels and from 200 KB to 1 MB. The preset uses 600 × 600 pixels under 200 KB, which fits all of them.</p>"""),
        ("signature", "Signature specifications", "__SPEC_sig_oci__" + """
<p>The signature must have a 3:1 width-to-height ratio. Minors who can't sign can use a left thumb impression; see the OCI portal for the exact rule.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES + """
<p>The OCI portal is strict about the face being centred with both ears visible and no shadow on the background.</p>"""),
    ],
    faqs=[
        ("What is the OCI photo size in pixels?", "Square, between 200 × 200 and roughly 900–1500 pixels. Our preset outputs 600 × 600 pixels under 200 KB."),
        ("Why does the OCI portal reject my signature?", "Usually the ratio. It must be 3:1 (for example 600 × 200 px). Crop tight around the signature first."),
    ],
    sources=[("OCI Services (Government of India)", "https://ociservices.gov.in/")],
    related=["india-evisa-photo.html", "us-visa-photo-requirements.html", "signature-size-guide.html"],
)

guide(
    slug="india-evisa-photo.html", category="Travel & visas", short="India e-Visa photo",
    card="Square JPEG, 10–300 KB", presets=["evisa"],
    title="India e-Visa Photo Requirements 2026 | ilovephoto.in",
    h1="India e-Visa photo requirements",
    desc="Photo requirements for an Indian e-Visa or regular visa application on indianvisaonline.gov.in: square JPEG, 10–300 KB, white background.",
    lede="Foreign nationals applying for an Indian e-Visa upload a square photo of their face. A poor photo is one of the most common reasons an e-Visa application is sent back.",
    sections=[
        ("specs", "Photo specifications", "__SPEC_evisa__" + """
<p>The official instructions ask for a JPEG with equal height and width, between 10 KB and 300 KB. Some guides quote a 1 MB limit for e-Visa; staying under 300 KB satisfies both.</p>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES + """
<p>The e-Visa photo should show the full face from the top of the hair to the chin, centred in the frame, with no border.</p>"""),
        ("passport", "Passport page scan", """
<p>The e-Visa also asks for a scan of your passport bio-data page as a PDF. That isn't a photo upload — scan it flat, in colour, and make sure the machine-readable lines at the bottom are sharp.</p>"""),
    ],
    faqs=[
        ("What size photo for an Indian e-Visa?", "Square JPEG, minimum 10 KB, maximum 300 KB. Our preset outputs 600 × 600 pixels."),
        ("Can I wear glasses?", "Avoid them. If you must, make sure there is no glare and your eyes are clearly visible."),
    ],
    sources=[("Indian Visa Online", "https://indianvisaonline.gov.in/evisa/")],
    related=["oci-card-photo-requirements.html", "us-visa-photo-requirements.html", "schengen-visa-photo-size.html"],
)

guide(
    slug="us-visa-photo-requirements.html", category="Travel & visas", short="US visa (DS-160) photo",
    card="600 × 600 px, under 240 KB", presets=["us"],
    title="US Visa Photo Requirements 2026 — DS-160 Upload from India | ilovephoto.in",
    h1="US visa photo requirements (DS-160)",
    desc="US visa photo requirements for the DS-160: square 600–1200 px JPEG under 240 KB, head size, no glasses — and how to get it right first time.",
    lede="Every US visa applicant uploads a digital photo in the DS-160 form. The same rules apply to US passport photos. The rules are strict, and the photo is checked again at the consulate.",
    sections=[
        ("specs", "Digital photo specifications", "__SPEC_us__" + """
<p>The photo must be square, between 600 × 600 and 1200 × 1200 pixels, in colour, JPEG, and 240 KB or smaller. The head (chin to top of hair) should take up 50–69% of the image height.</p>"""),
        ("rules", "Rules specific to US photos", """
<ul>
<li><strong>No glasses</strong> — not even clear prescription glasses, unless you have a medical statement.</li>
<li><strong>Taken in the last 6 months</strong> and showing your current appearance.</li>
<li><strong>White or off-white background</strong> with no shadows.</li>
<li><strong>No filters or edits</strong> — don't smooth skin or change colours.</li>
<li>Head coverings only for religious or medical reasons, with the full face visible.</li>
</ul>"""),
        ("framing", "Framing tip", """
<p>Turn on the face guide in the converter. Zoom so the oval runs from your chin to just above your hair, then drag to centre your face. Leave a little space above the head.</p>"""),
    ],
    faqs=[
        ("What size is the US visa photo?", "2 × 2 inches when printed. For the DS-160 upload: square JPEG, 600–1200 px per side, up to 240 KB."),
        ("Can I wear glasses in a US visa photo?", "No. Glasses have not been allowed in US visa photos since 2016, except with a medical statement."),
        ("What if the DS-160 photo tool rejects my photo?", "You can continue and bring a printed 2 × 2 inch photo to your visa appointment, but it is better to fix the upload: check the head size and background first."),
    ],
    sources=[("US Department of State — photo requirements", "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html")],
    related=["schengen-visa-photo-size.html", "india-evisa-photo.html", "oci-card-photo-requirements.html"],
)

guide(
    slug="schengen-visa-photo-size.html", category="Travel & visas", short="Schengen visa photo",
    card="35 × 45 mm prints", presets=["schengen"],
    title="Schengen Visa Photo Size 2026 — 35 × 45 mm Print Guide | ilovephoto.in",
    h1="Schengen visa photo size (35 × 45 mm)",
    desc="Schengen visa photo requirements for applicants from India: 35 × 45 mm ICAO-standard print, face 70–80% of the frame — and how to print your own.",
    lede="Most Schengen countries ask you to bring printed 35 × 45 mm photos to your VFS or embassy appointment. Because you print them yourself, you control the size — which is where this converter helps.",
    sections=[
        ("specs", "Photo specifications", "__SPEC_schengen__" + """
<p>Schengen photos follow the ICAO standard used for European passports: 35 mm wide × 45 mm high, with the face (chin to crown) taking 70–80% of the height — about 32–36 mm.</p>"""),
        ("print", "Printing at home or at a shop", """
<ol class="steps-list">
<li>Pick the Schengen preset and frame your face using the face guide.</li>
<li>Click <strong>Print sheet</strong>. The converter fills an A4 page with photos at the exact 35 × 45 mm size.</li>
<li>In the print dialog, set scale to <strong>100% / actual size</strong> (not “fit to page”).</li>
<li>Print on photo paper, or take the downloaded file to a print shop and ask for actual-size printing.</li>
<li>Measure one photo with a ruler — it should be exactly 35 mm wide.</li>
</ol>"""),
        ("rules", "Photo rules", COMMON_PHOTO_RULES + """
<p>Some countries (for example Germany and France) are strict about head size and background. Check the checklist from the embassy or VFS centre for your destination.</p>"""),
    ],
    faqs=[
        ("How many photos do I need for a Schengen visa?", "Usually one or two, depending on the country. Check your embassy or VFS checklist."),
        ("Is a 2 × 2 inch photo acceptable?", "No. Schengen photos must be 35 × 45 mm. 2 × 2 inch is the US size."),
    ],
    sources=[("VFS Global — visa application centres", "https://www.vfsglobal.com/")],
    related=["us-visa-photo-requirements.html", "uk-passport-photo-size.html", "take-passport-photo-at-home.html"],
)

guide(
    slug="uk-passport-photo-size.html", category="Travel & visas", short="UK passport photo",
    card="Online application, min 600 × 750 px", presets=["uk"],
    title="UK Passport Photo Size 2026 — Online Application Rules | ilovephoto.in",
    h1="UK passport photo size (online application)",
    desc="Digital photo requirements for applying for or renewing a UK passport online: at least 600 × 750 pixels, 50 KB–10 MB, plain light background.",
    lede="British citizens applying or renewing online upload a digital photo, which you can take yourself. (UK <em>visa</em> applicants have their photo taken at the visa application centre, so they don't need this.)",
    sections=[
        ("specs", "Digital photo specifications", "__SPEC_uk__" + """
<p>GOV.UK asks for a colour photo at least 600 pixels wide and 750 pixels tall, between 50 KB and 10 MB, taken in the last month. The preset outputs 900 × 1125 pixels, comfortably above the minimum.</p>"""),
        ("rules", "Rules specific to UK photos", """
<ul>
<li>Plain, light-coloured background that contrasts with you — cream and light grey work well.</li>
<li>Include head, shoulders and upper body; don't crop too tight — the online checker crops for you.</li>
<li>Plain expression, mouth closed, eyes open, no hair across the eyes.</li>
<li>Avoid glasses unless necessary; never sunglasses or tinted lenses.</li>
<li>Not edited with software (no filters or retouching).</li>
</ul>"""),
    ],
    faqs=[
        ("Can I take my own UK passport photo?", "Yes, for online applications. Ask someone else to take it — selfies are not accepted."),
        ("Is a UK visa photo the same?", "UK visa applicants usually have their photo taken at the visa centre during biometrics, so no upload is needed."),
    ],
    sources=[("GOV.UK — photos for passports", "https://www.gov.uk/photos-for-passports")],
    related=["schengen-visa-photo-size.html", "us-visa-photo-requirements.html", "take-passport-photo-at-home.html"],
)

guide(
    slug="linkedin-profile-photo-size.html", category="Profile", short="LinkedIn / résumé photo",
    card="Square, 400–800 px", presets=["linkedin"],
    title="LinkedIn Profile Photo Size 2026 — and Résumé Photos | ilovephoto.in",
    h1="LinkedIn profile photo size (and résumé photos)",
    desc="Best LinkedIn profile photo size, how to frame a professional headshot with your phone, and when to add a photo to an Indian résumé.",
    lede="LinkedIn accepts large photos, but displays them as a small circle. A square 800 × 800 pixel image, framed tight on your face, stays sharp everywhere it appears.",
    sections=[
        ("specs", "Recommended size", "__SPEC_linkedin__" + """
<p>LinkedIn recommends at least 400 × 400 pixels; larger is fine. Because the photo is shown as a circle, keep your face in the centre and leave some space around your head.</p>"""),
        ("tips", "What makes a good profile photo", """
<ul>
<li>Your face takes up about 60% of the frame.</li>
<li>Soft daylight from the front; avoid harsh overhead light.</li>
<li>Plain or softly blurred background.</li>
<li>Dress as you would for work in your field.</li>
<li>Smile naturally — unlike ID photos, a friendly expression helps here.</li>
</ul>"""),
        ("resume", "Résumé photos", """
<p>Many Indian employers and government job forms still expect a passport-size photo on the CV. Use a 3.5 × 4.5 cm image (the Voter ID preset produces one) and place it at the top-right.</p>"""),
    ],
    faqs=[
        ("What is the LinkedIn profile photo size?", "Minimum 400 × 400 pixels. 800 × 800 pixels is a good choice."),
        ("Should I use my passport photo on LinkedIn?", "You can, but a warmer, well-lit headshot with a natural smile usually works better."),
    ],
    sources=[("LinkedIn Help", "https://www.linkedin.com/help/linkedin")],
    related=["take-passport-photo-at-home.html", "photo-size-dpi-kb-explained.html", "pan-card-photo-size.html"],
)

guide(
    slug="signature-size-guide.html", category="Signatures", short="Signature size guide",
    card="PAN, NEET, UPSC, IBPS, OCI", presets=["sig_pan", "sig_neet", "sig_upsc", "sig_ibps", "sig_oci"],
    title="Signature Size for Online Forms 2026 — PAN, NEET, UPSC, IBPS, OCI | ilovephoto.in",
    h1="Signature size for online application forms",
    desc="How to scan your signature and resize it for PAN, NEET, UPSC, IBPS/SBI and OCI forms — pixel sizes, KB limits, and how to make it crisp and readable.",
    lede="Almost every form that asks for a photo also asks for your signature. Signatures are where most upload errors happen: wrong shape, too small a file, or a grey shadowy background.",
    sections=[
        ("how", "How to capture a clean signature", """
<ol class="steps-list">
<li>Sign in the middle of a plain white A4 sheet with a black ball-point or gel pen. Sign at your normal size.</li>
<li>Photograph it in daylight, holding the phone directly above the paper so the signature isn't slanted.</li>
<li>In the converter, pick your signature preset, then use <strong>Crop</strong> to cut tight around the signature.</li>
<li>Raise <strong>Contrast</strong> (about 150–180%) and <strong>Brightness</strong> a little until the paper is pure white and the ink is dark.</li>
<li>Download and check the file: the signature should fill most of the box and be easy to read.</li>
</ol>"""),
        ("pan", "PAN card signature (Protean)", "__SPEC_sig_pan__"),
        ("neet", "NEET UG signature", "__SPEC_sig_neet__"),
        ("upsc", "UPSC signature", "__SPEC_sig_upsc__"),
        ("ibps", "IBPS / SBI signature", "__SPEC_sig_ibps__" + """
<p>Signatures in CAPITAL letters are not accepted for bank exams.</p>"""),
        ("oci", "OCI signature", "__SPEC_sig_oci__"),
        ("mistakes", "Common signature mistakes", """
<ul>
<li><strong>Lots of empty paper around the signature</strong> — the signature becomes tiny after resizing. Crop tight.</li>
<li><strong>Grey background</strong> — shadows from your phone. Increase brightness and contrast.</li>
<li><strong>Signature on lined or coloured paper</strong> — use plain white.</li>
<li><strong>Different from your usual signature</strong> — it may be compared with your signature at the exam or bank.</li>
</ul>"""),
    ],
    faqs=[
        ("Should my signature be in black or blue ink?", "Black is safest — it scans with the most contrast. Most forms accept either."),
        ("How do I reduce my signature file to under 20 KB?", "Pick a signature preset — it compresses to fit the limit automatically. If a form has a minimum size, the converter also makes sure the file isn't too small."),
    ],
    sources=[("Protean (NSDL) PAN", "https://www.protean-tinpan.com/"), ("NEET UG — NTA", "https://neet.nta.nic.in/"),
             ("UPSC online", "https://upsconline.gov.in/"), ("IBPS", "https://www.ibps.in/"), ("OCI Services", "https://ociservices.gov.in/")],
    related=["pan-card-photo-size.html", "ibps-bank-exam-photo-size.html", "photo-size-dpi-kb-explained.html"],
)

# Search-facing copy: short titles (≤60 chars with suffix), descriptions ≤155 chars,
# and a one-paragraph direct answer shown at the top of each guide (featured
# snippets, AI overviews and answer engines quote this).
SEO = {
    "pan-card-photo-size.html": (
        "PAN Card Photo Size 2026: Protean & UTIITSL",
        "PAN card photo size: 197×276 px (2.5×3.5 cm, 200 DPI) under 50 KB for Protean; 213×213 px under 30 KB for UTIITSL. Signature size and rules.",
        "For a <strong>Protean (NSDL)</strong> PAN application, the photo is <strong>2.5 × 3.5 cm at 200 DPI — 197 × 276 pixels, JPEG, under 50 KB</strong>. For <strong>UTIITSL</strong> it is a square <strong>213 × 213 pixels, under about 30 KB</strong>. The Protean signature is 4.5 × 2 cm at 200 DPI (354 × 157 px), under 50 KB. No upload is needed if you apply with Aadhaar e-KYC."),
    "voter-id-photo-size.html": (
        "Voter ID Photo Size 2026 (Form 6 & Form 8)",
        "Voter ID photo size for Form 6 and Form 8: passport size 3.5×4.5 cm, white background, JPEG. Get a 413×531 px file under 100 KB free.",
        "The Voter ID (EPIC) photo for <strong>Form 6 or Form 8</strong> is a recent <strong>passport-size colour photo, 3.5 × 4.5 cm, on a plain white background</strong>, uploaded as JPEG. At 300 DPI that is <strong>413 × 531 pixels</strong>; keeping it under 100 KB works with every published limit."),
    "driving-licence-photo-size.html": (
        "Driving Licence Photo Size 2026 (Sarathi)",
        "Sarathi Parivahan learner's licence photo: JPEG between 10 KB and 20 KB, 420×525 px recommended. When the RTO takes the photo instead.",
        "For a <strong>learner's licence on Sarathi Parivahan</strong>, upload a <strong>JPEG between 10 KB and 20 KB</strong>; <strong>420 × 525 pixels</strong> is a safe size. For the permanent driving licence, many RTOs take your photo at the driving test, so no upload is needed."),
    "neet-photo-size.html": (
        "NEET UG Photo Size 2026: Passport & Postcard",
        "NEET UG 2026 photo size: passport photo and 4×6 postcard photo, JPEG 10–200 KB each, white background, plus signature and live photo rules.",
        "NEET UG needs a <strong>passport-size photo and a 4 × 6 inch postcard photo, each a JPEG between 10 KB and 200 KB</strong>, on a white background with the face covering about 80% of the frame. Since 2026 a <strong>live photo</strong> is also captured by webcam in the form. Use the same recent photo for both uploads."),
    "upsc-photo-size.html": (
        "UPSC Photo Size 2026: Photo, Signature, Date",
        "UPSC photo size: JPEG 20–200 KB, 350–1000 px per side, recent, with name and date below the face when required. Free resizer adds the strip.",
        "The UPSC photo is a <strong>JPEG between 20 KB and 200–300 KB</strong> (depending on the notice) with each side <strong>between 350 and 1000 pixels</strong>. It must be very recent and, when the notice asks, show <strong>your name and the date the photo was taken</strong> below the face. The signature follows the same limits."),
    "ibps-bank-exam-photo-size.html": (
        "IBPS & SBI Photo and Signature Size 2026",
        "IBPS and SBI exam photo: 200×230 px, JPEG, 20–50 KB. Signature: 140×60 px, 10–20 KB. Thumb impression, declaration and live photo rules.",
        "For IBPS (PO, Clerk, RRB, SO) and SBI forms, the <strong>photo is 200 × 230 pixels, JPEG, 20–50 KB</strong> and the <strong>signature is 140 × 60 pixels, JPEG, 10–20 KB</strong>. You also upload a left thumb impression and a handwritten declaration, and capture a live photo."),
    "cat-exam-photo-size.html": (
        "CAT Exam Photo Size 2026 (IIM CAT)",
        "CAT registration photo: 1200×1200 px JPEG. Keep it under 80 KB to pass every published limit. Signature size and exam-day tips.",
        "The CAT registration photo is commonly specified as <strong>1200 × 1200 pixels, JPEG</strong>. Published file limits differ (80 KB or 1 MB), so <strong>a file under 80 KB</strong> passes either. The signature is usually given as 80 × 35 mm."),
    "oci-card-photo-requirements.html": (
        "OCI Card Photo & Signature Size 2026",
        "OCI photo: square JPEG, 200×200 px minimum; 600×600 px under 200 KB is safe. OCI signature must be 3:1 width to height.",
        "The OCI photo is a <strong>square JPEG, at least 200 × 200 pixels</strong> — <strong>600 × 600 pixels under 200 KB</strong> fits every published limit. The OCI <strong>signature must have a 3:1 width-to-height ratio</strong>, for example 600 × 200 pixels."),
    "india-evisa-photo.html": (
        "India e-Visa Photo Requirements 2026",
        "India e-Visa photo: square JPEG, height equal to width, 10 KB to 300 KB, plain white background. Free private resizer.",
        "The Indian e-Visa photo must be a <strong>square JPEG (height equal to width) between 10 KB and 300 KB</strong>, showing the full face on a plain white background, centred, with no border."),
    "us-visa-photo-requirements.html": (
        "US Visa Photo Size 2026 (DS-160 Upload)",
        "US visa DS-160 photo: square JPEG 600×600 to 1200×1200 px, max 240 KB, head 50–69% of height, no glasses, taken in the last 6 months.",
        "The DS-160 photo must be a <strong>square colour JPEG, 600 × 600 to 1200 × 1200 pixels, 240 KB or smaller</strong>, with the head taking <strong>50–69% of the image height</strong>. No glasses, white or off-white background, taken in the last 6 months."),
    "schengen-visa-photo-size.html": (
        "Schengen Visa Photo Size: 35×45 mm Guide",
        "Schengen visa photo: 35×45 mm print, face 70–80% of height (32–36 mm), light background. Print correct-size photos at home on A4.",
        "A Schengen visa photo is a <strong>35 × 45 mm print</strong> with the face (chin to crown) taking <strong>70–80% of the height — about 32–36 mm</strong> — on a plain light background. Most countries ask you to bring one or two printed photos to the VFS or embassy appointment."),
    "uk-passport-photo-size.html": (
        "UK Passport Photo Size (Online) 2026",
        "UK passport digital photo: at least 600×750 px, 50 KB to 10 MB, plain light background, taken in the last month by someone else.",
        "For an online UK passport application, the photo must be <strong>at least 600 pixels wide and 750 pixels tall, between 50 KB and 10 MB</strong>, in colour, against a plain light background, and taken in the last month."),
    "linkedin-profile-photo-size.html": (
        "LinkedIn Profile Photo Size 2026",
        "LinkedIn profile photo size: minimum 400×400 px, 800×800 px recommended, up to 8 MB. How to take a professional headshot with a phone.",
        "LinkedIn profile photos should be <strong>at least 400 × 400 pixels; 800 × 800 pixels</strong> stays sharp everywhere. Files up to 8 MB are accepted. Keep your face centred because the photo is shown as a circle."),
    "signature-size-guide.html": (
        "Signature Size for Online Forms 2026",
        "Signature size for PAN (354×157 px), NEET (10–30 KB), UPSC (20–200 KB), IBPS (140×60 px, 10–20 KB) and OCI (3:1). How to scan it cleanly.",
        "Common signature sizes: <strong>PAN (Protean) 354 × 157 px under 50 KB</strong>; <strong>IBPS/SBI 140 × 60 px, 10–20 KB</strong>; <strong>NEET 10–30 KB</strong>; <strong>UPSC 20–200 KB, 350–1000 px</strong>; <strong>OCI 3:1 ratio</strong>. Sign in black ink on white paper and crop tight before resizing."),
}
for g in GUIDES:
    g["title"], g["desc"], g["answer"] = SEO[g["slug"]]
    g["title"] += " | ilovephoto.in"

GUIDES_BY_SLUG = {g["slug"]: g for g in GUIDES}

# Article-style pages that aren't tied to a single preset
ARTICLES = [
    dict(slug="photo-not-required.html", short="When you don't upload a photo",
         card="Aadhaar, passport, JEE, SSC"),
    dict(slug="photo-size-dpi-kb-explained.html", short="Pixels, DPI & KB explained",
         card="Why “3.5 × 4.5 cm” isn't enough"),
    dict(slug="take-passport-photo-at-home.html", short="Take a photo at home",
         card="Phone, light, background, framing"),
]
for a in ARTICLES:
    GUIDES_BY_SLUG[a["slug"]] = a


def render_guide(g):
    body_sections = ""
    for sid, title, content in g["sections"]:
        for pid in g["presets"]:
            token = f"__SPEC_{pid}__"
            if token in content:
                content = content.replace(token, spec_table(pid, STATED[pid]))
        body_sections += f'<h2 id="{sid}">{title}</h2>\n{content}\n'
    main_pid = g["presets"][0]
    first = g["sections"][0]
    sources = "".join(f'<li><a href="{u}" rel="noopener">{esc(n)}</a></li>' for n, u in g["sources"])
    body = f"""<div class="wrap narrow page">
<div class="crumbs"><a href="/">Home</a> › <a href="/blog/">Guides</a> › {esc(g["short"])}</div>
<article class="prose">
<h1>{g["h1"]}</h1>
<div class="answer"><strong>Quick answer</strong><p>{g["answer"]}</p></div>
<p class="lede">{g["lede"]}</p>
<p class="meta">Last reviewed <time datetime="{LASTMOD}">{REVIEWED}</time> · {esc(g["category"])} · <a href="/blog/photo-size-chart.html">All sizes in one chart</a></p>
{toc(g["sections"] + [("faq", "FAQ", "")])}
{cta(main_pid, "Resize your photo for this form")}
{body_sections}
<h2 id="faq">Frequently asked questions</h2>
{faq_html(g["faqs"])}
<div class="note note-warn"><strong>Always check the portal</strong><p>Limits on government portals change between application cycles. If the form shows a different size, use those numbers — the converter's <em>Create custom preset</em> lets you enter any size.</p></div>
<div class="sources"><strong>Official sources</strong><ul>{sources}</ul></div>
{related(g["related"])}
</article>
</div>"""
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["desc"],
         "abstract": strip_tags(g["answer"]), "image": og_url("blog/" + g["slug"]),
         "datePublished": PUBLISHED, "dateModified": LASTMOD, "author": {"@type": "Organization", "name": "ilovephoto.in", "url": SITE},
         "publisher": {"@type": "Organization", "name": "ilovephoto.in", "url": SITE},
         "mainEntityOfPage": f'{SITE}/blog/{g["slug"]}'},
        faq_ld(g["faqs"]),
        crumbs_ld([("Home", "/"), ("Guides", "/blog/"), (g["short"], "/blog/" + g["slug"])]),
    ]
    page("blog/" + g["slug"], g["title"], g["desc"], body, active="/blog/", jsonld=ld,
         og=(g["short"] + " — size guide",
             f'{P[main_pid]["w"]} × {P[main_pid]["h"]} px · {kb_range(P[main_pid])} · reviewed {REVIEWED}'))


# What each portal publicly states — shown next to what the preset produces.
STATED = {
    "pan_protean": [("Dimensions", "3.5 cm (h) × 2.5 cm (w)"), ("Resolution", "200 DPI"), ("Format", "JPEG, colour"), ("File size", "Up to 50 KB")],
    "pan_uti": [("Dimensions", "213 × 213 px <small>(commonly published)</small>"), ("Resolution", "300 DPI"), ("Format", "JPEG"), ("File size", "Around 30 KB max")],
    "sig_pan": [("Dimensions", "2 cm (h) × 4.5 cm (w)"), ("Resolution", "200 DPI"), ("Format", "JPEG, black & white"), ("File size", "Up to 50 KB")],
    "voter": [("Dimensions", "Passport size, 3.5 × 4.5 cm"), ("Format", "JPEG"), ("File size", "Varies by guide <small>(we stay under 100 KB)</small>"), ("Background", "Plain white")],
    "dl": [("Format", "JPEG"), ("File size", "10–20 KB <small>(as reported by the portal's error message)</small>"), ("Background", "Plain white")],
    "neet": [("Dimensions", "Passport size <small>(no pixel size fixed)</small>"), ("Format", "JPEG"), ("File size", "10–200 KB"), ("Background", "White, face ~80% of frame")],
    "neet_pc": [("Dimensions", "4 × 6 inches"), ("Format", "JPEG"), ("File size", "10–200 KB"), ("Background", "White")],
    "sig_neet": [("Format", "JPEG"), ("File size", "Quoted as 4–30 KB or 10–100 KB <small>(we use the overlap)</small>")],
    "upsc": [("Dimensions", "350–1000 px each side"), ("Format", "JPEG"), ("File size", "20–300 KB <small>(200 KB in some 2026 guidance)</small>"), ("Other", "Recent; name &amp; date below the face when asked")],
    "sig_upsc": [("Dimensions", "350–1000 px each side"), ("Format", "JPEG"), ("File size", "20–300 KB")],
    "ibps": [("Dimensions", "200 × 230 px (preferred)"), ("Format", "JPEG"), ("File size", "20–50 KB")],
    "sig_ibps": [("Dimensions", "140 × 60 px (preferred)"), ("Format", "JPEG"), ("File size", "10–20 KB")],
    "cat": [("Dimensions", "1200 × 1200 px <small>(commonly published)</small>"), ("Format", "JPEG"), ("File size", "Quoted as 80 KB or 1 MB")],
    "oci": [("Dimensions", "Square, 200 × 200 px minimum"), ("Format", "JPEG"), ("File size", "Quoted between 200 KB and 1 MB")],
    "sig_oci": [("Dimensions", "3:1 ratio (width : height)"), ("Format", "JPEG")],
    "evisa": [("Dimensions", "Square (height = width)"), ("Format", "JPEG"), ("File size", "10–300 KB")],
    "us": [("Dimensions", "Square, 600–1200 px"), ("Format", "JPEG, colour"), ("File size", "Up to 240 KB"), ("Head size", "50–69% of image height")],
    "schengen": [("Dimensions", "35 × 45 mm print"), ("Head size", "70–80% of height (32–36 mm)"), ("Background", "Light grey or white")],
    "uk": [("Dimensions", "At least 600 × 750 px"), ("File size", "50 KB – 10 MB"), ("Background", "Plain, light-coloured")],
    "linkedin": [("Dimensions", "At least 400 × 400 px"), ("File size", "Up to 8 MB")],
}


# ─────────────────────────────────────────────────────────────────────────────
# Stand-alone articles
# ─────────────────────────────────────────────────────────────────────────────
def render_articles():
    # ── When you don't upload a photo
    faqs = [
        ("Can I upload my own photo for Aadhaar?", "No. Aadhaar photos are captured by the operator at an Aadhaar enrolment or update centre. To change it, book a biometric update at a centre."),
        ("Do I need to bring a photo to the Passport Seva Kendra?", "Adults don't — the photo is taken at the PSK or POPSK. Parents of very young children are sometimes asked to bring a recent photo; check your appointment instructions."),
        ("Why can't I upload a photo for JEE Main or SSC?", "They now use live photo capture through your webcam or phone to stop impersonation and reuse of old photos."),
    ]
    body = f"""<div class="wrap narrow page">
<div class="crumbs"><a href="/">Home</a> › <a href="/blog/">Guides</a> › When you don't upload a photo</div>
<article class="prose">
<h1>Forms where you don't upload your own photo</h1>
<p class="lede">For some documents, the photo is taken for you — at a centre or through a live camera check. Resizing a photo won't help with these, so here's what actually happens and how to prepare.</p>
<p class="meta">Last reviewed {REVIEWED}</p>
<table class="data-table"><thead><tr><th>Document / exam</th><th>How the photo is taken</th></tr></thead><tbody>
<tr><td><a href="#aadhaar">Aadhaar</a></td><td>Captured at the enrolment / update centre</td></tr>
<tr><td><a href="#passport">Indian passport (in India)</a></td><td>Captured at the PSK / POPSK during your appointment</td></tr>
<tr><td><a href="#live">JEE Main, SSC</a></td><td>Live webcam / phone capture inside the application</td></tr>
<tr><td><a href="#live">NEET UG, IBPS</a></td><td>Live capture <em>and</em> uploaded photos — see their guides</td></tr>
<tr><td><a href="#other">NREGA job card, UK &amp; Schengen visa biometrics</a></td><td>Taken by officials or at the visa centre</td></tr>
<tr><td><a href="#other">PAN via Aadhaar e-KYC / instant e-PAN</a></td><td>Copied from your Aadhaar record</td></tr>
</tbody></table>

<h2 id="aadhaar">Aadhaar</h2>
<p>Your Aadhaar photo is part of your biometric record, taken by a trained operator at an Aadhaar Seva Kendra or enrolment centre. You can't upload a photo online — not for a new Aadhaar, and not to change an existing one.</p>
<p><strong>To change your Aadhaar photo:</strong> book an appointment on the UIDAI website (or walk in), fill the update form at the centre, and the operator takes a new photo along with fingerprints and iris scan. A fee applies for biometric updates.</p>
<p><strong>Tip:</strong> because your Aadhaar photo is reused by other services (instant e-PAN, some DigiLocker and exam e-KYC flows), it's worth updating if it's very old.</p>

<h2 id="passport">Indian passport</h2>
<p>For fresh passports and re-issue in India, your photo is captured at the Passport Seva Kendra or Post Office PSK at the same counter as your fingerprints. Adults don't need to carry photos. Dress in plain, darker clothes (the background is white) and avoid heavy jewellery.</p>
<p>Applying from abroad? Rules differ by embassy or outsourcing centre — follow your embassy's checklist. If they ask for printed photos, use a custom preset with the size they give.</p>

<h2 id="live">Exams with live photo capture</h2>
<p>To stop impersonation, many exams now take your photo live through the camera during the application, and some compare it with your Aadhaar photo:</p>
<ul>
<li><strong>JEE Main</strong> (from the 2026 cycle) — live photo through webcam or the mobile QR option.</li>
<li><strong>SSC</strong> (CGL, CHSL, MTS, GD and others) — live photo inside the application; uploading a photo of a photo is treated as a violation. The <em>signature</em> is still uploaded as a file.</li>
<li><strong>NEET UG</strong> and <strong>IBPS / SBI</strong> — live capture <em>in addition to</em> uploaded photos. See the <a href="/blog/neet-photo-size.html">NEET</a> and <a href="/blog/ibps-bank-exam-photo-size.html">IBPS</a> guides.</li>
</ul>
<h3>How to pass a live photo check</h3>
<ul>
<li>Sit facing a window during the day; turn off overhead lights that cause shadows.</li>
<li>Use a plain light wall behind you.</li>
<li>Remove glasses, caps and masks; keep your hair off your face.</li>
<li>Look straight at the camera, at eye level — prop the phone or laptop up on books.</li>
<li>Look like your Aadhaar photo as far as you reasonably can (for example, same glasses-free face).</li>
</ul>

<h2 id="other">Other cases</h2>
<ul>
<li><strong>NREGA job card</strong> — the photo is taken by the Gram Panchayat during registration.</li>
<li><strong>UK and Schengen visa biometrics</strong> — UK visa photos are taken at the visa centre. For Schengen you usually bring printed photos — see the <a href="/blog/schengen-visa-photo-size.html">Schengen guide</a>.</li>
<li><strong>PAN via Aadhaar e-KYC</strong> — the photo comes from Aadhaar. Choose the scanned-images route if you want to use a different photo (<a href="/blog/pan-card-photo-size.html">PAN guide</a>).</li>
<li><strong>Ration card</strong> — online applications exist in many states, but photo specs differ by state. Use the size your state portal shows with a custom preset.</li>
</ul>
<h2 id="faq">Frequently asked questions</h2>
{faq_html(faqs)}
<div class="sources"><strong>Official sources</strong><ul>
<li><a href="https://uidai.gov.in/" rel="noopener">UIDAI (Aadhaar)</a></li>
<li><a href="https://www.passportindia.gov.in/" rel="noopener">Passport Seva</a></li>
<li><a href="https://jeemain.nta.nic.in/" rel="noopener">JEE Main — NTA</a></li>
<li><a href="https://ssc.gov.in/" rel="noopener">Staff Selection Commission</a></li>
</ul></div>
{related(["pan-card-photo-size.html", "neet-photo-size.html", "take-passport-photo-at-home.html"])}
</article></div>"""
    page("blog/photo-not-required.html", "No Photo Upload: Aadhaar, Passport, JEE, SSC | ilovephoto.in",
         "Aadhaar and Indian passport photos are taken at the centre; JEE Main and SSC use live photo capture. What happens, how to change your photo, and how to prepare.",
         body, active="/blog/", jsonld=[faq_ld(faqs), crumbs_ld([("Home", "/"), ("Guides", "/blog/"), ("When you don't upload a photo", "/blog/photo-not-required.html")])])

    # ── Pixels, DPI and KB explained
    faqs = [
        ("Does DPI change the file size?", "No. DPI is just a number stored in the file that says how big to print it. File size depends on pixel dimensions and compression."),
        ("Why is my file too small even though the photo looks fine?", "Small images (like 200 × 230 px) compress very well. If a form has a minimum KB, the converter raises quality and adds padding data to reach it."),
        ("Is PNG better than JPEG for forms?", "For photos, no — most portals only accept JPEG, and PNG files are much larger."),
    ]
    body = f"""<div class="wrap narrow page">
<div class="crumbs"><a href="/">Home</a> › <a href="/blog/">Guides</a> › Pixels, DPI &amp; KB explained</div>
<article class="prose">
<h1>Pixels, DPI and KB — what photo specs actually mean</h1>
<p class="lede">Form instructions mix three different measurements: physical size (cm or inches), pixels and file size (KB). Knowing how they relate makes most upload errors easy to fix.</p>
<p class="meta">Last reviewed {REVIEWED}</p>
<h2 id="three">The three numbers</h2>
<table class="data-table"><thead><tr><th>Measure</th><th>What it describes</th><th>Example</th></tr></thead><tbody>
<tr><td><strong>Pixels</strong></td><td>How many dots make up the image</td><td>413 × 531 px</td></tr>
<tr><td><strong>DPI</strong></td><td>How many of those dots fit in an inch when printed</td><td>300 DPI</td></tr>
<tr><td><strong>Physical size</strong></td><td>Pixels ÷ DPI — the printed size</td><td>3.5 × 4.5 cm</td></tr>
<tr><td><strong>File size (KB)</strong></td><td>How much storage the file takes, mostly decided by JPEG compression</td><td>10–200 KB</td></tr>
</tbody></table>
<h2 id="convert">Converting cm to pixels</h2>
<p>Pixels = centimetres ÷ 2.54 × DPI. So a 3.5 × 4.5 cm photo is:</p>
<ul>
<li>at <strong>300 DPI</strong>: 413 × 531 pixels</li>
<li>at <strong>200 DPI</strong>: 276 × 354 pixels</li>
</ul>
<p>If a form gives cm and DPI, you need both to get the right pixel size. If it gives only pixels, DPI usually doesn't matter for an upload.</p>
<h2 id="kb">Why file size is the usual problem</h2>
<p>Portals limit KB to keep their databases small. JPEG compression trades quality for size: the converter searches for the highest quality that still fits under the maximum, so you get the sharpest file allowed. Some forms (NEET, UPSC, IBPS, Sarathi) also set a <strong>minimum</strong>, to stop people uploading tiny, blurry images. If the image is too simple to reach that minimum, the converter adds harmless padding data to the file.</p>
<h2 id="mistakes">Common mistakes</h2>
<ul>
<li><strong>Stretching the photo to fit.</strong> Changing the shape (aspect ratio) squashes your face. Crop to the right shape first; the converter always crops instead of stretching.</li>
<li><strong>Using a screenshot.</strong> Screenshots of photos lose quality and often have the wrong size. Use the original photo.</li>
<li><strong>Photo of a printed photo.</strong> It looks dull and blurry, and live-capture exams treat it as a violation.</li>
<li><strong>Wrong format.</strong> iPhone photos are often HEIC; many portals need .jpg. The converter always outputs JPEG.</li>
<li><strong>Swapping photo and signature uploads.</strong> Check each box before submitting.</li>
</ul>
<h2 id="faq">Frequently asked questions</h2>
{faq_html(faqs)}
{related(["take-passport-photo-at-home.html", "signature-size-guide.html", "pan-card-photo-size.html"])}
</article></div>"""
    page("blog/photo-size-dpi-kb-explained.html", "Photo Size, DPI & KB Explained | ilovephoto.in",
         "What pixels, DPI, cm and KB mean in form photo instructions, how to convert cm to pixels, and why uploads get rejected for file size.",
         body, active="/blog/", jsonld=[faq_ld(faqs), crumbs_ld([("Home", "/"), ("Guides", "/blog/"), ("Pixels, DPI & KB explained", "/blog/photo-size-dpi-kb-explained.html")])])

    # ── Take a photo at home
    faqs = [
        ("Can I use my phone's portrait mode?", "Avoid it. Portrait mode blurs the background and can blur the edges of your hair and ears, which some checks reject."),
        ("Selfie or someone else?", "Ask someone else, standing 1–1.5 m away. Selfies distort the face (a bigger nose) and the arm often shows."),
        ("Can I edit out a messy background?", "This converter doesn't remove backgrounds. It's better to retake the photo against a plain wall — many portals reject edited photos."),
    ]
    body = f"""<div class="wrap narrow page">
<div class="crumbs"><a href="/">Home</a> › <a href="/blog/">Guides</a> › Take a photo at home</div>
<article class="prose">
<h1>How to take a passport-style photo at home</h1>
<p class="lede">You don't need a studio. A phone, a plain wall and a window are enough for a photo that passes for PAN, Voter ID, exams and visas.</p>
<p class="meta">Last reviewed {REVIEWED}</p>
<h2 id="setup">Set up</h2>
<ol class="steps-list">
<li><strong>Wall:</strong> stand about half a metre in front of a plain white or off-white wall. A white bedsheet pulled flat also works.</li>
<li><strong>Light:</strong> face a window in daytime. Turn off overhead lights — they cast shadows under your eyes and behind you.</li>
<li><strong>Camera:</strong> use the rear camera. Ask someone to stand 1–1.5 m away with the phone at your eye level. Don't zoom digitally.</li>
<li><strong>Clothes:</strong> plain, darker colours that contrast with the white background. No uniforms unless the form asks.</li>
</ol>
<h2 id="pose">Pose</h2>
<ul>
<li>Face the camera squarely, shoulders level.</li>
<li>Neutral expression, mouth closed, eyes open.</li>
<li>Hair away from eyes; remove glasses if the form doesn't allow them (US visa never does).</li>
<li>Take 5–10 shots and pick the sharpest.</li>
</ul>
<h2 id="convert">Turn it into a form-ready file</h2>
<ol class="steps-list">
<li>Open the <a href="/">converter</a> and upload the photo (HEIC from iPhone is fine).</li>
<li>Choose your document — the preview switches to the right shape.</li>
<li>Turn on the face guide, zoom until your face fills the oval, and drag to centre.</li>
<li>Download. The file is the right pixel size and within the KB limit.</li>
</ol>
<h2 id="checklist">Quick check before uploading</h2>
<ul>
<li>Is the background plain with no shadow behind your head?</li>
<li>Can you see both eyes clearly with no glare?</li>
<li>Is your face sharp when you zoom in?</li>
<li>Does it look like you today?</li>
</ul>
<h2 id="faq">Frequently asked questions</h2>
{faq_html(faqs)}
{related(["photo-size-dpi-kb-explained.html", "us-visa-photo-requirements.html", "neet-photo-size.html"])}
</article></div>"""
    page("blog/take-passport-photo-at-home.html", "Take a Passport-Size Photo at Home | ilovephoto.in",
         "Step-by-step: take a passport-size photo at home for PAN, Voter ID, exams and visas — background, light, pose, and how to resize it correctly.",
         body, active="/blog/", jsonld=[faq_ld(faqs), crumbs_ld([("Home", "/"), ("Guides", "/blog/"), ("Take a photo at home", "/blog/take-passport-photo-at-home.html")])])


# ─────────────────────────────────────────────────────────────────────────────
# FAQ, guides index, about, contact, legal
# ─────────────────────────────────────────────────────────────────────────────
FAQ_GROUPS = [
    ("Using the converter", [
        ("How do I use the converter?", "Upload a photo (or take one with the camera button), choose your document from the list, adjust the framing with zoom and drag, and click Download. The file is already the right size, format and KB."),
        ("Which file types can I upload?", "JPG, PNG, WebP, BMP and GIF work in every browser. HEIC (iPhone) works in browsers that can open it, such as Safari; elsewhere, set your iPhone to “Most Compatible” in Camera → Formats."),
        ("How do I frame my face correctly?", "Turn on the face guide. Zoom until your face fills the oval from chin to top of head, then drag the photo to centre it."),
        ("Can it remove or change my background?", "No. The fill colour only shows if you zoom out past the edge of the photo. For a clean background, retake the photo against a plain wall — see <a href=\"/blog/take-passport-photo-at-home.html\">how to take a photo at home</a>."),
        ("Can I add my name and date to the photo?", "Yes. Turn on “Name &amp; date strip” before downloading. It is used for UPSC and some state exams."),
        ("Can I print passport photos?", "Yes. Click Print sheet to fill an A4 page with photos at the exact physical size. Print at 100% / actual size, not “fit to page”."),
        ("My document isn't in the list.", "Click “Create custom preset” and enter the width, height, DPI and KB limits shown on the form. Custom presets are saved in your browser."),
    ]),
    ("File size and quality", [
        ("How does the converter hit the KB limit?", "It searches for the highest JPEG quality that still fits under the maximum, so you get the sharpest file allowed."),
        ("The form says the file is too small. What now?", "Use a preset with a minimum size (IBPS, NEET, UPSC, Sarathi). If an image can't reach the minimum at full quality, the converter adds harmless padding data so the portal accepts it."),
        ("Does it stretch my photo?", "Never. It crops to the right shape and scales evenly, so your face isn't squashed."),
        ("What DPI does the file have?", "The DPI value is written into the JPEG file, matching the preset. It doesn't change how the photo looks on screen."),
    ]),
    ("Privacy", [
        ("Is my photo uploaded anywhere?", "No. All processing happens in your browser using the Canvas API. Your photos and signatures never leave your device."),
        ("What do you store?", "Only custom presets you create, in your browser's local storage. The site uses Google Analytics and AdSense, which use cookies — see the <a href=\"/privacy-policy.html\">privacy policy</a>."),
        ("Does it work offline?", "Once the page has loaded, the conversion works without an internet connection."),
    ]),
    ("Documents", [
        ("Why isn't Aadhaar or the Indian passport in the list?", "For both, the photo is taken at the centre — you can't upload your own. See <a href=\"/blog/photo-not-required.html\">forms where you don't upload a photo</a>."),
        ("Why isn't JEE Main or SSC in the list?", "They now use live photo capture through your camera inside the form, so there's no photo file to prepare."),
        ("How accurate are the presets?", "They follow the instructions published by each portal, reviewed in " + REVIEWED + ". Where sources disagree, the preset uses values that satisfy all of them. Always check the form's own instructions."),
    ]),
]


def render_faq():
    blocks = ""
    all_faqs = []
    for i, (title, items) in enumerate(FAQ_GROUPS):
        blocks += f'<h2 id="g{i}">{title}</h2>\n{faq_html(items)}\n'
        all_faqs += items
    toc_html = "".join(f'<li><a href="#g{i}">{t}</a></li>' for i, (t, _) in enumerate(FAQ_GROUPS))
    body = f"""<div class="wrap narrow page">
<div class="crumbs"><a href="/">Home</a> › FAQ</div>
<article class="prose">
<h1>Frequently asked questions</h1>
<p class="lede">How the converter works, how it keeps files within limits, and what happens to your photos.</p>
<nav class="toc" aria-label="Sections"><strong>Sections</strong><ol>{toc_html}</ol></nav>
{blocks}
<div class="cta"><p>Still stuck?<span>Tell us which form you're filling and what error you see.</span></p><a class="btn btn-secondary" href="/contact.html">Contact us</a></div>
</article></div>"""
    page("blog/faq.html", "FAQ — Photo & Signature Converter | ilovephoto.in",
         "Answers about using the ilovephoto.in converter: framing, file size limits, minimum KB, printing, custom presets and privacy.",
         body, active="/blog/faq.html", jsonld=[faq_ld(all_faqs)])


def render_index():
    groups = {}
    for g in GUIDES:
        groups.setdefault(g["category"], []).append(g)
    sections = ""
    for cat, items in groups.items():
        cards = "".join(f'<a class="card-link" href="/blog/{g["slug"]}"><strong>{g["short"]}</strong><span>{g["card"]}</span></a>' for g in items)
        sections += f'<p class="section-label">{cat}</p><div class="cards">{cards}</div>'
    learn = "".join(f'<a class="card-link" href="/blog/{a["slug"]}"><strong>{a["short"]}</strong><span>{a["card"]}</span></a>' for a in ARTICLES)
    learn = '<a class="card-link" href="/blog/photo-size-chart.html"><strong>Photo size chart</strong><span>Every form in one table</span></a>' + learn
    learn += '<a class="card-link" href="/blog/faq.html"><strong>FAQ</strong><span>Using the converter, KB limits, privacy</span></a>'
    body = f"""<div class="wrap page">
<div class="crumbs"><a href="/">Home</a> › Guides</div>
<h1>Photo and signature guides</h1>
<p class="lede">Exact sizes, rules and common rejection reasons for each form — reviewed {REVIEWED}.</p>
{sections}
<p class="section-label">Learn</p><div class="cards">{learn}</div>
</div>"""
    page("blog/index.html", "Photo & Signature Size Guides 2026 | ilovephoto.in",
         "Photo and signature size guides for PAN, Voter ID, driving licence, NEET, UPSC, IBPS, CAT, OCI and visa applications.",
         body, active="/blog/")


def render_static():
    about = f"""<div class="wrap narrow page"><article class="prose">
<h1>About ilovephoto.in</h1>
<p class="lede">A free tool that turns any photo or signature into a file an Indian application form will accept — without uploading it anywhere.</p>
<h2>Why we built it</h2>
<p>Online forms reject photos for reasons that are hard to see: a file 3 KB over the limit, the wrong shape, or a size in centimetres that doesn't say how many pixels. Most “photo resizer” sites solve this by uploading your face to their server. We think a photo of your face and signature shouldn't leave your device to be resized.</p>
<h2>How it works</h2>
<p>The converter runs entirely in your browser using the HTML5 Canvas API. When you choose a document, it crops your photo to the right shape, scales it to the exact pixel size, writes the DPI into the file, and finds the highest JPEG quality that fits the KB limit. Nothing is sent to a server.</p>
<h2>What we cover — and what we don't</h2>
<p>We only include documents where <em>you</em> provide the photo: PAN, Voter ID, driving licence, exam forms like NEET, UPSC, IBPS and CAT, and visa and OCI applications. We don't include Aadhaar or the Indian passport, because those photos are taken at the centre, or exams like JEE Main and SSC that now use live camera capture. <a href="/blog/photo-not-required.html">More on that here</a>.</p>
<h2>How we check specifications</h2>
<p>Each guide lists what the portal asks for next to what our preset produces, and links to the official source. Portals don't always publish complete numbers, and different sources sometimes disagree; when that happens we choose values that satisfy every published limit and say so on the page. Specs were last reviewed in {REVIEWED}.</p>
<h2>Independence</h2>
<p>ilovephoto.in is an independent project. It isn't affiliated with any government department, exam body or embassy. The site is free to use and supported by ads.</p>
<div class="cta"><p>Found an outdated size?<span>Tell us — we update presets as portals change.</span></p><a class="btn btn-secondary" href="/contact.html">Contact us</a></div>
</article></div>"""
    page("about.html", "About | ilovephoto.in", "ilovephoto.in is a free, private photo and signature resizer for Indian application forms. Learn how it works and how we check specifications.", about, active="/about.html")

    contact = """<div class="wrap narrow page"><article class="prose">
<h1>Contact</h1>
<p class="lede">Questions, a preset request, or a size that's changed? Write to us at <a href="mailto:ilovephoto.in@gmail.com">ilovephoto.in@gmail.com</a> or use the form below — it opens your email app with the message filled in.</p>
<p>When reporting a rejected upload, include the form name and the exact error message. Please don't send your photo.</p>
<form class="form" id="contactForm" novalidate>
  <div class="form-row">
    <label>Your name<input type="text" id="cfName" autocomplete="name" required></label>
    <label>Email<input type="email" id="cfEmail" autocomplete="email" required></label>
  </div>
  <label>Topic<select id="cfSubject">
    <option>Preset request</option><option>Size has changed</option><option>Bug report</option><option>Other</option>
  </select></label>
  <label>Message<textarea id="cfMessage" required></textarea></label>
  <div><button class="btn btn-primary" type="submit">Open in email app</button></div>
  <div class="form-status" id="cfStatus" role="status"></div>
</form>
</article></div>
<script>
document.getElementById('contactForm').addEventListener('submit', function (e) {
  e.preventDefault();
  var name = document.getElementById('cfName').value.trim();
  var email = document.getElementById('cfEmail').value.trim();
  var msg = document.getElementById('cfMessage').value.trim();
  var status = document.getElementById('cfStatus');
  if (!name || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email) || !msg) {
    status.textContent = 'Please fill in your name, a valid email and a message.';
    return;
  }
  var subj = encodeURIComponent(document.getElementById('cfSubject').value + ' — ilovephoto.in');
  var body = encodeURIComponent('Name: ' + name + '\\nEmail: ' + email + '\\n\\n' + msg);
  window.location.href = 'mailto:ilovephoto.in@gmail.com?subject=' + subj + '&body=' + body;
  status.textContent = 'Your email app should open with the message ready. Press send there to deliver it.';
});
</script>"""
    page("contact.html", "Contact | ilovephoto.in", "Contact ilovephoto.in — request a preset, report a changed size or a bug.", contact)

    privacy = f"""<div class="wrap narrow page"><article class="prose">
<h1>Privacy policy</h1>
<p class="meta">Last updated {REVIEWED}</p>
<h2>Your photos stay on your device</h2>
<p>Photos and signatures you open in the converter are processed in your browser's memory using JavaScript and the HTML5 Canvas API. They are never uploaded to us or anyone else. When you close or reload the page, they are gone. Camera access, if you use it, is only used to take a photo on your device and is switched off as soon as you capture or cancel.</p>
<h2>What is stored in your browser</h2>
<p>Custom presets you create are saved in your browser's local storage so they're there next time. You can delete them in the converter or by clearing site data.</p>
<h2>Analytics and advertising</h2>
<p>We use <strong>Google Analytics</strong> to count visits and see which pages are used (for example pages viewed, browser type and approximate city-level location). We use <strong>Google AdSense</strong> to show ads; Google may use cookies to show ads based on your visits to this and other sites. Neither service receives your photos.</p>
<ul>
<li>Manage ad personalisation at <a href="https://adssettings.google.com/" rel="noopener">Google Ad Settings</a>.</li>
<li>Opt out of Google Analytics with the <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">browser add-on</a>.</li>
<li>See <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">how Google uses data from sites that use its services</a>.</li>
</ul>
<h2>Other third parties</h2>
<p>Fonts are loaded from Google Fonts, which receives a standard web request from your browser.</p>
<h2>Contact form</h2>
<p>The contact form opens your own email app with the message filled in. We receive it only if you send it, and we use your email address only to reply.</p>
<h2>Children</h2>
<p>The site is for a general audience. We don't knowingly collect personal information from children.</p>
<h2>Changes</h2>
<p>If this policy changes, we'll update this page and the date above.</p>
<h2>Contact</h2>
<p>Questions: <a href="mailto:ilovephoto.in@gmail.com">ilovephoto.in@gmail.com</a>.</p>
</article></div>"""
    page("privacy-policy.html", "Privacy Policy | ilovephoto.in", "How ilovephoto.in handles your data: photos are processed in your browser and never uploaded. Details on analytics, ads and local storage.", privacy)

    terms = f"""<div class="wrap narrow page"><article class="prose">
<h1>Terms of service</h1>
<p class="meta">Last updated {REVIEWED}</p>
<h2>Using the service</h2>
<p>ilovephoto.in (“the service”) is a free, browser-based tool for resizing photos and signatures. By using it you agree to these terms.</p>
<h2>Your responsibility</h2>
<ul>
<li>Use the service lawfully, and only with photos and signatures you have the right to use.</li>
<li>Don't use it to alter photos in a way that misrepresents your identity on an official application.</li>
<li>Check the requirements of the form you are submitting. Presets are based on published guidelines that can change without notice.</li>
</ul>
<h2>No warranty</h2>
<p>The service is provided “as is”. We do our best to keep presets accurate, but we don't guarantee that any file will be accepted by any portal, and we are not affiliated with any government body.</p>
<h2>Limitation of liability</h2>
<p>We are not liable for any loss arising from use of the service, including rejected or delayed applications.</p>
<h2>Content</h2>
<p>The site's code, design and text belong to ilovephoto.in. You may link to any page.</p>
<h2>Changes</h2>
<p>We may update these terms; the date above shows the latest version.</p>
<h2>Contact</h2>
<p><a href="mailto:ilovephoto.in@gmail.com">ilovephoto.in@gmail.com</a></p>
</article></div>"""
    page("terms-of-service.html", "Terms of Service | ilovephoto.in", "Terms for using the free ilovephoto.in photo and signature converter.", terms)


# Old URLs whose content no longer belongs on the site
REDIRECTS = {
    "blog/aadhar-photo-specifications.html": "/blog/photo-not-required.html#aadhaar",
    "blog/passport-photo-size.html": "/blog/photo-not-required.html#passport",
    "blog/ration-card-photo-size.html": "/blog/photo-not-required.html#other",
}


def render_redirects():
    for path, target in REDIRECTS.items():
        (ROOT / path).write_text(f"""<!DOCTYPE html>
<html lang="en-IN"><head><meta charset="UTF-8">
<title>Moved | ilovephoto.in</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{SITE}{target.split('#')[0]}">
<meta http-equiv="refresh" content="0; url={target}">
</head><body><p>This page has moved: <a href="{target}">{SITE}{target}</a></p></body></html>
""", encoding="utf-8")


def chart_rows():
    """(preset, guide) pairs in display order — the one table answer engines can cite."""
    return [(p, p["guide"]) for p in PRESETS]


def render_chart():
    rows = ""
    for p, guide in chart_rows():
        rows += (f'<tr><td><a href="/blog/{guide}">{esc(p["name"])}</a></td><td>{p["w"]} × {p["h"]} px</td>'
                 f'<td>{kb_range(p)}</td><td>{p["dpi"]}</td><td>{print_size(p)}</td>'
                 f'<td><a href="/?preset={p["id"]}">Resize</a></td></tr>')
    faqs = [
        ("What is passport size photo size in India?", "3.5 × 4.5 cm. At 300 DPI that is 413 × 531 pixels; at 200 DPI it is 276 × 354 pixels."),
        ("What is the PAN card photo size?", "2.5 × 3.5 cm at 200 DPI (197 × 276 pixels), JPEG under 50 KB for Protean; 213 × 213 pixels under 30 KB for UTIITSL."),
        ("Which forms don't need a photo upload?", "Aadhaar and the Indian passport (photo taken at the centre), and JEE Main and SSC (live webcam capture)."),
    ]
    body = f"""<div class="wrap page">
<div class="crumbs"><a href="/">Home</a> › <a href="/blog/">Guides</a> › Photo size chart</div>
<article class="prose">
<h1>Photo and signature size chart for Indian forms (2026)</h1>
<div class="answer"><strong>Quick answer</strong><p>Indian passport-size photos are <strong>3.5 × 4.5 cm (413 × 531 px at 300 DPI)</strong>. Online forms differ mainly in file size: PAN under 50 KB, Sarathi 10–20 KB, IBPS 20–50 KB, NEET 10–200 KB, UPSC 20–200 KB, US visa under 240 KB. The full chart is below.</p></div>
<p class="meta">Last reviewed <time datetime="{LASTMOD}">{REVIEWED}</time> · Each row links to a guide with sources</p>
<div class="table-scroll"><table class="data-table">
<thead><tr><th>Form</th><th>Pixels</th><th>File size</th><th>DPI</th><th>Printed size</th><th></th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p>Where official sources disagree, these sizes satisfy every published limit. Each guide shows what the portal asks for next to what the preset produces.</p>
<h2>Not in the chart</h2>
<p>Aadhaar, the Indian passport, JEE Main and SSC don't take an uploaded photo — <a href="/blog/photo-not-required.html">see why</a>.</p>
<h2 id="faq">Frequently asked questions</h2>
{faq_html(faqs)}
</article></div>"""
    table_ld = {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "Photo and signature size requirements for Indian application forms",
        "description": "Pixel dimensions, file-size limits and DPI for photos and signatures uploaded to Indian government, exam and visa forms.",
        "url": SITE + "/blog/photo-size-chart.html", "dateModified": LASTMOD, "isAccessibleForFree": True,
        "creator": {"@type": "Organization", "name": "ilovephoto.in", "url": SITE},
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    page("blog/photo-size-chart.html", "Photo Size Chart for Indian Forms 2026 | ilovephoto.in",
         "One chart of photo and signature sizes for PAN, Voter ID, Sarathi, NEET, UPSC, IBPS, CAT, OCI, e-Visa and US visa — pixels, KB and DPI.",
         body, active="/blog/", jsonld=[table_ld, faq_ld(faqs),
                                         crumbs_ld([("Home", "/"), ("Guides", "/blog/"), ("Photo size chart", "/blog/photo-size-chart.html")])],
         og=("Photo size chart for Indian forms", "PAN, Voter ID, NEET, UPSC, IBPS, OCI, visas — pixels, KB and DPI"))


def render_404():
    body = """<div class="wrap narrow page"><article class="prose">
<h1>Page not found</h1>
<p class="lede">That page doesn't exist — it may have moved when we reorganised the guides.</p>
<p><a class="btn btn-primary" href="/">Open the converter</a> <a class="btn btn-secondary" href="/blog/photo-size-chart.html">See all photo sizes</a></p>
</article></div>"""
    page("404.html", "Page not found | ilovephoto.in", "Page not found.", body, robots="noindex, follow")


def render_crawler_files():
    # Every search and AI crawler is welcome; nothing on the site is private.
    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
            "PerplexityBot", "Google-Extended", "Applebot", "Applebot-Extended", "DuckDuckBot", "YandexBot"]
    robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    (ROOT / "robots.txt").write_text(f"{robots}User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    chart = "\n".join(f'- {p["name"]}: {p["w"]}×{p["h"]} px, {kb_range(p)}, {p["dpi"]} DPI — {SITE}/blog/{p["guide"]}'
                      for p, _ in chart_rows())
    guides = "\n".join(f'- [{g["short"]}]({SITE}/blog/{g["slug"]}): {strip_tags(g["answer"])}' for g in GUIDES)
    articles = "\n".join(f'- [{a["short"]}]({SITE}/blog/{a["slug"]}): {a["card"]}' for a in ARTICLES)
    (ROOT / "llms.txt").write_text(f"""# ilovephoto.in

> Free photo and signature resizer for Indian application forms (PAN, Voter ID, Sarathi driving licence, NEET UG, UPSC, IBPS/SBI, CAT, OCI, India e-Visa, US visa, Schengen, UK passport). It outputs a JPEG with the exact pixel size, DPI and file-size window each portal accepts. All processing happens in the user's browser; photos are never uploaded. Specs last reviewed {REVIEWED}.

Key facts:
- Indian passport-size photo: 3.5 × 4.5 cm = 413 × 531 px at 300 DPI.
- Aadhaar and Indian passport photos are taken at the enrolment centre / Passport Seva Kendra — no upload.
- JEE Main (2026 cycle) and SSC use live webcam photo capture inside the form — no photo file to upload.
- Where official sources disagree, the site's presets use values that satisfy every published limit.

## Size chart
{chart}

## Guides
{guides}

## Explainers
{articles}
- [Photo size chart]({SITE}/blog/photo-size-chart.html): all sizes in one table
- [FAQ]({SITE}/blog/faq.html): using the converter, KB limits, privacy

## Tool
- [Converter]({SITE}/): open with ?preset=<id> to preselect a form, e.g. {SITE}/?preset=pan_protean
""", encoding="utf-8")

    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")


def render_presets_js():
    rows = [{k: v for k, v in p.items()} for p in PRESETS]
    (ROOT / "assets" / "presets.js").write_text(
        "// Generated by scripts/build_site.py — edit presets there, not here.\n"
        f"window.ILP_PRESETS = {json.dumps(rows, ensure_ascii=False, indent=1)};\n",
        encoding="utf-8")


def render_sitemap():
    urls = [("", "1.0"), ("blog/", "0.8"), ("blog/photo-size-chart.html", "0.8"), ("blog/faq.html", "0.6")]
    urls += [("blog/" + g["slug"], "0.7") for g in GUIDES]
    urls += [("blog/" + a["slug"], "0.6") for a in ARTICLES]
    urls += [("about.html", "0.4"), ("contact.html", "0.3"), ("privacy-policy.html", "0.2"), ("terms-of-service.html", "0.2")]
    body = "".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{LASTMOD}</lastmod><priority>{pr}</priority></url>\n" for u, pr in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n',
        encoding="utf-8")


if __name__ == "__main__":
    for g in GUIDES:
        render_guide(g)
    render_articles()
    render_faq()
    render_index()
    render_static()
    render_redirects()
    render_chart()
    render_404()
    render_crawler_files()
    make_og_image("index.html", "Resize your photo & signature for Indian forms",
                  "PAN, Voter ID, NEET, UPSC, IBPS, OCI, visas — exact pixels and KB")
    render_presets_js()
    render_sitemap()
    print(f"Built {len(GUIDES)} guides, {len(ARTICLES)} articles, {len(PRESETS)} presets.")
