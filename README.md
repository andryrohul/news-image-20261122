[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/andryrohul/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/andryrohul/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# THE SUNDAY GLOBE — Sunday 22 November 2026

A newspaper front page summing up the world's news of Sunday 22 November
2026 in one image, for the [make.fun bounty](https://make.fun/bounty/news-image-20261122)
"Sum up 22 November's world news in one image" (news-image-20261122).

## The page

36 stories, grouped by theme so the day reads at a glance — CLIMATE,
CONFLICT, SPORT, POLITICS, TECH and WORLD each get their own colour and
their own treatment:

- **3 hero stories** with large drawn scenes: the COP31 climate talks
  closing in on a deal in Antalya (a summit hall with delegates, a globe
  and a wall clock at 03:00 GMT), Russia's 400-drone and 110-missile night
  over Kyiv (a lit skyline under drone trails and starburst blasts), and
  Iran's strikes on US bases in Bahrain (a burning port building and a
  container tanker on a dawn sea).
- **10 secondary stories**, each with its own detailed mini scene: the
  burning Sparta II in the Gulf of Finland, the strike on Kryvyi Rih, the
  capsized mourners' boat in Bayelsa, coalition talks in Jerusalem, the
  Gaza aid-truck strike, the 'El Chapo Isidro' capture in Sinaloa, power
  rationing in Tehran, the Nvidia accounting probe, Bolsonaro in intensive
  care, and the AUKUS row in Canberra.
- **A dotted world map** with 13 numbered pins (one per pictured story,
  each in its own colour) plus small coloured dots for the remaining
  stories.
- **23 more stories** in the "ALSO ON THIS SUNDAY" list, grouped by theme
  (SPORT, POLITICS & POWER, CONFLICT & CRISIS, PEOPLE & PLACES), each with
  its own uniquely coloured number.
- A stats strip (~200 nations, 03:00 GMT, 400+ drones, 110 missiles, 7
  killed, 2 bases), region bars, a DATE CHECK box naming older news
  deliberately left out, and a sources line. Every story names its outlet;
  claims and forecasts are labelled as such.

## How it is built

`main.py` is Python standard library only (no Pillow, no network, no files
read). It draws everything in code — a hand-written 5x7 bitmap font with
thin single-cell strokes, flat vector scenes, and a pure-Python PNG encoder
(zlib + struct) — and writes `$MAKEFUN_OUTPUT_DIR/entry.png` (1024x1024,
deterministic: two runs produce byte-identical output).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
