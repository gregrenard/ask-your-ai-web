# Handover: Ask your AI about me

Read this first, then `TODO.md`. You are picking this project up with no memory of how it was built. Everything you need to finalize the website is in this repository; the conversation that produced it is not available. The reusable engine, the model benchmark and the test fixtures are in the owner's private product project and are not here.

## What it is

Ask your AI about me (domain ask-your-ai.me, a creation of Freedom.AI Lab) turns the address of a website into a fact sheet that AI assistants can read, a small box that opens the visitor's own assistant already briefed, a contact popup that ends in the owner's own form with the message prefilled, and install steps. The mission is to help the web become conversational. It is not a chatbot: no AI runs on the owner's site and no visitor message passes through the service. The owner approves every word. A kit costs 10 USD once; a hosted "kept current" plan is planned with no price set.

Why anyone would pay: the box that opens an assistant is free everywhere (askaiwidget.com, ask-widget.com, the open-source agilek/ask-ai-widget). Nobody writes a verified fact sheet from the owner's own site, hands the visitor to the owner's contact form with the message prepared, and keeps the sheet current with the owner's approval. That is the product.

## State of things

- The landing site is built, in six languages, and live as a noindex preview at https://gregrenard.github.io/ask-your-ai-web/ (this repository, GitHub Pages).
- Everything behind "Check my site" is simulated (read the site, fact sheet, checkout, account, dashboard). The contact form sends nothing. `TODO.md` lists what is left, in priority order, with blockers marked.
- A crawler and a widget builder exist in the private product project and are tested on two sites. The agent that turns a crawl into a fact sheet, the API, the payment and the accounts are not built.

## Map of this repository

- The repository root is the generated site: `index.html` (English) and `fr/`, `es/`, `it/`, `nl/`, `de/`, plus `llms.txt`, `llms-full.txt`, `ask-your-ai.md` (the fact sheet), `how-it-works.md`, `pricing.md`, `faq.md`, `robots.txt`, `sitemap.xml`, `assets/` (logo and share cards) and `ask-your-ai.js` (the built corner box). Never edit these by hand: change the source and rebuild.
- `site-src/` is the source: `index.src.html` (one page), `i18n/strings.txt` and `i18n/js.txt` (English, French, Spanish, Italian, Dutch, German side by side), `ai/*.tpl` (llms.txt, the fact sheet, how it works, pricing, FAQ), `build_site.py` (generator), `og_images.py` (share cards).
- `site-widget/` holds the config of the corner box on this site (`config.preview.json` for the GitHub Pages address, `config.json` for the real domain) and four small prompt files for Spanish, Italian, Dutch and German. Rebuilding the box needs the engine, which is not in this repository: ask the owner, or leave `ask-your-ai.js` as it is.
- `COPY.md` (every message of the site and the writing rules), `LAUNCH.md` (launch steps and known limits), `TODO.md` (what is left).

## How to build and test

- Pages: `python3 site-src/build_site.py` (add `--base https://ask-your-ai.me --index` at launch). It fails if an English phrase is not found in the source or if English text is left on a translated page.
- Share cards: `python3 site-src/og_images.py` (needs Chrome).
- Widget: built by the engine (private project) from `site-widget/config.preview.json`; the result is `ask-your-ai.js` at the repository root.
- Preview locally: open `index.html` in a browser (it works from the file system).
- Test headlessly with Chrome: `--headless=new --window-size=W,H --virtual-time-budget=3000 --screenshot=out.png file://...`. Headless Chrome enforces a minimum window width of about 500 px, so to see a 390 px phone layout put the page in an iframe of width 390 inside a harness page. `scroll-behavior: smooth` makes `scrollTo` animate; use `behavior: "instant"` in tests. Drive the simulated flow by clicking `[data-ex=example]`, then `#buy`, `#pay-ok`, `#to-app`, and count `Uncaught` in the Chrome log.
- To publish: commit the regenerated files and push, then wait about a minute for GitHub Pages and check the live pages.

## Rules that apply here

- Everything committed is in English, including commit messages and code comments. Commit messages explain what was broken, why it was fixed this way, the numbers and what was checked. No AI attribution lines.
- Nothing outward-facing without the owner's explicit go: no push, no repository creation, no email, no payment, no message to anyone. Check `gh auth status` and use the account that owns this repository.
- Never put a secret in the repository. API keys live outside it (for example `~/.config/openrouter/key`) and are never pasted in chat or committed. Payment and sign-in keys will be the same.
- No personal names, no named customers, no named competitors and no real example sites on the public site. The only example is the fictional Example Studio. No invented numbers, customers or testimonials: write "more and more" instead of a statistic nobody measured.
- Vocabulary: fact sheet (never "brief" in front of a visitor), box, check (the free diagnosis), kit (the 10 USD setup). Titles and paragraphs have no width cap in characters, so lines wrap only when they run out of room.
- The fact sheet and `llms.txt` state facts only. Assistants refuse instructions hidden in a fetched page, so behaviour belongs in the visitor's prompt built by the engine.
- The wordmark `ask·your·ai.me` with red dots is kept. The logo mark has three dots: blue, white (ring) and red.

## Decisions already taken

- One generated page per language on its own address (not a script that swaps text), for indexing.
- Sign-in with Clerk (a development instance exists) and payment with Stripe used directly, not Clerk Billing, which is subscription-only. The marketing site stays static; the app is a separate service at `app.ask-your-ai.me`. See section 3 of `TODO.md`.
- The check is free; the 10 USD kit pays to edit and download; the owner hosts everything.
- Title: "Make your website conversational." Name: Ask your AI about me.
- The preview stays noindex until the domain and the legal pages are ready; one flag removes it.

## Open decisions (the owner)

- The model provider key, so the model benchmark can run (in the private project).
- The Stripe account, the Clerk production setup on the domain, whether the account is created before or after payment, the price and promise of the hosted plan, the legal wording.
- Native review of the Spanish, Italian, Dutch and German copy, and the Dutch title.
- Whether to ask the owner of an example site for permission to show it publicly (no real example is shown today).

## Things learned the hard way

- A page script that looks up elements placed after it in the document throws and silently skips every handler after it; the page script runs on `DOMContentLoaded` for that reason.
- Switching steps must reset each section's inline display, not only a class.
- The box's widget sits at z-index 2147483000; the header is 2147483050 and the checkout dialog 2147483060 so the language menu and the dialog stay above it.
- The box's prompt template (in the engine, private project) tells the assistant to answer "yes" with confidence when a visitor hesitates. It was tuned on a personal site and does not fit a promise of honesty: re-test it for this product.
- Chained shell commands and background servers were sometimes refused by the permission layer on the owner's machine; split commands, and do not work around a refusal.
