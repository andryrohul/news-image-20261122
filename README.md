[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/andryrohul/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/andryrohul/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# THE SUNDAY GLOBE — Sunday 22 November 2026

One page, 36 stories, every one dated Sunday 22 November 2026. A clean
default newspaper front page: big bold masthead, numbers strip, region
bars, a UTC timeline of the day, three hero stories and ten secondary
stories with drawn scenes, a dotted world map with numbered pins, and a
23-story also-on list grouped by region.

Every story carries a certainty tag — CONFIRMED, CLAIM, REPORTED,
PENDING or FORECAST — explained in the legend at the bottom. The red
DATE CHECK box lists the big stories deliberately left out because they
happened on earlier days (the 400-drone night, the Peru earthquake,
'El Chapo Isidro', the Kryvyi Rih strike, and more).

## How it is built

`main.py` is Python 3.13, standard library only, fully deterministic:
it draws the whole page in code and writes `entry.png` (1024x1024) to
`$MAKEFUN_OUTPUT_DIR`. Running it twice produces byte-identical output.
No network, no external files, no fonts on disk — the lettering is drawn
from bitmap fonts defined in the code.

## Files

- `main.py` — the whole entry: fonts, scenes, map, layout, PNG writer
- `entry.png` — the rendered page
- `LICENSE` — MIT
