# seo-master V5 → V6 audit and change map

## Audit verdict

V5 is broad and safety-conscious, but its GEO section is a crawler/citability
checklist rather than a method for measuring generated recommendation and citation.
It also mixes evidence with rigid heuristics, promotes `llms.txt` beyond verified
adoption, conflates training agents with search agents, and contains commands that can
misreport XML, HTML, redirects, or analytics state.

V6 keeps the useful breadth and Liz safety rails while replacing unsupported
scores and promises with observable states, explicit denominators, platform
controls, fixed-query measurement, and proposal labels.

## Dimension scores

These are editorial audit scores, not performance claims. V6 scores measure
instruction completeness and claim safety before field use.

| Dimension | V5 | V6 | Why V6 changed |
|---|---:|---:|---|
| Scope and safety | 9/10 | 9/10 | Retains anti-patterns; adds authorization, access, sampling, locale, and house-property gates |
| Technical SEO | 7/10 | 9/10 | Separates crawl/index controls, rendered/raw evidence, sampling, sitemap parsing, and confidence |
| On-page SEO | 6/10 | 8/10 | Removes fixed character/link/H1 quotas; uses intent, task completion, and page decisions |
| Content and E-E-A-T | 6/10 | 8/10 | Makes E-E-A-T qualitative; adds traceable evidence, YMYL restraint, and proposal-labelled rubric |
| Keyword/demand research | 5/10 | 8/10 | Removes arbitrary overlap and volume math; adds evidence source, value, locale, and maintenance cost |
| Structured data | 5/10 | 8/10 | Removes rich-result assumptions; requires machine validation, visible parity, and current provider checks |
| Core Web Vitals | 8/10 | 9/10 | Preserves current thresholds; adds source/window/device and field-vs-lab discipline |
| **GEO depth** | **4/10** | **9/10** | Adds source-path model, platform matrix, answer units, crawler taxonomy, query corpus, metrics, experiments, and SEO-vs-GEO decisions |
| Backlinks | 6/10 | 8/10 | Replaces generic toxicity/disavow logic with evidence and material-risk gates |
| Analytics | 6/10 | 9/10 | Separates tag/token presence, runtime behavior, verified access, and report data |
| SERP/competitors | 6/10 | 8/10 | Adds reproducible context and AI-cited-source capture; removes word-count competition |
| Tracking/decision rules | 5/10 | 8/10 | Adds frozen corpora, annotations, variance, raw observations, and predeclared stop rules |
| Execution/evidence | 4/10 | 9/10 | Adds evidence ladder, method limits, confidence, parser-safe checks, rollback, and claim policy |
| Maintainability | 4/10 | 7/10 | Better internal structure and provenance, but remains intentionally large because the brief requires one full skill file |

No overall score is calculated: the dimensions are not equally important, and no
hidden weighting is defensible. GEO depth is the primary score required by this
audit.

### GEO score rationale

- **V5: 4/10.** Recognizes AI crawler access, entity signals, original
  facts, and citation-friendly structure. Loses points for an uncalibrated score,
  mandatory-looking `llms.txt`, stale crawler taxonomy, no retrieval-path model,
  no repeatable query corpus, no platform-separated metrics, and no causal limits.
- **V6: 9/10.** Covers generated mention/recommendation/citation as an operating
  system: eligibility → answer/evidence assets → repeated platform observations →
  attribution → decision. It does not receive 10/10 because Doubao lacks verified
  first-party public crawler/citation controls in this research pass, vendor
  systems remain black boxes, and V6 heuristics still need field calibration.

## Section-by-section map

| V5 section | Keep | Strengthen | Add | Delete/demote | Reason |
|---|---|---|---|---|---|
| 0. Quick start | Scoped entry prompts | Access and target declaration | Audit/edit mode, host/locale/site type, house gate | “Everything in one pass” implication | A useful run must disclose scope and unknowns |
| 1. Scope & when-not-to | Anti-pattern table verbatim | Material-only scope questions | Authorization, URL cap, AI-surface choice, protected areas | Ask-once rigidity | Missing access should constrain claims, not force guessing |
| 2. Technical audit | Reachability, robots, canonicals, redirects, sitemaps | Raw vs rendered, robots vs noindex, host-signal conflict, sample limits | Evidence record, indexability classes, parsed XML, crawl architecture | Unweighted `/100`; single binding as universal truth | Technical dependencies require observable states and scope |
| 3. On-page | Intent, titles, headings, links, alt text | Task completion and page-level disposition | KEEP/REWRITE/MERGE/REDIRECT/NOINDEX/DELETE output | Fixed title/meta lengths, exact H1, link count, first-100-word rule | Heuristics are not universal pass/fail requirements |
| 4. Content/E-E-A-T | Evidence, expertise, entities, anti-slop | Source traceability, first-hand proof, YMYL review, date integrity | Qualitative PASS/WEAK/FAIL/UNVERIFIED rubric | Any implication of a Google E-E-A-T score | Google exposes no E-E-A-T score; evidence must be inspectable |
| 5. Keywords | Intent-first clusters and pain language | Business value, conversion fit, locale/date/provider | Customer/support/site-search seeds, mapping and maintenance cost | `≥3/10` overlap, fixed secondary counts, undefined volume formula | Demand evidence must retain provenance and uncertainty |
| 6. Schema | Truthful JSON-LD and real product data | Visible parity, linked entities, machine validation | Current provider-eligibility check and rendered extraction | FAQ/HowTo/SearchAction rich-result assumptions; mental validation | Schema describes truth; it does not guarantee search or AI outcomes |
| 7. CWV | LCP/INP/CLS p75 thresholds | Field/lab separation and measured bottlenecks | Source, aggregation, device, window, test profile | Single-run pass claims | Reproducibility matters more than one score |
| 8. GEO/AEO | Entities, original facts, crawler/WAF checks, extractable content | Training vs search vs user fetch; platform-specific controls; claim caveats | Full generative-source model, platform matrix, answer units, content map, fixed query corpus, formulas, evidence ladder, experiments, SEO-vs-GEO matrix | Mandatory `llms.txt`, stale bot roles, arbitrary 0–100 citability outcome, causal “boost” language | This is the primary V6 upgrade: measure generated inclusion instead of assuming it |
| 9. Backlinks | Spam refusal, topically matched editorial links, original assets | Link-context evidence and mention reclamation | Coverage limits and decision log | Broad “toxic” handling and casual disavow | Provider risk scores alone do not establish material harm |
| 10. GSC + GA4 | No fabricated tokens/metrics; preserve house ID | Configuration vs runtime vs verified UI/API/data | Consent, SPA, stream/event semantics, report caveats | Calling token/tag presence verified analytics | Presence is not ownership, firing, collection, or report access |
| 11. SERP/competitors | Intent, features, competitor teardown | Locale/device/date and competitor type | AI surface and cited-source capture, confidence/effort table | Word-count comparison and blanket “untouchable” conclusions | SERPs are contextual and volatile |
| 12. Tracking/reporting | Segmentation and kill discipline | Frozen conditions, annotations, raw data, variance | Organic and AI visibility side by side; predeclared rules | “Permanent” SERPs, undefined cycles, arbitrary movement bands | Decisions require stable definitions and enough observations |
| 13. House rules | All eight Liz rules verbatim and exact `G-TXVLTJJ878` | Explicit house-property gate | Pre-existing-change and no-commit semantics | House-rule leakage to arbitrary sites | Protected rules remain exact without becoming universal SEO policy |
| 14. Algorithm | Dependency-first execution and severity | Evidence/access gates, verification, rollback | GEO subworkflow, attribution, unknowns, ownership | Rigid score ordering and inflated severity | A repeatable algorithm should expose what was and was not proven |
| 15. Commands | curl/git/GA4 checks | Timeouts, GET behavior, redirect bounds, quoted variables | Bot simulation caveat and parser requirement | Shell angle-bracket placeholders, HEAD proof, line-count XML, regex-complete HTML | Old commands could fail or return false confidence |
| 16. Output | Verdict, priorities, domain sections, next actions | Method, limits, evidence, scope, confidence, owner | Platform-separated GEO metrics, run protocol, cited URLs, rollback | Objective-looking scores without calibration | Reports must be auditable and decision-ready |
| 17. Failure patterns | Original table verbatim | Explicit crawler/measurement failures | Ten GEO V6 failure pairs | None of the protected original entries | Captures the highest-risk 2026 misconceptions |
| 18. Source note | Multi-source synthesis intent | Evidence precedence and runtime re-check | Official links, mounted-source roles, `【Proposal】` policy | Unsupported percentages, fixed “optimal” counts, broken portable dependency on a source file | Every material new claim gets a source class or proposal label |

## Major GEO corrections

| V5 premise | V6 treatment | Evidence basis |
|---|---|---|
| AI visibility is mostly bots + `llms.txt` + a content score | Model memory, indexed/live retrieval, and user-directed fetch are separate paths with different observability | Official OpenAI and Anthropic crawler-role separation |
| `ClaudeBot` is a citation crawler | `ClaudeBot` is potential training collection; `Claude-SearchBot` supports search; `Claude-User` supports user-directed access | Anthropic official crawler documentation, checked 2026-08-07 |
| `Google-Extended` is an AI Overview lever | Google Search AI features use normal Googlebot/Search eligibility and preview controls; Google-Extended applies to specified Gemini training/grounding uses | Google Search Central official documentation, checked 2026-08-07 |
| Allowing an AI bot means the site can be cited | Access is eligibility at one layer only; ranking, retrieval, mention, and citation remain unproven until observed | Official vendor wording plus V6 evidence ladder |
| A single AI answer demonstrates visibility | Freeze prompts and conditions, preserve all valid repeated runs, and show denominators and variance | `【Proposal】` measurement protocol derived from mounted GEO monitoring workflows |
| A generic score predicts citation | Separate readiness dimensions; validate outcomes with platform observations | Mounted citability/audit rubrics retained only as diagnostic inspiration |
| `llms.txt` is a baseline requirement | Optional measured experiment; no readiness points for existence | Community proposal plus absence of verified vendor citation-benefit claim |
| Doubao can be optimized through a known official crawler control | Mark crawler/retrieval mechanics unknown; measure the named Doubao surface directly | No first-party public control verified in this research pass |

## Claim-safety ledger

### Officially verified for V6

- OpenAI documents independent `OAI-SearchBot` and `GPTBot` controls and says
  `OAI-SearchBot` is used for ChatGPT search results:
  <https://platform.openai.com/docs/bots>
- Google says AI Overviews/AI Mode need no special optimization beyond normal
  Search eligibility; Googlebot and Search preview controls govern Search use:
  <https://developers.google.com/search/docs/appearance/ai-features>
- Google documents `Google-Extended` as a robots token for specified Gemini model
  training and grounding uses, not a separate HTTP crawler:
  <https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers>
- Perplexity documents `PerplexityBot` for search-result surfacing and
  `Perplexity-User` for user actions, with official IP lists:
  <https://docs.perplexity.ai/docs/resources/perplexity-crawlers>
- Anthropic documents distinct `ClaudeBot`, `Claude-SearchBot`, and `Claude-User`
  roles:
  <https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler>
- Current CWV “good” thresholds:
  <https://web.dev/articles/vitals>

### Sourced from mounted references, used conservatively

- Answer-first/self-contained passages, primary-source citations, explicit
  statistics, and original data are retained as testable content tactics from the
  GEO Optimizer and geo-skills references.
- Technical, schema, CWV, E-E-A-T, drift, and measurement workflow elements are
  synthesized from 30x-seo and Claude-SEO.
- No source-reported uplift percentage, platform weighting, “optimal” word count,
  or provider score is presented as a universal fact.

### Explicit proposals

V6 labels unvalidated internal methods `【Proposal】`, including:

- 20-prompt starting corpus;
- three fresh-session runs per prompt/platform;
- 50–200-word answer-unit starting range;
- controlled GEO experiment procedure;
- eight-dimension 0/1/2 readiness rubric;
- ordinal prioritization and initiative stop/continue rules.

## Verification checklist

- [x] `name: seo-master` retained with YAML frontmatter.
- [x] English body retained.
- [x] Liz's eight house rules preserved verbatim.
- [x] `G-TXVLTJJ878` spelling preserved.
- [x] When-not-to table preserved verbatim.
- [x] Original failure-pattern table preserved verbatim.
- [x] GEO now covers source paths, platform differences, automatic
  mention/recommendation/citation levers, measurement, content strategy, and
  SEO-vs-GEO priority.
- [x] `llms.txt` demoted to optional experiment.
- [x] New internal thresholds marked `【Proposal】`.
- [x] No absolute local source path appears in deliverables.
- [x] No repository, installed skill, template, audit file, payment code, commit,
  or remote was modified.

## Remaining risks

1. AI products, agents, interfaces, and documentation change quickly; re-check
   official links at execution time.
2. Doubao's public crawler/citation controls remain unverified; only direct,
   repeatable surface measurement is safe.
3. The proposed corpus sizes and answer-unit ranges need calibration by market,
   language, platform, and query class.
4. Generated answers are stochastic and personalized; V6 reduces but cannot
   eliminate measurement noise or establish causality without stronger designs.
