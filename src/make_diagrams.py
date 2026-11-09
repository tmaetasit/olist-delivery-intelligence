"""Draw the As-Is / To-Be process maps, the driver tree and two wireframes as SVG.

Usage:  python src/make_diagrams.py
Output: design/*.svg (GitHub renders SVG directly). Numbers come from docs/ws1_findings.md.
"""
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "design")
INK, INK2, LINE, FILL = "#0b0b0b", "#52514e", "#8a8984", "#ffffff"
BLUE, BLUE_T, RED, RED_T, LANE = "#2a78d6", "#e7f1fb", "#c0392b", "#fbebeb", "#f4f3ef"
FONT = "Arial, Helvetica, sans-serif"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<rect width="{w}" height="{h}" fill="#fcfcfb"/>')
        self.text(24, 36, title, 20, INK, weight="bold")
        self.parts.append(
            '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{LINE}"/></marker>'
            '<marker id="b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{BLUE}"/></marker></defs>')

    def text(self, x, y, s, size=13, color=INK, anchor="start", weight="normal"):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" '
                          f'text-anchor="{anchor}" font-weight="{weight}">{escape(s)}</text>')

    def box(self, x, y, w, h, lines, stroke=LINE, fill=FILL, dash=None, sw=1.3, size=12.5, rx=8):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        top = y + h / 2 - (len(lines) - 1) * (size + 4) / 2 + size / 3
        for i, (s, bold) in enumerate(lines):
            self.text(x + w / 2, top + i * (size + 4), s, size, INK, "middle", "bold" if bold else "normal")

    def rect(self, x, y, w, h, fill, stroke="none", rx=0, sw=1):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def arrow(self, pts, color=LINE, dash=None, marker="a"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        path = "M" + " L".join(f"{x} {y}" for x, y in pts)
        self.parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.5"{d} marker-end="url(#{marker})"/>')

    def badge(self, x, y, label, color=RED):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="11" fill="{color}"/>')
        self.text(x, y + 4.5, label, 12, "#ffffff", "middle", "bold")

    def save(self, name):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
               + "".join(self.parts) + "</svg>")
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)


LANES = ["Customer", "Olist platform", "Seller", "Carrier"]


def lanes(s, y0=70, h=110, left=150):
    for i, name in enumerate(LANES):
        y = y0 + i * h
        s.rect(24, y, s.w - 48, h - 6, LANE if i % 2 == 0 else "#fbfaf7", rx=6)
        s.text(40, y + h / 2, name, 14, INK2, weight="bold")
    return lambda i: y0 + i * h + (h - 6) / 2


def as_is():
    s = Svg(1240, 640, "As-Is: one promise for every route, nobody manages handover")
    cy = lanes(s)
    W, H = 150, 58
    s.box(170, cy(0) - H / 2, W, H, [("Places order", True), ("sees promise ≈ 24 days", False)])
    s.box(370, cy(1) - H / 2, W, H, [("Sets promise", True), ("one buffer, all routes", False)])
    s.box(560, cy(1) - H / 2, W, H, [("Approves payment", True), ("0.5 days", False)])
    s.box(560, cy(2) - H / 2, W, H, [("Prepares + hands over", True), ("2.5 d on time · 5.4 d late", False)])
    s.box(780, cy(3) - H / 2, W + 20, H, [("Transports", True), ("7.9 d on time · 27.9 d late", False)])
    s.box(780, cy(0) - H / 2, W + 20, H, [("Receives order", True), ("6.8% after the promise", False)])
    s.box(1010, cy(0) - H / 2, W + 40, H, [("Writes review", True), ("4.29 on time · 2.27 late", False)])
    s.arrow([(320, cy(0)), (345, cy(0)), (345, cy(1)), (368, cy(1))])
    s.arrow([(520, cy(1)), (558, cy(1))])
    s.arrow([(635, cy(1) + H / 2), (635, cy(2) - H / 2 - 2)])
    s.arrow([(710, cy(2)), (745, cy(2)), (745, cy(3)), (778, cy(3))])
    s.arrow([(865, cy(3) - H / 2), (865, cy(0) + H / 2 + 2)])
    s.arrow([(950, cy(0)), (1008, cy(0))])
    s.badge(512, cy(1) - H / 2 - 4, "1"); s.badge(702, cy(2) - H / 2 - 4, "2")
    s.badge(942, cy(3) - H / 2 - 4, "3"); s.badge(942, cy(0) - H / 2 - 4, "4")
    y = 530
    s.text(24, y, "Pain points (evidence from WS1)", 14, INK, weight="bold")
    notes = ["1  Promise ignores the route: state late rate 2.8%–21.5%, tied to ETA buffer (r = −0.72)",
             "2  Handover deadline not managed: a late handover lifts the late rate from 5.4% to 21.1%",
             "3  Transit is where late orders lose time: +19.9 days vs on-time orders; no carrier data",
             "4  Customer is not warned: even 1–3 days late cuts the review from 4.29 to 3.29"]
    for i, n in enumerate(notes):
        s.text(24 + (i % 2) * 610, y + 26 + (i // 2) * 24, n, 12.5, INK2)
    s.save("as_is_process.svg")


def to_be():
    s = Svg(1240, 640, "To-Be: route-calibrated promise and a managed seller handover")
    cy = lanes(s)
    W, H = 150, 58
    s.box(170, cy(0) - H / 2, W, H, [("Places order", True), ("sees route promise", False)])
    s.box(370, cy(1) - H / 2, W + 10, H, [("Route table promise", True), ("FR-01 · 85th pct transit", False)], BLUE, BLUE_T, sw=2)
    s.box(575, cy(1) - H / 2, W, H, [("Approves payment", True), ("deadline to seller", False)])
    s.box(565, cy(2) - H / 2, W + 20, H, [("Hands over", True), ("logged vs deadline · FR-04", False)], BLUE, BLUE_T, sw=2)
    s.box(790, cy(3) - H / 2, W + 20, H, [("Transports", True), ("transit time feeds FR-02", False)])
    s.box(790, cy(0) - H / 2, W + 20, H, [("Receives order", True), ("on the route promise", False)])
    s.box(1015, cy(0) - H / 2, W + 35, H, [("Writes review", True), ("tracked weekly", False)])
    s.box(1015, cy(1) - 44, W + 35, 88, [("Weekly loop", True), ("refresh route table → FR-01", False), ("seller tiers A/B/C", False),
                                           ("coach B · review C", False)], BLUE, BLUE_T, sw=2, size=12)
    s.box(370, cy(3) - H / 2, W + 10, H, [("Phase 2 (parked)", True), ("risk score + message", False)], LINE, FILL, dash="5 4")
    s.arrow([(320, cy(0)), (345, cy(0)), (345, cy(1)), (368, cy(1))])
    s.arrow([(530, cy(1)), (573, cy(1))])
    s.arrow([(650, cy(1) + H / 2), (650, cy(2) - H / 2 - 2)])
    s.arrow([(735, cy(2)), (760, cy(2)), (760, cy(3)), (788, cy(3))])
    s.arrow([(875, cy(3) - H / 2), (875, cy(0) + H / 2 + 2)])
    s.arrow([(960, cy(0)), (1013, cy(0))])
    s.arrow([(1107, cy(0) + H / 2), (1107, cy(1) - 46)], BLUE, "4 3", "b")
    y = 530
    s.text(24, y, "What changes", 14, INK, weight="bold")
    notes = ["Blue = new or changed step. Dashed = parked until volume is ~13× today (business case).",
             "Promise per route: seller state × customer state × distance band, refreshed weekly (FR-01, FR-02).",
             "Handover becomes a KPI: tiers A/B/C, coaching before penalties, seller sees the numbers (FR-04, FR-05).",
             "Every order logs the route-table version and tier used, so the pilot can be measured (FR-07)."]
    for i, n in enumerate(notes):
        s.text(24, y + 26 + i * 22, n, 12.5, INK2)
    s.save("to_be_process.svg")


def driver_tree():
    s = Svg(1100, 470, "Driver tree: most late orders are a transit and promise problem")
    s.box(40, 190, 200, 80, [("Late delivery rate", True), ("6.8% · 6,529 orders", False)], BLUE, BLUE_T, sw=2, size=14)
    s.box(320, 95, 240, 74, [("Seller handed over late", True), ("27.7% of late orders", False)], size=13)
    s.box(320, 290, 240, 74, [("Seller on time, still late", True), ("72.3% of late orders", False)], BLUE, BLUE_T, sw=2, size=13)
    s.box(640, 60, 410, 64, [("Late handover → late rate 21.1% vs 5.4%", True), ("Lever: seller SLA, tiers A/B/C (Option B)", False)])
    s.box(640, 140, 410, 64, [("Seller handling 5.4 days vs 2.5", True), ("90th-percentile seller: 25% handovers late", False)])
    s.box(640, 240, 410, 64, [("Carrier transit 27.9 days vs 7.9", True), ("No carrier ID in data → measure by route", False)])
    s.box(640, 320, 410, 64, [("Promise does not fit the route (r = −0.72)", True), ("Lever: route-calibrated ETA (Option A)", False)], BLUE, BLUE_T, sw=2)
    s.box(640, 400, 410, 50, [("Peak months: 12.4% Nov 2017 · 19.0% Mar 2018", True)])
    for (x1, y1), (x2, y2) in [((240, 230), (318, 132)), ((240, 230), (318, 327)), ((560, 132), (638, 92)),
                               ((560, 132), (638, 172)), ((560, 327), (638, 272)), ((560, 327), (638, 352)),
                               ((560, 327), (638, 425))]:
        xm = (x1 + x2) / 2
        s.arrow([(x1, y1), (xm, y1), (xm, y2), (x2, y2)])
    s.save("driver_tree.svg")


def wire_box(s, x, y, w, h, label=None, fill="#ffffff"):
    s.rect(x, y, w, h, fill, "#b5b4ae", rx=6, sw=1.2)
    if label:
        s.text(x + 14, y + 22, label, 12.5, INK2, weight="bold")


def row(s, x, y, cols, widths, bold=False):
    for c, w in zip(cols, widths):
        s.text(x, y, c, 12, INK2, weight="bold" if bold else "normal")
        x += w


def seller_portal():
    s = Svg(1000, 660, "Wireframe 1 — Seller portal: \"Your delivery score\" (US-04, FR-04/05)")
    wire_box(s, 24, 56, 952, 580, fill="#fbfaf7")
    s.rect(24, 56, 952, 44, "#e9e8e3", rx=6)
    s.text(44, 84, "olist seller  ·  Orders   Products   Delivery score   Payments", 13, INK2)
    wire_box(s, 48, 120, 280, 150, "Your tier this week")
    s.rect(70, 160, 90, 90, BLUE_T, BLUE, rx=45, sw=2)
    s.text(115, 217, "B", 40, BLUE, "middle", "bold")
    s.text(178, 190, "Was A last week", 12.5, INK2); s.text(178, 212, "Coaching message sent", 12.5, INK2)
    s.text(178, 234, "Rules: see thresholds ▸", 12.5, BLUE)
    wire_box(s, 348, 120, 300, 150, "Handover on time")
    s.text(370, 190, "88.4%", 34, INK, weight="bold"); s.text(370, 218, "Target ≥ 90% (tier A)", 12.5, INK2)
    s.rect(370, 232, 250, 10, "#e9e8e3", rx=5); s.rect(370, 232, 221, 10, BLUE, rx=5)
    wire_box(s, 668, 120, 284, 150, "Average review")
    s.text(690, 190, "3.9 ★", 34, INK, weight="bold"); s.text(690, 218, "Tier A needs ≥ 4.0", 12.5, INK2)
    wire_box(s, 48, 290, 600, 190, "Handover on time — last 12 weeks")
    pts = [(80 + i * 48, 440 - v) for i, v in enumerate([96, 104, 92, 110, 118, 100, 94, 80, 70, 86, 74, 62])]
    s.parts.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    s.parts.append(f'<line x1="70" y1="352" x2="630" y2="352" stroke="{INK2}" stroke-dasharray="5 4"/>')
    s.text(632, 348, "90%", 11, INK2, "end")
    wire_box(s, 668, 290, 284, 190, "How to improve")
    for i, t in enumerate(["• Hand over before the deadline", "• Ship multi-item orders together",
                           "• Update stock to avoid delays", "• Talk to your account manager ▸"]):
        s.text(686, 338 + i * 30, t, 12.5, INK2)
    wire_box(s, 48, 500, 904, 116, "Latest late handovers")
    wd = [140, 170, 170, 120, 140]
    row(s, 66, 548, ["Order", "Deadline", "Handed over", "Days late", "Customer state"], wd, True)
    for i, r in enumerate([["#7f3a…", "12 Mar 10:00", "13 Mar 16:20", "1", "BA"],
                           ["#c21d…", "09 Mar 10:00", "11 Mar 09:05", "2", "SP"]]):
        row(s, 66, 572 + i * 22, r, wd)
    s.save("wireframe_seller_portal.svg")


def ops_dashboard():
    s = Svg(1000, 660, "Wireframe 2 — Operations: \"Routes this week\" (US-03, FR-06)")
    wire_box(s, 24, 56, 952, 580, fill="#fbfaf7")
    s.rect(24, 56, 952, 44, "#e9e8e3", rx=6)
    s.text(44, 84, "Week: 12 Mar ▾     State: All ▾     Category: All ▾     Route table: v14 (updated Mon 06:00)", 13, INK2)
    for i, (label, val, sub) in enumerate([("Late delivery rate", "5.1%", "−1.7 pts vs pilot control"),
                                           ("Avg review", "4.18", "+0.07 vs last month"),
                                           ("Sellers entering tier C", "6", "of 678 with 30+ items"),
                                           ("Checkout conversion", "guardrail", "must not fall > 1 pt")]):
        x = 48 + i * 232
        wire_box(s, x, 120, 216, 100, label)
        s.text(x + 14, 178, val, 26, INK, weight="bold"); s.text(x + 14, 204, sub, 11.5, INK2)
    wire_box(s, 48, 240, 420, 376, "Late rate by customer state")
    s.parts.append(f'<path d="M150 300 L330 290 L400 350 L380 470 L300 560 L210 540 L160 450 Z" fill="{BLUE_T}" stroke="{BLUE}"/>')
    s.parts.append(f'<path d="M330 290 L400 350 L430 330 L410 290 Z" fill="#9ec5f4" stroke="{BLUE}"/>')
    s.text(258, 600, "(map: darker = later)", 11.5, INK2, "middle")
    wire_box(s, 488, 240, 464, 220, "10 worst routes this week")
    wd = [100, 70, 60, 105, 100]
    row(s, 506, 286, ["Route", "Orders", "Late", "Old promise", "New promise"], wd, True)
    for i, r in enumerate([["SP → AL", "84", "19%", "33 d", "38 d"], ["SP → MA", "121", "16%", "31 d", "35 d"],
                           ["MG → CE", "96", "14%", "32 d", "34 d"], ["…", "", "", "", ""]]):
        row(s, 506, 312 + i * 24, r, wd)
    wire_box(s, 488, 476, 464, 140, "Sellers entering tier C")
    for i, t in enumerate(["seller 4a3c…  ·  handover late 31%  ·  review 3.4  ·  Review call ▸",
                           "seller 9e1f…  ·  handover late 27%  ·  review 3.8  ·  Review call ▸"]):
        s.text(506, 522 + i * 26, t, 12, INK2)
    s.text(48, 652, "Illustrative numbers in the wireframes — layout only.", 11, INK2)
    s.save("wireframe_ops_dashboard.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    as_is(); to_be(); driver_tree(); seller_portal(); ops_dashboard()
