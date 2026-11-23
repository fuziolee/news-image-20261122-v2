# The World in One Day — Sunday, 22 November 2026 (v2)

A one-image summary of the world's news of Sunday 22 November 2026, drawn
from scratch by a Python program (`main.py`, standard library only) as a
clean newspaper front page: 37 stories across 7 regions, a UTC timeline,
a "WHERE IT HAPPENED" world map and a "DATE CHECK" banner.

Version 2 keeps the best 37 of the 50 verified stories from v1 so the
headlines can be set larger and the page is easier to read at a glance:
4 hero stories with illustrated scene cards, 12 more stories, and 21
one-liners.

The day's four big stories: the COP31 climate summit in Antalya ends with
no deal; Russia fires 186 drones at Ukraine overnight; Iran claims it hit
two US Patriot radars in Bahrain (denied by Bahrain and the US); and a
Russia-bound cargo ship burns in the Gulf of Finland after a drone attack.

## Competition

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/fuziolee/news-image-20261122-v2/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/fuziolee/news-image-20261122-v2/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

Rescue entry (v2) for [news-image-20261122](https://make.fun/bounty/news-image-20261122)
— "Sum up 22 November's world news in one image" ($100, 50 paid places).

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB), byte-identical on every run.

## Sources

AP, Reuters, BBC, Al Jazeera, Ukrainian Air Force, IRNA, US CENTCOM.
Every figure in the image is as the cited outlet reported it on 22 November 2026.
The image is a drawn illustration, not photographs.
