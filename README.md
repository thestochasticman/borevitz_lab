# borevitz-lab

Shared core primitives for [Borevitz Lab](https://borevitzlab.anu.edu.au/)
pipelines.

- **`borevitz_lab.query.Query`** — a frozen, hashable request to run a
  pipeline over a bounding box and date range. Derives cache directories
  (`tmp_dir`, `out_dir`, `aoi_dir`, `query_dir`) from a `stub` identifier,
  and maintains a file-locked JSON registry of all queries ever run so
  repeat runs reuse cached outputs. Constructors: direct bbox,
  `Query.from_lat_lon(...)` (point + km buffer), and
  `Query.build_from_paddocks(...)` (envelope of a GeoPackage / Shapefile /
  GeoJSON — requires the `paddocks` extra).
- **`borevitz_lab.config.Config`** — output/cache directories plus
  credentials (SILO email, TERN API key), loaded from
  `~/.config/BorevitzLab.json` (legacy `~/.config/PaddockTS.json` still honoured) or `BOREVITZ_LAB_*` / legacy `PADDOCKTS_*` environment variables.

Downstream projects (e.g.
[PaddockTS](https://github.com/thestochasticman/paddock-ts-local))
subclass `Query` to add their own derived output paths.

## Install

All lab repos share one conda environment, `borevitz_lab` — each repo's
`environment.yml` creates it if missing and adds its own packages if it
exists (never use `--prune`):

```bash
conda env update -n borevitz_lab -f environment.yml
conda activate borevitz_lab
pip install -e .
# with geopandas support for build_from_paddocks:
pip install -e '.[paddocks]'
```

## Test

```bash
python borevitz_lab/query.py  # prints True
```
