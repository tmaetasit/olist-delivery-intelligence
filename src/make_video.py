"""Make the ~3-minute captioned portfolio video (no voice; record a voiceover on top if wanted).

Usage:  python src/make_video.py      (after make_figures.py and the Power BI screenshots)
Output: reports/video/olist_delivery_intelligence.mp4
"""
import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "reports", "figures")
PBI = os.path.join(ROOT, "reports", "powerbi")
OUT = os.path.join(ROOT, "reports", "video")
TMP = os.path.join(ROOT, "build", "video")
W, H, FPS = 1920, 1080, 30

SURF, INK, INK2, BLUE, GRID, NAVY = "#fcfcfb", "#0b0b0b", "#52514e", "#2a78d6", "#e6e5e0", "#0d366b"
FD = "/usr/share/fonts/truetype/dejavu/"


def font(size, bold=False):
    return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def wrap_px(text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def base(kicker, title):
    im = Image.new("RGB", (W, H), SURF)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=BLUE)
    if kicker:
        d.text((120, 70), kicker.upper(), font=font(28, True), fill=BLUE)
    if title:
        d.text((120, 112), title, font=font(54, True), fill=INK)
    return im, d


def caption(d, text):
    d.line([120, 952, W - 120, 952], fill=GRID, width=2)
    lines = textwrap.wrap(text, 92)
    y = 975 if len(lines) > 1 else 990
    for ln in lines:
        d.text((W // 2, y), ln, font=font(32), fill=INK2, anchor="ma")
        y += 44


def paste_fit(im, path, box):
    x0, y0, x1, y1 = box
    pic = Image.open(path).convert("RGB")
    s = min((x1 - x0) / pic.width, (y1 - y0) / pic.height)
    pic = pic.resize((int(pic.width * s), int(pic.height * s)), Image.LANCZOS)
    x = x0 + ((x1 - x0) - pic.width) // 2
    y = y0 + ((y1 - y0) - pic.height) // 2
    ImageDraw.Draw(im).rectangle([x - 2, y - 2, x + pic.width + 1, y + pic.height + 1], outline=GRID, width=2)
    im.paste(pic, (x, y))


def chart(kicker, title, img, cap):
    im, d = base(kicker, title)
    paste_fit(im, img, (120, 215, W - 120, 925))
    caption(d, cap)
    return im


def tiles(kicker, title, items, cap, sub=None):
    im, d = base(kicker, title)
    n = len(items)
    gap, x0 = 40, 120
    w = (W - 240 - gap * (n - 1)) // n
    for i, (big, small) in enumerate(items):
        x = x0 + i * (w + gap)
        d.rounded_rectangle([x, 300, x + w, 700], radius=18, fill="#ffffff", outline=GRID, width=3)
        d.text((x + 40, 345), big, font=font(84 if n <= 3 else 72, True), fill=BLUE)
        f = font(34 if n <= 3 else 30)
        yy = 490
        for ln in wrap_px(small, f, w - 80):
            d.text((x + 40, yy), ln, font=f, fill=INK)
            yy += 46
    if sub:
        d.text((120, 760), sub, font=font(30), fill=INK2)
    caption(d, cap)
    return im


def scenes():
    s = []
    im, d = base("", "")
    d.text((120, 330), "Olist Delivery Intelligence", font=font(96, True), fill=INK)
    d.text((120, 470), "Why customers leave bad reviews, and which fix pays back first", font=font(44), fill=INK2)
    d.text((120, 640), "Maetasit Pittatanang  ·  Business Analyst portfolio", font=font(36, True), fill=BLUE)
    d.text((120, 700), "100k real orders · SQL · Python · Power BI · Excel", font=font(32), fill=INK2)
    caption(d, "Olist, a Brazilian marketplace, grew sales but not satisfaction. I analysed 100,000 real orders to find out why.")
    s.append(("01_title", im, 9))

    s.append(("02_question", tiles("The problem", "Delay costs stars, but it is not the whole story",
              [("2.27★", "Average review when the order is late"), ("4.29★", "Average review when on time"),
               ("67%", "of bad reviews come from on-time orders")],
              "Late orders get far worse reviews, yet two in three bad reviews come from orders that arrived on time.",
              "Analysis window Jan 2017 – Aug 2018 · 96,203 delivered orders"), 15))

    s.append(("03_approach", tiles("Approach", "One data foundation, five workstreams",
              [("WS0", "SQL star schema, 19/19 data-quality tests"), ("WS1", "Where and why delay happens"),
               ("WS2", "What unhappy customers say"), ("WS3", "Can we predict late orders?"),
               ("WS4", "Which fix pays back")],
              "I built a SQL pipeline with 19 data-quality tests, then ran five workstreams from diagnosis to business case."), 14))

    s.append(("04_score", chart("WS1 · Diagnose", "Every day late costs satisfaction", os.path.join(FIG, "fig1_score_by_delay.png"),
              "On time: 4.3 stars. One to three days late: 3.3. Eight or more days late: 1.7."), 14))

    s.append(("05_pbi_overview", chart("Power BI · Executive Overview", "One page for the whole story",
              os.path.join(PBI, "executive_overview.png"),
              "Power BI on a star schema with 24 DAX measures: late rate peaks in busy months, and the north-east misses most."), 15))

    s.append(("06_complaints", chart("WS2 · Voice of customer", "On-time orders fail on what arrives",
              os.path.join(FIG, "fig7_complaints.png"),
              "I classified 9,195 Portuguese reviews (macro-F1 0.82 on held-out labels). On-time complaints: 60% are about the product or fulfilment."), 17))

    s.append(("07_pbi_complaints", chart("Power BI · Why customers complain", "Split shipments look like missing items",
              os.path.join(PBI, "why_customers_complain.png"),
              "In multi-seller orders, 48% of complaints say an item is missing, against 13% for single-seller orders."), 14))

    s.append(("08_stages", chart("WS1 · Diagnose", "Late orders lose the time in transit",
              os.path.join(FIG, "fig2_stage_days.png"),
              "Late orders spend about 20 extra days with the carrier, and 72% of them had a seller who shipped on time."), 15))

    s.append(("09_states", chart("WS1 · Diagnose", "The promise is not calibrated by route",
              os.path.join(FIG, "fig3_states_buffer.png"),
              "States with less slack in the delivery promise miss it more often (r = −0.72)."), 14))

    s.append(("10_model", chart("WS3 · Predict", "A model helps, within limits",
              os.path.join(FIG, "fig5_model_recall.png"),
              "At payment approval the model finds 1.7× more late orders than a simple rule, but only 1 alert in 9 is right."), 15))

    s.append(("11_business_case", chart("WS4 · Business case", "The early-warning system does not pay back yet",
              os.path.join(FIG, "fig6_business_case.png"),
              "Early warning loses about R$ 40.5k in year one and needs ~13× today's volume to break even. Park it."), 15))

    s.append(("12_recommend", tiles("Recommendation", "Two cheap fixes, proven by a pilot",
              [("ETA", "Calibrate the delivery promise by route"), ("SLA", "Seller handover SLA and scorecard"),
               ("8,438", "orders in a 6-week A/B pilot")],
              "Fix the promise and the handover first, tell customers when an order ships in several boxes, and prove it with an A/B test."), 16))

    im, d = base("", "")
    d.text((120, 360), "Everything is reproducible", font=font(80, True), fill=INK)
    d.text((120, 490), "github.com/tmaetasit/olist-delivery-intelligence", font=font(46, True), fill=BLUE)
    d.text((120, 580), "SQL pipeline · Python analysis · Power BI · Excel business case · BRD and FRD", font=font(34), fill=INK2)
    caption(d, "Thanks for watching.")
    s.append(("13_close", im, 8))
    return s


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-2000:])


def main(frames_only=False):
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    parts, total = [], 0
    for name, im, dur in scenes():
        png = os.path.join(TMP, name + ".png")
        im.save(png)
        total += dur
        if frames_only:
            continue
        tmp, fin = os.path.join(TMP, name + ".tmp.mp4"), os.path.join(TMP, name + ".mp4")
        vf = (f"format=yuv420p,loop=-1:1,trim=duration={dur},fade=t=in:st=0:d=0.5:color={SURF},"
              f"fade=t=out:st={dur - 0.5}:d=0.5:color={SURF}")
        run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", png, "-vf", vf, "-r", str(FPS), "-c:v", "libx264",
             "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp])
        os.replace(tmp, fin)
        parts.append(fin)
    print(f"{len(parts) or 'frames only'} scenes, {total} s")
    if frames_only:
        return
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    out = os.path.join(OUT, "olist_delivery_intelligence.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out])
    print("wrote", out)


if __name__ == "__main__":
    main(frames_only="--frames" in sys.argv)
