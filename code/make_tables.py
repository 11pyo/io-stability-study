"""
Builds the paper's tables (Markdown) directly from results/results.json so that no number is typed by hand.

Usage: python -B make_tables.py <results.json> <output .md>
"""

import json
import os
import sys
import tempfile

ORDER = ("2015-16", "2016-17", "2017-18", "2018-19", "2020-21", "2021-22", "2022-23", "2023-24")


def pct(v):
    return f"{v * 100:.2f}"


def ci(c):
    return f"[{c[0]:+.3f}, {c[1]:+.3f}]"


def verdict(c, pos, neg, mid="not distinguishable"):
    return pos if c[0] > 0 else (neg if c[1] < 0 else mid)


def main(argv):
    if len(argv) != 3 or not os.path.isfile(argv[1]):
        print("usage: make_tables.py <results.json> <output .md>")
        return 2
    with open(argv[1], encoding="utf-8") as f:
        R = json.load(f)
    M = R["main_83_current_prices"]
    out = []

    out.append("### Table 1. Output hindcast with perfect foresight of the exogenous vector (83 sectors, current prices): WAPE of sectoral output, %\n")
    out.append("| Transition | Leontief | Ghosh | Direct demand (DL) | Direct supply (DG) | Uniform (U) | No change (N) | r = ln(Ghosh/Leontief) |")
    out.append("|---|---|---|---|---|---|---|---|")
    for t in ORDER:
        e = M["per_transition"][t]
        out.append(f"| {t} | {pct(e['wape_x_leontief'])} | {pct(e['wape_x_ghosh'])} | {pct(e['wape_x_DL'])} | {pct(e['wape_x_DG'])} | "
                   f"{pct(e['wape_x_U'])} | {pct(e['wape_x_N'])} | {e['r']:+.3f} |")
    p = M["pooled"]
    out.append(f"| Pooled | {pct(p['wape_x_leontief'])} | {pct(p['wape_x_ghosh'])} | {pct(p['wape_x_DL'])} | {pct(p['wape_x_DG'])} | "
               f"{pct(p['wape_x_U'])} | {pct(p['wape_x_N'])} | {M['point']['H1_r']:+.3f} |")

    out.append("\n### Table 2. Coefficient stability (83 sectors, current prices): WAPE of next-year intermediate flows, %\n")
    out.append("| Transition | Input coefficients (Leontief) | Allocation coefficients (Ghosh) | RAS-adjusted previous table |")
    out.append("|---|---|---|---|")
    for t in ORDER:
        e = M["per_transition"][t]
        out.append(f"| {t} | {pct(e['wape_z_leontief'])} | {pct(e['wape_z_ghosh'])} | {pct(e['wape_z_ras'])} |")
    out.append(f"| Pooled | {pct(p['wape_z_leontief'])} | {pct(p['wape_z_ghosh'])} | {pct(p['wape_z_ras'])} |")
    c = p["compilation"]
    out.append(f"| Extension-to-extension steps only | {pct(c['leontief'])} | {pct(c['ghosh'])} | {pct(c['ras'])} |")

    out.append("\n### Table 3. Pre-registered statistics and decisions (83 sectors, current prices; 90% bootstrap intervals over sectors)\n")
    out.append("| Hypothesis | Statistic | Estimate | 90% interval | Decision |")
    out.append("|---|---|---|---|---|")
    pt, iv = M["point"], M["interval90"]
    rows = [
        ("Gate", "WAPE(U) - WAPE(Leontief)", "gate_U_minus_leontief", "Leontief beats uniform scaling", "does not beat uniform scaling"),
        ("Gate", "WAPE(U) - WAPE(Ghosh)", "gate_U_minus_ghosh", "Ghosh beats uniform scaling", "does not beat uniform scaling"),
        ("H1", "r, eight transitions", "H1_r", "Leontief more accurate", "Ghosh more accurate"),
        ("H2", "d2 = r(O) - r(P)", "H2_d2", "interval above 0", "interval below 0"),
        ("H2b", "d2* = r(O*) - r(P*)", "H2b_d2star", "interval above 0", "interval below 0"),
        ("H3 Leontief", "ln WAPE_Z(P)/WAPE_Z(O)", "H3_leontief", "less stable in P", "more stable in P"),
        ("H3b Leontief", "ln WAPE_Z(P*)/WAPE_Z(O*)", "H3b_leontief", "less stable in P*", "more stable in P*"),
        ("H3 Ghosh", "ln WAPE_Z(P)/WAPE_Z(O)", "H3_ghosh", "less stable in P", "more stable in P"),
        ("H3b Ghosh", "ln WAPE_Z(P*)/WAPE_Z(O*)", "H3b_ghosh", "less stable in P*", "more stable in P*"),
        ("H4 Leontief", "ln WAPE(DL)/WAPE(Leontief)", "H4_leontief", "structure adds to direct effect", "structure worse than direct effect"),
        ("H4 Ghosh", "ln WAPE(DG)/WAPE(Ghosh)", "H4_ghosh", "structure adds to direct effect", "structure worse than direct effect"),
        ("H5 Leontief", "ln WAPE(T)/WAPE(Leontief), no foresight", "H5_leontief", "better than trend", "worse than trend"),
        ("H5 Ghosh", "ln WAPE(T)/WAPE(Ghosh), no foresight", "H5_ghosh", "better than trend", "worse than trend"),
    ]
    for name, stat, key, pos, neg in rows:
        out.append(f"| {name} | {stat} | {pt[key]:+.3f} | {ci(iv[key])} | {verdict(iv[key], pos, neg)} |")
    rc = M["rank_condition"]
    out.append(f"| H2 rank condition | two lowest r_t are the P transitions | order: {', '.join(rc['order_by_r'])} | - | {'holds' if rc['holds'] else 'does not hold'} |")

    out.append("\n### Table 4. Robustness of H1 and H2 (estimate and 90% interval)\n")
    out.append("| Variant | H1: r | H2: d2 | H2b: d2* | Rank condition |")
    out.append("|---|---|---|---|---|")
    def line(label, v, h1="H1_r", h2="H2_d2", h2b="H2b_d2star", rank=True):
        a, b = v["point"], v["interval90"]
        f = lambda k: f"{a[k]:+.3f} {ci(b[k])}" if k and k in a else "-"
        rk = ("holds" if v["rank_condition"]["holds"] else "does not hold") if rank else "-"
        out.append(f"| {label} | {f(h1)} | {f(h2)} | {f(h2b)} | {rk} |")
    line("Main: 83 sectors, current prices", M)
    line("R1: 165 sectors", R["R1_165_sectors"])
    line("R2: energy sectors excluded from scoring", R["R2_energy_excluded"])
    line("R3: median growth-rate error instead of WAPE", M, "R3_H1_log_ratio_of_medians", "R3_H2_d2_medians", None, False)
    line("R4: 2015 basis only", M, "R4_H1_r_basis2015", None, None, False)
    line("R4: 2020 basis only", M, "R4_H1_r_basis2020", None, None, False)
    line("R5: constant prices of the selling product", R["R5_constant_prices"])
    line("R6: without 2023-24", M, "R6_H1_r", "R6_H2_d2", None, False)

    out.append("\n_R1 reports H2 and H2b beyond the pre-registration, which specified H1 only for that check._\n")
    out.append("\n### Table 4b. H3 (coefficient stability in the shock transitions) in the robustness variants\n")
    out.append("| Variant | Leontief: P vs O | Leontief: P* vs O* | Ghosh: P vs O | Ghosh: P* vs O* |")
    out.append("|---|---|---|---|---|")
    for label, key in (("Main: current prices", "main_83_current_prices"), ("R2: energy sectors excluded", "R2_energy_excluded"),
                       ("R5: constant prices", "R5_constant_prices")):
        a, b = R[key]["point"], R[key]["interval90"]
        cells = [f"{a[k]:+.3f} {ci(b[k])}" for k in ("H3_leontief", "H3b_leontief", "H3_ghosh", "H3b_ghosh")]
        out.append(f"| {label} | " + " | ".join(cells) + " |")
    out.append("\n### Table 5. r by transition in the robustness variants\n")
    out.append("| Transition | Main | R1: 165 sectors | R2: energy excluded | R5: constant prices |")
    out.append("|---|---|---|---|---|")
    for t in ORDER:
        g = lambda k: f"{R[k]['per_transition'][t]['r']:+.3f}"
        out.append(f"| {t} | {g('main_83_current_prices')} | {g('R1_165_sectors')} | {g('R2_energy_excluded')} | {g('R5_constant_prices')} |")

    out.append("\n### Table 6. Hindcast without foresight (T3; 83 sectors, current prices): WAPE of sectoral output, %\n")
    out.append("| Transition | Leontief | Ghosh | Trend (T) | No change (N) |")
    out.append("|---|---|---|---|---|")
    for t in ORDER:
        e = M["per_transition"][t]
        if "t3_wape_x_T" in e:
            out.append(f"| {t} | {pct(e['t3_wape_x_leontief'])} | {pct(e['t3_wape_x_ghosh'])} | {pct(e['t3_wape_x_T'])} | {pct(e['t3_wape_x_N'])} |")

    out.append("\n### Table 7. Secondary measures by transition (83 sectors, current prices)\n")
    out.append("| Transition | Median abs. growth error, Leontief (pp) | Ghosh (pp) | Spearman, Leontief | Spearman, Ghosh | Sectors below 0.05% of output (excluded) |")
    out.append("|---|---|---|---|---|---|")
    for t in ORDER:
        e = M["per_transition"][t]
        out.append(f"| {t} | {e['growth_abs_err_median_leontief']:.2f} | {e['growth_abs_err_median_ghosh']:.2f} | "
                   f"{e['spearman_leontief']:.3f} | {e['spearman_ghosh']:.3f} | {e['n_tiny_excluded']} |")
    sm = M["spearman_median"]
    out.append(f"| Median over transitions | - | - | {sm['leontief']:.3f} | {sm['ghosh']:.3f} | - |")

    out.append("\n### Data notes\n")
    out.append("```json\n" + json.dumps(R["inputs"], ensure_ascii=False, indent=1, sort_keys=True) + "\n```")

    text = "\n".join(out) + "\n"
    d = os.path.dirname(os.path.abspath(argv[2]))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        # [SECURE] Atomic write (Category 3)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, argv[2])
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    print("tables written:", len(out), "lines")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# --------------------------------------------------
# Security Checklist
# Applied:
#   - Input validation: results file must exist; output written atomically (Category 1, 3)
#   - Resource release: files via context managers (Category 5)
# Not Applied:
#   - [WARN] Authentication: not applicable - local formatting script
# --------------------------------------------------
