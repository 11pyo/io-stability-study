# Demand-driven or supply-driven? A pre-registered hindcast comparison of the Leontief and Ghosh models on Korean input-output tables, 2015-2024

*Wonpyo Han, Independent Researcher, Republic of Korea. Working paper, November 2026. Data, code and pre-registration: https://github.com/11pyo/io-stability-study. All numbers come from `results/results.json` through `code/make_tables.py`; tables are in `paper/tables.md`.*

**Keywords:** input-output analysis; Leontief model; Ghosh model; coefficient stability; hindcast; pre-registration; Korea

**JEL codes:** C67, C53, E23

## Abstract

Input-output analysis offers two mirror-image ways to carry one year's inter-industry structure into the
next: the demand-driven Leontief model, which holds input coefficients fixed, and the supply-driven Ghosh
model, which holds allocation coefficients fixed. We compare how well each reproduces next-year sectoral
output on the Bank of Korea's annual tables for 2015-2024 (83 and 165 sectors, eight within-basis
transitions), following the design of Bon (1986) and Dietzenbacher and Hoen (2006). Hypotheses, statistics
and decision rules were fixed and committed before any result was computed. With perfect foresight of the
exogenous vector, both models miss next-year output by about 2.5-2.7% (pooled weighted absolute percentage
error 2.72% for Leontief and 2.47% for Ghosh) and both clearly beat uniform scaling (5.48%) and their
direct-effect-only counterparts. The two models are not distinguishable at 83 sectors (log error ratio
-0.095, 90% interval -0.234 to +0.050); this result is fragile, since Ghosh is more accurate at 165 sectors and within the 2020 basis. Our directional prediction, that the supply-driven model would gain
ground in the 2020-22 recovery and price-shock transitions, is not supported. Coefficient stability did
deteriorate in those transitions for both models, by roughly 35-45%, although 2022-23 was equally unstable and the contrast is confounded with the change of benchmark basis. Without foresight, both models improve
on trend extrapolation only marginally and lose to a no-change forecast in three of six transitions. An
unplanned observation is that the relative accuracy of the two models drifts over the decade, almost monotonically in the main specification, from
Leontief ahead in 2015-17 to Ghosh ahead in 2022-24; a similar but less regular pattern appears in constant
prices. We report it as exploratory.

## 1. Introduction

A table of inter-industry transactions can be read down its columns or along its rows. Reading down the
columns gives input coefficients: how much of each product a sector buys per unit of its output. Holding
these fixed gives the Leontief model, in which final demand drives output. Reading along the rows gives
allocation coefficients: what share of a sector's output goes to each buyer. Holding these fixed gives the
Ghosh (1958) model, in which primary inputs drive output. The second reading has been criticised as
implausible as a quantity model (Oosterhaven 1988), reinterpreted as a price model (Dietzenbacher 1997) and
criticised again (de Mesnard 2009), and ways to make it more plausible have been proposed (Guerra and Sancho
2011). It remains in use, especially for supply disruptions, alongside dynamic production-network models
that relax fixed coefficients altogether (Pichler et al. 2022).

Whatever its interpretation, each model implies a concrete calculation that can be checked against the
next year's table. Bon (1986) proposed comparing the two models' stability in this way, and Dietzenbacher
and Hoen (2006) applied the comparison to Dutch tables for 1948-84. We repeat the exercise for Korea, 2015-2024, for three reasons. The period contains
a recovery from a pandemic and a large energy price shock, the kind of episode for which supply-side
reasoning is usually invoked. Annual tables at two levels of detail are public. And the comparison can be
pre-registered: there are enough arbitrary choices in such an exercise (error measure, pooling, which
years count as "shock" years) that fixing them in advance is worth the trouble.

The contribution is therefore not a new model. It is a replication on a recent period with decision rules
fixed beforehand, a constant-price check that addresses a known asymmetry between the two models, and an
honest record of a directional prediction that failed.

## 2. Data

We use the Bank of Korea's input-output tables at producer prices, domestic transactions, in current
prices. Tables for 2015-2019 follow the 2015 benchmark; tables for 2020-2024 follow the 2020 benchmark. The
benchmark years are survey-based; the other years are extension tables. We form transitions only within a
basis, which gives eight: 2015-16 to 2018-19 and 2020-21 to 2023-24. The pandemic year itself, 2019-20,
falls across the rebasing and cannot be studied this way: tables from different benchmark bases differ in
classification and compilation, so a cross-basis transition would mix structural change with rebasing.

From each table we read only the domestic intermediate block Z and total output x. Final demand
$f = x - Z\iota$ and primary inputs $w = x - Z'\iota$ ($\iota$ a vector of ones) are derived, so both accounting identities hold exactly; w
therefore includes imported intermediates. The published final-demand total agrees with the derived one to
within 1e-6 in every table. At 83 sectors no sector has non-positive output; at 165 sectors one sector in
the 2020 basis has, and is removed. A few sectors have negative derived final demand (one or two at 83
sectors, three to seven at 165), which reflects inventory change; none has negative primary inputs in
current prices. In constant prices one or two sectors have negative primary inputs in most years (Data
notes in the tables file); they are kept.

The 20 workbooks were downloaded on 13 November 2026 from the Bank of Korea's statistics system and their
SHA-256 hashes recorded; the analysis script refuses a file whose hash is not in the record.

## 3. Method

### 3.1 Models and baselines

For a transition from $t$ to $t+1$, with input coefficients $A_t = Z_t \hat{x}_t^{-1}$ and allocation
coefficients $B_t = \hat{x}_t^{-1} Z_t$, next-year output is reproduced as

```latex
\begin{aligned}
\text{Leontief:}\quad & \tilde{x}_{t+1} = (I - A_t)^{-1} f_{t+1} \\
\text{Ghosh:}\quad & \tilde{x}_{t+1}' = w_{t+1}' (I - B_t)^{-1} \\
\text{Direct demand only (DL):}\quad & \tilde{x}_{t+1} = x_t + f_{t+1} - f_t \\
\text{Direct supply only (DG):}\quad & \tilde{x}_{t+1} = x_t + w_{t+1} - w_t
\end{aligned}
```

Two further baselines are no change (N) and uniform scaling by aggregate output growth (U).

Because the identity $x_{t+1} = (I - A_{t+1})^{-1} f_{t+1}$ holds exactly, the model errors here are caused only by
coefficient change. This is a conditional hindcast: it says how much is lost by using last year's structure,
not how well output can be forecast.

A second exercise drops the foresight. The exogenous vector is extrapolated linearly from the two preceding
years, and the models are compared with linear extrapolation of output itself (T) and with no change. Six
transitions have the necessary history.

Coefficient stability is measured directly as well: next-year intermediate flows are predicted with
last-year coefficients and next-year output, from the column side for Leontief and from the row side for
Ghosh. As a reference we also adjust last year's flow matrix to next year's row and column totals by RAS.

### 3.2 Measures and decision rules

The primary measure is the weighted absolute percentage error, pooled as a ratio of sums over all
sectors $i$ and transitions in a set, and relative accuracy is its log ratio, positive when Leontief is more
accurate:

```latex
\mathrm{WAPE} = \frac{\sum |\tilde{x}_{i,t+1} - x_{i,t+1}|}{\sum x_{i,t+1}}, \qquad
r = \ln \frac{\mathrm{WAPE}_{\text{Ghosh}}}{\mathrm{WAPE}_{\text{Leontief}}}
```
 Intervals are 90% percentile intervals from 10,000 bootstrap resamples of sectors, drawn within
each basis and keeping a sector's errors in all transitions together; models are solved once and not
re-solved on resamples. The intervals describe sampling of sectors, not of years, and no multiplicity
correction is applied.

The pre-registered hypotheses were:

- H1: Leontief versus Ghosh over all eight transitions, no direction predicted.
- H2: the Ghosh model does relatively better in the shock transitions P = {2020-21, 2021-22} than in the
  other six. Because P contains a benchmark-to-extension step, a second contrast (H2b) uses 2021-22 against
  the five other extension-to-extension steps, and a rank condition requires the two P transitions to have
  the two lowest r. A shift is claimed only if all three hold.
- H3: coefficients are less stable in P, for each model, with the same second contrast.
- H4: each model beats its direct-effect-only counterpart.
- H5: without foresight, each model beats trend extrapolation.

Six robustness checks were fixed in advance: 165 sectors; energy sectors excluded from scoring; median
growth-rate error instead of WAPE; each basis separately; constant prices; and dropping 2023-24.

### 3.3 Why constant prices matter for this comparison

If each product sells at one price to all buyers, that price cancels in the allocation coefficient
$B_{ij} = p_i z_{ij} / (p_i q_i)$ but not in the input coefficient $A_{ij} = (p_i / p_j)\, a_{ij}$. In current prices the
Ghosh calculation is algebraically a cost-push price calculation (Dietzenbacher 1997), so it is helped by
relative price changes that hurt the Leontief calculation. A current-price result in favour of Ghosh during
a price shock would therefore not show that quantities are supply-driven. We address this by dividing each
row of Z and x by the producer price index of the selling sector (83 sectors mapped to the Bank of Korea's
producer price groups, 15 of them through a higher-level index), recomputing f and w from the identities,
and repeating the tests. Under this deflation B is unchanged and A becomes the physical coefficient.

### 3.4 Pre-registration and deviations

The design was reviewed before any number was computed by a reviewer who saw no data (an AI agent run
separately from the analysis); the review changed the
relative-accuracy statistic from a difference to a log ratio, added the second period contrast, the rank
condition, the constant-price check and the RAS reference, and tightened the bootstrap description. The
document was then committed (da90baf), followed by the analysis code (c99b243). One amendment was made
before any result existed: the price series mapped to one service sector had no values for 2015-17 and was
replaced by its parent index (a8c31d3). The analysis ran once (c749470). Everything in Section 5 was
conceived after seeing the results and is labelled exploratory.

### 3.5 Independent verification and one known defect

A separate re-implementation, written from the raw workbooks without the study's modules (by another AI
agent; scripts in `code/independent_check/`), reproduced every per-transition and pooled error in Tables 1,
2 and 6, the pooled r at 83 and 165 sectors, and the energy-excluded r, to within 5e-15. The bootstrap
intervals, the constant-price variant, the secondary measures and robustness checks R3, R4 and R6 were
reviewed in code but not recomputed.

The verification found one defect. The flow tables contain negative cells (88-125 at 83 sectors, 460-526
at 165), and the RAS routine stops after 1,000 iterations without reporting whether it converged. At 83
sectors it converges in every transition (23-55 iterations), so the RAS reference in Table 2 is sound. At
165 sectors it fails to converge for 2023-24, where one row's positive and negative flows nearly cancel;
the 165-sector RAS figures in the results file are therefore invalid and are not reported. No hypothesis
statistic uses RAS.

### 3.6 Use of generative AI

This study was carried out with substantial assistance from generative AI: Anthropic's Claude models
(Claude Fable 5.2 and Claude Opus 5.5, used through Claude Code, November 2026). The AI systems were used to
write the data-download and analysis code, run the pre-registered analysis, draft the pre-registration and
this text, and, as separately run agents, to review the design before data were seen and to re-implement
the main calculations independently. The research question, the decision to publish the result whatever its
direction, and responsibility for the content rest with the author, who reviewed the code, the results and
the text. Every number in the paper is generated by code from public data, and the code and its commit
history are public.

## 4. Results

### 4.1 Both structures work, to within about 2.5-2.7%

With perfect foresight, last year's structure reproduces next year's sectoral output with a pooled WAPE of
2.72% (Leontief) and 2.47% (Ghosh) (Table 1). Uniform scaling misses by 5.48% and no change by 7.36%, so
the gate is passed: both models beat uniform scaling, by 2.8 and 3.0 percentage points with intervals well
above zero (Table 3). Both also beat their direct-effect-only counterparts (H4 supported: log ratios +0.253
and +0.327), although, as noted in advance, this is close to an accounting necessity: the direct-only error
is exactly the change in a sector's intermediate sales or purchases.

Rank correlations between hindcast and actual growth are high for both models and higher for Ghosh in every
transition (median 0.69 for Leontief and 0.79 for Ghosh; Table 7).

### 4.2 H1: the two models are not distinguishable at 83 sectors

Pooled over eight transitions, r = -0.095 with a 90% interval of -0.234 to +0.050 (Table 3). The point
estimate favours Ghosh by about 9%, but the interval includes zero, so by the pre-registered rule the
models are not distinguishable. The robustness checks agree in sign in most variants and disagree in
strength (Table 4). At 165 sectors the interval lies below zero (r = -0.127, -0.238 to -0.016): Ghosh is
more accurate. With energy sectors excluded from scoring the difference disappears (r = -0.006). In constant
prices it shrinks to -0.030 with an interval centred near zero. By basis, Leontief is ahead in the 2015
basis (+0.110, interval includes zero) and Ghosh in the 2020 basis (-0.206, interval -0.379 to -0.025).

Under the pre-registered rule the primary result stands and is labelled fragile: two robustness checks
(165 sectors; the 2020 basis alone) reach a different decision. The models are not distinguishable at 83
sectors; the Ghosh point estimate moves toward zero when energy sectors are excluded or prices are held
constant, but those intervals overlap with the main one, so we do not attribute the difference to either.

### 4.3 H2: no shift towards the supply-driven model in the shock transitions

The prediction was that Ghosh would do relatively better in 2020-21 and 2021-22 than elsewhere. The contrast
has the predicted sign but is small and its interval includes zero (d2 = +0.061, -0.142 to +0.264); the
second contrast is smaller still (+0.025); and the rank condition fails, because the two lowest values of r
are 2023-24 and 2022-23, not the shock transitions (Table 3). None of the three components holds, in any
variant (Table 4; the 165-sector H2 values go beyond the pre-registration). H2 is not supported.

### 4.4 H3: coefficients were less stable in the shock transitions

Intermediate flows predicted from last year's coefficients miss by 6-8% in the 2015-basis transitions
and by 11-12% in 2020-21 and 2021-22 (Table 2). The log ratios are +0.371 for input coefficients and +0.309 for
allocation coefficients, with intervals above zero, and the second contrast agrees (+0.336 and +0.283). H3
is supported for both models, in current and in constant prices and with energy sectors excluded
(Table 4b).

Two qualifications. First, 2022-23 is as unstable as the two shock transitions (12.3% and 11.0%), and the
whole 2020 basis is less stable than the 2015 basis, so the contrast may measure a difference between bases
as much as a shock. Second, the RAS reference shows how much of the instability is not captured by row and
column totals: adjusting last year's flows to next year's margins still misses by 5.3% in the
extension-to-extension steps, against 8.6-8.8% for the fixed-coefficient predictions. The pre-registered
compilation rule (RAS error below a quarter of the model error) is not triggered.

### 4.5 H5: without foresight the models add little

When the exogenous vector must itself be extrapolated, errors rise to 4.2-11.1% (Table 6). Both models are
better than trend extrapolation of output by the pre-registered rule (log ratios +0.048 and +0.074,
intervals just above zero), but the gain is a few tenths of a percentage point, and by construction it only
shows that last year's coefficient change does not carry over. More telling is the comparison we did not
build a hypothesis around: the no-change forecast beats both models in 2018-19, 2022-23 and 2023-24. A
structure that is accurate when the driver is known does not help when the driver is unknown.

## 5. Exploratory observation: a drift in relative accuracy

Ordered by time, r falls almost monotonically: +0.214, +0.214, +0.068, -0.052 in the 2015 basis and
-0.130, -0.142, -0.261, -0.301 in the 2020 basis (Table 1). Leontief is ahead early and Ghosh late, and the
largest Ghosh advantage comes in 2022-24, after the shock. A similar pattern appears at 165 sectors and,
less regularly, in constant prices; it is weaker with energy sectors excluded (Table 5).

We did not predict this and have not tested it. Three readings are possible. It may be a property of how
extension tables were compiled under each benchmark; the two bases differ in classification detail and
source data. It may be real: allocation patterns across buyers may have become more stable relative to
input mixes. Or it may be chance across eight transitions. The data here cannot separate these. A direct
check would use the benchmark-to-benchmark linked tables, which are compiled independently of the annual
extension method.

## 6. Limits

- The comparison is conditional on knowing next year's final demand or primary inputs. It measures
  structural stability, not forecasting skill, and Section 4.5 shows how little survives without foresight.
- Extension tables are partly produced by updating benchmark structures. If the updating procedure holds
  one kind of coefficient closer to fixed than the other, it would favour the corresponding model. The RAS
  reference does not rule this out.
- Current prices mix price and quantity change. The constant-price variant uses one price index per selling
  sector, 15 of 83 through a parent index, and does not deflate imports separately.
- Eight transitions in one country. The intervals reflect which sectors happen to be in the tables, not
  which years happened to be observed, and about 30 intervals are reported without correction.
- The period contrast is confounded with the benchmark basis: both shock transitions are in the 2020 basis.
- Nothing here bears on the economic interpretation of the Ghosh model. A more accurate hindcast does not
  make supply-driven quantities plausible; in current prices it may only reflect that nominal allocation
  shares are insensitive to prices.

## 7. Conclusion

On Korean tables for 2015-2024, last year's inter-industry structure reproduces next year's sectoral output
to within about 2.5-2.7% when the driver is known, whichever way the table is read. The two readings are
not distinguishable at 83 sectors; the supply-driven one is slightly more accurate at 165 sectors and within
the 2020 basis, so that result is fragile. Coefficients of both kinds were markedly less stable in the 2020-basis transitions, including but not only
the shock years. The supply-driven
model did not gain in the shock transitions specifically, contrary to our prediction. And without knowledge
of the driver, neither model reliably improves on assuming that nothing changes.

For users of input-output models the practical reading is modest: a fixed structure is a good accounting
device for propagating a known change, a poor forecaster, and the choice between the two readings of the
table matters less for accuracy than the stability of the period one applies it to.

## Declarations

Funding: none. Competing interests: none. Data availability: all source tables are public (Bank of Korea);
code, pre-registration and results are openly available (see Reproducibility).

## Reproducibility

Pre-registration, code, concordance and results are at https://github.com/11pyo/io-stability-study. The commit sequence is:
da90baf (pre-registration and model definitions), c99b243 (analysis code and synthetic tests), a8c31d3
(amendment 1), c749470 (results). `python -B code/analysis.py <panel dir> <ppi csv> results` reproduces
`results/results.json` (SHA-256 d8681d19...); `code/make_tables.py` rebuilds the tables. The source
workbooks are public and are identified by hash in the provenance record.

## References

Bibliographic details were checked against publisher or RePEc records on 13 November 2026.

- Bon, R. (1986). Comparative stability analysis of demand-side and supply-side input-output models. *International Journal of Forecasting*, 2(2), 231-235. https://doi.org/10.1016/0169-2070(86)90112-3
- de Mesnard, L. (2009). Is the Ghosh model interesting? *Journal of Regional Science*, 49(2), 361-372.
- Dietzenbacher, E. (1997). In vindication of the Ghosh model: a reinterpretation as a price model. *Journal of Regional Science*, 37(4), 629-651. https://doi.org/10.1111/0022-4146.00073
- Dietzenbacher, E., and Hoen, A. R. (2006). Coefficient stability and predictability in input-output models: a comparative analysis for the Netherlands. *Construction Management and Economics*, 24(7), 671-680. https://doi.org/10.1080/01446190600567985
- Ghosh, A. (1958). Input-output approach in an allocation system. *Economica*, 25(97), 58-64.
- Guerra, A.-I., and Sancho, F. (2011). Revisiting the original Ghosh model: can it be made more plausible? *Economic Systems Research*, 23(3), 319-328.
- Miller, R. E., and Blair, P. D. (2009). *Input-Output Analysis: Foundations and Extensions* (2nd ed.). Cambridge University Press.
- Oosterhaven, J. (1988). On the plausibility of the supply-driven input-output model. *Journal of Regional Science*, 28(2), 203-217. https://doi.org/10.1111/j.1467-9787.1988.tb01208.x
- Pichler, A., Pangallo, M., del Rio-Chanona, R. M., Lafond, F., and Farmer, J. D. (2022). Forecasting the propagation of pandemic shocks with a dynamic input-output model. *Journal of Economic Dynamics and Control*, 144, 104527. https://doi.org/10.1016/j.jedc.2022.104527
