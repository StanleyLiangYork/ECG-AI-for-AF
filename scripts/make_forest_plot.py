#!/usr/bin/env python3
"""
Generate the two-panel point-estimate figure for the AF semantic-AI review.

Panel A  paired sensitivity and specificity at patient or case level
Panel B  model discrimination (AUROC / C-statistic)

Nothing is pooled. The panels display point estimates side by side for
comparison only, because the targets, index tests, units of analysis and
underlying datasets differ and several datasets overlap.

Usage
-----
    python scripts/make_forest_plot.py --accuracy TABLE1.csv --auroc TABLE2.csv
           [-o OUT.png] [--dpi 300]

Example
    python3 scripts/make_forest_plot.py \
      --accuracy data/table1_diagnostic_accuracy.csv \
      --auroc data/table2_auroc_discrimination.csv \
      -o figures/forest_point_estimates.png

Input columns
-------------
accuracy CSV : study, index_test, target_condition, n_positive, n_negative,
               sensitivity, sens_95CI_low, sens_95CI_high,
               specificity, spec_95CI_low, spec_95CI_high
auroc CSV    : study, model, target_condition, metric, value, ci_low, ci_high,
               dispersion, n, notes

A row in the AUROC table whose `metric` is not a plain AUROC (for example
macro-AUROC averaged over several rhythm labels) is drawn in grey and flagged
in its label, because it does not estimate AF-specific discrimination and is
not comparable with the other points.
"""
import argparse, csv, re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

INK, MUTED = "#14375E", "#5A6B82"
SENS_C, SPEC_C, AUROC_C, NONCOMP_C = "#1F5F8B", "#C1521E", "#5E8C31", "#8A8A8A"


def num(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def is_af_specific(metric):
    m = str(metric).strip().lower()
    return "macro" not in m


def load_accuracy(path):
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            npos, nneg = num(re.sub(r"[^\d.]", "", r.get("n_positive", "") or "")), \
                         num(re.sub(r"[^\d.]", "", r.get("n_negative", "") or ""))
            n = int(npos + nneg) if npos and nneg else None
            out.append(dict(
                study=r["study"], test=r.get("index_test", ""),
                target=r.get("target_condition", ""), n=n,
                sens=num(r.get("sensitivity")), sl=num(r.get("sens_95CI_low")),
                sh=num(r.get("sens_95CI_high")),
                spec=num(r.get("specificity")), pl=num(r.get("spec_95CI_low")),
                ph=num(r.get("spec_95CI_high"))))
    return out


def load_auroc(path):
    out = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            out.append(dict(
                study=r["study"], model=r.get("model", ""), metric=r.get("metric", "AUROC"),
                target=r.get("target_condition", ""), value=num(r.get("value")),
                lo=num(r.get("ci_low")), hi=num(r.get("ci_high")),
                disp=(r.get("dispersion") or "").strip(), n=(r.get("n") or "").strip(),
                af=is_af_specific(r.get("metric", ""))))
    return out


def short(txt, limit=38):
    txt = re.sub(r"\s+", " ", str(txt)).strip()
    return txt if len(txt) <= limit else txt[:limit - 1].rstrip() + "…"


def plot(acc, aur, out, dpi=300):
    """Vertical layout is specified in inches from the top of the canvas and then
    converted to figure fractions, so the two panels cannot collide."""
    na, nb = len(acc), len(aur)
    FIG_W = 10.4
    L, W = 0.340, 0.635                     # axes left / width as figure fractions

    A_TOP, A_ROW = 1.30, 0.86
    A_BOT = A_TOP + A_ROW * na
    B_TITLE = A_BOT + 0.92                  # room for panel A x-label
    B_TOP = B_TITLE + 0.30
    B_ROW = 0.74
    B_BOT = B_TOP + B_ROW * nb
    FIG_H = B_BOT + 0.78

    def fy(inches): return 1.0 - inches / FIG_H

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax_a = fig.add_axes([L, fy(A_BOT), W, (A_BOT - A_TOP) / FIG_H])
    ax_b = fig.add_axes([L, fy(B_BOT), W, (B_BOT - B_TOP) / FIG_H])

    fig.text(0.5, fy(0.30), "Point estimates with 95% CIs for AF-related outcomes "
             "in the 15 included studies", ha="center", va="top",
             fontsize=14.5, fontweight="bold", color=INK)
    fig.text(0.5, fy(0.62), "Displayed for comparison only. Not pooled, because targets, "
             "index tests, units of analysis and datasets differ and overlap.",
             ha="center", va="top", fontsize=10.5, style="italic", color=MUTED)

    # ---------------------------------------------------------------- panel A
    fig.text(L + W / 2, fy(A_TOP - 0.22), "A. AF detection — sensitivity and specificity "
             "(patient/case level)", ha="center", va="bottom",
             fontsize=12.5, fontweight="bold", color=INK)
    for i, r in enumerate(acc):
        y = na - 1 - i
        for val, lo, hi, colour, mk, dy in (
                (r["sens"], r["sl"], r["sh"], SENS_C, "o", 0.17),
                (r["spec"], r["pl"], r["ph"], SPEC_C, "s", -0.17)):
            if val is None:
                continue
            if lo is not None and hi is not None:
                ax_a.plot([lo, hi], [y + dy] * 2, color=colour, lw=2.2,
                          solid_capstyle="round", zorder=2)
            else:
                ax_a.text(val + 0.016, y + dy, "no CI", va="center",
                          fontsize=8.5, color=MUTED)
            ax_a.plot(val, y + dy, marker=mk, markersize=9, color=colour, zorder=3)
        lab = f"{r['study']} — {short(r['test'], 22)}\n{short(r['target'], 26)}"
        if r["n"]:
            lab += f", n={r['n']:,}"
        ax_a.text(-0.02, y, lab, transform=ax_a.get_yaxis_transform(), ha="right",
                  va="center", fontsize=9.5, color=INK, linespacing=1.35, clip_on=False)
    ax_a.axvline(0.5, color="#D8DEE5", ls=":", lw=1.2, zorder=1)
    ax_a.set_xlim(0, 1.05)
    ax_a.set_ylim(-0.6, na - 0.4)
    ax_a.set_yticks([])
    ax_a.set_xlabel("Proportion (sensitivity / specificity)", fontsize=10.5, color=INK)
    for sp in ("top", "right", "left"):
        ax_a.spines[sp].set_visible(False)
    ax_a.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=SENS_C,
                                markersize=9, label="Sensitivity"),
                         Line2D([0], [0], marker="s", color="w", markerfacecolor=SPEC_C,
                                markersize=9, label="Specificity")],
                loc="lower left", fontsize=10, frameon=False)

    # ---------------------------------------------------------------- panel B
    fig.text(L + W / 2, fy(B_TITLE), "B. Model discrimination — AUROC "
             "(different targets; not pooled)", ha="center", va="bottom",
             fontsize=12.5, fontweight="bold", color=INK)
    for i, r in enumerate(aur):
        y = nb - 1 - i
        colour = AUROC_C if r["af"] else NONCOMP_C
        if r["lo"] is not None and r["hi"] is not None:
            ax_b.plot([r["lo"], r["hi"]], [y] * 2, color=colour, lw=2.2,
                      solid_capstyle="round", zorder=2)
            tag = r["disp"] if r["disp"] and "CI" not in r["disp"] else "95% CI"
        else:
            tag = f"{r['value']:.3g} (CI NR)"
        ax_b.plot(r["value"], y, marker="D", markersize=9, color=colour, zorder=3)
        ax_b.text(min(r["value"] + 0.005, 1.0), y + 0.19, tag, fontsize=8.5,
                  color=MUTED, va="bottom")
        lab = f"{r['study']} — {short(r['model'], 22)}\n{short(r['target'], 26)}"
        if r["n"]:
            lab += f", n={short(r['n'], 12)}"
        if not r["af"]:
            lab += "\n(not AF-specific)"
        ax_b.text(-0.02, y, lab, transform=ax_b.get_yaxis_transform(), ha="right",
                  va="center", fontsize=9.5, color=INK if r["af"] else NONCOMP_C,
                  linespacing=1.35, clip_on=False)
    lo_x = min(0.60, min(r["value"] for r in aur) - 0.04)
    ax_b.set_xlim(lo_x, 1.015)
    ax_b.set_ylim(-0.6, nb - 0.4)
    ax_b.set_yticks([])
    ax_b.set_xlabel("AUROC / C-statistic", fontsize=10.5, color=INK)
    ax_b.grid(axis="x", color="#E6EBF0", lw=0.9)
    ax_b.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax_b.spines[sp].set_visible(False)
    if any(not r["af"] for r in aur):
        fig.text(L + W / 2, fy(FIG_H - 0.20), "Grey diamond: metric is not AF-specific and is "
                 "not comparable with the other points.", ha="center", va="bottom",
                 fontsize=9.5, style="italic", color=NONCOMP_C)

    fig.savefig(out, dpi=dpi, facecolor="white")
    if str(out).lower().endswith(".png"):
        fig.savefig(str(out)[:-4] + ".pdf", facecolor="white")
    print(f"wrote {out}  (panel A {na} rows, panel B {nb} rows)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--accuracy", required=True)
    ap.add_argument("--auroc", required=True)
    ap.add_argument("-o", "--out", default="forest_point_estimates.png")
    ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args()
    acc, aur = load_accuracy(a.accuracy), load_auroc(a.auroc)
    if not acc or not aur:
        sys.exit("no rows loaded")
    plot(acc, aur, a.out, a.dpi)


if __name__ == "__main__":
    main()
