# borevitz-lab

**The shared core of the Borevitz Lab software ecosystem** — one `Query`,
one `Config`, one conda environment, used by every lab package.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Borevitz Lab](https://img.shields.io/badge/Borevitz%20Lab-ANU-2ea44f)](https://borevitzlab.anu.edu.au/)

```python
from datetime import date
from borevitz_lab.query import Query

query = Query(
    bbox=[148.36265, -33.52606, 148.38265, -33.50606],  # [W, S, E, N]
    start=date(2024, 1, 1),
    end=date(2024, 12, 31),
    stub='my_farm',
)
```

Every downstream package takes a `Query` and answers it — same identity,
same caches, same reproducibility guarantees everywhere.

| Package | Built on this core | What it does |
|---|---|---|
| [`pysentinel2`](https://github.com/thestochasticman/pysentinel2) | `Query`, `Config` | Self-filling local Sentinel-2 datacube — nothing downloaded twice |
| [`pysilo`](https://github.com/thestochasticman/pysilo) | `Query`, `Config` | Cached SILO daily climate — fetch once per ~5 km grid point |
| [`pyozwald`](https://github.com/thestochasticman/pyozwald) | `Query`, `Config` | Cached OzWALD meteorology + 8-day biophysical series — fetch once per grid point |
| [`pycopdem`](https://github.com/thestochasticman/pycopdem) | `Query`, `Config` | Cached Copernicus 30 m DEM + on-read slope/TWI/aspect/HLI — one download per chunk |
| [`pyslga`](https://github.com/thestochasticman/pyslga) | `Query`, `Config` | Cached SLGA soil properties (16 attributes × 6 depths) — one download per chunk |
| [`PaddockTS`](https://github.com/thestochasticman/paddocktimeseries) | `Query`, `Config` | Paddock segmentation, time series, phenology, reports |

---

## `Query` — the identity layer

A **frozen, hashable request**: *this region, this date range*. Two
queries with the same inputs are the same query — they share every
cached artefact on disk.

```python
q.bbox_hash    # region identity  (bbox snapped to ~100 m, then SHA-256)
q.time_hash    # date-range identity
q.out_dir      # final outputs for this stub
q.tmp_dir      # scratch space for this stub
```

Storage layout is *not* `Query`'s concern — packages derive their own
cache locations (usually from the hashes) in their own `Paths` class.

Three ways to build one:

```python
Query(bbox=[w, s, e, n], start=..., end=..., stub='site_a')

Query.from_lat_lon(lat=-34.38, lon=148.48, buffer_km=2.0,
                   start=..., end=..., stub='site_b')

Query.build_from_paddocks(paddocks_filepath='paddocks.gpkg',   # .gpkg / .shp / .geojson
                          start=..., end=..., stub='site_c')
```

Every constructed query is recorded in a file-locked registry
(`{out_dir}/queries.json`). Re-running an identical query is a no-op;
reusing a `stub` for *different* inputs raises `ValueError` — stubs
uniquely name a query, forever.

## `Config` — the environment layer

Where data lives and which credentials to use. Loaded once, from the
first source found:

| Source | Example |
|---|---|
| `~/.config/BorevitzLab.json` | `{"out_dir": "...", "email": "...", "tern_api_key": "..."}` |
| `BOREVITZ_LAB_*` env vars | `BOREVITZ_LAB_OUTDIR`, `BOREVITZ_LAB_TMPDIR`, `BOREVITZ_LAB_EMAIL`, `BOREVITZ_LAB_TERN_KEY` |
| Built-in defaults | `~/Documents/BorevitzLab-Outputs` · `~/Downloads/BorevitzLab-Tmp` |

Or bypass files entirely:

```python
from borevitz_lab.config import Config

cfg = Config(out_dir='/data/outputs', tmp_dir='/data/tmp')
q = Query(..., config=cfg)
```

## Design rules

The conventions every lab package follows:

- **No inheritance.** One generic `Query`; packages *compose* with it
  (functions and small classes taking a `Query`/`Config`), never
  subclass it.
- **`Config` vs `Paths`.** User-settable inputs live on `Config`;
  locations *derived* from a `Query` or `Config` live on a per-package
  `Paths` class.
- **Layered APIs.** Data-layer functions are query-agnostic
  (`bbox, start, end`); thin `*_query` adapters connect them to the
  reproducibility layer.

---

## Install

### The whole lab in one command

`borevitz_lab.yml` builds the entire ecosystem — this core, the five
data stores, PaddockTS, JupyterLab, and the full geospatial/ML stack —
from the public conda channel, no checkouts:

```bash
conda env create -f https://raw.githubusercontent.com/thestochasticman/borevitz_lab/main/borevitz_lab.yml
conda activate borevitz_lab
```

### Just this package

```bash
conda install -c conda-forge -c thestochasticman borevitz-lab
```

### From source

All lab repos share one conda environment, **`borevitz_lab`**. Each
repo's `environment.yml` creates it if missing and augments it if
present (additive — never use `--prune`):

```bash
conda env update -n borevitz_lab -f environment.yml
conda activate borevitz_lab
pip install -e .
```

Optional extra for `Query.build_from_paddocks`:

```bash
pip install -e '.[paddocks]'   # adds geopandas
```

## Test

```bash
python borevitz_lab/query.py    # True
python borevitz_lab/config.py   # prints the resolved config
```

## License

[MIT](LICENSE) · Borevitz Lab, Australian National University
