#!/usr/bin/env python3
"""Build the six language pages of the landing site.

  python3 site-src/build_site.py [--base https://example.com/prefix] [--out web]

Reads site-src/index.src.html and site-src/i18n/{strings,js}.txt, writes <out>/index.html (English) and
<out>/<lang>/index.html for fr, es, it, nl, de, with canonical and hreflang links, a language menu and the
page script's strings. The dashboard section (id="s-app") is left in English on purpose.

Every English phrase of strings.txt must be found in the source page, and no translated page may keep a
recognisable English sentence outside the dashboard, script and style blocks; otherwise the build fails.
"""
import argparse, json, os, re, sys, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = [("en", "English", "EN"), ("fr", "Français", "FR"), ("es", "Español", "ES"),
         ("it", "Italiano", "IT"), ("nl", "Nederlands", "NL"), ("de", "Deutsch", "DE")]
CODES = [l[0] for l in LANGS]
# the site root is ../web in the product project and the repository root in the public repository
DEFAULT_OUT = os.path.join(HERE, "..", "web") if os.path.isdir(os.path.join(HERE, "..", "web")) else os.path.join(HERE, "..")
PROTECTED = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<section class="step" id="s-app">.*?</section>)', re.S)


def rows(path):
    out = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in line.split(" ||| ")]
        if len(parts) != 6 and not (os.path.basename(path) == "js.txt" and len(parts) == 7):
            sys.exit("%s:%d: expected %d columns, got %d" % (path, n, 6 if path.endswith("strings.txt") else 7, len(parts)))
        out.append(parts)
    return out


def load():
    html = {}
    for r in rows(os.path.join(HERE, "i18n", "strings.txt")):
        html[r[0]] = dict(zip(CODES, r))
    js = {}
    for r in rows(os.path.join(HERE, "i18n", "js.txt")):
        js[r[0]] = {c: v.replace("\\n", "\n") for c, v in zip(CODES, r[1:])}
    return html, js


def href(cur, target):
    root = "" if cur == "en" else "../"
    if target == "en":
        return root or "./"
    return root + target + "/" if cur != target else "./"


def abs_url(base, code):
    return base.rstrip("/") + ("/" if code == "en" else "/%s/" % code)


def translate(src, code, table, report):
    parts = PROTECTED.split(src)
    keys = sorted(table, key=len, reverse=True)
    tokens = {}
    seen = set()
    for i, seg in enumerate(parts):
        if i % 2 == 1:
            continue
        for k in keys:
            if k in seg:
                tok = "\x00%d\x00" % len(tokens)
                tokens[tok] = table[k][code]
                seg = seg.replace(k, tok)
                seen.add(k)
        parts[i] = seg
    out = "".join(parts)
    for tok, tr in tokens.items():
        out = out.replace(tok, tr)
    missing = [k for k in table if k not in seen]
    if missing:
        report.append((code, "phrases not found in the source page", missing))
    return out


STOP = re.compile(r"\b(the|and|your|you|with|for|from|is|are|it|of|to|on)\b", re.I)


def leftovers(html):
    body = PROTECTED.sub(" ", html)
    body = re.sub(r"<[^>]+>", "\n", body)
    keep = ("ChatGPT", "Claude", "Gemini", "Perplexity", "WordPress", "Wix", "Squarespace", "Webflow", "Framer", "Freedom.AI", "Ask your AI about me", "on-premise", "On-Premise")
    bad = []
    for line in body.split("\n"):
        t = line.strip()
        if len(t) < 12:
            continue
        for k in keep:
            t = t.replace(k, "")
        if len(STOP.findall(t)) >= 2:
            bad.append(line.strip()[:110])
    return bad


FAQ_KEYS = [("Will the AI say wrong things about me?", "It only uses the fact sheet you approve. Every fact is checked against your own pages, and when something isn't published the AI says so."),
            ("Does it work on my platform?", "If you can add a script to your pages, yes: WordPress, Wix, Squarespace, Webflow, Framer or plain HTML."),
            ("Who receives the messages?", "You do, through your own contact form. The AI only fills it in. The visitor reviews and sends."),
            ("What happens when my site changes?", "With the kit, you run the check again. With the hosted plan, we re-read your site every month and you approve what changed."),
            ("Do I need to be technical?", "No. You paste an address, read one page, and add one line.")]
META_KEY = "Make your website conversational. Your visitors' own AI learns your facts, answers from them and sends the right people to you."


def tr(table, code, key):
    return key if code == "en" else table[key][code]


def headline(table, code):
    return (tr(table, code, "Make your website") + " " + tr(table, code, "conversational.")).strip()


def meta_block(base, code, table):
    desc = tr(table, code, META_KEY)
    title = "Ask your AI about me \u2014 " + headline(table, code)
    img = base.rstrip("/") + "/assets/og-%s.png" % code
    url = abs_url(base, code)
    esc = lambda x: H.escape(x, quote=True)
    tags = ['<meta name="theme-color" content="#1e2a5a">',
            '<meta property="og:type" content="website">', '<meta property="og:site_name" content="Ask your AI about me">',
            '<meta property="og:title" content="%s">' % esc(title), '<meta property="og:description" content="%s">' % esc(desc),
            '<meta property="og:url" content="%s">' % url, '<meta property="og:image" content="%s">' % img,
            '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            '<meta property="og:locale" content="%s">' % {"en": "en_US", "fr": "fr_FR", "es": "es_ES", "it": "it_IT", "nl": "nl_NL", "de": "de_DE"}[code],
            '<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:title" content="%s">' % esc(title),
            '<meta name="twitter:description" content="%s">' % esc(desc), '<meta name="twitter:image" content="%s">' % img]
    org = base.rstrip("/") + "/#org"
    graph = [
        {"@type": "Organization", "@id": org, "name": "Freedom.AI Lab", "url": "https://www.freedom.ai"},
        {"@type": "WebSite", "@id": base.rstrip("/") + "/#site", "name": "Ask your AI about me", "url": url, "inLanguage": code, "publisher": {"@id": org}},
        {"@type": "SoftwareApplication", "name": "Ask your AI about me", "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
         "description": desc, "inLanguage": CODES, "creator": {"@id": org},
         "offers": {"@type": "Offer", "name": "Kit", "price": "10", "priceCurrency": "USD", "availability": "https://schema.org/PreOrder", "url": url + "#pricing"}},
        {"@type": "FAQPage", "inLanguage": code, "mainEntity": [
            {"@type": "Question", "name": tr(table, code, q), "acceptedAnswer": {"@type": "Answer", "text": tr(table, code, a)}} for q, a in FAQ_KEYS]}]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/")
    return "\n".join(tags) + '\n<script type="application/ld+json">%s</script>' % ld


def write_ai_files(base, out):
    base = base.rstrip("/")
    langlist = "\n".join("- [%s](%s): %s" % (n, abs_url(base, c), n) for c, n, _ in LANGS)
    langlist = "\n".join("- [%s](%s)" % (n, abs_url(base, c)) for c, n, _ in LANGS)
    texts = {}
    for name in ("llms.txt", "ask-your-ai.md", "how-it-works.md", "pricing.md", "faq.md"):
        t = open(os.path.join(HERE, "ai", name + ".tpl"), encoding="utf-8").read()
        t = t.replace("{{BASE}}", base).replace("{{LANGLIST}}", langlist)
        texts[name] = t
        open(os.path.join(out, name), "w", encoding="utf-8").write(t)
    full = texts["llms.txt"].split("## Facts and guides")[0].rstrip() + "\n\n"
    for name in ("ask-your-ai.md", "how-it-works.md", "pricing.md", "faq.md"):
        full += "\n\n---\n\n" + texts[name].rstrip() + "\n"
    open(os.path.join(out, "llms-full.txt"), "w", encoding="utf-8").write(full)
    open(os.path.join(out, "robots.txt"), "w", encoding="utf-8").write(
        "# Public preview. Pages carry a noindex tag until launch; remove it (build_site.py --index) when the domain is live.\n"
        "User-agent: *\nAllow: /\n\n"
        + "".join("User-agent: %s\nAllow: /\n\n" % bot for bot in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "PerplexityBot", "Google-Extended"))
        + "Sitemap: %s/sitemap.xml\n" % base)
    urls = []
    for c, _, _ in LANGS:
        alts = "".join('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (x, abs_url(base, x)) for x in CODES)
        alts += '<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % abs_url(base, "en")
        urls.append("<url><loc>%s</loc>%s</url>" % (abs_url(base, c), alts))
    for name in ("ask-your-ai.md", "how-it-works.md", "pricing.md", "faq.md"):
        urls.append("<url><loc>%s/%s</loc></url>" % (base, name))
    open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://gregrenard.github.io/ask-your-ai-web")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--index", action="store_true", help="allow indexing (launch): replaces the noindex tag")
    a = ap.parse_args()
    src = open(os.path.join(HERE, "index.src.html"), encoding="utf-8").read()
    table, js = load()
    problems = []
    for code, label, short in LANGS:
        page = src if code == "en" else translate(src, code, table, problems)
        root = "" if code == "en" else "../"
        links = "".join('<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (href(code, c), c, c, ' aria-current="true"' if c == code else "", n)
                        for c, n, _ in LANGS)
        head = '<link rel="canonical" href="%s">\n' % abs_url(a.base, code)
        head += "".join('<link rel="alternate" hreflang="%s" href="%s">\n' % (c, abs_url(a.base, c)) for c in CODES)
        head += '<link rel="alternate" hreflang="x-default" href="%s">' % abs_url(a.base, "en")
        T = {k: v[code] for k, v in js.items()}
        page = (page.replace("{{LANG}}", code).replace("{{ROOT}}", root).replace("{{LANGCODE}}", short)
                .replace("{{LANGLINKS}}", links).replace("{{HEADLINKS}}", head)
                .replace("/*T*/{}", json.dumps(T, ensure_ascii=False))
                .replace("{{META}}", meta_block(a.base, code, table))
                .replace("{{ROBOTS}}", '<meta name="robots" content="index,follow">' if a.index else '<meta name="robots" content="noindex">'))
        if "{{" in page:
            problems.append((code, "unfilled placeholder", re.findall(r"\{\{[A-Z]+\}\}", page)))
        if code != "en":
            lo = leftovers(page)
            if lo:
                problems.append((code, "English text left on the page", lo))
        out_dir = os.path.abspath(a.out if code == "en" else os.path.join(a.out, code))
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(page)
        print("wrote", os.path.relpath(os.path.join(out_dir, "index.html")), len(page), "bytes")
    write_ai_files(a.base, os.path.abspath(a.out))
    print("wrote llms.txt, llms-full.txt, ask-your-ai.md, how-it-works.md, pricing.md, faq.md, robots.txt, sitemap.xml")
    if problems:
        for code, what, items in problems:
            print("\nPROBLEM [%s] %s:" % (code, what))
            for it in items[:25]:
                print("   -", it)
        sys.exit(1)
    print("ok: %d languages, %d phrases, %d script strings" % (len(LANGS), len(table), len(js)))


if __name__ == "__main__":
    main()
