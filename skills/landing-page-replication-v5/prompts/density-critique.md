# When to load: Loop 3 gate debates; after audit.py numbers; vision pass on two screenshots
# Precondition: Target shot + replica shot (same viewport width)
# Output: IMR-ish judgment, missing elements, cut vs add recommendation

# Density critique prompt

Give the model **two images** (target left/first, replica second) plus optional `audit.py --imr` output.

```text
You are checking landing-page density fidelity — not brand taste.

1. Blur both to ~10px in your mind. Describe dark/light mass shapes. Do they match?
2. Estimate ink-mass: hero / mid / dark bands. Flag any band where replica feels >8% emptier.
3. Count product surfaces (windows/cards with UI) in hero. Target vs replica.
4. List MISSING density elements (rows, chips, charts, secondary floats) — max 7, priority order.
5. List elements to REMOVE (noise that flattens rhythm) — max 5.
6. Opportunity cost: recommend finish 2 surfaces at 90% OR add a new section? Pick one.
7. Generic-SaaS sniff: if wordmark covered, is replica closer to anti-reference "{anti_ref}" than to target?
8. Runtime sniff (v4): if target has canvas/WebGL/long scroll, note whether this still-frame PASS could hide Static Snapshot (Gallery I) or Scroll Compress (Gallery J). Do not declare ship-ready on density alone.
9. End with: PASS / FAIL on density gate, one sentence why.
```

Fill `{anti_ref}` from Two-Reference Rule. Prefer FAIL + concrete missing list over vague "add polish."
