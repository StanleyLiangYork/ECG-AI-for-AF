#!/usr/bin/env python3
"""
Generate a QUADAS-3 (or PROBAST+AI) risk-of-bias traffic-light plot from a CSV.

Usage
-----
    python scripts/make_traffic_light_plot.py INPUT.csv [-o OUTPUT.png] [--tool quadas3|probast]
           [--title TEXT] [--subtitle TEXT] [--dpi 300]
-----
Example
python3 scripts/make_traffic_light_plot.py \
  data/quadas3_traffic_light_plot_data_integrate.csv \
  --tool quadas3 \
  -o figures/quadas3_traffic_light_plot.png

python3 scripts/make_traffic_light_plot.py \
  data/probast_ai_traffic_light_plot_data_integrate.csv \
  --tool probast \
  -o figures/probast_ai_traffic_light_plot.png
  


Input CSV
---------
One row per estimate (QUADAS-3) or per model (PROBAST+AI). Required columns:

  QUADAS-3   study_label,
             participants_risk_of_bias, index_test_risk_of_bias,
             target_condition_risk_of_bias, analysis_risk_of_bias,
             overall_risk_of_bias,
             participants_applicability, index_test_applicability,
             target_condition_applicability, overall_applicability

  PROBAST+AI study_label,
             development_participants_quality, development_predictors_quality,
             development_outcome_quality, development_analysis_quality,
             development_overall_quality,
             development_participants_applicability, development_predictors_applicability,
             development_outcome_applicability, development_overall_applicability
             (and the matching evaluation_* columns; each model yields two rows)

Cell values may be: low | high | insufficient_information | unclear | not_applicable
Row order in the CSV is preserved in the plot.
"""
import argparse, csv, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ---------------------------------------------------------------- judgement styling
STYLE = {
    "low":                      ("#2E9B45", "+",  "white"),
    "high":                     ("#D62F2F", "✕", "white"),
    "insufficient_information": ("#F0C020", "?",  "#4A3000"),
    "unclear":                  ("#F0C020", "?",  "#4A3000"),
    "not_applicable":           ("#DCDCDC", "–", "#666666"),
    "":                         ("#DCDCDC", "–", "#666666"),
}
LEGEND = {
    "quadas3": [("low", "Low risk / concern  (+)"),
                ("high", "High risk / concern  (✕)"),
                ("insufficient_information", "Insufficient information  (?)")],
    "probast": [("low", "Low risk / concern  (+)"),
                ("high", "High risk / concern  (✕)"),
                ("unclear", "Unclear  (?)")],
}

SPECS = {
    "quadas3": dict(
        rob=[("participants_risk_of_bias", "D1"), ("index_test_risk_of_bias", "D2"),
             ("target_condition_risk_of_bias", "D3"), ("analysis_risk_of_bias", "D4"),
             ("overall_risk_of_bias", "Overall")],
        app=[("participants_applicability", "A1"), ("index_test_applicability", "A2"),
             ("target_condition_applicability", "A3"), ("overall_applicability", "Overall")],
        title="QUADAS-3 Risk of Bias and Applicability Summary",
        subtitle="Diagnostic test-accuracy studies",
        footer=("Domains —   D1/A1: Patient Selection      D2/A2: Index Test      "
                "D3/A3: Reference Standard (Target Condition)      D4: Analysis"),
    ),
    "probast": dict(
        rob=[("participants", "D1"), ("predictors", "D2"), ("outcome", "D3"),
             ("analysis", "D4"), ("overall", "Overall")],
        app=[("participants", "A1"), ("predictors", "A2"), ("outcome", "A3"), ("overall", "Overall")],
        title="PROBAST+AI Risk of Bias and Applicability Summary",
        subtitle="Prognostic prediction-model studies",
        footer=("Domains —   D1/A1: Participants and data sources      D2/A2: Predictors      "
                "D3/A3: Outcome      D4: Analysis"),
    ),
}


def load_quadas(path):
    rows, spec = [], SPECS["quadas3"]
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            rows.append((r.get("study_label") or r.get("study_id", ""),
                         [r.get(k, "") for k, _ in spec["rob"]],
                         [r.get(k, "") for k, _ in spec["app"]]))
    return rows


def load_probast(path):
    """Each model contributes a development row and an evaluation row."""
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            label = r.get("study_label") or r.get("study_id", "")
            for track, suffix_rob, suffix_app, tag in (
                ("development", "_quality", "_applicability", "development"),
                ("evaluation", "_risk_of_bias", "_applicability", "evaluation"),
            ):
                rob = [r.get(f"{track}_{d}{'_overall_quality' if False else ''}", "") for d, _ in []]
                rob = [r.get(f"{track}_{d}{suffix_rob}" if d != "overall"
                             else f"{track}_overall{suffix_rob}", "") for d, _ in SPECS["probast"]["rob"]]
                app = [r.get(f"{track}_{d}{suffix_app}" if d != "overall"
                             else f"{track}_overall{suffix_app}", "") for d, _ in SPECS["probast"]["app"]]
                rows.append((f"{label} ({tag})", rob, app))
    return rows


def plot(rows, spec, legend_key, out, dpi=300, title=None, subtitle=None):
    n = len(rows)
    n_rob, n_app = len(spec["rob"]), len(spec["app"])
    DX, GAP, PAD = 1.0, 1.25, 0.30           # pitch, block gap, extra pad before "Overall"
    x_rob = [i * DX + (PAD if i == n_rob - 1 else 0) for i in range(n_rob)]
    x_app = [x_rob[-1] + GAP + i * DX + (PAD if i == n_app - 1 else 0) for i in range(n_app)]

    fig_w = 2.9 + 0.62 * (n_rob + n_app)
    fig_h = 3.4 + 0.46 * n
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    for r, (label, rob, app) in enumerate(rows):
        y = n - 1 - r
        ax.text(-0.85, y, label, ha="right", va="center", fontsize=13)
        for x, v in list(zip(x_rob, rob)) + list(zip(x_app, app)):
            col, sym, fg = STYLE.get(str(v).strip().lower(), STYLE[""])
            ax.plot(x, y, marker="o", markersize=26, markerfacecolor=col,
                    markeredgecolor="black", markeredgewidth=1.3, linestyle="None", zorder=2)
            ax.text(x, y, sym, ha="center", va="center", fontsize=13,
                    fontweight="bold", color=fg, zorder=3)

    for x, (_, lab) in zip(x_rob, spec["rob"]):
        ax.text(x, n - 0.35, lab, ha="center", va="bottom", fontsize=13, fontweight="bold")
    for x, (_, lab) in zip(x_app, spec["app"]):
        ax.text(x, n - 0.35, lab, ha="center", va="bottom", fontsize=13, fontweight="bold")

    mid_r = (x_rob[0] + x_rob[-1]) / 2
    mid_a = (x_app[0] + x_app[-1]) / 2
    ax.text(mid_r, n + 0.35, "RISK OF BIAS", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color="#333333")
    ax.text(mid_a, n + 0.35, "APPLICABILITY", ha="center", va="bottom",
            fontsize=15, fontweight="bold", color="#333333")

    xsep = (x_rob[-1] + x_app[0]) / 2
    ax.plot([xsep, xsep], [-0.6, n + 0.2], color="#BBBBBB", lw=1.2, ls=(0, (4, 4)), zorder=1)

    ax.set_xlim(-6.2, x_app[-1] + 0.7)
    ax.set_ylim(-1.5, n + 1.5)
    ax.axis("off")

    fig.suptitle(title or spec["title"], fontsize=22, fontweight="bold", y=0.985)
    ax.text((x_rob[0] + x_app[-1]) / 2 - 2.6, n + 1.15, subtitle or spec["subtitle"],
            ha="center", va="bottom", fontsize=15, style="italic")
    ax.text(-6.0, -1.05, spec["footer"], ha="left", va="center", fontsize=12.5, color="#222222")

    handles = [Line2D([0], [0], marker="s", color="w",
                      markerfacecolor=STYLE[k][0], markeredgecolor="black",
                      markersize=17, label=lab) for k, lab in LEGEND[legend_key]]
    leg = fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.005),
                     ncol=len(handles), frameon=True, fontsize=14, title="Judgement",
                     title_fontsize=15, handletextpad=0.6, columnspacing=2.2, borderpad=0.9)
    leg.get_frame().set_edgecolor("#BBBBBB")

    plt.subplots_adjust(left=0.02, right=0.99, top=0.88, bottom=0.16)
    fig.savefig(out, dpi=dpi, facecolor="white", bbox_inches="tight")
    if str(out).lower().endswith(".png"):
        fig.savefig(str(out)[:-4] + ".pdf", facecolor="white", bbox_inches="tight")
    print(f"wrote {out}  ({n} rows)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_in")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--tool", choices=["quadas3", "probast"], default="quadas3")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args()

    rows = load_quadas(a.csv_in) if a.tool == "quadas3" else load_probast(a.csv_in)
    if not rows:
        sys.exit("no rows found in " + a.csv_in)
    out = a.out or (a.csv_in.rsplit(".", 1)[0] + "_plot.png")
    plot(rows, SPECS[a.tool], a.tool, out, a.dpi, a.title, a.subtitle)


if __name__ == "__main__":
    main()
