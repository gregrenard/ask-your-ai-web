# Launch checklist for the site

## What the build produces

`python3 site-src/build_site.py` writes six pages (English at the root, French, Spanish, Italian, Dutch and German in subfolders) plus llms.txt, llms-full.txt, ask-your-ai.md, how-it-works.md, pricing.md, faq.md, robots.txt and sitemap.xml. `python3 site-src/og_images.py` writes the six 1200x630 share cards. The widget is built from `site-widget/config.preview.json` (preview address) or `site-widget/config.json` (domain) with the engine (private project), then copied to `ask-your-ai.js` at the repository root.

## At launch, in this order

1. Point ask-your-ai.me at the host and add the CNAME file.
2. Rebuild the pages first with `python3 site-src/build_site.py --base https://ask-your-ai.me --index`. The `--index` flag replaces the noindex tag with index,follow; nothing else changes. Do this before the widget, because the widget kit copies `ask-your-ai.md`.
3. Rebuild the widget with `site-widget/config.json` (it targets https://ask-your-ai.me) and copy `ask-your-ai.js` to the repository root.
4. Re-render the share cards if the copy changed, check the six pages and the widget on desktop and on a phone, and check that `https://ask-your-ai.me/llms.txt` and `/ask-your-ai.md` load.
5. Verify the domain in Google Search Console and Bing Webmaster Tools, submit `sitemap.xml`, and request indexing for the home page and the French, Spanish, German, Italian and Dutch pages.
6. Publish the terms, the privacy policy and the refund policy before any real payment, and replace the simulated checkout.

## Known limits of the current build

- The six translations were written by the assistant and have not been reviewed by native speakers. Registers: vous (fr), tú (es), tu (it), je (nl), Sie (de). Review `site-src/i18n/strings.txt` and `js.txt`; both list the languages side by side.
- The account dashboard (section s-app of the page) is a simulated mockup and stays in English.
- The facts file and the guides are in English only: assistants answer in the visitor's language. The box's prompt starts in the page's language.
- The contact link built by the assistant opens the English page's form, because the box holds a single contact address.
