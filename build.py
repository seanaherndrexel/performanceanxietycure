#!/usr/bin/env python3
"""Static site builder for performanceanxietycure.com (stdlib only).

Content lives in:
  pages/method/*.html   principle pages (front matter: title, description, order, slug, nav)
  pages/*.html          standalone pages (home, buy, about, disclaimer)
  posts/*.html          blog articles (front matter: title, description, date, slug, keywords)
Output goes to public/.
"""
import html, json, os, re, shutil, datetime

SITE_URL = "https://performanceanxietycure.com"
SITE_NAME = "The Performance Anxiety Cure"
BOOK_TITLE = "The Performance Anxiety Cure"
BOOK_SUBTITLE = "A Proven Action Plan for Men to Finally Enjoy Sex Without Performance Anxiety"
AUTHOR = "Sean Stephens"
# Swap this for the book's direct Amazon link (amazon.com/dp/ASIN) once the listing is live.
BUY_URL = "https://www.amazon.com/s?k=The+Performance+Anxiety+Cure+Sean+Stephens"

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")


def read_doc(path):
    raw = open(path, encoding="utf-8").read()
    meta = {}
    m = re.match(r"\s*<!--(.*?)-->", raw, re.S)
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        raw = raw[m.end():]
    meta["body"] = raw.strip()
    return meta


def esc(s):
    return html.escape(s, quote=True)


def buy_box(variant="inline"):
    return f'''<aside class="buybox {variant}">
  <a href="{BUY_URL}" class="buybox-cover" rel="nofollow sponsored noopener" target="_blank"><img src="/static/img/cover.jpg" alt="{esc(BOOK_TITLE)} book cover" width="160" height="256" loading="lazy"></a>
  <div>
    <p class="eyebrow">The full action plan</p>
    <p class="buybox-title">{esc(BOOK_TITLE)}</p>
    <p>Fifteen chapters on stopping the fear loop, talking to a partner, getting past the moments that trip you up, and building confidence that lasts.</p>
    <a class="btn btn-red" href="{BUY_URL}" rel="nofollow sponsored noopener" target="_blank">Get the book on Amazon</a>
  </div>
</aside>'''


def inject_cta(body):
    """Drop a buy box after the third paragraph of long content."""
    if body.count("</p>") < 6:
        return body
    idx = -1
    for _ in range(3):
        idx = body.index("</p>", idx + 1)
    cut = idx + len("</p>")
    return body[:cut] + "\n" + buy_box("inline") + body[cut:]


def method_nav(methods, current=None):
    items = []
    for i, m in enumerate(methods, 1):
        cls = ' class="active"' if m["slug"] == current else ""
        items.append(f'<li{cls}><a href="/method/{m["slug"]}/"><span>{i:02d}</span>{esc(m["nav"])}</a></li>')
    return '<ol class="method-list">' + "".join(items) + "</ol>"


def layout(title, description, path, content, schema=None, og_type="website"):
    canonical = SITE_URL + path
    full_title = title if SITE_NAME in title else f"{title} | {SITE_NAME}"
    schema_tag = ""
    if schema:
        schema_tag = '<script type="application/ld+json">' + json.dumps(schema) + "</script>"
    year = datetime.date.today().year
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/static/img/cover.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/static/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/site.css">
{schema_tag}
</head>
<body>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="/">Performance<span>Anxiety</span>Cure</a>
    <nav class="nav">
      <a href="/method/">The Method</a>
      <a href="/blog/">Blog</a>
      <a href="/about/">About the Book</a>
      <a class="btn btn-red btn-sm" href="/buy/">Buy the Book</a>
    </nav>
  </div>
</header>
<main>
{content}
</main>
<section class="final-cta">
  <div class="wrap final-cta-inner">
    <img src="/static/img/cover.jpg" alt="{esc(BOOK_TITLE)} by {AUTHOR}" width="200" height="320" loading="lazy">
    <div>
      <p class="eyebrow">Ready to stop feeding the fear?</p>
      <h2>Get the complete plan in {esc(BOOK_TITLE)}</h2>
      <p>The pages on this site cover the principles. The book walks you through every step, including what to say, what to do in the moment, and how to handle the night it goes wrong.</p>
      <a class="btn btn-red btn-lg" href="{BUY_URL}" rel="nofollow sponsored noopener" target="_blank">Buy it on Amazon</a>
    </div>
  </div>
</section>
<footer class="site-footer">
  <div class="wrap">
    <p><a href="/method/">The Method</a> · <a href="/blog/">Blog</a> · <a href="/about/">About the Book</a> · <a href="/buy/">Buy the Book</a> · <a href="/disclaimer/">Medical Disclaimer</a></p>
    <p class="small">The information on this site is educational and is not medical advice. Talk to your doctor about any health concern or before taking any medication. © {year} {AUTHOR}.</p>
  </div>
</footer>
<a class="sticky-buy" href="{BUY_URL}" rel="nofollow sponsored noopener" target="_blank">Get the book on Amazon</a>
</body>
</html>'''


def write(path, text):
    full = os.path.join(OUT, path.strip("/"), "index.html") if not path.endswith(".html") and not path.endswith(".xml") and not path.endswith(".txt") else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)


def fmt_date(d):
    return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")


def post_card(p):
    return f'''<article class="card">
  <p class="meta">{fmt_date(p["date"])}</p>
  <h3><a href="/blog/{p["slug"]}/">{esc(p["title"])}</a></h3>
  <p>{esc(p["description"])}</p>
  <a class="more" href="/blog/{p["slug"]}/">Read the article</a>
</article>'''


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "static"))

    methods = []
    mdir = os.path.join(ROOT, "pages", "method")
    for f in os.listdir(mdir):
        if f.endswith(".html"):
            methods.append(read_doc(os.path.join(mdir, f)))
    methods.sort(key=lambda m: int(m.get("order", 99)))

    posts = []
    pdir = os.path.join(ROOT, "posts")
    today = datetime.date.today().isoformat()
    for f in os.listdir(pdir):
        if f.endswith(".html"):
            p = read_doc(os.path.join(pdir, f))
            if p.get("date", today) <= today:
                posts.append(p)
    posts.sort(key=lambda p: p["date"], reverse=True)

    urls = [("/", today)]

    # Method pages
    for i, m in enumerate(methods):
        prev_link = f'<a href="/method/{methods[i-1]["slug"]}/">&larr; {esc(methods[i-1]["nav"])}</a>' if i > 0 else '<a href="/method/">&larr; All principles</a>'
        next_link = f'<a href="/method/{methods[i+1]["slug"]}/">{esc(methods[i+1]["nav"])} &rarr;</a>' if i < len(methods) - 1 else '<a href="/buy/">Get the full book &rarr;</a>'
        content = f'''<section class="page-hero"><div class="wrap narrow">
  <p class="eyebrow">Principle {i+1:02d} of {len(methods):02d}</p>
  <h1>{esc(m["title"])}</h1>
  <p class="lede">{esc(m["description"])}</p>
</div></section>
<div class="wrap with-side">
  <article class="prose">{inject_cta(m["body"])}
  <nav class="pager">{prev_link}{next_link}</nav>
  </article>
  <aside class="side">{buy_box("side")}<div class="side-nav"><p class="eyebrow">The method</p>{method_nav(methods, m["slug"])}</div></aside>
</div>'''
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": m["title"], "description": m["description"],
                  "author": {"@type": "Person", "name": AUTHOR}, "mainEntityOfPage": SITE_URL + f"/method/{m['slug']}/",
                  "image": SITE_URL + "/static/img/cover.jpg"}
        write(f"/method/{m['slug']}/", layout(m["title"], m["description"], f"/method/{m['slug']}/", content, schema, "article"))
        urls.append((f"/method/{m['slug']}/", today))

    # Method index
    cards = "".join(f'''<a class="principle" href="/method/{m["slug"]}/"><span class="num">{i:02d}</span><h3>{esc(m["title"])}</h3><p>{esc(m["description"])}</p></a>''' for i, m in enumerate(methods, 1))
    content = f'''<section class="page-hero"><div class="wrap narrow">
  <p class="eyebrow">The Method</p>
  <h1>Eight Principles That Take the Fear Out of Sex</h1>
  <p class="lede">Performance anxiety runs on a loop. Each principle below breaks one link in it. Read them in order, then get the book for the full step-by-step plan.</p>
</div></section>
<div class="wrap"><div class="principles">{cards}</div>{buy_box("wide")}</div>'''
    write("/method/", layout("The Method: 8 Principles to Beat Performance Anxiety", "A step-by-step guide to the principles behind The Performance Anxiety Cure, from breaking the fear loop to rebuilding real confidence in bed.", "/method/", content))
    urls.append(("/method/", today))

    # Blog posts
    for i, p in enumerate(posts):
        related = [x for x in posts if x["slug"] != p["slug"]][:3]
        rel_html = ""
        if related:
            rel_html = '<section class="related"><h2>Keep reading</h2><div class="cards">' + "".join(post_card(x) for x in related) + "</div></section>"
        content = f'''<section class="page-hero"><div class="wrap narrow">
  <p class="eyebrow"><a href="/blog/">Blog</a> · {fmt_date(p["date"])}</p>
  <h1>{esc(p["title"])}</h1>
  <p class="lede">{esc(p["description"])}</p>
</div></section>
<div class="wrap with-side">
  <article class="prose">{inject_cta(p["body"])}
  {buy_box("wide")}
  </article>
  <aside class="side">{buy_box("side")}<div class="side-nav"><p class="eyebrow">The method</p>{method_nav(methods)}</div></aside>
</div>
<div class="wrap">{rel_html}</div>'''
        schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["description"],
                  "datePublished": p["date"], "dateModified": p["date"], "keywords": p.get("keywords", ""),
                  "author": {"@type": "Person", "name": AUTHOR}, "mainEntityOfPage": SITE_URL + f"/blog/{p['slug']}/",
                  "image": SITE_URL + "/static/img/cover.jpg",
                  "publisher": {"@type": "Organization", "name": SITE_NAME}}
        write(f"/blog/{p['slug']}/", layout(p["title"], p["description"], f"/blog/{p['slug']}/", content, schema, "article"))
        urls.append((f"/blog/{p['slug']}/", p["date"]))

    # Blog index
    listing = "".join(post_card(p) for p in posts) or "<p>New articles are on the way.</p>"
    content = f'''<section class="page-hero"><div class="wrap narrow">
  <p class="eyebrow">Blog</p>
  <h1>Straight Talk on Performance Anxiety</h1>
  <p class="lede">Plain-language articles on what's happening in your head and body, and what to do about it.</p>
</div></section>
<div class="wrap"><div class="cards">{listing}</div></div>'''
    write("/blog/", layout("Performance Anxiety Blog", "Articles on sexual performance anxiety in men: causes, the fear loop, talking to a partner, and practical ways to get your confidence back.", "/blog/", content))
    urls.append(("/blog/", posts[0]["date"] if posts else today))

    # Standalone pages
    for name, path in (("home", "/"), ("buy", "/buy/"), ("about", "/about/"), ("disclaimer", "/disclaimer/")):
        d = read_doc(os.path.join(ROOT, "pages", f"{name}.html"))
        body = d["body"].replace("{{BUY_URL}}", BUY_URL)
        body = body.replace("{{METHOD_LIST}}", method_nav(methods))
        body = body.replace("{{LATEST_POSTS}}", "".join(post_card(p) for p in posts[:3]) or "<p>New articles are on the way.</p>")
        body = body.replace("{{BUY_BOX}}", buy_box("wide"))
        schema = None
        if name in ("home", "buy"):
            schema = {"@context": "https://schema.org", "@type": "Book", "name": BOOK_TITLE, "alternativeHeadline": BOOK_SUBTITLE,
                      "author": {"@type": "Person", "name": AUTHOR}, "bookFormat": "https://schema.org/EBook",
                      "image": SITE_URL + "/static/img/cover.jpg", "url": SITE_URL + "/buy/", "inLanguage": "en",
                      "offers": {"@type": "Offer", "url": BUY_URL, "availability": "https://schema.org/InStock"}}
        write(path, layout(d["title"], d["description"], path, body, schema))
        if name != "disclaimer":
            urls.append((path, today))

    # 404
    write("404.html", layout("Page Not Found", "That page doesn't exist.", "/404.html",
          '<section class="page-hero"><div class="wrap narrow"><h1>That page wandered off</h1><p class="lede"><a href="/">Head back home</a> or <a href="/method/">start with the method</a>.</p></div></section>'))

    # Sitemap + robots
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    seen = set()
    for u, d in urls:
        if u in seen:
            continue
        seen.add(u)
        sm.append(f"<url><loc>{SITE_URL}{u}</loc><lastmod>{d}</lastmod></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm))
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"Built {len(methods)} method pages, {len(posts)} posts.")


if __name__ == "__main__":
    main()
