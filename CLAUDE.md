# p2d-resourcepack

The Place2Die server resource pack (not a plugin). Shared project rules are in the
`place2die` skill; this file holds the repo-specific ones. Linear epic: PERSO-44
(PERSO-81 pack repo, PERSO-83 models, PERSO-84 BetterModel).

## Layout

- `pack/`: pack sources, zipped as-is. `assets/<namespace>/` with one namespace per plugin,
  equal to the plugin's key namespace (`p2d_survival`, `p2d_zombies`, `p2d_loot`...).
- `tools/p2dpack/`: Python 3.13 tooling, standard library only.
  - `validation/`: `PackValidator` runs `Check` strategies (`checks.py`) over a `PackTree`.
  - `merge.py`: `PackMerger` merges BetterModel's pack (`PackSource`: folder or zip).
  - `archive.py`: `DeterministicZip`. `build.py`: the pipeline. `release/`: gitmoji semver.
  - `cli.py`: `./pack.py validate | build | version`.
- `tests/`: unittest, mirrors `tools/p2dpack`; fixtures in `tests/testing/`.

## Rules

- `./pack.py build` and `python3 -m unittest discover -s tests -t .` pass before a commit.
- Asset paths are lowercase `[a-z0-9_./-]`; item textures under `textures/item/`.
- Item ids match the plugin's `CustomItem` key: check the plugin source, don't guess.
- A plugin sets `item_model` only after a release ships the asset.
- No dependency outside the standard library (keeps CI to setup-python only).
- Placeholder art is listed in `scripts/placeholders.py` and the README table.
- Commit assets with `:bento:`; tooling changes with the gitmoji of their intent.
