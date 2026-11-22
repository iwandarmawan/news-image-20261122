# THE WORLD TODAY — Sunday 22 November 2026

[![make.fun](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/iwandarmawan/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/iwandarmawan/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A one-page newspaper front page summing up the world news of Sunday
22 November 2026, drawn by a pure-stdlib Python 3.13 program
(`main.py`, own PNG encoder + 5x7 bitmap font, no network, deterministic).

## Stories (all verified against Reuters / AP / ANI reporting, 22 Nov 2026)

- **COP31 close to final deal** — new package announced in Antalya, Turkey;
  COP31 presidents Australia + Turkey hope for consensus; plenary to approve
  Sunday morning; delegates have until 03:00 GMT to object.
- **Five killed in Gaza floods** — four children among the dead after heavy
  rains collapsed a sandbank in central Gaza; 70,000 tents flooded;
  1,500 emergency calls.
- **Nepal PM lands in Delhi** — Balendra Shah arrives for a two-day state
  visit, his first trip abroad since taking office in March; talks with
  Prime Minister Modi on Monday.
- **M 4.1 quake hits Myanmar** — 02:35 IST, depth 95 km
  (lat 24.404 N, long 94.616 E); no casualties reported.

## Run

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB). Two runs produce
identical bytes.

Bounty: https://make.fun/bounty/news-image-20261122
