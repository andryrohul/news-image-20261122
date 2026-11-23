# The Sunday Ledger — 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/andryrohul/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/andryrohul/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A picture-led newspaper front page summing up the world's news of
Sunday 22 November 2026 in one 1024×1024 image: 36 verified stories,
13 of them with their own drawn scene, a world map with pins, a
numbers strip, and a DATE CHECK box listing the big stories from
other days that were deliberately left out.

## How it works

`main.py` draws the whole page with the Python 3.13 standard library
only — no Pillow, no network, no fonts on disk. It defines its own
5×7 bitmap font, draws every scene (COP31 dawn in Antalya, drones
over Kyiv, radars in Bahrain, and ten more) with plain shapes and a
fixed random seed, and writes a deterministic PNG.

## Run

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output is `out/entry.png`. Running it twice writes byte-identical
files.

## Bounty

[Sum up 22 November's world news in one image](https://make.fun/bounty/news-image-20261122)
