#!/usr/bin/env python3
"""
Generate the AI- and knowledge-graph-specific reporting-practice matrix.

Each cell classifies what a study disclosed about one reporting practice. The
matrix is descriptive: no cell feeds a QUADAS-3, PROBAST+AI or GRADE judgment.

Usage
-----
    python make_reporting_matrix.py INPUT.csv [-o OUT.png] [--title TEXT]
           [--note TEXT] [--dpi 300]

Example
    python3 make_reporting_matrix.py ai_kg_reporting_matrix_data.csv \
      -o ai_kg_reporting_matrix.png

Input CSV
---------
One row per study. The first column holds the study label; every remaining
column is a reporting practice and becomes a column of the matrix. Row and
column order in the CSV is preserved.

Cell values are mapped to one of four classes by VALUE_CLASS below:

    adequate        reported in full            green, check mark
    partial         reported in part, or only implied   amber, tilde
    absent          not reported                red, cross
    n/a             practice does not apply     grey, dash

An unrecognised value is drawn as "absent" and reported on stderr, so a new
vocabulary term cannot pass unnoticed.
"""
import argparse, csv, sys, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

INK = "#14375E"

CLASS = {                       # class -> (fill, glyph, glyph colour)
    "adequate": ("#1FA14A", "✓", "white"),
    "partial":  ("#EFA31D", "∼", "white"),
    "absent":   ("#E0322B", "✗", "white"),
    "n/a":      ("#DCDCDC", "–", "#6E6E6E"),
}
LEGEND = [("adequate", "Reported / adequate"), ("partial", "Partial or indirect"),
          ("absent", "Not reported"), ("n/a", "Not applicable")]

VALUE_CLASS = {
    # patient / institution-level train-test separation
    "explicit": "adequate",
    "implied by external dataset only": "partial",
    "not reported": "absent",
    # temporal leakage safeguard
    "prospective enrolment": "adequate",
    "external dataset; temporal separation not stated": "partial",
    "cross-validation only": "absent",
    "internal hold-out only": "absent",
    "none": "absent",
    # transductive KG construction
    "n/a (no kg)": "n/a",
    "not addressed": "absent",
    # LLM version / prompt / temperature
    "version, prompt, temperature": "adequate",
    "version, prompt": "partial",
    "version": "partial",
    "n/a (no llm)": "n/a",
    # reproducibility artefacts
    "code, weights": "adequate",
    "code": "partial",
}

SHORT = {
    "Patient/institution-level train-test separation": "Train-test\nseparation",
    "Temporal leakage safeguard": "Temporal-leakage\nsafeguard",
    "Transductive KG construction": "Transductive\nKG build",
    "LLM version / prompt / temperature reported": "LLM version,\nprompt, temp.",
    "Reproducibility artefacts": "Reproducibility\nartefacts",
}
DEFAULT_NOTE = "Descriptive only; no cell contributes to a GRADE downgrading decision."


def classify(value):
    v = str(value).strip().lower()
    if v in VALUE_CLASS:
        return VALUE_CLASS[v]
    print(f"warning: unrecognised cell value {value!r}; drawn as 'not reported'",
          file=sys.stderr)
    return "absent"


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit("no rows found in " + path)
    cols = list(rows[0].keys())
    return rows, cols[0], cols[1:]


def header(col):
    return SHORT.get(col) or "\n".join(textwrap.wrap(col, 16))


def plot(rows, key, practices, out, dpi=300, title=None, note=None):
    nr, nc = len(rows), len(practices)
    fig_w = 3.5 + 1.55 * nc
    fig_h = 2.55 + 0.42 * nr
    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0.255, 0.145, 0.725, 0.72])
    ax.set_xlim(0, nc)
    ax.set_ylim(0, nr)
    ax.invert_yaxis()
    ax.axis("off")

    for r, row in enumerate(rows):
        ax.text(-0.06, r + 0.5, row[key], ha="right", va="center",
                fontsize=12, color=INK, transform=ax.get_yaxis_transform(),
                clip_on=False)
        for c, col in enumerate(practices):
            cls = classify(row.get(col, ""))
            fill, glyph, fg = CLASS[cls]
            ax.add_patch(Rectangle((c + 0.012, r + 0.06), 0.976, 0.88,
                                   facecolor=fill, edgecolor="white", lw=1.4))
            ax.text(c + 0.5, r + 0.5, glyph, ha="center", va="center",
                    fontsize=13, fontweight="bold", color=fg)

    for c, col in enumerate(practices):
        ax.text(c + 0.5, -0.12, header(col), ha="center", va="bottom",
                fontsize=11.5, fontweight="bold", color=INK, linespacing=1.15)

    fig.suptitle(title or "AI- and knowledge-graph-specific reporting practices",
                 fontsize=16, fontweight="bold", color=INK, y=0.978)
    fig.text(0.5, 0.098, note or DEFAULT_NOTE, ha="center", va="top",
             fontsize=11, style="italic", color="#5A6B82")

    handles = [Line2D([0], [0], marker="s", color="w", markerfacecolor=CLASS[k][0],
                      markeredgecolor="white", markersize=15, label=lab)
               for k, lab in LEGEND]
    leg = fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.008),
                     ncol=4, frameon=True, fontsize=11.5, handletextpad=0.6,
                     columnspacing=2.0, borderpad=0.7)
    leg.get_frame().set_edgecolor("#C4CCD4")
    for t in leg.get_texts():
        t.set_color(INK)

    fig.savefig(out, dpi=dpi, facecolor="white")
    if str(out).lower().endswith(".png"):
        fig.savefig(str(out)[:-4] + ".pdf", facecolor="white")
    print(f"wrote {out}  ({nr} studies x {nc} practices)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_in")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--note", default=None)
    ap.add_argument("--dpi", type=int, default=300)
    a = ap.parse_args()
    rows, key, practices = load(a.csv_in)
    plot(rows, key, practices, a.out or (a.csv_in.rsplit(".", 1)[0] + ".png"),
         a.dpi, a.title, a.note)


if __name__ == "__main__":
    main()
