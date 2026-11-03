# Getting ilovephoto.in found — submission checklist

The site-side work (titles, descriptions, structured data, preview images, `llms.txt`, `robots.txt`, sitemap, IndexNow) is done in the code. The steps below need your own accounts, so they have to be done by you. Work top to bottom — the first four matter far more than everything after them.

## 1. Search engines (do these first)

| Where | What to do | Why |
|---|---|---|
| [Google Search Console](https://search.google.com/search-console) | You already verified the site. Go to **Sitemaps** → submit `sitemap.xml`. Then **URL inspection** → paste `https://ilovephoto.in/blog/photo-size-chart.html` → **Request indexing**. Repeat for the homepage and your top 3 guides. | Google is most of your traffic and feeds Gemini / AI Overviews. |
| [Bing Webmaster Tools](https://www.bing.com/webmasters) | **Import from Google Search Console** (one click, no extra verification). Submit `sitemap.xml`. | Bing's index powers **ChatGPT search, Microsoft Copilot, DuckDuckGo, Yahoo and Ecosia**. This is the single most important step for AI answers. |
| IndexNow | After each deploy, run `python scripts/indexnow.py`. | Pings Bing, Yandex, Seznam, Naver and Yep instantly. |
| [Yandex Webmaster](https://webmaster.yandex.com) | Optional. Add the site and submit the sitemap. | Small share of Indian traffic. |

Not needed: Google's old "ping" URL was retired in 2023. Perplexity, ChatGPT, Claude and Apple don't have submission forms — they crawl (allowed in `robots.txt`) and use Bing/Google results.

## 2. Places where people (and AI models) find tools

These count as genuine mentions. Each needs an account; write in your own words and say plainly that you built it.

- **[Product Hunt](https://www.producthunt.com/)** — launch on a Tuesday–Thursday. Title idea: "ilovephoto.in — resize photos for Indian govt & exam forms, never uploaded".
- **[AlternativeTo](https://alternativeto.net/)** — list it as an alternative to "Passport Photo Maker", "iLoveIMG" and "ResizePixel".
- **[Google Business Profile](https://business.google.com/)** — skip; it's for places with an address.
- **GitHub** — make the repo public (if it isn't already) with a good README and topics like `photo-resizer`, `india`, `pan-card`. Developers and AI models read GitHub.
- **[Hacker News "Show HN"](https://news.ycombinator.com/showhn.html)** — the privacy angle (runs in the browser, nothing uploaded) is what interests that audience.

## 3. Communities where the actual users are (biggest real-world impact)

Answer real questions; don't drop links where nobody asked. One helpful answer that solves someone's problem beats 50 directory listings.

- **Quora** — search "PAN card photo size", "NEET photo size", "UPSC photo name and date", "IBPS photo size increase KB". Answer with the exact numbers from the guide, then link it.
- **Reddit** — r/UPSC, r/NEET, r/JEENEETards, r/IndianBankExams, r/india (weekly threads), r/IndiaTax for PAN. Read each subreddit's rules on self-promotion first.
- **Telegram / WhatsApp exam groups** — share before NEET, UPSC and IBPS application windows open. Timing matters more than anything else.
- **YouTube** — a 60-second screen recording "How to make your NEET photo 10–200 KB in your phone" with the link in the description. Short videos rank in Google for these queries.

## 4. Things to avoid

- Paid "submit to 500 directories" services and link farms. Google treats them as spam, and they can get the site demoted.
- Copying the same post across many forums.
- Fake reviews or upvotes.

## 5. Keep it fresh (ongoing)

- Before each big application window (NEET ~Feb, UPSC ~Jan/Feb, IBPS ~Jul/Aug, CAT ~Aug), check the official notice, update the preset in `scripts/build_site.py`, bump `REVIEWED`/`LASTMOD`, rebuild, push, and run `python scripts/indexnow.py`. Pages with a recent review date that match the current notice get cited by AI answers.
- In Search Console → **Performance**, look for queries where you're in position 5–15, and add a FAQ answering exactly that query to the matching guide.
