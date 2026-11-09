"""WS4: build the Excel business case and the seller scorecard from the mart.

Usage:  python src/ws4_build_excel.py
Output: reports/excel/business_case.xlsx, reports/excel/seller_scorecard.xlsx
Measured inputs are computed here from data/processed/olist.db; assumptions are
yellow cells the reader can change. All results are Excel formulas.
"""
import os
import sqlite3

import pandas as pd
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XL = os.path.join(ROOT, "reports", "excel")
F = "Arial"
BLUE, BLACK, GREEN = Font(name=F, color="0000FF"), Font(name=F), Font(name=F, color="008000")
BOLD, TITLE = Font(name=F, bold=True), Font(name=F, bold=True, size=14)
HEAD = Font(name=F, bold=True, color="FFFFFF")
HEAD_FILL, YELLOW = PatternFill("solid", fgColor="1F3864"), PatternFill("solid", fgColor="FFFF00")
GREY = PatternFill("solid", fgColor="F2F2F2")
THIN = Border(bottom=Side(style="thin", color="BFBFBF"))
BRL, BRL2 = 'R$ #,##0;(R$ #,##0);"-"', 'R$ #,##0.00;(R$ #,##0.00);"-"'
PCT, PCT2, NUM, NUM1 = '0.0%;(0.0%);"-"', '0.00%', '#,##0;(#,##0);"-"', '#,##0.0'


def measured(con):
    o = pd.read_sql("""SELECT f.*, c.customer_unique_id FROM fact_orders f JOIN dim_customer c USING (customer_id)
                       WHERE is_delivered = 1 AND chronology_error = 0""", con, parse_dates=["purchase_ts"])
    last12 = o[o.purchase_month.between("2017-09", "2018-08")]
    rv = last12[last12.review_score.notna()]
    win = o[o.in_window == 1].sort_values("purchase_ts")
    first = win.drop_duplicates("customer_unique_id").copy()
    first["n"] = first.customer_unique_id.map(win.groupby("customer_unique_id").order_id.count())
    rep = first.groupby("is_late").apply(lambda g: (g.n > 1).mean(), include_groups=False)
    metrics = pd.read_csv(os.path.join(ROOT, "data", "processed", "ws3", "metrics.csv"), index_col=0)
    return {
        "orders": len(last12), "late_rate": last12.is_late.mean(), "aov": last12.revenue.sum() / len(last12),
        "low_late": rv[rv.is_late == 1].is_low_review.mean(), "low_ontime": rv[rv.is_late == 0].is_low_review.mean(),
        "rep_late": rep.loc[1], "rep_ontime": rep.loc[0],
        "extra_orders": (first[first.n > 1].n - 1).mean(),
        "recall": metrics.loc["Logistic regression", "recall_top10"],
    }


def header(ws, row, labels, widths=None):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=t)
        c.font, c.fill, c.alignment = HEAD, HEAD_FILL, Alignment(wrap_text=True, vertical="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def put(ws, ref, value, font=BLACK, fmt=None, fill=None, note=None):
    c = ws[ref]
    c.value, c.font = value, font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if note:
        c.comment = Comment(note, "Analyst")
    return c


def business_case(m):
    wb = Workbook()
    # ---------------- README ----------------
    ws = wb.active
    ws.title = "README"
    ws.column_dimensions["A"].width = 110
    rows = [
        ("Business Case — Delivery Risk Early-Warning (Option C)", TITLE),
        ("Question (BQ9): does flagging risky orders and messaging customers pay back, and what save rate does it need?", BOLD),
        ("", BLACK),
        ("How to read the colours", BOLD),
        ("Blue text = measured from the Olist data (src/ws4_build_excel.py). Do not edit; rerun the script instead.", BLUE),
        ("Yellow cell = assumption. Change it to test your own view; every result updates.", BLACK),
        ("Black text = formula. Green text = link to another sheet.", BLACK),
        ("", BLACK),
        ("Sheets", BOLD),
        ("Inputs — measured facts and the volume scale factor.", BLACK),
        ("Scenarios — assumptions for Conservative / Base / Optimistic.", BLACK),
        ("Model — benefit, cost, ROI, payback and break-even per scenario.", BLACK),
        ("Sensitivity — year-1 net benefit (base scenario) by save rate and volume scale.", BLACK),
        ("Options — the three interventions compared (Impact × Effort).", BLACK),
        ("", BLACK),
        ("Break-even with Goal Seek: Data → What-If Analysis → Goal Seek → Set cell Model!C17 to 0 by changing Scenarios!C5.", BLACK),
        ("The Model sheet also gives the break-even save rate directly (row 21), because benefit is linear in save rate.", BLACK),
        ("", BLACK),
        ("Every cost and save-rate figure is an ASSUMPTION for a portfolio case study, not a company number.", BOLD),
    ]
    for i, (t, f) in enumerate(rows, 1):
        ws.cell(row=i, column=1, value=t).font = f
    ws["A6"].fill = YELLOW

    # ---------------- Inputs ----------------
    ws = wb.create_sheet("Inputs")
    header(ws, 3, ["Input", "Value", "Unit", "Source / note"], [48, 14, 12, 80])
    ws["A1"].value, ws["A1"].font = "Inputs", TITLE
    src = "fact_orders, delivered, valid timestamps, purchased Sep 2017 – Aug 2018 (last 12 months)"
    inp = [
        (4, "Delivered orders per year", m["orders"], "orders", NUM, src),
        (5, "Late delivery rate", m["late_rate"], "%", PCT, src),
        (6, "Average order value (AOV)", m["aov"], "BRL", BRL2, src + "; revenue = item prices"),
        (7, "Low-review rate, late orders", m["low_late"], "%", PCT, "Reviews of 1–2 stars; same population"),
        (8, "Low-review rate, on-time orders", m["low_ontime"], "%", PCT, "Same population"),
        (9, "Repeat-purchase rate, first order late", m["rep_late"], "%", PCT2, "Customers by customer_unique_id, first order in Jan 2017 – Aug 2018"),
        (10, "Repeat-purchase rate, first order on time", m["rep_ontime"], "%", PCT2, "Same"),
        (11, "Extra orders per repeat customer", m["extra_orders"], "orders", '0.00', "Same"),
        (12, "Model recall at top 10% risk", m["recall"], "%", PCT, "docs/model_card.md, logistic regression, test months Apr–Aug 2018"),
    ]
    for r, label, v, unit, fmt, note in inp:
        ws[f"A{r}"], ws[f"C{r}"], ws[f"D{r}"] = label, unit, note
        put(ws, f"B{r}", round(float(v), 4), BLUE, fmt)
    ws["A13"], ws["C13"], ws["D13"] = "Share of orders flagged", "%", "Policy: act on the riskiest 10% (assumption)"
    put(ws, "B13", 0.10, BLUE, PCT, YELLOW)
    ws["A14"], ws["C14"], ws["D14"] = "Volume scale factor", "x", ("1 = volume in this dataset. The Kaggle data may be a subset of Olist's real "
                                                                 "volume; raise this to test a larger business (assumption)")
    put(ws, "B14", 1, BLUE, '0.0"x"', YELLOW)
    ws["A16"].value, ws["A16"].font = "Derived (per year, at scale 1)", BOLD
    der = [
        (17, "Late orders per year", "=B4*B5", "orders", NUM),
        (18, "Late orders caught by the model", "=B17*B12", "orders", NUM),
        (19, "Orders flagged per year", "=B4*B13", "orders", NUM),
        (20, "Low reviews avoided per saved order", "=B7-B8", "reviews", '0.000'),
        (21, "Repeat probability gained per saved order", "=B10-B9", "%", PCT2),
    ]
    for r, label, f, unit, fmt in der:
        ws[f"A{r}"], ws[f"C{r}"] = label, unit
        put(ws, f"B{r}", f, BLACK, fmt)
    for r in range(4, 22):
        for col in "ACD":
            ws[f"{col}{r}"].font = Font(name=F)

    # ---------------- Scenarios ----------------
    ws = wb.create_sheet("Scenarios")
    ws["A1"].value, ws["A1"].font = "Scenarios (assumptions — yellow cells)", TITLE
    header(ws, 4, ["Assumption", "Conservative", "Base", "Optimistic", "Why this range"], [52, 15, 15, 15, 70])
    sc = [
        (5, "Save rate: share of caught late orders whose bad review is prevented", [0.10, 0.25, 0.40], PCT,
         "A proactive message and wider ETA soften the experience; the pilot measures the true rate"),
        (6, "Cost to handle one low review / complaint (BRL)", [10, 20, 35], BRL,
         "Service contact time, goodwill vouchers, refunds; no company figure available"),
        (7, "Contribution margin on repeat GMV", [0.10, 0.15, 0.20], PCT,
         "Marketplace take rate after costs; no company figure available"),
        (8, "Messaging cost per flagged order (BRL)", [0.10, 0.05, 0.03], BRL2, "SMS / e-mail / push"),
        (9, "One-off build effort (person-days)", [40, 30, 20], NUM, "Scoring job, message trigger, ETA rule, dashboard"),
        (10, "Day rate (BRL)", [800, 800, 800], BRL, "Blended data / engineering rate"),
        (11, "Annual run cost (BRL)", [30000, 20000, 12000], BRL, "Monitoring, monthly retraining, support"),
    ]
    for r, label, vals, fmt, why in sc:
        ws[f"A{r}"], ws[f"E{r}"] = label, why
        ws[f"A{r}"].font = ws[f"E{r}"].font = Font(name=F)
        for col, v in zip("BCD", vals):
            put(ws, f"{col}{r}", v, BLUE, fmt, YELLOW)
    ws["A4"].alignment = Alignment(wrap_text=True)

    # ---------------- Model ----------------
    ws = wb.create_sheet("Model")
    ws["A1"].value, ws["A1"].font = "Model — year 1 (BRL)", TITLE
    header(ws, 3, ["Line", "Conservative", "Base", "Optimistic", "Formula logic"], [48, 16, 16, 16, 60])
    lines = [
        (4, "Saved late orders", "=Inputs!$B$18*Inputs!$B$14*Scenarios!{c}5", NUM, "Caught late orders × scale × save rate"),
        (5, "Low reviews avoided", "={c}4*Inputs!$B$20", NUM, "Saved × (low rate late − low rate on time)"),
        (6, "Complaint cost avoided", "={c}5*Scenarios!{c}6", BRL, "Low reviews avoided × cost per complaint"),
        (7, "Extra repeat customers", "={c}4*Inputs!$B$21", '#,##0.0', "Saved × repeat-rate gap"),
        (8, "Extra repeat GMV", "={c}7*Inputs!$B$11*Inputs!$B$6", BRL, "× extra orders × AOV"),
        (9, "Margin on extra repeat GMV", "={c}8*Scenarios!{c}7", BRL, "× contribution margin"),
        (10, "Annual benefit", "={c}6+{c}9", BRL, ""),
        (12, "Messaging cost", "=Inputs!$B$19*Inputs!$B$14*Scenarios!{c}8", BRL, "Flagged orders × scale × cost per message"),
        (13, "Run cost", "=Scenarios!{c}11", BRL, ""),
        (14, "Build cost (one-off)", "=Scenarios!{c}9*Scenarios!{c}10", BRL, "Person-days × day rate"),
        (15, "Year-1 cost", "=SUM({c}12:{c}14)", BRL, ""),
        (17, "Year-1 net benefit", "={c}10-{c}15", BRL, "Goal Seek target"),
        (18, "Year-1 ROI", "=IFERROR({c}17/{c}15,0)", PCT, "Net ÷ cost"),
        (19, "Payback (years)", '=IF({c}10-{c}12-{c}13<=0,"Never",{c}14/({c}10-{c}12-{c}13))', '0.0', "Build cost ÷ yearly net after running costs"),
        (21, "Break-even save rate (year 1)", "=IFERROR({c}15/({c}10/Scenarios!{c}5),0)", PCT,
         "Save rate that makes year-1 net = 0 (above 100% = impossible)"),
        (22, "Break-even volume scale (at this save rate)", "=IFERROR(({c}13+{c}14)/(({c}10-{c}12)/Inputs!$B$14),0)", '0.0"x"',
         "How many times today's volume is needed for year-1 net = 0"),
    ]
    for r, label, f, fmt, logic in lines:
        ws[f"A{r}"], ws[f"E{r}"] = label, logic
        ws[f"A{r}"].font = BOLD if r in (10, 15, 17, 21, 22) else Font(name=F)
        ws[f"E{r}"].font = Font(name=F, italic=True, color="595959")
        for col in "BCD":
            put(ws, f"{col}{r}", f.format(c=col), BLACK, fmt)
            if r in (10, 15, 17):
                ws[f"{col}{r}"].border = Border(top=Side(style="thin"))
                ws[f"{col}{r}"].font = Font(name=F, bold=True)
    ws["A11"].value, ws["A16"].value = "", ""
    ws.conditional_formatting.add("B17:D17", FormulaRule(formula=["B17<0"], font=Font(name=F, bold=True, color="C00000")))

    # ---------------- Sensitivity ----------------
    ws = wb.create_sheet("Sensitivity")
    ws["A1"].value, ws["A1"].font = "Year-1 net benefit (BRL), base scenario", TITLE
    ws["A2"].value = "Rows: save rate. Columns: volume scale. Other inputs = Base column of Scenarios."
    ws["A2"].font = Font(name=F, italic=True)
    ws["A4"].value, ws["A4"].font = "Save rate ↓ / Scale →", BOLD
    scales, rates = [1, 5, 10, 20, 50], [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
    for j, s in enumerate(scales):
        put(ws, f"{get_column_letter(j + 2)}4", s, BLUE, '0"x"', YELLOW)
    for i, rt in enumerate(rates):
        r = i + 5
        put(ws, f"A{r}", rt, BLUE, PCT, YELLOW)
        for j in range(len(scales)):
            col = get_column_letter(j + 2)
            f = (f"={col}$4*(Inputs!$B$18*$A{r}*(Inputs!$B$20*Scenarios!$C$6"
                 f"+Inputs!$B$21*Inputs!$B$11*Inputs!$B$6*Scenarios!$C$7)-Inputs!$B$19*Scenarios!$C$8)"
                 f"-Scenarios!$C$11-Scenarios!$C$9*Scenarios!$C$10")
            put(ws, f"{col}{r}", f, BLACK, BRL)
    ws.column_dimensions["A"].width = 24
    for j in range(len(scales)):
        ws.column_dimensions[get_column_letter(j + 2)].width = 16
    ws.conditional_formatting.add("B5:F10", FormulaRule(formula=["B5<0"], fill=PatternFill("solid", fgColor="FBEBEB")))
    ws.conditional_formatting.add("B5:F10", FormulaRule(formula=["B5>=0"], fill=PatternFill("solid", fgColor="E5F4E4")))
    ws["A12"].value = "Red = loses money in year 1. Green = pays back in year 1."
    ws["A12"].font = Font(name=F, italic=True)

    # ---------------- Options ----------------
    ws = wb.create_sheet("Options")
    ws["A1"].value, ws["A1"].font = "Options compared (WS4)", TITLE
    header(ws, 3, ["Option", "What changes", "Evidence (WS1–WS3)", "Effort", "Impact", "Quantified here?", "Recommendation"],
           [26, 42, 52, 10, 10, 16, 40])
    opts = [
        ("A. Route-calibrated ETA", "Set the promised date per state / distance band instead of one buffer",
         "State late rate vs ETA buffer correlation −0.72; late rate 2.8%–21.5% by state; transit is +19.9 days for late orders",
         "Low", "High", "No — needs conversion data", "Do first: config change, attacks the main cause"),
        ("B. Seller handover SLA", "Coach and then penalise sellers above 25% handover-late (90th percentile)",
         "Late handover raises late rate 5.4% → 21.1%; but 72% of late orders had on-time sellers",
         "Medium", "Medium", "No", "Do second: Seller Scorecard tiers A/B/C"),
        ("C. Early warning + proactive message", "Score orders at approval; message the top 10%; widen their ETA",
         "Model recall 24.6% at top 10%, precision 10.9%; 1–3 days late already costs 1 star",
         "High", "Low–Med", "Yes — Model sheet", "Pilot only if the Model sheet passes break-even at real volume"),
    ]
    for i, row in enumerate(opts, 4):
        for j, v in enumerate(row, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.font, c.alignment = Font(name=F), Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[i].height = 62

    for s in wb.worksheets:
        s.sheet_view.showGridLines = s.title not in ("README",)
    path = os.path.join(XL, "business_case.xlsx")
    wb.save(path)
    return path


def scorecard(con):
    items = pd.read_sql("""
        SELECT i.seller_id, s.state AS seller_state, s.city AS seller_city, p.category, i.order_id, i.price,
               i.handover_late, f.is_late, f.review_score, f.is_low_review
        FROM fact_order_items i JOIN fact_orders f USING (order_id)
        JOIN dim_seller s USING (seller_id) JOIN dim_product p USING (product_id)
        WHERE f.in_window = 1 AND f.is_delivered = 1 AND f.chronology_error = 0""", con)
    g = items.groupby("seller_id")
    df = pd.DataFrame({
        "seller_state": g.seller_state.first(), "seller_city": g.seller_city.first(),
        "main_category": g.category.agg(lambda s: s.mode().iat[0]),
        "items": g.size(), "orders": g.order_id.nunique(), "revenue_brl": g.price.sum().round(2),
        "handover_late_items": g.handover_late.sum().astype(int), "late_orders_items": g.is_late.sum().astype(int),
        "avg_review": g.review_score.mean().round(3), "low_review_items": g.is_low_review.sum().astype(int),
    }).reset_index().sort_values("items", ascending=False)

    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    ws.column_dimensions["A"].width = 105
    for i, (t, f) in enumerate([
        ("Seller Scorecard — Tier A / B / C (US-04)", TITLE),
        ("Delivered orders Jan 2017 – Aug 2018. Item level: a seller's own items only.", BLACK),
        ("", BLACK),
        ("Data — one row per seller (values from src/ws4_build_excel.py; refresh by rerunning the script, or connect", BLACK),
        ("        this sheet to data/processed/mart/*.csv with Power Query and group by seller_id).", BLACK),
        ("Scorecard — rates and tier by formula; thresholds on the Settings sheet (yellow).", BLACK),
        ("Lookup — type a seller_id to pull its card with INDEX/MATCH (XLOOKUP works the same in Excel 365).", BLACK),
        ("Summary — sellers and items per tier by state, with COUNTIFS. Insert a PivotTable on Scorecard for more cuts.", BLACK),
        ("", BLACK),
        ("Tier rules: C if handover-late ≥ C threshold OR avg review < C threshold; B if above the B thresholds; else A.", BOLD),
        ("Sellers below the minimum items get 'Too few items' and no tier.", BLACK),
    ], 1):
        ws.cell(row=i, column=1, value=t).font = f

    st = wb.create_sheet("Settings")
    st.column_dimensions["A"].width, st.column_dimensions["B"].width, st.column_dimensions["C"].width = 44, 12, 60
    header(st, 1, ["Setting", "Value", "Why"])
    for r, (label, v, fmt, why) in enumerate([
        ("Minimum items to be tiered", 30, NUM, "Below this, rates are too noisy"),
        ("Tier C: handover-late rate at or above", 0.25, PCT, "90th percentile of sellers with 30+ items (WS1)"),
        ("Tier C: average review below", 3.5, '0.0', "Assumption"),
        ("Tier B: handover-late rate at or above", 0.10, PCT, "About twice the median (4.9%)"),
        ("Tier B: average review below", 4.0, '0.0', "Assumption; overall average is ~4.1"),
    ], 2):
        st[f"A{r}"], st[f"C{r}"] = label, why
        st[f"A{r}"].font = st[f"C{r}"].font = Font(name=F)
        put(st, f"B{r}", v, BLUE, fmt, YELLOW)

    dt = wb.create_sheet("Data")
    cols = list(df.columns)
    header(dt, 1, cols, [36, 8, 22, 26, 8, 8, 14, 12, 12, 10, 12])
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            c = dt.cell(row=i, column=j, value=None if pd.isna(v) else v)
            c.font = BLUE
    n = len(df) + 1
    dt.freeze_panes = "A2"

    sc = wb.create_sheet("Scorecard", 1)
    heads = ["seller_id", "State", "Main category", "Items", "Revenue (BRL)", "Handover-late rate",
             "Late-order rate", "Avg review", "Low-review rate", "Tier"]
    header(sc, 1, heads, [36, 8, 26, 9, 15, 12, 12, 10, 12, 14])
    for r in range(2, n + 1):
        f = {
            "A": f"=Data!A{r}", "B": f"=Data!B{r}", "C": f"=Data!D{r}", "D": f"=Data!E{r}", "E": f"=Data!G{r}",
            "F": f"=IFERROR(Data!H{r}/Data!E{r},0)", "G": f"=IFERROR(Data!I{r}/Data!E{r},0)",
            "H": f"=IF(Data!J{r}=\"\",\"\",Data!J{r})", "I": f"=IFERROR(Data!K{r}/Data!E{r},0)",
            "J": (f"=IF(D{r}<Settings!$B$2,\"Too few items\",IF(OR(F{r}>=Settings!$B$3,AND(H{r}<>\"\",H{r}<Settings!$B$4)),\"C\","
                  f"IF(OR(F{r}>=Settings!$B$5,AND(H{r}<>\"\",H{r}<Settings!$B$6)),\"B\",\"A\")))"),
        }
        fmts = {"D": NUM, "E": BRL, "F": PCT, "G": PCT, "H": '0.00', "I": PCT}
        for col, val in f.items():
            c = sc[f"{col}{r}"]
            c.value, c.font = val, (GREEN if col in "ABCDEH" else BLACK)
            if col in fmts:
                c.number_format = fmts[col]
    sc.freeze_panes = "B2"
    sc.auto_filter.ref = f"A1:J{n}"
    sc.conditional_formatting.add(f"A2:J{n}", FormulaRule(formula=['$J2="C"'], fill=PatternFill("solid", fgColor="FBEBEB")))
    sc.conditional_formatting.add(f"A2:J{n}", FormulaRule(formula=['$J2="B"'], fill=PatternFill("solid", fgColor="F9EEDA")))

    lk = wb.create_sheet("Lookup", 2)
    lk.column_dimensions["A"].width, lk.column_dimensions["B"].width = 26, 40
    lk["A1"].value, lk["A1"].font = "Seller card", TITLE
    lk["A3"].value, lk["A3"].font = "Type a seller_id →", BOLD
    put(lk, "B3", df.seller_id.iat[0], BLUE, fill=YELLOW, note="Example: the seller with the most items. Paste any seller_id.")
    for r, (label, col, fmt) in enumerate([("State", "B", None), ("Main category", "C", None), ("Items", "D", NUM),
                                            ("Revenue (BRL)", "E", BRL), ("Handover-late rate", "F", PCT),
                                            ("Late-order rate", "G", PCT), ("Avg review", "H", '0.00'),
                                            ("Low-review rate", "I", PCT), ("Tier", "J", None)], 5):
        lk[f"A{r}"].value, lk[f"A{r}"].font = label, Font(name=F)
        put(lk, f"B{r}", f'=IFERROR(INDEX(Scorecard!{col}:{col},MATCH($B$3,Scorecard!A:A,0)),"Not found")', GREEN, fmt)

    sm = wb.create_sheet("Summary", 3)
    sm["A1"].value, sm["A1"].font = "Sellers by tier and state", TITLE
    tiers = ["A", "B", "C", "Too few items"]
    header(sm, 3, ["State"] + [f"Tier {t}" if len(t) == 1 else t for t in tiers] + ["Items in tier C", "Share of items in C"],
           [10, 10, 10, 10, 14, 15, 18])
    states = df.groupby("seller_state")["items"].sum().sort_values(ascending=False).index.tolist()
    for i, s in enumerate(states, 4):
        sm[f"A{i}"].value, sm[f"A{i}"].font = s, Font(name=F)
        for j, t in enumerate(tiers):
            col = get_column_letter(j + 2)
            put(sm, f"{col}{i}", f'=COUNTIFS(Scorecard!$B:$B,$A{i},Scorecard!$J:$J,"{t}")', BLACK, NUM)
        put(sm, f"F{i}", f'=SUMIFS(Scorecard!$D:$D,Scorecard!$B:$B,$A{i},Scorecard!$J:$J,"C")', BLACK, NUM)
        put(sm, f"G{i}", f'=IFERROR(F{i}/SUMIFS(Scorecard!$D:$D,Scorecard!$B:$B,$A{i}),0)', BLACK, PCT)
    t = len(states) + 4
    sm[f"A{t}"].value, sm[f"A{t}"].font = "Total", BOLD
    for col in "BCDEF":
        put(sm, f"{col}{t}", f"=SUM({col}4:{col}{t - 1})", BOLD, NUM)
    put(sm, f"G{t}", f'=IFERROR(F{t}/SUM(Scorecard!$D:$D),0)', BOLD, PCT)
    path = os.path.join(XL, "seller_scorecard.xlsx")
    wb.save(path)
    return path


if __name__ == "__main__":
    os.makedirs(XL, exist_ok=True)
    con = sqlite3.connect(os.path.join(ROOT, "data", "processed", "olist.db"))
    print(business_case(measured(con)))
    print(scorecard(con))
