# Pre-registration: demand-driven versus supply-driven input-output hindcasts, Korea 2015-2024

Status: fixed before any hindcast, error, or coefficient-change number was computed. An independent review
of a first draft (no data involved) was incorporated before this version was frozen. Later changes go into a
dated "Amendments" section with the reason, never by editing the text above it.

## 1. Question

Given one year's input-output structure, how well does it reproduce the next year's sectoral output when
the exogenous vector is known, and does the demand-driven (Leontief) or the supply-driven (Ghosh) model do
this better? Was the answer different in the post-pandemic recovery and price-shock transitions (2020-21,
2021-22)? The pandemic year itself (2019-20) cannot be studied: it falls across a rebasing.

The design follows Bon (1986) and Dietzenbacher and Hoen (2006, Dutch tables 1948-84): coefficient
stability, hindcast with perfect foresight of the exogenous vector, hindcast without it. This is a
replication on another country and period, at two classification levels, with decision rules fixed in advance.

## 2. Data

- Bank of Korea input-output tables, producer prices, domestic transactions table, current prices.
- Years 2015-2019 (2015 benchmark basis) and 2020-2024 (2020 benchmark basis). 20 workbooks, downloaded
  2026-11-13 from the ECOS file service; SHA-256 in `PROVENANCE_ecos_panel.txt` in the data folder.
- Classification: 83 sectors (primary) and 165 sectors (robustness 1 only).
- Transitions t -> t+1 only within a basis: 2015-16, 2016-17, 2017-18, 2018-19, 2020-21, 2021-22, 2022-23,
  2023-24 (eight). 2015-16 and 2020-21 are benchmark-to-extension steps; the other six are
  extension-to-extension steps.

From each table only the domestic intermediate block Z (n x n, rows sell, columns buy) and total output x
(column 9290) are used. Everything else is derived so that both accounting identities hold exactly:

- domestic final demand f_i = x_i - sum_j Z_ij (includes exports and inventory change)
- primary inputs w_j = x_j - sum_i Z_ij (value added plus imported intermediates)
- input coefficients A = Z diag(x)^-1, allocation coefficients B = diag(x)^-1 Z

Checks. A table is rejected if its sector codes differ from the other years of its basis, or if
max_i |(Z 1)_i + f_i^pub - x_i| / x_i > 1e-6, where f^pub is the published final-demand total (column 9190).
If a table is rejected, every transition that uses it is dropped and named; a hypothesis that loses a
transition of its shock period is reported as "not testable". Sectors with x <= 0 in any year of a basis are
dropped from that basis by deleting their rows and columns of Z while keeping x of the others, so their
flows move into f and w and both identities still hold; the count is reported. The spectral radius of A_t
(equal to that of B_t) must be below 1. Counts of sectors with f < 0 or w < 0 are reported.

## 3. What was seen before fixing this document

- Sheet names, sector codes and names, and column codes of all 20 workbooks; the first data row of one 2016
  table while checking the layout.
- The 33-sector 2019 and 2020 tables were used in an earlier, separate exercise (cross-basis 2019-20).
  No within-basis transition and no 83- or 165-sector number was computed.
- Item names (not values) of the producer price index file, to build the concordance of robustness 5.
- Prior literature was searched; its numerical results were not read.

## 4. Tests

For every transition t -> t+1. All model quantities are computed once on the full system of a basis.

**T1 Coefficient stability.** Intermediate flows of t+1 predicted with the coefficients of t:
Leontief side Zhat_ij = A_t,ij * x_{t+1,j}; Ghosh side Zhat_ij = B_t,ij * x_{t+1,i}.
Measure WAPE_Z = sum|Zhat - Z_{t+1}| / sum Z_{t+1}. For resampling, every cell is attributed to its row
(selling) sector in both models.
Compilation check: Z_t is RAS-adjusted to the row and column sums of Z_{t+1} (convergence 1e-9, at most
1,000 iterations) and WAPE_Z(RAS) is reported for every transition.

**T2 Hindcast with perfect foresight of the exogenous vector.**
- Leontief: xhat = (I - A_t)^-1 f_{t+1}
- Ghosh: xhat' = w_{t+1}' (I - B_t)^-1
- Baselines: N (no change, xhat = x_t); U (uniform, xhat = x_t * sum x_{t+1} / sum x_t);
  DL (direct demand only, xhat = x_t + f_{t+1} - f_t); DG (direct supply only, xhat = x_t + w_{t+1} - w_t).

Because x_{t+1} = (I - A_{t+1})^-1 f_{t+1} holds exactly, the model errors in T2 measure only the effect of
coefficient change. T2 is a conditional hindcast, not a forecast, and says nothing about predicting f or w.
The DL error equals -(Z_{t+1} - Z_t) 1 exactly, and the DG error the corresponding column sums.

**T3 Hindcast without perfect foresight.** The exogenous vector is extrapolated linearly from the two
preceding years of the same basis: fhat_{t+1} = 2 f_t - f_{t-1}, what_{t+1} = 2 w_t - w_{t-1}; models as in
T2. Baselines: T (xhat = 2 x_t - x_{t-1}) and N. Six transitions qualify (2016-17, 2017-18, 2018-19, 2021-22,
2022-23, 2023-24). By construction xhat_Leontief - xhat_T = (L_{t-1} - L_t) f_{t-1} (and the mirror image for
Ghosh), so T3 tests whether last year's coefficient change carries over, nothing more. The 2021-22
extrapolation starts from the 2020 trough.

**Error measures** (on t+1 output):
- primary: WAPE_x = sum_i |xhat_i - x_{t+1,i}| / sum_i x_{t+1,i}, per transition; "pooled" means the ratio of
  sums over all sector-transitions in the set.
- secondary: absolute error of growth rates, |xhat_i / x_t,i - x_{t+1,i} / x_t,i| in percentage points, pooled
  over all sector-transitions, median (first) and mean; sectors with x_t,i below 0.05% of total output are
  excluded from this measure and counted. Spearman rank correlation of predicted and actual growth per
  transition, summarised by its median over transitions.

## 5. Hypotheses and decision rules

Relative accuracy is measured by r = ln(WAPE_x(Ghosh) / WAPE_x(Leontief)); r > 0 means Leontief is more accurate.

Uncertainty. Only per-sector quantities (|e_it| and x_{t+1,i} for each transition, T1 numerators and
denominators) are resampled; models are not re-solved. Sectors are resampled with replacement within each
basis separately (10,000 draws, seed 20261113), keeping a sector's values for all transitions of its basis
together; 90% percentile intervals. The intervals treat the eight transitions as fixed. No multiplicity
correction is applied across the intervals reported; this is stated in the paper.

Sets: P = {2020-21, 2021-22}; O = the other six. P* = {2021-22}; O* = {2016-17, 2017-18, 2018-19, 2022-23,
2023-24} (extension-to-extension steps only).

- **Gate.** If neither model has a lower pooled WAPE_x than baseline U, H1 is reported as "a comparison of
  two models that are both worse than uniform scaling".
- **H1 (Leontief vs Ghosh, perfect foresight).** r pooled over the eight transitions, 83 sectors.
  "Leontief more accurate" if the interval lies above 0, "Ghosh more accurate" if below, otherwise
  "not distinguishable". No direction is predicted.
- **H2 (price-shock transitions).** d2 = r(O) - r(P). Prediction d2 > 0 (Ghosh relatively better in P).
  H2b: d2* = r(O*) - r(P*), same prediction. Rank condition: r_t of the two P transitions are the two
  lowest of the eight (probability 1/28 if the order were random). "Shift in the shock transitions" is
  claimed only if the intervals of d2 and d2* both lie above 0 and the rank condition holds; if only some
  hold, the result is reported as "partial" with each component shown.
- **H3 (stability drops in the shock transitions).** For each model s = ln(WAPE_Z(P) / WAPE_Z(O)) and
  s* with P*, O*. Prediction: positive. Supported for a model only if both intervals lie above 0.
- **H4 (structure adds to direct effects).** ln(WAPE_x(DL) / WAPE_x(Leontief)) and
  ln(WAPE_x(DG) / WAPE_x(Ghosh)), pooled. Supported for a model if the interval lies above 0. Reported with
  the caveat that this is close to an accounting necessity.
- **H5 (without foresight).** T3, pooled over six transitions: ln(WAPE_x(T) / WAPE_x(model)) for each model.
  A model is "better than trend" only if the interval lies above 0. No direction is predicted.
- **Compilation rule.** If WAPE_Z(RAS) pooled over the six extension-to-extension transitions is below
  0.25 * min(WAPE_Z(Leontief), WAPE_Z(Ghosh)) pooled over the same transitions, the H1 result is reported
  as "may reflect how extension tables are compiled".

Robustness, fixed now and reported whatever the outcome. If a robustness result contradicts the primary
result, the primary result stands and is labelled "fragile".
1. 165 sectors instead of 83: H1 only.
2. Energy sectors excluded from scoring: sectors 06, 16, 45, 46 of the 83-sector classification stay in the
   model but are left out of every numerator and denominator; H1-H3.
3. Secondary error measures in place of WAPE_x for H1 and H2 (ratio of medians in place of r).
4. Each basis separately for H1.
5. Constant prices of the selling product: rows of Z and x divided by the producer price index of the row
   sector (2020 = 100, annual; concordance `data/ppi_to_io83.csv`, 14 of 83 sectors use a higher-level
   index); f and w recomputed from the identities; H1-H3 rerun. Under this deflation the allocation
   coefficients B are unchanged and the input coefficients become A_ij * p_j / p_i.
6. Without the 2023-24 transition (the 2024 table may be preliminary): H1, H2.

## 6. Limits stated in advance

- **Current prices and the Ghosh model.** With one price per product, the product price cancels in
  B_ij but not in A_ij, and the Ghosh hindcast is algebraically a Leontief cost-push price calculation.
  In current prices, support for H2 or for the Leontief side of H3 therefore shows that nominal allocation
  coefficients do not move with prices; it is not evidence that quantities are supply-driven. Robustness 5
  is the check; the conclusion on H2 is drawn from current and constant prices together.
- **Confounding of the period contrast.** P contains one of the two benchmark-to-extension steps and lies
  entirely in the 2020 basis. H2b and H3b remove the first problem, not the second.
- **Extension tables** are partly compiled by updating benchmark coefficients, which may understate true
  coefficient change. The RAS check and the compilation rule address this only indirectly.
- Eight transitions in one country. Intervals reflect sampling of sectors, not of years.
- The supply-driven model's economic interpretation is disputed; this study compares hindcast accuracy only.
- Double deflation in robustness 5 can produce negative real primary inputs; they are counted, not removed.

## 7. Not done

No independent production statistics, no model fitting, no tuning of any constant after results are seen.
Analyses invented after seeing results are labelled "exploratory" in the paper.

## Amendments

**Amendment 1 (2026-11-13, before any result was seen).** The first run stopped while loading prices: the
producer price series mapped to sector 79 (문화 및 여행 관련 서비스) has no values for 2015-2017. Sector 79 is
now mapped, for all years, to the next higher index 예술, 스포츠 및 여가 관련 서비스 (substitutes: 15 of 83
sectors instead of 14). The run had not written or printed any statistic; no result informed this change.
