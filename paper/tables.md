### Table 1. Output hindcast with perfect foresight of the exogenous vector (83 sectors, current prices): WAPE of sectoral output, %

| Transition | Leontief | Ghosh | Direct demand (DL) | Direct supply (DG) | Uniform (U) | No change (N) | r = ln(Ghosh/Leontief) |
|---|---|---|---|---|---|---|---|
| 2015-16 | 1.96 | 2.42 | 2.18 | 2.46 | 4.61 | 5.12 | +0.214 |
| 2016-17 | 2.00 | 2.47 | 2.76 | 3.42 | 5.75 | 7.40 | +0.214 |
| 2017-18 | 1.95 | 2.09 | 2.54 | 2.58 | 4.34 | 5.61 | +0.068 |
| 2018-19 | 2.16 | 2.05 | 2.05 | 2.25 | 4.39 | 4.59 | -0.052 |
| 2020-21 | 3.13 | 2.75 | 5.39 | 5.19 | 6.15 | 11.23 | -0.130 |
| 2021-22 | 3.49 | 3.03 | 5.50 | 5.53 | 7.21 | 11.41 | -0.142 |
| 2022-23 | 3.65 | 2.81 | 3.82 | 3.05 | 6.35 | 6.66 | -0.261 |
| 2023-24 | 2.71 | 2.00 | 2.83 | 2.41 | 4.40 | 5.61 | -0.301 |
| Pooled | 2.72 | 2.47 | 3.50 | 3.43 | 5.48 | 7.36 | -0.095 |

### Table 2. Coefficient stability (83 sectors, current prices): WAPE of next-year intermediate flows, %

| Transition | Input coefficients (Leontief) | Allocation coefficients (Ghosh) | RAS-adjusted previous table |
|---|---|---|---|
| 2015-16 | 6.99 | 7.74 | 4.18 |
| 2016-17 | 6.28 | 7.59 | 3.49 |
| 2017-18 | 7.03 | 7.17 | 4.08 |
| 2018-19 | 7.93 | 8.29 | 5.15 |
| 2020-21 | 12.44 | 11.69 | 8.15 |
| 2021-22 | 12.27 | 11.38 | 8.31 |
| 2022-23 | 12.33 | 11.04 | 7.76 |
| 2023-24 | 8.83 | 8.05 | 5.10 |
| Pooled | 9.58 | 9.30 | 5.99 |
| Extension-to-extension steps only | 8.77 | 8.57 | 5.29 |

### Table 3. Pre-registered statistics and decisions (83 sectors, current prices; 90% bootstrap intervals over sectors)

| Hypothesis | Statistic | Estimate | 90% interval | Decision |
|---|---|---|---|---|
| Gate | WAPE(U) - WAPE(Leontief) | +0.028 | [+0.022, +0.034] | Leontief beats uniform scaling |
| Gate | WAPE(U) - WAPE(Ghosh) | +0.030 | [+0.024, +0.037] | Ghosh beats uniform scaling |
| H1 | r, eight transitions | -0.095 | [-0.234, +0.050] | not distinguishable |
| H2 | d2 = r(O) - r(P) | +0.061 | [-0.142, +0.264] | not distinguishable |
| H2b | d2* = r(O*) - r(P*) | +0.025 | [-0.236, +0.270] | not distinguishable |
| H3 Leontief | ln WAPE_Z(P)/WAPE_Z(O) | +0.371 | [+0.259, +0.488] | less stable in P |
| H3b Leontief | ln WAPE_Z(P*)/WAPE_Z(O*) | +0.336 | [+0.199, +0.471] | less stable in P* |
| H3 Ghosh | ln WAPE_Z(P)/WAPE_Z(O) | +0.309 | [+0.200, +0.420] | less stable in P |
| H3b Ghosh | ln WAPE_Z(P*)/WAPE_Z(O*) | +0.283 | [+0.164, +0.400] | less stable in P* |
| H4 Leontief | ln WAPE(DL)/WAPE(Leontief) | +0.253 | [+0.194, +0.309] | structure adds to direct effect |
| H4 Ghosh | ln WAPE(DG)/WAPE(Ghosh) | +0.327 | [+0.249, +0.403] | structure adds to direct effect |
| H5 Leontief | ln WAPE(T)/WAPE(Leontief), no foresight | +0.048 | [+0.007, +0.090] | better than trend |
| H5 Ghosh | ln WAPE(T)/WAPE(Ghosh), no foresight | +0.074 | [+0.035, +0.117] | better than trend |
| H2 rank condition | two lowest r_t are the P transitions | order: 2023-24, 2022-23, 2021-22, 2020-21, 2018-19, 2017-18, 2016-17, 2015-16 | - | does not hold |

### Table 4. Robustness of H1 and H2 (estimate and 90% interval)

| Variant | H1: r | H2: d2 | H2b: d2* | Rank condition |
|---|---|---|---|---|
| Main: 83 sectors, current prices | -0.095 [-0.234, +0.050] | +0.061 [-0.142, +0.264] | +0.025 [-0.236, +0.270] | does not hold |
| R1: 165 sectors | -0.127 [-0.238, -0.016] | +0.077 [-0.077, +0.227] | +0.036 [-0.166, +0.234] | does not hold |
| R2: energy sectors excluded from scoring | -0.006 [-0.144, +0.136] | +0.000 [-0.196, +0.197] | -0.086 [-0.338, +0.154] | does not hold |
| R3: median growth-rate error instead of WAPE | -0.090 [-0.244, +0.102] | +0.065 [-0.216, +0.360] | - | - |
| R4: 2015 basis only | +0.110 [-0.099, +0.331] | - | - | - |
| R4: 2020 basis only | -0.206 [-0.379, -0.025] | - | - | - |
| R5: constant prices of the selling product | -0.030 [-0.161, +0.104] | +0.157 [-0.081, +0.391] | +0.108 [-0.155, +0.368] | does not hold |
| R6: without 2023-24 | -0.062 [-0.208, +0.087] | +0.120 [-0.105, +0.343] | - | - |

### Table 5. r by transition in the robustness variants

| Transition | Main | R1: 165 sectors | R2: energy excluded | R5: constant prices |
|---|---|---|---|---|
| 2015-16 | +0.214 | +0.207 | +0.281 | +0.165 |
| 2016-17 | +0.214 | +0.119 | +0.294 | +0.228 |
| 2017-18 | +0.068 | -0.131 | +0.160 | +0.161 |
| 2018-19 | -0.052 | -0.067 | -0.001 | +0.040 |
| 2020-21 | -0.130 | -0.177 | -0.057 | -0.163 |
| 2021-22 | -0.142 | -0.179 | +0.039 | -0.112 |
| 2022-23 | -0.261 | -0.198 | -0.147 | -0.101 |
| 2023-24 | -0.301 | -0.311 | -0.313 | -0.224 |

### Table 6. Hindcast without foresight (T3; 83 sectors, current prices): WAPE of sectoral output, %

| Transition | Leontief | Ghosh | Trend (T) | No change (N) |
|---|---|---|---|---|
| 2016-17 | 5.08 | 5.82 | 5.28 | 7.40 |
| 2017-18 | 4.47 | 4.16 | 4.56 | 5.61 |
| 2018-19 | 5.44 | 5.62 | 5.77 | 4.59 |
| 2021-22 | 7.13 | 6.72 | 7.28 | 11.41 |
| 2022-23 | 10.78 | 11.06 | 11.78 | 6.66 |
| 2023-24 | 7.07 | 5.89 | 7.25 | 5.61 |

### Table 7. Secondary measures by transition (83 sectors, current prices)

| Transition | Median abs. growth error, Leontief (pp) | Ghosh (pp) | Spearman, Leontief | Spearman, Ghosh | Sectors below 0.05% of output (excluded) |
|---|---|---|---|---|---|
| 2015-16 | 1.57 | 2.03 | 0.720 | 0.805 | 2 |
| 2016-17 | 2.22 | 1.90 | 0.787 | 0.818 | 2 |
| 2017-18 | 1.85 | 2.02 | 0.793 | 0.813 | 2 |
| 2018-19 | 2.16 | 2.09 | 0.614 | 0.748 | 2 |
| 2020-21 | 3.33 | 3.11 | 0.652 | 0.696 | 2 |
| 2021-22 | 3.65 | 3.31 | 0.722 | 0.781 | 2 |
| 2022-23 | 2.98 | 2.56 | 0.559 | 0.827 | 2 |
| 2023-24 | 3.08 | 2.10 | 0.571 | 0.741 | 2 |
| Median over transitions | - | - | 0.686 | 0.793 | - |

### Data notes

```json
{
 "165": {
  "2015": {
   "dropped_nonpositive_output": [],
   "n_sectors": 165,
   "negative_f": {
    "2015": 3,
    "2016": 4,
    "2017": 3,
    "2018": 5,
    "2019": 5
   },
   "negative_w": {
    "2015": 0,
    "2016": 0,
    "2017": 0,
    "2018": 0,
    "2019": 0
   }
  },
  "2020": {
   "dropped_nonpositive_output": [
    "062"
   ],
   "n_sectors": 165,
   "negative_f": {
    "2020": 4,
    "2021": 4,
    "2022": 3,
    "2023": 4,
    "2024": 7
   },
   "negative_w": {
    "2020": 0,
    "2021": 0,
    "2022": 0,
    "2023": 0,
    "2024": 0
   }
  }
 },
 "83": {
  "2015": {
   "dropped_nonpositive_output": [],
   "n_sectors": 83,
   "negative_f": {
    "2015": 1,
    "2016": 1,
    "2017": 1,
    "2018": 1,
    "2019": 2
   },
   "negative_w": {
    "2015": 0,
    "2016": 0,
    "2017": 0,
    "2018": 0,
    "2019": 0
   }
  },
  "2020": {
   "dropped_nonpositive_output": [],
   "n_sectors": 83,
   "negative_f": {
    "2020": 2,
    "2021": 2,
    "2022": 2,
    "2023": 2,
    "2024": 2
   },
   "negative_w": {
    "2020": 0,
    "2021": 0,
    "2022": 0,
    "2023": 0,
    "2024": 0
   }
  }
 },
 "83_constant_prices": {
  "2015": {
   "negative_f": {
    "2015": 1,
    "2016": 1,
    "2017": 1,
    "2018": 1,
    "2019": 2
   },
   "negative_w": {
    "2015": 1,
    "2016": 1,
    "2017": 1,
    "2018": 1,
    "2019": 1
   }
  },
  "2020": {
   "negative_f": {
    "2020": 2,
    "2021": 2,
    "2022": 2,
    "2023": 2,
    "2024": 2
   },
   "negative_w": {
    "2020": 0,
    "2021": 1,
    "2022": 2,
    "2023": 2,
    "2024": 1
   }
  }
 }
}
```
