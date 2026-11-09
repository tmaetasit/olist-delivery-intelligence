# 3-Minute Video Script

The captioned video is ready: [reports/video/olist_delivery_intelligence.mp4](../reports/video/olist_delivery_intelligence.mp4) (3:01, 1920×1080, no sound). Rebuild it with `python src/make_video.py`.

To add your voice, read the "Say" column over the video; each line matches one scene. Record in any phone or screen recorder, then join the sound with:

```
ffmpeg -i reports/video/olist_delivery_intelligence.mp4 -i voice.m4a -map 0:v -map 1:a -c:v copy -c:a aac -shortest olist_with_voice.mp4
```

| Time | Scene | Say |
|---|---|---|
| 0:00 | Title | "Hi, I'm Maetasit, a business analyst. Olist, a Brazilian marketplace, grew sales but not customer satisfaction. I analysed 100,000 real orders to find out why." |
| 0:09 | The problem | "Late orders average 2.3 stars against 4.3 on time. But two in three bad reviews come from orders that arrived on time, so delivery is not the whole story." |
| 0:24 | Approach | "I built a SQL pipeline with 19 data-quality tests, then ran five workstreams, from diagnosis to business case." |
| 0:38 | Score by delay | "Every day late costs satisfaction: one to three days late already loses a full star." |
| 0:52 | Power BI overview | "This is the Power BI report: late deliveries spike in busy months, and the north-east misses the promise most." |
| 1:07 | Complaints | "So why do on-time orders get bad reviews? I classified 9,195 Portuguese reviews. Sixty percent of on-time complaints are about the product or fulfilment: missing, wrong or damaged items." |
| 1:24 | Power BI complaints | "In orders from several sellers, almost half the complaints say an item is missing. Items ship separately, and the first box looks incomplete." |
| 1:38 | Stage days | "For late orders, the delay is with the carrier: about twenty extra days in transit. Seventy-two percent had a seller who shipped on time." |
| 1:53 | States | "States with less slack in the promise miss it more. The delivery promise is not calibrated by route." |
| 2:07 | Model | "A model at payment approval finds 1.7 times more late orders than a simple rule, but only one alert in nine is right, so it suits low-cost actions only." |
| 2:22 | Business case | "The early-warning system loses about forty thousand reais in year one. It needs thirteen times today's volume, so I'd park it." |
| 2:37 | Recommendation | "My recommendation: calibrate the promise by route, add a seller handover SLA, tell customers when an order ships in several boxes, and prove it with a six-week A/B test of 8,400 orders." |
| 2:53 | Close | "Everything is reproducible on GitHub. Thanks for watching." |

## ฉบับภาษาไทย (อ่านทับวิดีโอได้เลย)

| เวลา | พูด |
|---|---|
| 0:00 | "สวัสดีครับ ผมเมธาสิทธิ์ เป็น Business Analyst ครับ Olist เป็นมาร์เก็ตเพลสในบราซิลที่ยอดขายโต แต่ความพึงพอใจไม่โตตาม ผมวิเคราะห์ออเดอร์จริงแสนรายการเพื่อหาสาเหตุครับ" |
| 0:09 | "ออเดอร์ที่ส่งช้าได้เฉลี่ย 2.3 ดาว ส่วนที่ตรงเวลาได้ 4.3 ดาว แต่ 2 ใน 3 ของรีวิวแย่กลับมาจากออเดอร์ที่ส่งตรงเวลา แปลว่าเรื่องส่งช้าไม่ใช่ทั้งหมด" |
| 0:24 | "ผมสร้าง SQL pipeline พร้อมการทดสอบคุณภาพข้อมูล 19 ข้อ แล้วแบ่งงานเป็น 5 ส่วน ตั้งแต่วินิจฉัยไปจนถึง Business Case" |
| 0:38 | "ช้าทุกวันเสียความพึงพอใจ แค่ช้า 1–3 วันก็หายไป 1 ดาวเต็ม" |
| 0:52 | "นี่คือรายงาน Power BI ส่งช้าพุ่งในช่วงเดือนที่ยุ่ง และภาคตะวันออกเฉียงเหนือพลาดนัดมากที่สุด" |
| 1:07 | "แล้วทำไมออเดอร์ตรงเวลาถึงได้รีวิวแย่ ผมจัดหมวดรีวิวภาษาโปรตุเกส 9,195 รายการ พบว่า 60% เป็นเรื่องสินค้าและการแพ็ก เช่น ของขาด ผิด หรือเสียหาย" |
| 1:24 | "ในออเดอร์หลายผู้ขาย เกือบครึ่งบอกว่าของไม่ครบ เพราะของแยกกล่องมา กล่องแรกเลยดูเหมือนของหาย" |
| 1:38 | "ส่วนออเดอร์ที่ช้า เวลาหายไปตอนขนส่งราว 20 วัน และ 72% ผู้ขายส่งมอบตรงเวลา" |
| 1:53 | "รัฐที่วันสัญญาเผื่อเวลาน้อยจะพลาดบ่อยกว่า วันที่สัญญาไม่ได้ปรับตามเส้นทาง" |
| 2:07 | "Model ตอนอนุมัติการชำระเงินหาออเดอร์ที่จะช้าได้มากกว่ากฎง่ายๆ 1.7 เท่า แต่เตือนถูกแค่ 1 ใน 9 จึงเหมาะกับมาตรการต้นทุนต่ำเท่านั้น" |
| 2:22 | "ระบบเตือนล่วงหน้าขาดทุนราว 4 หมื่นเรียลในปีแรก ต้องมีปริมาณงาน 13 เท่าถึงจะคุ้ม ผมจึงแนะนำให้พักไว้ก่อน" |
| 2:37 | "ข้อเสนอคือปรับวันที่สัญญาตามเส้นทาง ทำ SLA การส่งมอบของผู้ขาย บอกลูกค้าเมื่อของมาหลายกล่อง และพิสูจน์ด้วย A/B test 6 สัปดาห์ ราว 8,400 ออเดอร์" |
| 2:53 | "ทุกอย่างทำซ้ำได้บน GitHub ขอบคุณที่รับชมครับ" |
