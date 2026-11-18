# TODO: what is left to finalize Ask your AI about me

Status on 2026-11-18. The engine, the model benchmark and the test fixtures are in the owner's private product project and are not in this repository; items that need them say so. Legend: [x] done, [ ] to do, (owner) a decision or action that only the owner can take, (blocker) must be done before the site is public and indexed.

## Where we are

- The landing site is built, in six languages, with a sticky menu, llms.txt and AI-readiness files, share cards and its own corner box. It is live as a noindex preview at https://gregrenard.github.io/ask-your-ai-web/.
- Everything behind the "Check my site" button is simulated: nothing is crawled, no fact sheet is written, nothing is charged, no account exists, and the contact form sends nothing.
- The engine (crawler, widget builder, templates) exists in the owner's private project and is not in this repository, but the agent that writes the fact sheet from the crawl, the API, the payment and the accounts do not exist yet.

## 0. The honesty problem to fix first (blocker)

- [ ] The page says "Free. No account." about a check that does not exist yet. Before the site is indexed or announced, either build the real free check (section 2) or change the main button to a waitlist ("Tell me when it's ready") with a real email capture (needs the endpoint of section 1). Recommended: waitlist first, real check next, so the site can launch before the engine is finished.
- [ ] Keep the "Mockup / simulated" footer and the MOCKUP chip until the real flow replaces the simulation.

## 1. To open the site to the public (blockers)

- [ ] (owner) Point ask-your-ai.me at the host (GitHub Pages custom domain: a CNAME file, DNS records at the registrar, Enforce HTTPS) and decide whether www redirects to the bare domain.
- [ ] Rebuild with the domain: widget from `site-widget/config.json`, then `python3 site-src/build_site.py --base https://ask-your-ai.me --index`, then check all six pages and the widget on the real domain. Steps are in `LAUNCH.md`.
- [ ] Real contact: a form endpoint that actually delivers (an Apps Script endpoint or an email relay), a public contact address, and a test that a message arrives. The corner box's backup popup depends on it too.
- [ ] Legal pages in the six languages or at least English with a clear link: terms of use, privacy policy (what is crawled, what is stored, the named sub-processors: Clerk (sign-in), Stripe (payment), the model provider and the hosting providers, and that the data is not used for training), refund policy, a way to delete an account and its data. (owner) approve the wording; have a lawyer look before real payments.
- [ ] (owner) Native review of the Spanish, Italian, Dutch and German copy, and a look at the French. Tables: `site-src/i18n/strings.txt` and `js.txt`. Decide the registers (vous, tú, tu, je, Sie) and the Dutch title.
- [ ] A 404 page, an apple-touch icon and a web manifest, and the real favicon set (the SVG exists).
- [ ] Remove or replace the simulated dashboard from the public page, or keep it clearly labelled as a preview.
- [ ] Decide on analytics: none, or a cookie-free one, and say so on the privacy page. Today the site sets no cookies and loads no third-party scripts.

## 2. Make the free check real (the engine)

- [ ] Run the model benchmark (`bench/model_bench.py` in the private project) once the OpenRouter key is in `~/.config/openrouter/key` (owner): two free models, three under 0.1 USD per million input tokens, and a paid reference. Pick the cheapest model whose briefs have no invented numbers and whose recall against a hand-written brief is close. Read the briefs, do not trust the numbers alone.
- [ ] The agent: crawl output in, fact sheet and config.json out, with the rules of `engine/SKILL.md` in the prompt, structured output for the config, a fact check that every number, name and date appears in the crawled text, `lint_brief`, and a list of contradictions and unverifiable facts shown to the owner.
- [ ] The service: a small API behind a job queue, with headless Chrome for script-built sites, a limit on pages, bytes, tokens and time per job, a block on private and loopback addresses (SSRF), rate limits per IP and per domain, a captcha, robots.txt respected and an honest user agent.
- [ ] Hosting for the service and for the secrets (never in the repository), logs without personal data, and a cost cap per day.
- [ ] The result page: the fact sheet next to a live preview of the box in the site's colours, the exact prompt a visitor sends, the unverified facts and contradictions, and the "what would an AI say about you" readout with a shareable result URL and its own share card (designed in the brief, not built).
- [ ] Test the pipeline on two real sites against their hand-written briefs, and on three sites we did not write.

## 3. Accounts and payment: Clerk for sign-in, Stripe for money

Decision taken: Clerk for authentication (it replaces the earlier Supabase default), and Stripe used directly for payment, not Clerk Billing. Why: Clerk Billing covers subscriptions only (no one-time charge) and adds a 0.7% fee on top of Stripe's own, while the 10 USD kit is a one-time purchase, so Stripe Checkout and a webhook are needed anyway; one Stripe account then also serves the later monthly plan, with one customer portal. Clerk's free plan covers 50,000 retained users (read on clerk.com/pricing on 2026-11-18; re-check before relying on it). A Clerk development instance already exists (its screen shows "Development mode").

Architecture: the marketing site stays static on GitHub Pages. Clerk's JavaScript can load on a static page, but the dashboard, the Stripe webhook and the entitlement check need a server, so the app is a separate service at `app.ask-your-ai.me` (Next.js on Vercel is Clerk's native path) that calls the engine service. Do not try to bolt Clerk onto `index.html`.

Steps, in order:

- [ ] a. App skeleton at `app.ask-your-ai.me` with one route that verifies a Clerk session on the server.
- [ ] b. Clerk sign-in on the development instance (email code or link, social sign-in optional). (owner) Production instance: Clerk gives DNS records to add on the domain (check its current requirements) and new keys; do it at the same moment as the domain in section 1. It removes the "Development mode" badge, and users of the development instance do not carry over to production.
- [ ] c. Stripe in test mode: Checkout with `mode: payment` for the 10 USD kit, `client_reference_id` set to the Clerk user ID, success and cancel URLs back to the app. (owner) Create the Stripe account (keys, bank, tax) and the product.
- [ ] d. Webhook on `checkout.session.completed`: verify the signature, record the entitlement idempotently (our own table keyed by the Clerk user ID, or Clerk user metadata). Choose the database host for sites, crawls, fact-sheet versions, widget configs and entitlements.
- [ ] e. Gate editing and the kit download on the entitlement. The kit generator: a zip with the fact sheet, `ask-your-ai.js`, `INTEGRATE.md`, a demo page, the contact endpoint and a prompt for the owner's own assistant, in the owner's language.
- [ ] f. The dashboard: sites, fact sheet in three layers (generated, owner edits, merged), widget settings, install, billing through Stripe's customer portal, profile and account deletion through Clerk's built-in components plus deletion of our own data.
- [ ] g. Install guides per platform (WordPress, Wix, Squarespace, Webflow, Framer, plain HTML), including which plan each builder needs for custom code, and a "test in a private window" tip.
- [ ] h. (owner) Decide the order of account and payment. The mockup and the copy say the account is created with the email used to pay and a sign-in link is sent (pay first). Clerk can do that through its Backend API (create the user and a sign-in token; verify that sign-in tokens exist in the current backend SDK before relying on it). The more common pattern is to sign in before checkout, with fewer moving parts. If sign-in comes first, the kit page and one FAQ answer change in all six languages.
- [ ] i. Switch Stripe and Clerk to live only after the legal pages of section 1 exist.

## 4. After launch: kept current and hosted

- [ ] (owner) Price and promise of the "kept current" plan (re-read frequency, response time).
- [ ] The monthly plan is a Stripe subscription on the same Stripe account and customer portal, not Clerk Billing (subscriptions only, plus a fee on top of Stripe's).
- [ ] Hosted widget with a domain allowlist, a scheduled re-crawl, a diff the owner approves, and a rule that a line the owner edited is never overwritten.
- [ ] A browser event when the box or an assistant is used (for example `ask-your-ai:open`), so owners can count openings in their own analytics.
- [ ] Two more assistants as options, Grok and Mistral, which accept a prefilled question in the URL.
- [ ] A public opt-in gallery of live boxes and a small "Powered by" link in the free box, removable on the paid plan.
- [ ] The contact link built by the assistant should open the page in the visitor's language (today the box has one contact address, the English page).

## 5. Quality gates before announcing

- [ ] Lighthouse on mobile for the six pages (target above 95 and a largest contentful paint under 2 seconds); the widget script is about 90 KB before compression because it carries six languages: measure it, and lazy-load it if it costs the score.
- [ ] An accessibility pass: keyboard on the language menu and the corner box, contrast in dark mode, focus order, reduced motion (the animations already stop for it).
- [ ] A real phone test on iOS and Android, and dark mode on all six pages.
- [ ] The 5-second test with five non-technical people: if three say "a chatbot", switch the title to "Let your visitors' AI talk to your website." (see `COPY.md`).
- [ ] Re-test the box's prompt for this product: the template tells the assistant to answer "yes" with confidence when a visitor hesitates, which does not fit our promise of honesty. Run real conversations on ChatGPT, Claude, Gemini and Perplexity before launch.
- [ ] Validate the structured data (schema.org validator), the hreflang set and the sitemap, and check that llms.txt and the fact sheet load on the real domain.

## 6. Launch and growth

- [ ] Google Search Console and Bing Webmaster Tools: verify the domain, submit `sitemap.xml`, request indexing for the home page and each language. IndexNow for Bing on every change.
- [ ] First links, because links are what make indexing fast: the repository README, freedom.ai and the other sites we control, a launch post, Product Hunt, Hacker News, LinkedIn and X, directories.
- [ ] Publish the free "what would an AI say about you" check as the shareable hook, and watch Search Console for the six languages.
- [ ] (owner) Decide whether to ask the owner of an example site for permission to show it publicly; until then no real example is shown.

## 7. Housekeeping

- [ ] A design-tool draft of the site was set aside because its output was not what was expected. Decide whether to send a sharper brief (`DESIGN-BRIEF.md` is not in this repository) or to keep the hand-built page.
- [ ] Keep `COPY.md` and `LAUNCH.md` in step with this file.
