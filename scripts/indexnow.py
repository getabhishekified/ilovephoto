"""Tells IndexNow search engines (Bing, Yandex, Seznam, Naver, Yep) that the site's pages changed.

Bing's index also feeds ChatGPT search, Copilot and DuckDuckGo. Run this after a
deploy is live, because the engines fetch the key file from the site to verify it:

    python scripts/indexnow.py
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site import INDEXNOW_KEY, ROOT, SITE  # noqa: E402

urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
payload = json.dumps({
    "host": SITE.split("//")[1],
    "key": INDEXNOW_KEY,
    "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt",
    "urlList": urls,
}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow accepted {len(urls)} URLs (HTTP {r.status})")
except urllib.error.HTTPError as e:
    print(f"IndexNow returned HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
    sys.exit(1)
