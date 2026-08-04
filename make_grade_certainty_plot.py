#!/usr/bin/env python3
"""
Generate the GRADE domain-rating and certainty figure from a GRADE evidence profile CSV.

Usage
-----
    python make_grade_certainty_plot.py PROFILE.csv [-o OUT.png] [--labels LABELS.csv]
           [--title TEXT] [--note TEXT] [--dpi 600] [--no-key]

Example
    python3 make_grade_certainty_plot.py \
      /path/to/grade_evidence_profile_integrate.csv \
      --labels /path/to/grade_outcome_short_labels.csv \
      -o grade_certainty_column.png

Input CSV
---------
One row per outcome-level body of evidence. Required columns:

    outcome_id, outcome,
    risk_of_bias, inconsistency, indirectness, imprecision, publication_bias,
    final_certainty

Domain cell values may be:
    not_serious | serious | very_serious | not_estimable | not_assessable | no_evidence

final_certainty is free text (e.g. "Very low", "No evidence"); it is drawn as a pill
whose colour is looked up in CERTAINTY, defaulting to the "Very low" style.

Row order in the CSV is preserved.

Short labels
------------
The key block under the figure uses short outcome labels. These are editorial and are
not part of the evidence profile, so they live in a separate two-column CSV passed with
--labels (columns: outcome_id, short_label). Without --labels the full `outcome` text
from the profile is used instead.
"""
import argparse, csv, sys, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D

INK = "#14375E"          # headings, labels
RULE = "#1A1A1A"         # grid lines

# judgement -> (fill, symbol, symbol colour)
STYLE = {
    "not_serious":    ("#2E9B45", "+",   "white"),
    "serious":        ("#F2695C", "–",   "white"),
    "very_serious":   ("#A5142A", "– –", "white"),
    "not_estimable":  ("#F0BE20", "?",   "#4A3000"),
    "not_assessable": ("#F0BE20", "?",   "#4A3000"),
    "no_evidence":    ("#DCDCDC", "·",   "#8A8A8A"),
    "":               ("#DCDCDC", "·",   "#8A8A8A"),
}
LEGEND_ORDER = [
    ("not_serious",   "Not serious (+)"),
    ("serious",       "Serious (–)"),
    ("very_serious",  "Very serious (– –)"),
    ("not_estimable", "Not estimable (?)"),
    ("no_evidence",   "No evidence (·)"),
]
# final_certainty -> (fill, edge, text colour)
CERTAINTY = {
    "no evidence": ("#E0E0E0", "#9A9A9A", "#3C3C3C"),
    "_default":    ("#F2695C", "#A5142A", "white"),
}
DOMAINS = [("risk_of_bias", "Risk of bias"), ("inconsistency", "Inconsistency"),
           ("indirectness", "Indirectness"), ("imprecision", "Imprecision"),
           ("publication_bias", "Publication\nbias")]

DEFAULT_NOTE = ("Symbols show how seriously each domain was downgraded, "
                "from not serious to very serious.")


REQUIRED = ["outcome_id", "final_certainty"] + [c for c, _ in DOMAINS]


def load_profile(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit("no rows found in " + path)
    cols = rows[0].keys()
    missing = [c for c in REQUIRED if c not in cols]
    if missing:
        # The study-level GRADE export carries the five domain columns but grades
        # nothing, so it would otherwise render a blank-labelled figure in silence.
        if "study_id" in cols or "valid_final_grade_unit" in cols:
            sys.exit(
                f"{path} looks like the STUDY-level GRADE export, not an outcome-level "
                "evidence profile.\nGRADE certainty belongs to a body of evidence "
                "assembled per outcome; the study-level file records only what each "
                "study contributes and grades nothing.\nUse "
                "grade_evidence_profile_integrate.csv instead.\n"
                f"(missing column(s): {', '.join(missing)})")
        sys.exit("missing required column(s): " + ", ".join(missing))
    return rows


def load_labels(path):
    if not path:
        return {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return {r["outcome_id"]: r["short_label"] for r in csv.DictReader(fh)}


def plot(rows, labels, out, dpi=600, title=None, note=None, show_key=True):
    """Layout is specified in inches measured from the top of the canvas, then
    converted to figure fractions, so bands cannot silently overlap."""
    n = len(rows)
    nd = len(DOMAINS)

    # ---- vertical layout, inches from top of canvas
    TITLE_Y   = 0.11
    GRID_TOP  = 0.885
    ROW_H     = 0.276
    grid_bot  = GRID_TOP + ROW_H * n
    LEG_TOP   = grid_bot + 0.25
    LEG_H     = 0.10 + 0.115 * 3            # three legend rows plus padding
    NOTE_Y    = LEG_TOP + LEG_H + 0.13
    KEY_HEAD  = NOTE_Y + 0.31
    KEY_TOP   = KEY_HEAD + 0.13
    KEY_STEP  = 0.122
    fig_h     = (KEY_TOP + KEY_STEP * n + 0.14) if show_key else (NOTE_Y + 0.30)
    fig_w     = 3.4

    def fy(inches_from_top):
        return 1.0 - inches_from_top / fig_h

    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = fig.add_axes([0.135, fy(grid_bot), 0.845, (grid_bot - GRID_TOP) / fig_h])

    x_cert, cert_w = nd + 0.27, 1.58
    ax.set_xlim(-0.12, 6.95)
    ax.set_ylim(0, n)
    ax.axis("off")

    # ---- grid box and rules
    ax.add_patch(Rectangle((0, 0), nd, n, fill=False, ec=RULE, lw=1.0, zorder=3))
    for i in range(1, nd):
        ax.plot([i, i], [0, n], color=RULE, lw=0.6, zorder=3)
    for j in range(1, n):
        ax.plot([0, nd], [j, j], color=RULE, lw=0.6, zorder=3)

    # ---- rotated column headers, drawn above the axes
    for i, (_, lab) in enumerate(DOMAINS):
        ax.text(i + 0.5, n + 0.10, lab, rotation=90, ha="center", va="bottom",
                fontsize=5.8, fontweight="bold", color=INK, linespacing=0.95,
                clip_on=False)
    ax.text(x_cert + cert_w / 2, n + 0.10, "Certainty", rotation=90, ha="center",
            va="bottom", fontsize=5.8, fontweight="bold", color=INK, clip_on=False)

    # ---- rows
    for r, row in enumerate(rows):
        y = n - 1 - r + 0.5
        ax.text(-0.28, y, row.get("outcome_id", ""), ha="right", va="center",
                fontsize=6.5, fontweight="bold", color=INK)
        for i, (col, _) in enumerate(DOMAINS):
            fill, sym, fg = STYLE.get(str(row.get(col, "")).strip().lower(), STYLE[""])
            ax.plot(i + 0.5, y, marker="o", markersize=11.0, markerfacecolor=fill,
                    markeredgecolor=RULE, markeredgewidth=0.6, linestyle="None", zorder=4)
            ax.text(i + 0.5, y, sym, ha="center", va="center", fontsize=4.8,
                    fontweight="bold", color=fg, zorder=5)

        cert = str(row.get("final_certainty", "")).strip()
        cf, ce, ct = CERTAINTY.get(cert.lower(), CERTAINTY["_default"])
        ax.add_patch(FancyBboxPatch((x_cert, y - 0.30), cert_w, 0.60,
                     boxstyle="round,pad=0,rounding_size=0.10",
                     facecolor=cf, edgecolor=ce, lw=0.8, zorder=4,
                     mutation_aspect=0.5))
        ax.text(x_cert + cert_w / 2, y, cert, ha="center", va="center",
                fontsize=5.8, fontweight="bold", color=ct, zorder=5)

    # ---- title
    fig.text(0.5, fy(TITLE_Y), title or "GRADE domain ratings and evidence certainty",
             ha="center", va="top", fontsize=8.2, fontweight="bold", color=INK)

    # ---- legend band
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=STYLE[k][0],
                      markeredgecolor=RULE, markeredgewidth=0.5, markersize=5.0, label=lab)
               for k, lab in LEGEND_ORDER]
    leg = fig.legend(handles=handles, loc="upper center",
                     bbox_to_anchor=(0.5, fy(LEG_TOP)), ncol=2, frameon=True,
                     fontsize=6.0, handletextpad=0.45, columnspacing=1.2,
                     labelspacing=0.38, borderpad=0.6)
    leg.get_frame().set_edgecolor("#C4CCD4")
    leg.get_frame().set_linewidth(0.7)
    for t in leg.get_texts():
        t.set_color(INK)

    # ---- italic note (wrapped so a longer custom note cannot run off the canvas)
    note_txt = "\n".join(textwrap.wrap(note or DEFAULT_NOTE, width=95)) or ""
    fig.text(0.5, fy(NOTE_Y), note_txt, ha="center", va="top",
             fontsize=4.9, style="italic", color="#44506A", linespacing=1.35)

    # ---- outcome key
    if show_key:
        fig.text(0.055, fy(KEY_HEAD), "Bodies of evidence", ha="left", va="top",
                 fontsize=6.5, fontweight="bold", color=INK)
        for i, row in enumerate(rows):
            oid = row.get("outcome_id", "")
            lab = labels.get(oid) or row.get("outcome", "")
            yy = fy(KEY_TOP + i * KEY_STEP)
            fig.text(0.055, yy, oid, ha="left", va="top", fontsize=5.8,
                     fontweight="bold", color=INK)
            fig.text(0.155, yy, lab, ha="left", va="top", fontsize=5.8, color="#33415C")

    fig.savefig(out, dpi=dpi, facecolor="white")
    if str(out).lower().endswith(".png"):
        fig.savefig(str(out)[:-4] + ".pdf", facecolor="white")
    print(f"wrote {out}  ({n} bodies of evidence)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_in")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--labels", default=None, help="CSV with columns outcome_id, short_label")
    ap.add_argument("--title", default=None)
    ap.add_argument("--note", default=None)
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--no-key", action="store_true", help="omit the bodies-of-evidence key block")
    a = ap.parse_args()

    rows = load_profile(a.csv_in)
    labels = load_labels(a.labels)
    out = a.out or (a.csv_in.rsplit(".", 1)[0] + "_certainty.png")
    plot(rows, labels, out, a.dpi, a.title, a.note, show_key=not a.no_key)


if __name__ == "__main__":
    main()
