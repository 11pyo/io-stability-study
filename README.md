# Demand-driven or supply-driven? Leontief vs Ghosh hindcasts on Korean input-output tables, 2015-2024

Wonpyo Han (Independent Researcher). A small pre-registered study. It asks how well one year's inter-industry structure reproduces the next
year's sectoral output, reading the table down its columns (Leontief, demand-driven) or along its rows
(Ghosh, supply-driven), on the Bank of Korea's annual tables (83 and 165 sectors, eight within-basis
transitions).

**Paper (PDF): [paper/paper.pdf](paper/paper.pdf)**

**Main findings** (text in [paper/manuscript.md](paper/manuscript.md), numbers in [paper/tables.md](paper/tables.md))

- Knowing next year's final demand or primary inputs, both models miss sectoral output by about 2.5%
  (pooled WAPE 2.72% Leontief, 2.47% Ghosh) and clearly beat uniform scaling (5.48%).
- The two are not distinguishable at 83 sectors; Ghosh is slightly more accurate at 165 sectors.
- The predicted gain of the supply-driven model in the 2020-22 recovery and price-shock transitions was
  **not** found. Coefficient stability fell by roughly 35-45% from 2020 for both models.
- Without knowing the driver, neither model reliably beats a no-change forecast.

## How the study was run

| Step | Commit |
|---|---|
| Pre-registration, price concordance, model definitions (before any result) | `da90baf` |
| Analysis code and synthetic tests (before the first run on real tables) | `c99b243` |
| Amendment 1 (missing price years for one sector; no result seen) | `a8c31d3` |
| The one pre-registered run (`results/results.json`) | `c749470` |
| Paper draft, generated tables, independent-verification notes | later commits |

The study was carried out with AI assistance. The design was reviewed before it was frozen by a separate
AI agent that saw no data, and the main numbers were recomputed by another agent with separately written
code ([code/independent_check/](code/independent_check/), [results/NOTES.md](results/NOTES.md)).

## Reproduce

```bash
pip install numpy openpyxl
python code/ecos_fetch_io.py <data dir>            # downloads the 20 Bank of Korea workbooks (unofficial file service)
python code/analysis.py <data dir> <producer-price csv> results
python code/make_tables.py results/results.json paper/tables.md
python -m pytest code                               # synthetic-data tests
```

The producer price index file (Bank of Korea ECOS 4.1.1.1, basic classification, annual, 2013-2025) is
needed only for the constant-price robustness check. Source tables are public and are not redistributed
here; `code/ecos_fetch_io.py` records each file's SHA-256 and the analysis refuses files not in that record.

## License

Code: Apache-2.0 (`LICENSE`). Text of the paper and the tables: CC BY 4.0. Please cite as
"Han, W. (2026), Demand-driven or supply-driven? A pre-registered hindcast comparison of the Leontief and
Ghosh models on Korean input-output tables, 2015-2024, working paper,
https://github.com/11pyo/io-stability-study".
