#!/usr/bin/env python3
"""
Generate the paradigm x clinical-task matrix of included studies from a CSV.

Usage
-----
    python make_paradigm_matrix.py INPUT.csv [-o OUT.png] [--title TEXT] [--dpi 600]

Example
    python3 make_paradigm_matrix.py paradigm_task_matrix_data.csv \
      -o paradigm_task_matrix.png

Input CSV
---------
One row per study. Required columns:

    study_label, paradigm, task, unit, external_validation

`paradigm` and `task` give the row and column. Rows and columns appear in the
order defined by PARADIGMS and TASKS below; any value not listed there is
appended after them, so the figure never silently drops a study.

`unit` may be patient, record, segment, or none. "none" marks a study with no
AF-specific estimate and is drawn grey. `external_validation` is yes or no; yes
adds a star marker denoting external or cross-dataset validation.
"""
import argparse, csv, sys, textwrap
from collections import OrderedDict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

INK = "#14375E"

PARADIGMS = ["General-purpose multimodal LLM", "ECG-as-language / foundation model",
             "Clinical-text NLP / phenotyping", "Knowledge-based reasoning / KG",
             "Integrated KG + LLM"]
TASKS = ["Direct detection", "Rhythm classification", "Phenotyping",
         "Incident risk", "Decision support"]
TASK_SHORT = {"Rhythm classification": "Rhythm\nclassif.", "Direct detection": "Direct\ndetection",
              "Phenotyping": "Pheno-\ntyping", "Incident risk": "Incident\nrisk",
              "Decision support": "Decision\nsupport"}

UNIT = OrderedDict([
    ("patient", ("#1F6FA8", "Patient/case-level")),
    ("record",  ("#D2691E", "ECG record-level")),
    ("segment", ("#E0B024", "Segment/beat-level")),
    ("none",    ("#808080", "No AF-specific est.")),
])


def wrap_paradigm(p, width=19):
    """Wrap to a fixed character width so no row label overruns the left margin."""
    return "\n".join(textwrap.wrap(p, width=width)) or p


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit("no rows found in " + path)
    for c in ("study_label", "paradigm", "task", "unit", "external_validation"):
        if c not in rows[0]:
            sys.exit("missing required column: " + c)
    return rows


def plot(rows, out, dpi=300, title=None):
    paradigms = PARADIGMS + [p for p in dict.fromkeys(r["paradigm"] for r in rows)
                             if p not in PARADIGMS]
    tasks = TASKS + [t for t in dict.fromkeys(r["task"] for r in rows) if t not in TASKS]
    nr, nc = len(paradigms), len(tasks)

    cell = {}
    for r in rows:
        cell.setdefault((r["paradigm"], r["task"]), []).append(r)

    fig_w = 2.1 + 1.15 * nc
    fig_h = 2.6 + 1.05 * nr
    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0.30, 0.180, 0.68, 0.675])
    ax.set_xlim(-0.5, nc - 0.5)
    ax.set_ylim(-0.5, nr - 0.5)
    ax.invert_yaxis()
    ax.axis("off")

    for i in range(nr):
        for j in range(nc):
            ax.add_patch(FancyBboxPatch((j - 0.44, i - 0.40), 0.88, 0.80,
                         boxstyle="round,pad=0,rounding_size=0.06",
                         facecolor="#F7F9FB", edgecolor="#C9D2DA", lw=1.0, zorder=1))

    for j, t in enumerate(tasks):
        ax.text(j, -0.60, TASK_SHORT.get(t, t.replace(" ", "\n")), ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=INK, linespacing=1.15)
    for i, p in enumerate(paradigms):
        ax.text(-0.62, i, wrap_paradigm(p), ha="right", va="center",
                fontsize=11, fontweight="bold", color=INK, linespacing=1.2)

    for (p, t), studies in cell.items():
        i, j = paradigms.index(p), tasks.index(t)
        k = len(studies)
        span = 0.42
        xs = [j] if k == 1 else [j - span/2 + span * m / (k - 1) for m in range(k)]
        for x, st in zip(xs, studies):
            colour = UNIT.get(st["unit"].strip().lower(), UNIT["none"])[0]
            ext = st["external_validation"].strip().lower() == "yes"
            if ext:
                ax.plot(x, i, marker="o", markersize=20, markerfacecolor=colour,
                        markeredgecolor="#12283C", markeredgewidth=3.2,
                        linestyle="None", zorder=3)
                ax.plot(x, i, marker="*", markersize=9, markerfacecolor="white",
                        markeredgecolor="white", linestyle="None", zorder=4)
            else:
                ax.plot(x, i, marker="o", markersize=20, markerfacecolor=colour,
                        markeredgecolor=colour, markeredgewidth=1.0,
                        linestyle="None", zorder=3)

    fig.suptitle(title or "Included studies by paradigm and clinical task",
                 fontsize=17, fontweight="bold", color=INK, y=0.975)

    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                      markeredgecolor=c, markersize=11, label=lab)
               for c, lab in UNIT.values()]
    leg = fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.055),
                     ncol=2, frameon=True, fontsize=11.5, handletextpad=0.6,
                     columnspacing=2.0, labelspacing=0.5, borderpad=0.8)
    leg.get_frame().set_edgecolor("#C4CCD4")
    for tx in leg.get_texts():
        tx.set_color(INK)

    fig.text(0.5, 0.028, "One marker per study;  ★ = external / cross-dataset validation",
             ha="center", va="bottom", fontsize=11, style="italic", color="#44506A")

    fig.savefig(out, dpi=dpi, facecolor="white")
    if str(out).lower().endswith(".png"):
        fig.savefig(str(out)[:-4] + ".pdf", facecolor="white")
    print(f"wrote {out}  ({len(rows)} studies, {nr} paradigms x {nc} tasks)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_in")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args()
    rows = load(a.csv_in)
    plot(rows, a.out or (a.csv_in.rsplit(".", 1)[0] + ".png"), a.dpi, a.title)


if __name__ == "__main__":
    main()
