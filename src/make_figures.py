"""Make the PNG charts used in the README and the executive deck.

Usage:  python src/make_figures.py   (after build_db, ws1_diagnose, ws3_model, ws4_build_excel)
Output: reports/figures/*.png
"""
import os

import matplotlib
import pandas as pd
from openpyxl import load_workbook

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "reports", "figures")
BLUE, GREY, RED = "#2a78d6", "#c3c2b7", "#e34948"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e0"
BLUES = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})


def frame(title, subtitle, size=(9, 5)):
    fig, ax = plt.subplots(figsize=size)
    fig.text(0.02, 0.96, title, fontsize=15, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.89, subtitle, fontsize=10.5, color=INK2, va="top")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    return fig, ax


def save(fig, name, source, left=0.09):
    fig.text(0.02, 0.015, f"Source: {source}", fontsize=8.5, color=INK2)
    fig.subplots_adjust(top=0.80, bottom=0.14, left=left, right=0.97)
    fig.savefig(os.path.join(OUT, name), dpi=160)
    plt.close(fig)
    print("wrote", name)


def fig_score_by_delay():
    t = pd.read_csv(f"{P}/ws1/score_by_late_band.csv")
    fig, ax = frame("One to three days late already costs a full star",
                    "Average review score by days late, delivered orders Jan 2017 – Aug 2018")
    colors = [GREY] + BLUES[1:4]
    bars = ax.bar(t.late_band, t.avg_score, color=colors, width=0.6)
    for b, v, n in zip(bars, t.avg_score, t.orders):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", color=INK, fontweight="bold")
        ax.text(b.get_x() + b.get_width() / 2, 0.15, f"{n:,} orders", ha="center", color=INK if n == t.orders.iat[0] else "white", fontsize=9)
    ax.set_ylim(0, 5)
    ax.set_ylabel("Average review score (1–5)")
    save(fig, "fig1_score_by_delay.png", "Olist dataset; src/ws1_diagnose.py")


def fig_stage_days():
    t = pd.read_csv(f"{P}/ws1/stage_durations.csv", index_col=0)
    stages = {"approval_days": "Payment approval", "handling_days": "Seller handling", "transit_days": "Carrier transit"}
    t = t.loc[list(stages)].rename(index=stages)
    fig, ax = frame("Late orders lose 20 extra days in carrier transit",
                    "Average days per stage, on-time vs late orders")
    y = range(len(t))
    ax.barh([i + 0.2 for i in y], t["on time"], height=0.38, color=GREY, label="On time")
    ax.barh([i - 0.2 for i in y], t["late"], height=0.38, color=BLUE, label="Late")
    for i, (a, b) in enumerate(zip(t["on time"], t["late"])):
        ax.text(a + 0.3, i + 0.2, f"{a:.1f}", va="center", color=INK2)
        ax.text(b + 0.3, i - 0.2, f"{b:.1f}", va="center", color=INK, fontweight="bold")
    ax.set_yticks(list(y)); ax.set_yticklabels(t.index); ax.invert_yaxis()
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID)
    ax.set_xlabel("Days")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "fig2_stage_days.png", "Olist dataset; src/ws1_diagnose.py", left=0.19)


def fig_states():
    t = pd.read_csv(f"{P}/ws1/states.csv")
    r = t.late_rate.corr(t.avg_eta_buffer)
    fig, ax = frame(f"Less slack in the promise, more missed promises (r = {r:.2f})",
                    "Customer states with 100+ orders: average ETA buffer vs late delivery rate; bubble = orders")
    ax.scatter(t.avg_eta_buffer, t.late_rate * 100, s=t.orders / 40 + 20, color=BLUE, alpha=0.75,
               edgecolor=SURF, linewidth=2)
    for _, row in t.iterrows():
        if row.customer_state in ("AL", "MA", "SP", "RJ", "AM", "RO", "PR"):
            ax.annotate(row.customer_state, (row.avg_eta_buffer, row.late_rate * 100), xytext=(7, 4),
                        textcoords="offset points", color=INK, fontsize=10, fontweight="bold")
    ax.set_xlabel("Average ETA buffer (days the promise exceeds actual delivery)")
    ax.set_ylabel("Late delivery rate (%)")
    ax.grid(axis="x", color=GRID)
    save(fig, "fig3_states_buffer.png", "Olist dataset; src/ws1_diagnose.py")


def fig_monthly():
    t = pd.read_csv(f"{P}/ws1/monthly.csv")
    fig, ax = frame("Late deliveries spike in peak months",
                    "Late delivery rate by purchase month")
    ax.plot(t.purchase_month, t.late_rate * 100, color=BLUE, linewidth=2, marker="o", markersize=4)
    for m in ("2017-11", "2018-03"):
        v = t.loc[t.purchase_month == m, "late_rate"].iat[0] * 100
        ax.annotate(f"{m}: {v:.1f}%", (m, v), xytext=(0, 9), textcoords="offset points", ha="center",
                    color=INK, fontweight="bold")
    ax.set_xticks(range(0, len(t), 3)); ax.set_xticklabels(t.purchase_month[::3])
    ax.set_ylim(0, 22); ax.set_ylabel("Late delivery rate (%)")
    save(fig, "fig4_monthly_late.png", "Olist dataset; src/ws1_diagnose.py")


def fig_model():
    t = pd.read_csv(f"{P}/ws3/metrics.csv")
    fig, ax = frame("The model finds 1.7× more late orders than the seller rule",
                    "Share of all late orders found in the riskiest 10%, test months Apr – Aug 2018")
    colors = [BLUE if m == "Logistic regression" else GREY for m in t.model]
    bars = ax.bar(t.model, t.recall_top10 * 100, color=colors, width=0.6)
    for b, v, p in zip(bars, t.recall_top10, t.precision_top10):
        ax.text(b.get_x() + b.get_width() / 2, v * 100 + 0.6, f"{v:.1%}", ha="center", color=INK, fontweight="bold")
        ax.text(b.get_x() + b.get_width() / 2, 1.0, f"precision {p:.1%}", ha="center", color=INK, fontsize=9)
    ax.set_ylabel("Recall at top 10% (%)"); ax.set_ylim(0, 30)
    save(fig, "fig5_model_recall.png", "Olist dataset; src/ws3_model.py")


def fig_business_case():
    wb = load_workbook(os.path.join(ROOT, "reports", "excel", "business_case.xlsx"), data_only=True)
    m = wb["Model"]
    net = [m[f"{c}17"].value for c in "BCD"]
    labels = ["Conservative", "Base", "Optimistic"]
    fig, ax = frame("Early warning loses money in every scenario at today's volume",
                    f"Year-1 net benefit, BRL. Base case breaks even only at {m['C22'].value:.1f}× today's order volume")
    bars = ax.bar(labels, net, color=RED, width=0.55)
    for b, v in zip(bars, net):
        ax.text(b.get_x() + b.get_width() / 2, v - 2500, f"R$ {v:,.0f}", ha="center", va="top", color=INK, fontweight="bold")
    ax.axhline(0, color=INK2, linewidth=1)
    ax.set_ylim(min(net) * 1.25, 5000)
    ax.set_ylabel("Year-1 net benefit (BRL)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x / 1000:,.0f}k"))
    save(fig, "fig6_business_case.png", "reports/excel/business_case.xlsx (assumptions labelled)")


def fig_complaints():
    f = os.path.join(P, "ws2", "low_reviews_classified.csv")
    if not os.path.exists(f):
        return
    d = pd.read_csv(f)
    names = {"not_delivered": "Not delivered", "late": "Late", "partial_or_missing": "Partial / missing item",
             "wrong_item": "Wrong item", "damaged_defective": "Damaged / defective",
             "quality_not_as_described": "Quality / not as described", "seller_service": "Seller service",
             "other": "Other / unclear"}
    t = pd.crosstab(d.complaint, d.is_late, normalize="columns").mul(100)
    order = ["partial_or_missing", "quality_not_as_described", "wrong_item", "damaged_defective",
             "not_delivered", "late", "seller_service", "other"]
    t = t.reindex(order)
    fig, ax = frame("On-time orders get low reviews for what arrives, not when",
                    f"Complaint mix of {len(d):,} 1-2 star reviews with text, by delivery status (%)", size=(9.5, 5.4))
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID, linewidth=0.8)
    y = range(len(order)); h = 0.38
    b1 = ax.barh([i - h / 2 for i in y], t[0], h, color=BLUE, label=f"On time (n={int((d.is_late==0).sum()):,})")
    b2 = ax.barh([i + h / 2 for i in y], t[1], h, color=GREY, label=f"Late (n={int((d.is_late==1).sum()):,})")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_width() + 0.6, b.get_y() + b.get_height() / 2, f"{b.get_width():.0f}%", va="center", fontsize=9, color=INK2)
    ax.set_yticks(list(y)); ax.set_yticklabels([names[k] for k in order]); ax.invert_yaxis()
    ax.set_xlim(0, 70); ax.legend(frameon=False, loc="lower right")
    save(fig, "fig7_complaints.png", "Olist reviews; Portuguese rule classifier, macro-F1 0.82 on held-out labels", left=0.25)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig_score_by_delay(); fig_stage_days(); fig_states(); fig_monthly(); fig_model(); fig_business_case(); fig_complaints()
