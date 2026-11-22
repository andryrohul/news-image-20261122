# THE SUNDAY WORLD — Sunday 22 November 2026

A broadsheet front page summing up the world's news of Sunday 22 November
2026 in one image, for the make.fun bounty
"Sum up 22 November's world news in one image" (news-image-20261122).

## The image

38 stories, each with its own drawn picture and its own colour — no two
stories share a colour or an illustration:

- **3 hero stories** with full drawn scenes: the COP31 climate talks closing
  in on a deal in Antalya, Russia's 400-drone / 110-missile night attack on
  Ukraine, and Iran's strikes on US bases in Bahrain.
- **10 secondary stories** with their own mini scenes: the burning Sparta II
  in the Gulf of Finland, the strike on Kryvyi Rih, the capsized mourners'
  boat in Bayelsa, coalition talks in Jerusalem, the Gaza aid-vehicle strike,
  the 'El Chapo Isidro' capture in Sinaloa, power rationing in Tehran, the
  Nvidia accounting probe, Bolsonaro in intensive care, and the AUKUS row in
  Canberra.
- **A dotted world map** with 38 numbered pins, one per story, each in its
  story's colour.
- **25 more stories** in the "ALSO ON THIS SUNDAY" list, each with its own
  pictogram (database, game controller, plane, house fire, candle, race car,
  ballot box, cedar tree, swimmer, and more).
- **A UTC timeline** marking the 03:00 GMT COP31 objection deadline, region
  bars, a DATE CHECK box naming older news deliberately left out, and a
  sources line. Every story names its outlet; claims and forecasts are
  labelled as such.

## How it is built

`main.py` is Python standard library only (no Pillow, no network, no files
read). It draws everything in code — a hand-written 5x7 vector font, flat
vector scenes, and a pure-Python PNG encoder (zlib + struct) — and writes
`$MAKEFUN_OUTPUT_DIR/entry.png` (1024x1024, deterministic: two runs produce
byte-identical output).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
