---
archive: Pontus Abrahamsson — frontend CI under 2 minutes
source_conversation: https://x.com/pontusab/status/2121982070193058191
conversation_id: "2121982070193058191"
---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2121630861502378328
published: 2026-11-14 23:46:30 Asia/Shanghai (UTC+8)
post_id: "2121630861502378328"

CI is now the most important thing to make fast.

---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2121982070193058191
published: 2026-11-15 23:02:04 Asia/Shanghai (UTC+8)
post_id: "2121982070193058191"
quoted: "2121630861502378328"

Our frontend CI is now under 2 minutes. What we did:

- tsc to bun check
- oxlint, every rule we can turn on
- shards filled by recorded test time
- PRs run only the tests the diff can reach
- lint, typecheck, build and tests all run in parallel https://t.co/Ix8NwrHg9u

---

author: Jonghyuk Lee (@jonghyukbuilds)
source: https://x.com/jonghyukbuilds/status/2121984240086859786
published: 2026-11-15 23:10:42 Asia/Shanghai (UTC+8)
post_id: "2121984240086859786"
in_reply_to: "2121982070193058191"

@pontusab How do you work out which tests a diff can reach? Import graph?

---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2121985296933761035
published: 2026-11-15 23:14:54 Asia/Shanghai (UTC+8)
post_id: "2121985296933761035"
in_reply_to: "2121984240086859786"

@jonghyukbuilds Vitest --changed vs the merge base: a test runs if it imports a changed file. Non-imported inputs (lockfile, configs, generated client) force a full run, merge queue + main always run everything

---

author: ivanmaierg (@imaierg)
source: https://x.com/imaierg/status/2121984067847717351
published: 2026-11-15 23:10:00 Asia/Shanghai (UTC+8)
post_id: "2121984067847717351"
in_reply_to: "2121982070193058191"

@pontusab I'm working on this and am glad to confirm this is the direction to go.

---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2121985514677170205
published: 2026-11-15 23:15:45 Asia/Shanghai (UTC+8)
post_id: "2121985514677170205"
in_reply_to: "2121984067847717351"

@imaierg The runtime map is the biggest win, our heaviest tests mount the real route tree so the import graph pulls them in on almost any change

---

author: Jonghyuk Lee (@jonghyukbuilds)
source: https://x.com/jonghyukbuilds/status/2121987150598246754
published: 2026-11-15 23:22:15 Asia/Shanghai (UTC+8)
post_id: "2121987150598246754"
in_reply_to: "2121985296933761035"

@pontusab Huh, didn't think of the generated client as a full-run trigger. Does a lockfile bump alone make CI take forever?

---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2121987736542613738
published: 2026-11-15 23:24:35 Asia/Shanghai (UTC+8)
post_id: "2121987736542613738"
in_reply_to: "2121987150598246754"

@jonghyukbuilds Yes, a lockfile bump runs the full suite, a dep change can shift any test. But full ≠ forever: 10 duration-balanced shards at ~150s each

---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2121990184816484483
published: 2026-11-15 23:34:19 Asia/Shanghai (UTC+8)
post_id: "2121990184816484483"
quoted: "2121982070193058191"
image: 2026-11-15-pontusab-2121990184816484483.png
image_source: https://pbs.twimg.com/media/HXLS0KeaoAAbf85.png
image_size: 3680x5008

Instructions to get your CI under 2 minutes ⚡ https://t.co/GZzfvJsGIb https://t.co/vIqyh9enMH

---

author: Pontus Abrahamsson (@pontusab)
source: https://x.com/pontusab/status/2122282105992560756
published: 2026-11-16 18:54:18 Asia/Shanghai (UTC+8)
post_id: "2122282105992560756"
conversation_id: "2122282105992560756"
follow_up_to: "2121982070193058191"
image: 2026-11-16-pontusab-2122282105992560756.png
image_source: https://pbs.twimg.com/media/HXPcU0zbIAA9fYx.png
image_size: 3240x2036

The fastest CI run is the one that never fails. Pre-commit hooks are back, and Lefthook makes them fast.

- Bun formatter
- Oxlint
- React Doctor https://t.co/9YAdTHZV1J
