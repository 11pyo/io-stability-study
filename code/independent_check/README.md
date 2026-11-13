# Independent re-implementation

Written separately from `code/analysis.py` and `code/iomodel.py` (no shared code) to recompute the main
numbers from the raw workbooks with openpyxl and numpy only.

```bash
python extract.py <panel dir> <work dir>          # reads the 20 workbooks, writes one .npz per table
python verify.py <work dir> ../../results/results.json
```

It reproduces the per-transition and pooled WAPE of output and of intermediate flows, the RAS reference at
83 sectors, the no-foresight hindcasts, and the pooled log ratio r at 83 and 165 sectors and with energy
sectors excluded. It does not recompute the bootstrap intervals, the constant-price variant, the secondary
measures, or robustness checks R3, R4 and R6.
