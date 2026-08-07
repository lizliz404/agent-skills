---
name: seo-master
description: >
  Audits, improves, and reports evidence-backed SEO and generative-engine
  visibility across technical, on-page, content, schema, performance, GEO/AEO,
  links, analytics, SERP, and tracking workflows. Use when a user requests an
  SEO/GEO audit, AI citation or brand-mention analysis, search remediation,
  content optimization, or a prioritized organic-discovery plan.
---

# seo-master

Evidence first. Separate observed facts, inferences, and proposals. Never present
technical eligibility as a promise of ranking, citation, recommendation, or
traffic.

## 0. Quick start

Use the smallest workflow that answers the request:

```text
Audit [site] for technical SEO + GEO. Read-only. Sample [N] URLs.
Fix on-page + truthful schema for [URL]. Preserve brand and analytics.
Measure AI visibility for [brand] across [platforms] with [query set].
Compare SEO vs GEO opportunities for [market, locale, device].
```

Before work, state:

- target host, locale, audience, site type, and conversion goal;
- read-only audit or authorized edits;
- access available: repository, browser, logs, GSC, GA4, rank data, AI tools;
- sample or full crawl, URL cap, and time window;
- house property: yes/no. Apply section 13 only when yes.

If required access is missing, continue with observable evidence and label the
unobservable layer `UNVERIFIED`; do not fill gaps with estimates.

## 1. Scope & when-not-to

### Do run when

- The site has a public discovery or acquisition goal.
- The user asks about rankings, citations, AI mentions, crawlability, content,
  schema, performance, links, analytics, or search reporting.
- A deployable path exists and the requested access is authorized.

### Do NOT run (anti-patterns)

| Situation | Action |
|-----------|--------|
| Private-by-design sites (e.g. red-flowers: noindex + WAF CN) | Skip entirely — never SEO-refine |
| Dead / abandoned projects with no publish path | Report kill criteria; do not polish |
| Spam tactics (PBNs, cloaking, link farms, doorway pages) | Refuse; propose white-hat alternative |
| Keyword stuffing / hidden text | Strip; rewrite pain-first |
| Fabricating GSC verification tokens / fake metrics | REPORT presence only; never invent |
| Brand/asset redesign under SEO pretext | Out of scope (see House rules) |
| `projects/_templates/**`, `docs/AUDIT.md`, payment code | Do not touch |

### Scope questions

Ask only questions that materially alter execution:

1. Which canonical host, markets, languages, and priority conversions?
2. Audit only, recommendations, or code/content changes?
3. Which evidence sources are authorized and available?
4. Which AI surfaces matter to the audience: ChatGPT, Gemini, Google AI
   Overviews/AI Mode, Perplexity, Doubao, Claude, or another engine?
5. What must remain untouched?

Record unresolved choices as assumptions. Never let a missing optional data
source block checks that can be performed safely.

## 2. Technical SEO audit

Audit in dependency order: reachability → renderability → crawlability →
indexability → canonicalization → discovery → internal architecture.

### 2.1 Evidence sample

Include at minimum, when in scope:

- homepage;
- one URL per indexable template;
- priority conversion pages;
- one paginated, filtered, localized, and JavaScript-heavy URL where present;
- redirect, 404, soft-404 candidate, and canonical duplicate samples;
- URLs reported by GSC or logs, if access exists.

For every finding record URL, timestamp, method, observed value, expected value,
evidence, confidence, impact, and affected scope. Do not extrapolate a sampled
finding to the whole site without a crawl or corroborating data.

### 2.2 Reachability, rendering, and crawlability

- Record DNS/TLS failures, final GET status, redirect chain, latency, and host.
- Compare raw HTML with rendered DOM for canonical, robots meta, headings,
  links, primary copy, and structured data.
- Parse `robots.txt` for the tested user agent. A `Disallow` controls crawling;
  it is not a page-level `noindex`.
- Check WAF/CDN responses separately from robots policy. A spoofed user-agent
  request does not authenticate a vendor crawler.
- Test robots and sitemap files on every host/subdomain that serves sampled URLs,
  redirects to or from the canonical host, or appears in hreflang/sitemaps.
- Flag infinite spaces: parameters, faceted paths, calendars, session IDs,
  internal search, and duplicate sort orders.

### 2.3 Indexability

For each sampled URL classify:

`INDEXABLE`, `EXCLUDED-AS-INTENDED`, `BLOCKED-BY-TECHNICAL-CONFLICT`, or
`UNVERIFIED-IN-INDEX`.

Check:

- final status is indexable content, not redirect/error/soft error;
- `meta robots` and `X-Robots-Tag`;
- whether robots permits the tested crawler to fetch page-level directives; if
  blocked, classify the directive's crawler visibility as `UNVERIFIED`;
- canonical target status, indexability, locale, and content equivalence;
- GSC URL Inspection/indexing reports when authorized;
- orphan status and internal-link discoverability.

Never claim “indexed” from a 200 response, sitemap entry, or `site:` query alone.

### 2.4 Canonical, host, redirects, and hreflang

- Treat owner intent, production bindings, redirects, canonicals, sitemaps,
  internal links, and analytics configuration as evidence. Resolve conflicts;
  do not assume one signal is universally authoritative.
- Require one-hop permanent redirects for retired canonical URLs where safe.
- Reject loops, chains, protocol/host oscillation, mass redirects to irrelevant
  pages, and query loss that changes meaning.
- Require self-referential canonical on canonical pages unless a documented
  cross-domain or variant strategy says otherwise.
- For localized equivalents, require reciprocal valid language-region codes,
  indexable canonical targets, and `x-default` only when a true fallback exists.

### 2.5 Sitemaps and architecture

- Parse XML; do not count matching lines.
- Validate sitemap-index recursion, XML syntax, HTTP status, canonical host,
  indexable URLs, `lastmod` truthfulness, and URL limits.
- Exclude redirects, errors, duplicates, blocked/noindex URLs, internal search,
  and noncanonical parameters.
- Confirm priority pages receive descriptive internal links from the topic,
  product, category, or locale hubs that contain them in the site architecture.
- Report crawl depth as observed distribution, not a universal pass/fail number.

### 2.6 Technical scorecard

Use statuses, not a pseudo-scientific score:

| Layer | Status | Evidence | Scope | Confidence | Next action |
|---|---|---|---|---|---|
| Reach/render | PASS/FIX/BLOCK/UNVERIFIED | URL/log | sample/all | H/M/L | ... |
| Crawl/index | PASS/FIX/BLOCK/UNVERIFIED | directive/GSC | sample/all | H/M/L | ... |
| Canonical/redirect | PASS/FIX/BLOCK/UNVERIFIED | chain/HTML | sample/all | H/M/L | ... |
| Sitemap/links | PASS/FIX/BLOCK/UNVERIFIED | parsed XML/crawl | sample/all | H/M/L | ... |

## 3. On-page SEO

Optimize the page for one primary intent and the jobs needed to satisfy it.

1. Match title, visible heading, opening, sections, media, and CTA to intent.
2. Make titles and descriptions specific and nonduplicative; judge truncation
   from rendered SERPs when available, not a fixed character quota.
3. Use a clear page topic and logical heading hierarchy. Do not enforce “exactly
   one H1” as a ranking rule; flag confusing document structure.
4. Put the useful answer before biography, history, or promotional filler.
5. Add internal links where they advance the task, using descriptive anchors.
6. Give images meaningful alternatives when informative; use empty `alt` for
   decorative images.
7. Check visible copy against canonical, schema, Open Graph, and product facts.
8. Remove doorway duplication, hidden text, keyword stuffing, and templated
   filler.

Output: `KEEP`, `REWRITE`, `MERGE`, `REDIRECT`, `NOINDEX`, or `DELETE` for each
page, with evidence and destination where applicable.

## 4. Content & E-E-A-T

E-E-A-T is a qualitative quality lens, not a published Google score.

### 4.1 Evidence gate

For consequential claims, require:

- a named source, first-party evidence, or clearly described methodology;
- author/reviewer identity and demonstrated competence for the claim where an
  incorrect answer could affect health, safety, rights, or material decisions;
- publication and material-update dates when freshness matters;
- ownership, editorial, contact, correction, privacy, and commercial disclosure
  required by the site's function, jurisdiction, risk, or commercial incentives;
- claims that match the cited source and do not exceed it.

For YMYL topics, escalate unsupported medical, legal, financial, or safety advice.
Never create credentials, reviews, test results, customers, or outcomes.

### 4.2 CORE-EEAT review

`【Proposal】` Use this internal rubric for diagnosis only:

| Dimension | Test |
|---|---|
| Coverage | Does the page complete the user's task and answer necessary follow-ups? |
| Originality | Is there first-hand evidence, analysis, data, or a useful synthesis? |
| Recency | Are time-sensitive claims reviewed and dated? |
| Evidence | Can a reviewer trace consequential claims to reliable sources? |
| Experience | Are first-hand methods, constraints, and outcomes demonstrated? |
| Expertise | Does the author/reviewer demonstrate credentials or first-hand competence for the claim? |
| Authority | Do independent sources in the same field recognize the entity or work? |
| Trust | Are identity, incentives, limitations, and corrections transparent? |

Assign `PASS`, `WEAK`, `FAIL`, or `UNVERIFIED` per dimension. Do not average the
labels into a claimed Google score.

### 4.3 Semantic gap and refresh

- Build an entity/attribute/question map from the query set, SERP, customer
  language, and first-party data.
- Add missing concepts only when they help the task; avoid synonym padding.
- Preserve URLs with earned value unless evidence favors merge/redirect.
- Refresh changed facts and examples; do not change dates without material work.
- Prefer one useful new fact, example, test, or decision aid over generic length.

## 5. Keyword and demand research

Treat keywords as evidence of demand and language, not insertion targets.

### Intent-first table

| Query cluster | Intent | Audience/job | Evidence source | Business value | Existing URL | Action |
|---|---|---|---|---|---|---|
| ... | learn/compare/buy/navigate | ... | GSC/SERP/research | H/M/L | ... | keep/create/merge |

### Workflow

1. Seed from products, problems, customer interviews, site search, sales/support,
   GSC, paid-search terms, and competitor/category language.
2. Expand variants by task, entity, comparison, alternative, constraint, locale,
   and funnel stage.
3. Inspect current SERPs by locale/device/date; classify dominant intent and
   result type.
4. Cluster by shared intent and answer requirements, not an arbitrary overlap
   threshold.
5. Map one canonical page or page family per cluster; identify cannibalization.
6. Prioritize by evidenced demand, conversion fit, strategic value, feasibility,
   authority gap, and maintenance cost.
7. Label volume, difficulty, and trend data with provider, geography, and date.

`【Proposal】` If comparable volume data is unavailable, use ordinal H/M/L inputs
with written reasons. Do not invent numeric opportunity scores.

## 6. Structured data / JSON-LD

Structured data describes visible truth; it does not guarantee rankings, rich
results, or AI citations.

### Type selection

- Use the most specific Schema.org type supported by page content.
- `Organization`/`LocalBusiness`: real identity, sameAs, contact, location.
- `WebSite`: site identity; add actions only when the action truly works.
- `Article`/`NewsArticle`: author, dates, headline, image, publisher.
- `Product`/`SoftwareApplication`: real product attributes; include `Offer` only
  with current price, currency, availability, and URL.
- `BreadcrumbList`: visible navigational hierarchy.
- `VideoObject`, `Event`, `JobPosting`, `Recipe`, or other types only when page
  content and current provider eligibility support them.
- FAQ or How-to markup may describe visible content, but never promise a Google
  rich result or AI extraction; check current provider documentation first.

### Validation

1. Extract every JSON-LD block from raw and rendered HTML.
2. Parse as JSON; resolve duplicate/conflicting entities and stable `@id` links.
3. Match every claim to visible content and current facts.
4. Validate vocabulary with Schema.org tooling.
5. Validate provider eligibility with the provider's current rich-result docs
   and test when that provider supports the page's structured-data type.
6. Save errors/warnings with URL and timestamp. Never “validate mentally.”
7. **No fake `price: 0`** on paid products; omit Offer if price unknown.

## 7. Performance / Core Web Vitals

Use field data at the 75th percentile when available; use lab data to diagnose.
Google's current “good” thresholds are LCP ≤2.5 s, INP ≤200 ms, and CLS ≤0.1
([official reference](https://web.dev/articles/vitals)). Re-check the reference
at runtime.

Record:

- source: CrUX, PageSpeed Insights, GSC CWV, RUM, or lab;
- URL-level or origin-level aggregation;
- device, locale, connection/CPU profile, sample window, and collection date;
- field status and lab reproduction separately.

Prioritize the measured bottleneck:

- LCP: server response, critical resource discovery, image/font priority.
- INP: long tasks, main-thread work, hydration, event handlers.
- CLS: unsized media/ads/embeds, injected content, font swaps.

Do not claim a pass from one Lighthouse run. Re-test representative templates
under fixed conditions and verify field movement after the reporting window.

## 8. GEO / AEO — generative recommendation and citation

GEO here means increasing the probability that a brand, product, fact, or page
is retrieved, mentioned, recommended, or cited in a generated answer. It is not
“traditional SEO plus an `llms.txt` file.”

### 8.1 Source-selection model

Diagnose three distinct paths:

| Path | What can happen | Observable levers | Measurement limit |
|---|---|---|---|
| Model memory | A model recalls learned associations without live retrieval | durable entity/fact consistency; broad legitimate recognition | training corpus and attribution usually unobservable |
| Search/retrieval | Engine retrieves an index or live sources for the prompt | crawl/index eligibility, relevance, answer fit, authority, freshness | retrieval/reranking systems are platform-specific black boxes |
| User-directed fetch | A user action causes the engine to fetch a page | fetcher access, page availability, renderability, answer clarity | one fetch does not imply future indexing or citation |

This separation is supported by vendors publishing different training, search,
and user-fetch agents (OpenAI and Anthropic official crawler docs). Never use a
bot hit, training opt-in, or organic rank as proof of generated inclusion.

For every observed answer, record whether search/retrieval was visibly enabled.
If the interface does not disclose it, mark the path `UNKNOWN`.

### 8.2 Platform matrix

Verify current behavior at execution time; interfaces and controls change.

| Surface | Safe current statement | Primary control/evidence | Do not infer |
|---|---|---|---|
| ChatGPT search | `OAI-SearchBot` is used to surface sites in ChatGPT search; its control is independent of `GPTBot` training control | robots policy, official IP ranges, answer citations | allowed means ranked/cited |
| Google AI Overviews / AI Mode | Standard SEO eligibility applies; Google says there are no extra requirements or special optimizations | `Googlebot`; indexability; `nosnippet`, `data-nosnippet`, `max-snippet`, `noindex` | `Google-Extended` controls these Search features |
| Gemini outside Search | Product and grounding behavior must be tested in the named Gemini surface | visible citations, official product docs; `Google-Extended` for specified training/grounding uses | Google Search behavior equals every Gemini product |
| Perplexity | `PerplexityBot` surfaces and links sites in search results; `Perplexity-User` serves user-triggered requests | robots policy for bot, official IP lists, visible citations | crawler access guarantees recommendation |
| Claude search | `Claude-SearchBot` supports search quality; `Claude-User` supports user-directed retrieval; `ClaudeBot` is for potential training data | robots policy, official docs, visible citations | `ClaudeBot` is the citation crawler |
| Doubao | No first-party public crawler/citation control was verified for this V6 research pass | repeatable manual tests, visible citations, consented referral/log data | `Bytespider` purpose or access guarantees Doubao inclusion |

Official references:

- [OpenAI crawlers](https://platform.openai.com/docs/bots)
- [Google AI features in Search](https://developers.google.com/search/docs/appearance/ai-features)
- [Google common crawlers / Google-Extended](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers)
- [Perplexity crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers)
- [Anthropic crawlers](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)

### 8.3 Crawler and retrieval eligibility

1. Read robots groups for the exact agent; account for precedence and each
   subdomain.
2. Check page status, canonical, robots meta, `X-Robots-Tag`, and rendered
   availability.
3. Check CDN/WAF policy and logs. Compare source IP against the vendor's current
   official ranges before attributing a request; user-agent strings are spoofable.
4. Separate training policy from search/citation policy:
   - OpenAI: `GPTBot` training; `OAI-SearchBot` search; `ChatGPT-User` user action.
   - Anthropic: `ClaudeBot` training; `Claude-SearchBot` search;
     `Claude-User` user action.
   - Perplexity: `PerplexityBot` search; `Perplexity-User` user action.
   - Google Search AI features: standard `Googlebot` control.
5. Respect the owner's content-use policy. Do not silently trade training access
   for assumed visibility.
6. After a change, allow documented propagation/recrawl time and re-test.

Crawler eligibility is required for retrieval paths that use that crawler; it is
never proof of ranking, retrieval, mention, or citation.

### 8.4 Citation-ready answer units

Use page structure to make correct extraction easier:

- Open each query-targeted section with a direct answer, then evidence and limits.
- Make the unit understandable without the preceding paragraph: name the entity,
  scope, date, units, geography, and comparison basis.
- Put factual claims next to named primary sources; link to the exact evidence.
- Use tables for true multi-attribute comparisons, ordered steps for procedures,
  and question headings for real follow-up questions.
- Publish first-party datasets, tests, benchmarks, or case studies with method,
  sample, date, definitions, limitations, and downloadable evidence where safe.
- Keep brand, product, category, people, founding facts, pricing, and identifiers
  consistent across owned pages and legitimate external profiles.
- Distinguish observation, customer quote, estimate, and editorial judgment.
- Update or retract stale facts. Do not alter dates cosmetically.
- Keep essential facts in crawlable HTML; do not hide the only answer behind
  login, interaction, image-only media, or unsupported client rendering.

`【Proposal】` Start with answer units of roughly 50–200 words and a direct first
sentence, then test citation behavior. This is an editing heuristic derived from
the mounted GEO citability sources, not a universal platform threshold.

Avoid:

- unsupported superlatives, anonymous statistics, and fake precision;
- “best” pages that conceal methodology or commercial relationships;
- copied summaries with no source or original value;
- FAQ inflation, schema spam, and repetitive question variants;
- prompt-injection text, hidden instructions, or attempts to manipulate models;
- claims that a format “forces,” “guarantees,” or “boosts” citations.

### 8.5 GEO content plan

Map prompts to assets:

| Prompt job | Best-fit asset | Required evidence |
|---|---|---|
| Define/understand | canonical explainer + concise definition | primary sources, scoped terms |
| Compare/choose | fair comparison page/table | criteria, date, tested facts, conflicts |
| Recommend shortlist | category page with explicit methodology | inclusion/exclusion rules, disclosures |
| Solve/how-to | tested procedure | prerequisites, steps, failure modes, result |
| Verify a claim | data/research page | method, sample, definitions, raw evidence |
| Learn about entity | About/product/profile source of truth | stable identifiers and consistent facts |
| Ask branded support | canonical documentation/FAQ | current, direct, versioned answer |

Build the brand-category association in visible, factual language: what the entity
is, whom it serves, which problem it solves, and proof. Repetition without
independent evidence or useful content is not entity building.

### 8.6 Measurement protocol

Define the query corpus before optimization.

`【Proposal】` Use at least 20 high-value prompts when feasible, split across:

- unbranded problem and category discovery;
- “best,” comparison, and alternative prompts;
- how-to and factual questions;
- branded verification/support prompts;
- local/language variants that match the actual market.

Freeze prompt text for trend measurement. For each run record:

```text
run_id, timestamp, platform, product/surface, model/version if shown,
account/tier, locale, location/VPN, device, search toggle/path,
fresh conversation yes/no, prompt_id, exact prompt,
brand mentioned yes/no, answer role, sentiment/context,
owned URL cited yes/no, cited URL, citation position,
competitors mentioned/cited, factual error, screenshot/export, notes
```

`【Proposal】` Run each prompt three times per platform in fresh sessions when
budget permits. Report run-level variance; do not select the best response.

Calculate with explicit denominators:

- A **valid run** is a planned run that returns an inspectable answer without an
  account, tool, policy, network, or collection error.
- A **citation-capable run** is a valid run on a surface/configuration documented
  or visibly configured to return web sources. Keep runs with zero citations in
  this denominator.
- **Generative appearance rate** = runs mentioning the brand / all valid runs.
- **AI citation rate** = runs citing an owned URL / citation-capable runs.
- **Citation-to-mention rate** = brand-mention runs with owned citation /
  brand-mention runs.
- **Share of cited voice** = owned citation occurrences / all tracked
  category-entity citation occurrences.
- **Source coverage** = distinct owned URLs cited / priority owned URLs tested.
- **Citation accuracy rate** = correct supported owned citations / audited owned
  citations.

Report every metric as `numerator/denominator (rate)`. If the denominator is zero,
report `N/A` and the zero-denominator reason. Report each platform separately.
Combine only with predeclared weights tied to audience usage; show the unweighted
data beside the composite.

### 8.7 Evidence ladder and attribution

| Level | Evidence | Safe claim |
|---|---|---|
| E0 | no direct observation | hypothesis only |
| E1 | crawler/config inspection | eligible or blocked at tested layer |
| E2 | one generated-answer observation | appeared/did not appear in that run |
| E3 | repeated fixed-corpus runs | observed rate for platform/window/config |
| E4 | repeated tests plus logs/referrals/conversions | association across retrieval and business outcomes |

- Bot hits prove requests, not citation.
- AI referral traffic undercounts activity when referrers are absent or altered.
- A citation proves one answer used a source, not that every statement came from it.
- Manual tests are snapshots, not population estimates.
- Never claim causality from a before/after change without a design that rules out
  query, model, index, competitor, seasonality, and personalization changes.

### 8.8 Experiment design

`【Proposal】` Run controlled GEO experiments:

1. Choose matched page/query groups and save a pre-change baseline.
2. Change one class of lever: answer units, evidence, original data, entity facts,
   technical access, or internal discovery.
3. Preserve prompt corpus, platform settings, locale, and collection protocol.
4. Record crawl/index lag; do not start the post window before the changed page is
   observable.
5. Compare run-level rates and uncertainty, plus organic, referral, and conversion
   guardrails.
6. Keep, revise, or revert based on evidence. Store counterexamples.

Treat local GEO-tool scores as readiness diagnostics, not outcome validation.

### 8.9 GEO vs SEO priority

| Condition | Priority |
|---|---|
| Site cannot be crawled, rendered, indexed, or canonically understood | SEO foundation first |
| Google AI Overviews/AI Mode is the target | Standard Google SEO eligibility first; add answer/evidence improvements |
| Audience uses answer engines for category discovery/comparison | GEO experiment high |
| Site has unique data/expertise but weak extractability | GEO content high |
| Demand is navigational, local-map, or transaction-led with weak AI usage | SEO/local/CRO high |
| Brand is mentioned but facts/citations are wrong | GEO entity/source-of-truth high |
| No baseline or query corpus exists | Measurement first |

Default to shared work—technical access, useful pages, verifiable facts, and clear
structure—then fund platform-specific work only when measured opportunity warrants it.

### 8.10 `llms.txt`

`llms.txt` is a community proposal, not a universal ranking or citation directive.
The mounted GEO sources support checking and experimenting with it, but this V6
found no official OpenAI, Google Search, Perplexity, Anthropic, or Doubao claim
that publishing it improves inclusion.

`【Proposal】` Add it only when:

- maintenance ownership exists;
- links are canonical, public, and useful;
- it does not expose private or unpublished material;
- it is measured as an experiment.

Its absence is not an SEO/GEO defect. Never give it readiness points merely for
existing.

### 8.11 GEO readiness rubric

`【Proposal】` Score each dimension `0=blocked/absent`, `1=partial/unverified`,
`2=working with evidence`:

1. retrieval eligibility;
2. index/render availability;
3. answer-unit clarity;
4. claim evidence and first-party value;
5. entity consistency;
6. query-to-asset coverage;
7. repeated platform measurement;
8. attribution/business-outcome linkage.

Report the eight values separately. A total is an internal triage aid, not a
prediction of citation probability.

## 9. Backlinks and external authority

### Profile analysis

- Use GSC links plus an authorized provider when available; state coverage limits.
- Review referring domains/pages, relevance, editorial context, destination,
  anchor distribution, acquisition trend, and lost links.
- Separate manipulative links from normal scraper/spam noise.
- Check unlinked brand mentions and incorrect citations that can be reclaimed.

### Risk handling

Do not call links “toxic” from a provider score alone. Remove or disavow only with
documented evidence of manipulative activity and material risk, such as a manual
action or known paid-link scheme. Preserve a decision log.

### Earn links and citations

- original datasets, tools, benchmarks, and transparent methods;
- expert contributions and primary-source commentary;
- genuinely useful comparison/reference pages;
- broken-link replacement where the asset is a true substitute;
- correction outreach for inaccurate facts or broken citations.

No PBNs, paid-link laundering, mass guest-post spam, or automated outreach sludge.

## 10. Analytics wiring (GSC + GA4)

### GSC

- Distinguish verification-token presence, current verified ownership, API/UI
  access, and data availability.
- A meta/DNS token is evidence of configuration, not proof of current access.
- Domain properties may cover subdomains; do not demand a subdomain meta token.
- Record property type, date range, search type, country/device filters, and
  anonymization/row-limit caveats.

### GA4

- Distinguish source-code presence, network request, DebugView/realtime event,
  stream configuration, and report/API access.
- On Liz house properties, preserve `G-TXVLTJJ878` exactly. Outside section 13,
  call it a measurement ID.
- Test consent state, duplicate tags, cross-domain rules, SPA navigation, and
  conversion/key-event semantics when in scope.
- Never infer collected users or conversions from a tag string alone.

### Reporting shape

Show clicks, impressions, CTR, average position, organic sessions/users, engaged
sessions, conversions/key events, landing page, query cluster, locale/device, and
comparison window only when the source is accessible. Otherwise mark `UNVERIFIED`.

## 11. SERP and competitor analysis

Capture exact query, locale, device, date/time, personalization state, and source.

- Record organic results, local/video/image/shopping/news features, featured
  snippets, discussions, AI Overviews/AI Mode, and cited sources.
- Compare intent coverage, evidence, entity authority, information gain, format,
  freshness, UX, links, and conversion path—not word count alone.
- Separate true business competitors, organic competitors, and AI-cited sources.
- Identify answer/source gaps the site can satisfy honestly.
- Re-check volatile SERPs; one observation is not a stable market fact.

Output an opportunity table with query cluster, observed surface, winning source,
why it may satisfy the task, evidence gap, feasible asset, impact, effort, and
confidence.

## 12. Rank, AI-visibility, and outcome tracking

### Tracking setup

- Freeze keyword/query corpus, landing-page mapping, locale, device, and platform.
- Track organic rank/landing URL beside generated mentions/citations.
- Annotate releases, migrations, campaigns, algorithm events, model/product
  changes, and known outages.
- Segment branded/unbranded, intent, market, template, and conversion value.
- Keep raw observations so metric definitions can be recomputed.

### Decision rules

`【Proposal】` Predeclare stop/continue rules per initiative. Example:

- continue when leading evidence improves without technical or conversion harm;
- investigate when the canonical URL changes, variance spikes, or citations become
  inaccurate;
- stop when the site has no publish path, no audience fit, no measurable surface,
  or maintenance cost exceeds documented value.

Do not call a SERP permanently occupied or an initiative causal from two points.

## 13. House rules (Liz) — verbatim-accurate

Follow exactly on house properties:

1. **GA4 shared property ID `G-TXVLTJJ878` — never change/remove.**
2. **No brand/asset changes:** logos, fonts, palette, icons.
3. **Copy pain-first, EN default; no AI-slop filler.**
4. **Minimal change;** never rewrite whole files; **no new dependencies.**
5. **Never fabricate GSC verification tokens;** REPORT presence only.
6. **Don't touch** `projects/_templates/**`, `docs/AUDIT.md`, payment code.
7. **red-flowers** (reading site) is **private-by-design** (noindex + WAF CN) — **never SEO-refine it.**
8. **Verification:**
   - `git status -s` matches claimed files (leave pre-existing dirt unstaged)
   - `grep` GA4 ID count on touched HTML
   - sitemap `<loc>` count sane; robots head sane
   - **Stage selectively; never `git add -A`**

### Extra house semantics (operational)

- Apply these rules only after confirming a Liz house property.
- Preserve pre-existing changes and report them separately.
- Treat production bindings as strong host-intent evidence; investigate conflicts
  before migration.
- Do not stage or commit unless explicitly requested.

## 14. Execution algorithm

1. Scope gate: objective, target, access, authorization, exclusions, sample.
2. Snapshot: git/worktree state if local; date, host, redirects, robots, sitemaps.
3. Technical gate: reach/render/crawl/index/canonical before content polishing.
4. Analytics gate: identify observable and unverified layers.
5. Page/content/schema/CWV audit on representative templates.
6. Demand/SERP/competitor work when query evidence is in scope.
7. GEO audit:
   - platform and retrieval-path matrix;
   - crawler/WAF eligibility;
   - query-to-asset and answer-unit review;
   - fixed-corpus baseline;
   - citation, mention, accuracy, and source metrics.
8. Backlink/external-authority review when data exists.
9. Prioritize dependency first, then impact × confidence ÷ effort; keep the raw
   dimensions visible rather than pretending the quotient is precise.
10. Make only authorized minimal changes.
11. Verify changed files, behavioral checks, analytics preservation, and
    regressions.
12. Report method, evidence, unknowns, rollback, owners, and next measurement.

### Severity rubric

| Severity | Definition | Examples |
|---|---|---|
| P0 | production, legal, privacy, or discovery catastrophe requiring immediate action | public private data; sitewide accidental noindex; destructive redirect |
| P1 | material discovery, trust, or conversion blocker | broken canonical migration; key templates unavailable; false product facts |
| P2 | bounded opportunity or quality defect | weak answer units; missing contextual links; incomplete evidence |
| P3 | optional experiment or polish | `llms.txt` trial; low-value formatting refinement |

Severity depends on affected scope and business impact. Missing optional schema or
an AI crawler blocked by policy is not automatically P0/P1.

## 15. Commands and evidence cheatsheet

Set variables; do not paste angle-bracket placeholders into a shell:

```bash
host="example.com"
base="https://${host}"

# Final GET status, effective URL, redirects, timing.
curl -sS -L --max-redirs 10 --connect-timeout 10 --max-time 30 \
  -o /dev/null -w 'status=%{http_code} url=%{url_effective} redirects=%{num_redirects} time=%{time_total}\n' \
  "${base}/"

# Full response headers for one GET.
curl -sS --connect-timeout 10 --max-time 30 -D - -o /dev/null "${base}/"

# Robots and sitemap content. Inspect complete files or save outside protected paths.
curl -sS --connect-timeout 10 --max-time 30 "${base}/robots.txt"
curl -sS --connect-timeout 10 --max-time 30 "${base}/sitemap.xml"

# Compare responses to user-agent strings; this does not authenticate vendor bots.
curl -sS -A "OAI-SearchBot" -o /dev/null -w '%{http_code}\n' "${base}/"
curl -sS -A "PerplexityBot" -o /dev/null -w '%{http_code}\n' "${base}/"

# House verification.
git status -s
grep -oF "G-TXVLTJJ878" "path/to/touched.html" | wc -l
```

Parse XML/HTML with a real parser when correctness matters. Do not use line-count
grep as an XML element count, regex as a complete HTML parser, HEAD as proof of GET
behavior, or source presence as proof that analytics fires.

Never claim GSC/GA4 UI state, index inclusion, bot identity, or generated citation
without direct evidence.

## 16. Output template

```markdown
# SEO/GEO report — [host] — [date]

## Verdict
SHIP | FIX | BLOCK | KILL

## Method and limits
- Scope/sample:
- Access:
- Locale/device/window:
- Unknowns:

## P0 / P1 / P2
| Priority | Finding | Evidence | Scope | Confidence | Impact | Effort | Owner |

## Technical / on-page / content / schema / CWV
- Observed:
- Expected:
- Evidence:
- Action:

## GEO
- Target platforms and retrieval paths:
- Crawler/WAF eligibility:
- Query corpus and run protocol:
- Valid runs and run-level variance:
- Appearance rate — numerator/denominator:
- AI citation rate — numerator/denominator:
- Citation-to-mention rate — numerator/denominator:
- Share of cited voice — numerator/denominator:
- Source coverage — numerator/denominator:
- Citation accuracy — numerator/denominator:
- Cited URLs and competitors:
- Answer/evidence/entity gaps:

## Analytics and outcomes
- GSC verification/access:
- GA4 G-TXVLTJJ878 on house properties: intact|missing|n/a
- Organic/referral/conversion evidence:

## Changes and verification
- Files/actions:
- Tests:
- Rollback:

## Next actions
1. [dependency-first action, owner, due/measurement]
```

## 17. Failure patterns (do not repeat)

| Pattern | Instead |
|---------|---------|
| Optimize content on noindex URLs | Fix indexability first |
| Sitemap of duplicate/wrong-host URLs | Fix canonical host, then sitemap |
| DNS-based canonical migration | Read bindings; then migrate |
| Fake GSC meta to clear a checklist | Report only |
| price:0 JSON-LD | Real price or omit Offer |
| AI-slop refresh | Pain-first specifics |
| `git add -A` | Explicit paths |
| SEO-refine red-flowers | Skip |
| Demand subdomain GSC tokens under domain property | Mark n/a |
| Ignore CF managed AI bot blocks | Flag to operator |

V6 additions:

| Pattern | Instead |
|---|---|
| Treat robots `Disallow` as `noindex` | Test crawling and indexing controls separately |
| Treat allowed AI bot as citation proof | Report eligibility only; run fixed-corpus tests |
| Treat bot user-agent as authenticated | Verify current official IP ranges and logs |
| Treat `GPTBot` or `ClaudeBot` as search crawlers | Separate training, search, and user-fetch agents |
| Treat `Google-Extended` as AI Overview control | Use Googlebot/Search preview controls per official docs |
| Require or score `llms.txt` as a standard | Optional measured experiment only |
| Publish generic FAQ/schema for “GEO” | Build useful answer units backed by evidence |
| Cherry-pick one favorable AI answer | Report all valid fixed-protocol runs |
| Merge platform rates without denominators | Report platform/surface metrics separately |
| Claim causality from before/after | Control protocol and state confounders/limits |

## 18. Source synthesis and claim policy

Use this precedence:

1. current first-party platform documentation for product/crawler controls;
2. primary research for measured effects;
3. direct site, log, analytics, and fixed-protocol observations;
4. mounted practitioner tools as hypotheses and executable heuristics;
5. `【Proposal】` for unvalidated thresholds or internal decision rules.

Mounted source synthesis:

- GEO Optimizer: audit model, crawler/access diagnostics, Princeton GEO method
  summary, measurement/drift concepts.
- geo-skills: answer-block, citability, platform-test, crawler, and comparison
  workflows.
- 30x-seo: technical, quality-gate, E-E-A-T, CWV, and AI-visibility workflows.
- Claude-SEO: GEO/AI-visibility, Google AI guidance, drift, schema, and safe-fetch
  workflows.

Do not import unsupported platform percentages, fixed “optimal” word counts,
provider scores, or causal boost claims as facts. Re-check all official links in
section 8 at execution time and label changes. When evidence conflicts, report the
conflict and prefer the narrower claim.
