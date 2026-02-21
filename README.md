# 🏭 SCM Dashboard — CJ Supply Chain Management

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

ระบบ Dashboard สำหรับบริหารจัดการ Supply Chain ของ CJ  
วิเคราะห์ยอดขาย, สต็อก, OOS, โปรโมชั่น และ Purchase Order

---

## 📋 โมดูลทั้งหมด

| โมดูล | รายละเอียด |
|---|---|
| 🏠 Dashboard | ภาพรวม Revenue, SKU, OOS, Promo |
| 📈 Sales Forecasting | พยากรณ์ยอดขาย M1-M4 ราย SKU |
| 📦 Inventory Management | DOH Store/DC, Stock Value by Category |
| ⚠️ OOS Analysis | วิเคราะห์สินค้าขาดสต็อก แยกตาม Severity |
| 🔍 OOS Reconcile | Root Cause Analysis + แนวทางแก้ไข |
| 📅 Monthly Forecast M1-M4 | Demand Forecast 4 เดือนข้างหน้า |
| 🎯 Promo Demand Forecast | พยากรณ์ยอดขายตามแผนโปรโมชั่น |
| 🏷️ Promotions | แผนโปรโมชั่นทั้งหมด |
| 📋 Supply Planning | PO Tracking & Fill Rate |
| 📊 Reports | Sales / Inventory / Promotion / Supply |
| 📤 Upload Data | อัปโหลดข้อมูลใหม่ |

---

## 🔍 Global Filter

ทุกหน้ามี Filter ที่ Sidebar ใช้ได้พร้อมกัน:
- **Division** — แผนกสินค้า
- **Category** — หมวดหมู่สินค้า
- **Supplier** — ชื่อ Supplier
- **Brand** — แบรนด์สินค้า
- **CJ Code** — รหัสสินค้า
- **Description** — ชื่อสินค้า

---

## 🚀 วิธี Run บนเครื่อง (Local)

### 1. ติดตั้ง Python dependencies
```bash
pip install -r requirements.txt
```

### 2. วางไฟล์ให้ครบ
```
project/
    ├── scm_streamlit.py
    ├── scm_v2.json
    ├── requirements.txt
    └── README.md
```

### 3. Run
```bash
streamlit run scm_streamlit.py
```

เปิด Browser ที่ `http://localhost:8501`

---

## ☁️ Deploy บน Streamlit Cloud

1. Fork หรือ Clone repo นี้
2. ไปที่ [share.streamlit.io](https://share.streamlit.io)
3. เชื่อมต่อ GitHub account
4. เลือก repo → `scm_streamlit.py` → **Deploy**

---

## 📁 โครงสร้างไฟล์

```
├── scm_streamlit.py    # Streamlit App หลัก
├── scm_v2.json         # ข้อมูล CJ (pre-processed)
├── requirements.txt    # Python dependencies
└── README.md           # ไฟล์นี้
```

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — Web UI
- **Plotly** — Interactive Charts
- **Pandas** — Data Processing
- **JSON** — Pre-processed Data Storage

---

## 📊 ข้อมูลที่ใช้

| ไฟล์ต้นฉบับ | รายละเอียด |
|---|---|
| Combine_SaleOut.xlsx | ยอดขายรายวัน (512K rows) |
| Combine_Stock_CJ.xlsx | สต็อก DC/Store รายสัปดาห์ |
| Combine_Pro.xlsx | แผนโปรโมชั่น |
| Combine_Sale_In.xlsx | Purchase Orders |
| Product_Information.xlsx | ข้อมูลสินค้า Master |
| MOQ_LeadTime.xlsx | MOQ และ Lead Time |

> ข้อมูลถูก pre-process และบันทึกเป็น `scm_v2.json` แล้ว

---

## ⚠️ หมายเหตุ

- ข้อมูลใน `scm_v2.json` เป็นข้อมูลจริงจาก CJ — **อย่า push ขึ้น Public repo**
- แนะนำใช้ **Private repository** สำหรับข้อมูล production
