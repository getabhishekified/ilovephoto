# I ♥ Photo — ilovephoto.in

Free, private photo and signature resizer for Indian application forms. Runs entirely in the browser — photos are never uploaded.

🌐 **Live at [ilovephoto.in](https://ilovephoto.in)**

## What it does

Pick a form, add a photo, and download a JPEG with the exact pixel size, DPI and file-size window the portal accepts. It finds the highest JPEG quality under the maximum, and if a form also has a minimum (IBPS, NEET, UPSC, Sarathi), it pads the file with a JPEG comment segment so it isn't rejected as too small.

Other features: drag-to-reposition and zoom, face guide, crop, straighten, brightness/contrast, optional name & date strip (UPSC), A4 print sheet at actual size, and custom presets saved in the browser.

## Which forms are included

Only forms where **the applicant provides the photo**: PAN (Protean & UTIITSL), Voter ID, Sarathi learner's licence, NEET UG, UPSC, IBPS/SBI, CAT, OCI, India e-Visa, US visa, Schengen, UK passport, LinkedIn, plus signature presets.

Deliberately excluded: Aadhaar and the Indian passport (photo taken at the centre), JEE Main and SSC (live webcam capture), NREGA (taken by officials). The guide `blog/photo-not-required.html` explains these.

## Project layout

| Path | What it is |
|---|---|
| `index.html` | The converter (hand-written, no framework) |
| `assets/site.css` | Shared styles for every page |
| `assets/presets.js` | Preset data used by the converter — **generated** |
| `blog/*.html`, `about.html`, `contact.html`, legal pages, `sitemap.xml` | **Generated** content pages |
| `scripts/build_site.py` | Generator — presets, guide content and page templates live here |

To change a preset or guide, edit `scripts/build_site.py` and run:

```bash
python scripts/build_site.py
```

Commit the generated files; GitHub Pages serves the repo as-is (no build step on deploy).

## Privacy

Images are processed with the Canvas API in the browser and never sent anywhere. The site uses Google Analytics and Google AdSense — see `privacy-policy.html`.

## License

MIT
