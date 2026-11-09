# LinkedIn Post Drafts

Attach: the 3-minute video (`reports/video/olist_delivery_intelligence.mp4`), or `reports/figures/fig7_complaints.png` + `fig6_business_case.png`. Add the GitHub link in the first comment.

## English

I analysed 100,000 real e-commerce orders to answer one question: why do customers leave bad reviews, and which fix pays back first?

What I found:
📦 Late orders average 2.27★ vs 4.29★ on time, and even 1–3 days late costs a full star.
🚚 72% of late orders had a seller who shipped on time. The delay is in carrier transit (+20 days), and the delivery promise isn't calibrated by route.
💬 2 in 3 bad reviews come from orders that arrived on time. I classified 9,195 Portuguese review comments: 60% of on-time complaints are about the product or fulfilment (missing, wrong, damaged), not speed. In multi-seller orders, half the complaints say an item is missing: split shipments look broken.
💸 The early-warning system I planned to build loses money at this volume. So I changed my recommendation to a route-based promise plus a seller SLA, with a 6-week A/B pilot.

Built with SQL, Power BI/DAX, Python (pm4py, scikit-learn, SHAP) and Excel. BRD, KPI dictionary, user stories, RACI, FRD and a business case are all in the repo.

The hardest part wasn't the model. It was being willing to say "don't build this" when the numbers said so.

#BusinessAnalysis #DataAnalytics #PowerBI #SQL #Portfolio

## ภาษาไทย

ผมวิเคราะห์ออเดอร์ e-commerce จริง 100,000 รายการ เพื่อตอบคำถามเดียว: ทำไมลูกค้ารีวิวแย่ และควรแก้อะไรก่อนถึงจะคุ้ม

สิ่งที่เจอ:
📦 ออเดอร์ส่งช้าได้รีวิวเฉลี่ย 2.27 ดาว ส่วนออเดอร์ตรงเวลาได้ 4.29 ดาว แค่ช้า 1–3 วันคะแนนก็หายไป 1 ดาวเต็ม
🚚 72% ของออเดอร์ที่ช้า ผู้ขายส่งมอบตรงเวลา ปัญหาไปเกิดตอนขนส่ง (ช้ากว่าปกติ 20 วัน) และวันที่สัญญากับลูกค้าไม่ได้ปรับตามเส้นทาง
💬 2 ใน 3 ของรีวิวแย่มาจากออเดอร์ที่ส่งตรงเวลา ผมจัดหมวดข้อความรีวิวภาษาโปรตุเกส 9,195 รายการ พบว่า 60% ของคำร้องเรียนในออเดอร์ตรงเวลาเป็นเรื่องสินค้าและการแพ็ก (ของขาด ผิด เสียหาย) ไม่ใช่ความเร็ว และในออเดอร์หลายผู้ขาย ครึ่งหนึ่งบอกว่าของไม่ครบ เพราะของแยกกล่องมาไม่พร้อมกัน
💸 ระบบเตือนล่วงหน้าที่ตั้งใจจะทำตั้งแต่แรกกลับขาดทุน ผมจึงเปลี่ยนข้อเสนอเป็นปรับวันที่สัญญาตามเส้นทาง ควบคู่กับ SLA ผู้ขาย แล้วพิสูจน์ด้วย A/B test 6 สัปดาห์

ใช้ SQL, Power BI/DAX, Python และ Excel มีเอกสาร BA ครบใน GitHub ทั้ง BRD, KPI, User Stories, RACI, FRD และ Business Case

สิ่งที่ยากที่สุดไม่ใช่การทำ Model แต่คือการกล้าบอกว่า "ไม่ควรสร้าง" เมื่อตัวเลขบอกแบบนั้น

#BusinessAnalyst #DataAnalytics #PowerBI #Portfolio
