# Notes on results.json (run c749470)

- `R1_165_sectors.pooled.wape_z_ras` and `R1_165_sectors.pooled.compilation.ras` are INVALID: RAS did not
  converge for the 165-sector 2023-24 transition (negative cells; found by independent verification).
  They are not used by any hypothesis and are not reported in the paper. The 83-sector RAS values converged.
- Independent verification reproduced the 83-sector per-transition and pooled WAPE values (output and
  intermediate flows, including RAS), the T3 values,
  and the pooled r at 83 and 165 sectors and with energy sectors excluded, to within 5e-15.
  Not recomputed independently: bootstrap intervals, constant-price variant (R5), secondary measures, R3, R4, R6.
