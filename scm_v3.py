"""
Supply Chain Management System - Streamlit App
Run: streamlit run scm_streamlit.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SCM Dashboard | CJ",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    .block-container { padding: 1rem 1.5rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 18px;
        border-left: 4px solid #0F4C81;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07);
        margin-bottom: 8px;
    }
    .page-title { font-size: 1.6rem; font-weight: 800; color: #0F172A; margin: 0; }
    .page-sub { color: #64748B; font-size: 0.8rem; margin-top: 2px; }
    .badge-critical { background:#FEE2E2; color:#DC2626; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }
    .badge-high { background:#FEF3C7; color:#D97706; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }
    .badge-medium { background:#FEF9C3; color:#CA8A04; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }
    .badge-low { background:#DCFCE7; color:#16A34A; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    .stSelectbox label, .stMultiSelect label { font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== COLORS ====================
C_PRIMARY  = "#0F4C81"
C_ACCENT   = "#E8562A"
C_SUCCESS  = "#1A9E6C"
C_WARNING  = "#F59E0B"
C_DANGER   = "#DC2626"
C_PURPLE   = "#7C3AED"
C_TEAL     = "#0D9488"
C_GRAY     = "#64748B"
PALETTE    = [C_PRIMARY, C_ACCENT, C_SUCCESS, C_WARNING, C_PURPLE, C_TEAL, C_DANGER,
              "#06B6D4", "#9333EA", "#16A34A", "#CA8A04", "#0EA5E9"]

# ==================== LOAD DATA ====================
@st.cache_data
def load_json_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_data():
    # ถ้ามีไฟล์ที่ upload ใน session → ใช้ตัวนั้น
    if st.session_state.get("uploaded_data") is not None:
        return st.session_state["uploaded_data"]
    # ไม่งั้นโหลดจาก local file
    json_path = os.path.join(os.path.dirname(__file__), "scm_v2.json")
    if os.path.exists(json_path):
        return load_json_file(json_path)
    return None

if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None

DATA = get_data()
if DATA is None:
    st.error("❌ ไม่พบไฟล์ scm_v2.json — กรุณา Upload ไฟล์ scm_v2.json ในหน้า '📤 Upload Data'")
    st.stop()
FO   = DATA.get("filter_options", {})

# ==================== HELPERS ====================
def fmt(n):
    if n is None: return "—"
    if n >= 1e6: return f"{n/1e6:.1f}M"
    if n >= 1e3: return f"{n/1e3:.1f}K"
    return f"{round(n):,}"

def fmtB(n):
    return f"฿{fmt(n)}" if n is not None else "—"

def fmtP(n):
    return f"{(n or 0):.1f}%"

def to_df(lst):
    return pd.DataFrame(lst) if lst else pd.DataFrame()

def apply_filter(lst, f):
    """Filter list of dicts by global filter dict"""
    if not lst:
        return []
    result = []
    for item in lst:
        if f.get("division") and f["division"] != "All":
            if (item.get("division") or "") != f["division"]:
                continue
        if f.get("category") and f["category"] != "All":
            if (item.get("cat") or "") != f["category"]:
                continue
        if f.get("supplier") and f["supplier"] != "All":
            if f["supplier"] not in (item.get("supplier") or ""):
                continue
        if f.get("brand") and f["brand"] != "All":
            if (item.get("brand") or "") != f["brand"]:
                continue
        if f.get("cj_id"):
            if f["cj_id"] not in (item.get("id") or ""):
                continue
        if f.get("desc_text"):
            if f["desc_text"].lower() not in (item.get("desc") or "").lower():
                continue
        result.append(item)
    return result

# ==================== GLOBAL FILTER (SIDEBAR) ====================
st.sidebar.markdown("## 🏭 SCM Dashboard")
st.sidebar.markdown(f"📅 ข้อมูล ณ **{DATA.get('latest_stock_date','')}**")
st.sidebar.markdown("---")

# Navigation
PAGES = {
    "🏠 Dashboard":             "dashboard",
    "📈 Sales Forecasting":     "sales",
    "📦 Inventory Management":  "inventory",
    "⚠️ OOS Analysis":          "oos",
    "🔍 OOS Reconcile":         "reconcile",
    "📅 Monthly Forecast M1-M4":"fc_monthly",
    "🎯 Promo Demand Forecast":  "fc_promo",
    "🏷️ Promotions":             "promotions",
    "📋 Supply Planning":        "supply",
    "📊 Reports":                "reports",
    "📤 Upload Data":            "upload",
}
selected_page = st.sidebar.radio("📂 เลือกโมดูล", list(PAGES.keys()), label_visibility="collapsed")
page = PAGES[selected_page]

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Global Filter")
st.sidebar.caption("ตัว Filter นี้ใช้กับทุกหน้า")

div_opts   = ["All"] + (FO.get("divisions", []))
cat_opts   = ["All"] + (FO.get("categories", []))
sup_opts   = ["All"] + (FO.get("suppliers", []))
brand_opts = ["All"] + (FO.get("brands", []))

f_div  = st.sidebar.selectbox("Division",  div_opts,  index=0)
f_cat  = st.sidebar.selectbox("Category",  cat_opts,  index=0)
f_sup  = st.sidebar.selectbox("Supplier",  sup_opts,  index=0)
f_brand= st.sidebar.selectbox("Brand",     brand_opts,index=0)
f_cj   = st.sidebar.text_input("CJ Code",   placeholder="เช่น 20021338")
f_desc = st.sidebar.text_input("Description",placeholder="ค้นหาชื่อสินค้า")

GF = {"division": f_div, "category": f_cat, "supplier": f_sup,
      "brand": f_brand, "cj_id": f_cj.strip(), "desc_text": f_desc.strip()}

active_filters = sum(1 for k, v in GF.items() if v and v != "All")
if active_filters:
    st.sidebar.success(f"🔵 Active filters: {active_filters}")

# ==================== PAGE: DASHBOARD ====================
if page == "dashboard":
    st.markdown('<p class="page-title">🏠 Dashboard Overview</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-sub">ข้อมูล ณ {DATA["latest_stock_date"]} · CJ Supply Chain Management</p>', unsafe_allow_html=True)
    st.markdown("---")

    ms   = to_df(DATA.get("monthly_sales", []))
    top  = to_df(apply_filter(DATA.get("top_skus", []), GF))
    oos  = to_df(apply_filter(DATA.get("oos_items", []), GF))
    pros = to_df(apply_filter(DATA.get("promotions", []), GF))

    cur_rev  = ms["amt"].iloc[-1]  if not ms.empty else 0
    prev_rev = ms["amt"].iloc[-2]  if len(ms) > 1 else cur_rev
    rev_chg  = (cur_rev - prev_rev) / prev_rev * 100 if prev_rev else 0
    cur_skus = int(ms["skus"].iloc[-1]) if not ms.empty else 0
    oos_cnt  = len(oos)
    crit_cnt = len(oos[oos["severity"].isin(["Critical","High"])]) if not oos.empty else 0
    act_pro  = len(pros[pros["status"] == "Active"]) if not pros.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Revenue (ล่าสุด)", fmtB(cur_rev), f"{rev_chg:+.1f}%")
    c2.metric("📦 Active SKUs", f"{cur_skus:,}", "เดือนล่าสุด")
    c3.metric("⚠️ OOS Items", f"{oos_cnt}", f"{crit_cnt} Critical/High")
    c4.metric("🎯 Active Promos", f"{act_pro}", "กำลังดำเนินการ")

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Monthly Revenue & Volume Trend")
        if not ms.empty:
            ms["period_short"] = ms["period"].str.slice(5) if "period" in ms.columns else ms.get("month", ms.index).astype(str).str.slice(5)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=ms["period_short"], y=ms.get("promo_qty", [0]*len(ms))/1000,
                                 name="Promo Qty(K)", marker_color="#FDE68A", offsetgroup=0), secondary_y=False)
            fig.add_trace(go.Bar(x=ms["period_short"], y=ms.get("normal_qty", [0]*len(ms))/1000,
                                 name="Normal Qty(K)", marker_color=C_TEAL, opacity=0.7, offsetgroup=0,
                                 base=ms.get("promo_qty", pd.Series([0]*len(ms)))/1000), secondary_y=False)
            fig.add_trace(go.Scatter(x=ms["period_short"], y=ms["amt"]/1e6,
                                     name="Revenue(฿M)", line=dict(color=C_PRIMARY, width=3),
                                     mode="lines+markers"), secondary_y=True)
            fig.update_layout(height=300, barmode="stack", legend=dict(orientation="h", y=-0.2),
                               margin=dict(t=10, b=0))
            fig.update_yaxes(title_text="Qty (K)", secondary_y=False)
            fig.update_yaxes(title_text="Revenue (฿M)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 DOH Distribution")
        doh = to_df(DATA.get("doh_distribution", []))
        if not doh.empty:
            fig = px.bar(doh, x="range", y="count", color="range",
                         color_discrete_sequence=[d.get("color", C_PRIMARY) for d in DATA["doh_distribution"]],
                         labels={"count": "SKU Count"}, height=300)
            fig.update_layout(showlegend=False, margin=dict(t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f"🏆 Top SKUs ({len(top)} items)")
        if not top.empty:
            st.dataframe(
                top[["id","desc","cat","division","qty","amt","promo_pct"]].head(15)
                  .rename(columns={"id":"CJ Code","desc":"Description","cat":"Category",
                                   "division":"Division","qty":"Qty","amt":"Revenue","promo_pct":"Promo%"}),
                use_container_width=True, height=300, hide_index=True
            )

    with col4:
        st.subheader("📊 Promo vs Normal Mix")
        if not ms.empty:
            fig = go.Figure()
            fig.add_bar(x=ms["period_short"], y=ms.get("promo_qty", [0]*len(ms)), name="Promo", marker_color=C_ACCENT)
            fig.add_bar(x=ms["period_short"], y=ms.get("normal_qty", [0]*len(ms)), name="Normal", marker_color=C_PRIMARY)
            fig.update_layout(barmode="stack", height=300, margin=dict(t=10, b=0),
                               legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: SALES FORECASTING ====================
elif page == "sales":
    st.markdown('<p class="page-title">📈 Sales Forecasting</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">AI Trend Analysis · พยากรณ์รายเดือน M1-M4 จากข้อมูล 8 เดือนล่าสุด</p>', unsafe_allow_html=True)
    st.markdown("---")

    fc_all = apply_filter(DATA.get("forecast", []), GF)
    ms     = to_df(DATA.get("monthly_sales", []))

    if not fc_all:
        st.warning("ไม่พบข้อมูล — ลองเปลี่ยน Filter ครับ")
    else:
        fc_df = to_df(fc_all)
        sku_options = [f"{r['id']} | {r['desc']}" for r in fc_all]
        col_sel, col_info = st.columns([1, 2])
        with col_sel:
            sel_label = st.selectbox("เลือก SKU", sku_options)
        sel_idx = sku_options.index(sel_label)
        sel = fc_all[sel_idx]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 M1 มี.ค.", fmt(sel.get("M1")))
        c2.metric("📅 M2 เม.ย.", fmt(sel.get("M2")))
        c3.metric("📅 M3 พ.ค.", fmt(sel.get("M3")))
        c4.metric("📅 M4 มิ.ย.", fmt(sel.get("M4")))

        hist = sel.get("history", [])
        hist_df = pd.DataFrame(hist)
        nm = ["2026-03", "2026-04", "2026-05", "2026-06"]
        fc_pts = pd.DataFrame({"month": nm, "forecast": [sel.get("M1"), sel.get("M2"), sel.get("M3"), sel.get("M4")]})

        fig = go.Figure()
        if not hist_df.empty:
            fig.add_trace(go.Scatter(x=hist_df["month"], y=hist_df["qty"], name="Actual",
                                     line=dict(color=C_PRIMARY, width=2.5), mode="lines+markers"))
        fig.add_trace(go.Scatter(x=fc_pts["month"], y=fc_pts["forecast"], name="Forecast",
                                 line=dict(color=C_ACCENT, width=2, dash="dash"),
                                 mode="lines+markers"))
        fig.add_vline(x="2026-02", line_dash="dot", line_color="#CBD5E1",
                      annotation_text="Now", annotation_position="top")
        fig.update_layout(title=f"{sel['id']}: {sel['desc']} | {sel['cat']}",
                          xaxis_title="Month", yaxis_title="Qty", height=320,
                          legend=dict(orientation="h", y=-0.2), margin=dict(t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Promo vs Normal Sales Mix")
        if not ms.empty:
            ms["p"] = ms.get("period", ms.get("month", pd.Series())).str.slice(5)
            fig2 = go.Figure()
            fig2.add_bar(x=ms["p"], y=ms.get("promo_qty", []), name="Promo", marker_color=C_ACCENT)
            fig2.add_bar(x=ms["p"], y=ms.get("normal_qty", []), name="Normal", marker_color=C_PRIMARY)
            fig2.update_layout(barmode="stack", height=240, margin=dict(t=10, b=0))
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader(f"📋 Forecast Summary ({len(fc_all)} SKUs)")
        fc_tbl = fc_df[["id","desc","cat","division","supplier","M1","M2","M3","M4"]].copy()
        fc_tbl["4M Total"] = fc_tbl[["M1","M2","M3","M4"]].sum(axis=1)
        st.dataframe(fc_tbl.rename(columns={"id":"CJ Code","desc":"Description","cat":"Category",
                                             "division":"Division","supplier":"Supplier"}),
                     use_container_width=True, height=350, hide_index=True)

# ==================== PAGE: INVENTORY ====================
elif page == "inventory":
    st.markdown('<p class="page-title">📦 Inventory Management</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-sub">ข้อมูล ณ {DATA["latest_stock_date"]}</p>', unsafe_allow_html=True)
    st.markdown("---")

    oos_all = apply_filter(DATA.get("oos_items", []), GF)
    oos_df  = to_df(oos_all)
    cat_all = apply_filter(DATA.get("cat_inventory", []), GF)
    cat_df  = to_df(cat_all) if cat_all else to_df(DATA.get("cat_inventory", []))

    low3  = len([i for i in oos_all if (i.get("doh_store") or 999) < 3])
    low7  = len([i for i in oos_all if 3 <= (i.get("doh_store") or 999) < 7])
    high30= len([i for i in oos_all if (i.get("doh_store") or 0) > 30])
    total_val = sum(r.get("total_val", 0) or 0 for r in cat_all)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Critical < 3d", f"{low3}", "ต้องสั่งด่วนมาก")
    c2.metric("🟠 Low 3–7d",     f"{low7}", "ควรสั่งเร็วๆ นี้")
    c3.metric("⬆️ High > 30d",   f"{high30}", "พิจารณาทำโปร")
    c4.metric("💰 Total Value",   fmtB(total_val), f"{len(cat_df)} Categories")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Avg DOH Store vs DC by Category")
        if not cat_df.empty:
            chart_df = cat_df.dropna(subset=["avg_doh_store"]).sort_values("avg_doh_store").head(15)
            fig = go.Figure()
            fig.add_bar(y=chart_df["cat"], x=chart_df["avg_doh_store"], name="DOH Store",
                        orientation="h", marker_color=C_PRIMARY)
            fig.add_bar(y=chart_df["cat"], x=chart_df["avg_doh_dc"], name="DOH DC",
                        orientation="h", marker_color=C_TEAL)
            fig.add_vline(x=7,  line_dash="dash", line_color=C_DANGER,  annotation_text="7d")
            fig.add_vline(x=14, line_dash="dash", line_color=C_WARNING, annotation_text="14d")
            fig.update_layout(barmode="group", height=380, xaxis_range=[0,60],
                               margin=dict(t=10, b=0), legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💰 Stock Value by Category (฿M)")
        if not cat_df.empty:
            val_df = cat_df.dropna(subset=["total_val"]).sort_values("total_val", ascending=False).head(15)
            fig = px.bar(val_df, x="total_val", y="cat", orientation="h",
                         labels={"total_val": "Value (฿)", "cat": "Category"},
                         color_discrete_sequence=[C_ACCENT], height=380)
            fig.update_traces(texttemplate="%{x:.2s}", textposition="outside")
            fig.update_layout(margin=dict(t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"📋 Category Inventory Detail ({len(cat_df)} rows)")
    if not cat_df.empty:
        disp = cat_df[["division","cat","skus","avg_doh_store","avg_doh_dc","store_qty","dc_qty","store_val","dc_val","total_val"]].copy()
        disp.columns = ["Division","Category","SKUs","Avg DOH Store","Avg DOH DC","Store Qty","DC Qty","Store Value","DC Value","Total Value"]
        for col in ["Store Value","DC Value","Total Value"]:
            disp[col] = disp[col].apply(lambda x: fmtB(x) if pd.notna(x) else "—")
        for col in ["Store Qty","DC Qty"]:
            disp[col] = disp[col].apply(lambda x: fmt(x) if pd.notna(x) else "—")
        st.dataframe(disp, use_container_width=True, height=400, hide_index=True)

# ==================== PAGE: OOS ANALYSIS ====================
elif page == "oos":
    st.markdown('<p class="page-title">⚠️ Out-of-Stock Analysis</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-sub">ข้อมูล ณ {DATA["latest_stock_date"]}</p>', unsafe_allow_html=True)
    st.markdown("---")

    oos_all = apply_filter(DATA.get("oos_items", []), GF)
    oos_df  = to_df(oos_all)

    col_sev, col_sort = st.columns([3, 1])
    with col_sev:
        sev_filter = st.radio("Severity", ["All","Critical","High","Medium","Low"], horizontal=True)
    with col_sort:
        sort_by = st.selectbox("Sort by", ["Severity","DOH Store (Low→High)","Lost Sales"])

    if not oos_df.empty and sev_filter != "All":
        oos_df = oos_df[oos_df["severity"] == sev_filter]

    if not oos_df.empty:
        ord_map = {"Critical":0,"High":1,"Medium":2,"Low":3}
        if sort_by == "Severity":
            oos_df["_ord"] = oos_df["severity"].map(ord_map)
            oos_df = oos_df.sort_values("_ord")
        elif sort_by == "DOH Store (Low→High)":
            oos_df = oos_df.sort_values("doh_store", na_position="last")
        elif sort_by == "Lost Sales":
            oos_df = oos_df.sort_values("lost", ascending=False)

    critical = len(oos_df[oos_df["severity"]=="Critical"]) if not oos_df.empty else 0
    high     = len(oos_df[oos_df["severity"]=="High"])     if not oos_df.empty else 0
    medium   = len(oos_df[oos_df["severity"]=="Medium"])   if not oos_df.empty else 0
    low      = len(oos_df[oos_df["severity"]=="Low"])      if not oos_df.empty else 0
    tot_lost = oos_df["lost"].sum() if not oos_df.empty else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("🔴 Critical", critical)
    c2.metric("🟠 High",     high)
    c3.metric("🟡 Medium",   medium)
    c4.metric("🟢 Low",      low)
    c5.metric("📉 Lost/Day", fmt(tot_lost))
    c6.metric("📋 Total",    len(oos_df))

    st.markdown("---")

    if not oos_df.empty:
        # Chart: OOS by category
        byCat = oos_df.groupby(["cat","severity"]).size().reset_index(name="count")
        if not byCat.empty:
            top15cats = oos_df["cat"].value_counts().head(14).index.tolist()
            byCat = byCat[byCat["cat"].isin(top15cats)]
            fig = px.bar(byCat, x="count", y="cat", color="severity", orientation="h",
                         color_discrete_map={"Critical":C_DANGER,"High":C_WARNING,"Medium":"#EAB308","Low":C_SUCCESS},
                         title="OOS by Category & Severity", height=320)
            fig.update_layout(margin=dict(t=40, b=0), legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"📋 OOS Item List ({len(oos_df)} items)")
        disp = oos_df[["id","desc","cat","division","supplier","brand","severity","cause",
                        "doh_store","doh_dc","dc1_oos","dc2_oos","dc4_oos","store_qty","dc_qty","lost"]].copy()
        disp.columns = ["CJ Code","Description","Category","Division","Supplier","Brand","Severity","Root Cause",
                         "DOH Store","DOH DC","DC1 OOS%","DC2 OOS%","DC4 OOS%","Store Qty","DC Qty","Lost/Day"]
        st.dataframe(disp, use_container_width=True, height=450, hide_index=True)
    else:
        st.info("ไม่พบข้อมูล OOS สำหรับ Filter ที่เลือก")

# ==================== PAGE: OOS RECONCILE ====================
elif page == "reconcile":
    st.markdown('<p class="page-title">🔍 OOS Reconcile & Root Cause Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">วิเคราะห์สาเหตุการ OOS และแนวทางแก้ไขแต่ละกรณี</p>', unsafe_allow_html=True)
    st.markdown("---")

    oos_all = apply_filter(DATA.get("oos_items", []), GF)
    oos_df  = to_df(oos_all)

    ACTS = {
        "Partial OOS (some SKU/Store)": {
            "root": "สต็อกกระจายไม่ทั่วถึง บาง SKU/Store ไม่มีสินค้า อาจเกิดจาก assortment ไม่ครบหรือ allocation ไม่สมดุล",
            "action": "ทบทวน store assortment plan · ปรับ allocation DC→Store · ตรวจ replenishment frequency",
            "prio": "Low",
        },
        "Low Store Stock (< 7 days)": {
            "root": "Store stock เหลือน้อย ต่ำกว่า 7 วัน อาจเกิดจากยอดขายสูงกว่าคาดหรือ replenishment ล่าช้า",
            "action": "เร่ง DC→Store replenishment · ตรวจ auto-replenishment trigger · เพิ่ม safety stock ที่ร้าน",
            "prio": "High",
        },
        "Critical Low Stock - No DC": {
            "root": "Store วิกฤต และ DC ไม่มีสต็อกสำรอง ความเสี่ยงสูงมากในการเกิด OOS เต็มรูปแบบ",
            "action": "ออก Emergency PO ทันที · ประสาน Buyer + Supplier · พิจารณาหาสินค้าทดแทน",
            "prio": "Critical",
        },
        "Critical Low Store Stock": {
            "root": "Store วิกฤต (< 3 วัน) แต่ DC ยังมีสต็อก ปัญหาอยู่ที่การ replenish DC→Store",
            "action": "Replenishment ฉุกเฉิน DC→Store · ตรวจระบบ auto-replenishment · แจ้ง Store Manager",
            "prio": "Critical",
        },
        "No Stock (DC+Store)": {
            "root": "ไม่มีสต็อกทั้ง DC และร้าน PO อาจยังไม่มาถึงหรือ lead time เกินกำหนด",
            "action": "Emergency PO · ติดต่อ supplier โดยตรง · ทำ substitution plan · แจ้ง buyer",
            "prio": "Critical",
        },
        "Store OOS - DC Has Stock": {
            "root": "DC มีสต็อกแต่ยังไม่กระจายลงร้าน อาจเป็นปัญหา logistics หรือ allocation delay",
            "action": "เร่ง DC→Store transfer · ตรวจ allocation system · ประสานทีม logistics",
            "prio": "High",
        },
        "DC OOS - Store Has Stock": {
            "root": "DC หมดสต็อก ร้านยังพอมีแต่จะหมดเร็ว ควรสั่งซื้อทันที",
            "action": "สั่งซื้อเพิ่ม · ตรวจ reorder point · ปรับ min stock level ที่ DC",
            "prio": "Medium",
        },
    }
    PRIO_COLOR = {"Critical": C_DANGER, "High": C_WARNING, "Medium": "#EAB308", "Low": C_SUCCESS}

    if oos_df.empty:
        st.warning("ไม่พบข้อมูล — ลองเปลี่ยน Filter ครับ")
    else:
        cause_grp = oos_df.groupby("cause").agg(count=("id","count"), lost=("lost","sum")).reset_index()
        cause_grp = cause_grp.sort_values("count", ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(cause_grp, values="count", names="cause",
                         title="OOS Cause Distribution", height=280,
                         color_discrete_sequence=PALETTE)
            fig.update_traces(textposition="inside", textinfo="percent")
            fig.update_layout(margin=dict(t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(cause_grp[cause_grp["lost"] > 0], x="lost", y="cause",
                          orientation="h", title="Est. Lost Sales by Cause (units/day)",
                          color_discrete_sequence=[C_DANGER], height=280)
            fig2.update_layout(margin=dict(t=40, b=0))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        for _, row in cause_grp.iterrows():
            cause = row["cause"]
            act   = ACTS.get(cause, {"root": "ตรวจสอบข้อมูล", "action": "ตรวจสอบข้อมูล", "prio": "Low"})
            prio_color = PRIO_COLOR.get(act["prio"], C_GRAY)
            with st.expander(f"**{cause}** — {row['count']} items · Lost: {fmt(row['lost'])}/day  [{act['prio']}]", expanded=(act["prio"]=="Critical")):
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown(f"**🔎 Root Cause**")
                    st.info(act["root"])
                with cc2:
                    st.markdown(f"**✅ แนวทางแก้ไข**")
                    st.success(act["action"])
                samples = oos_df[oos_df["cause"] == cause].head(5)
                if not samples.empty:
                    st.caption("ตัวอย่างสินค้า:")
                    st.dataframe(
                        samples[["id","desc","cat","doh_store","doh_dc","lost"]].rename(
                            columns={"id":"CJ Code","desc":"Description","cat":"Category",
                                     "doh_store":"DOH Store","doh_dc":"DOH DC","lost":"Lost/Day"}),
                        use_container_width=True, hide_index=True
                    )

# ==================== PAGE: MONTHLY FORECAST M1-M4 ====================
elif page == "fc_monthly":
    st.markdown('<p class="page-title">📅 Monthly Demand Forecast M1–M4</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">พยากรณ์ M1(มี.ค.) M2(เม.ย.) M3(พ.ค.) M4(มิ.ย.) 2026 ราย SKU</p>', unsafe_allow_html=True)
    st.markdown("---")

    fc_all = apply_filter(DATA.get("forecast", []), GF)
    if not fc_all:
        st.warning("ไม่พบข้อมูล")
    else:
        fc_df = to_df(fc_all)
        sku_opts = [f"{r['id']} | {r['desc']}" for r in fc_all]
        sel_label = st.selectbox("🔍 เลือก SKU เพื่อดู Chart", sku_opts)
        sel_idx = sku_opts.index(sel_label)
        sel = fc_all[sel_idx]

        c1, c2, c3, c4 = st.columns(4)
        last_hist = (sel.get("history") or [{}])[-1].get("qty", 0)
        m1_chg = (sel.get("M1", 0) - last_hist) / last_hist * 100 if last_hist else 0
        c1.metric("📅 M1 มี.ค. 2026", fmt(sel.get("M1")), f"{m1_chg:+.1f}%")
        c2.metric("📅 M2 เม.ย. 2026", fmt(sel.get("M2")))
        c3.metric("📅 M3 พ.ค. 2026", fmt(sel.get("M3")))
        c4.metric("📅 M4 มิ.ย. 2026", fmt(sel.get("M4")))

        hist  = pd.DataFrame(sel.get("history", []))
        nm    = ["2026-03","2026-04","2026-05","2026-06"]
        fc_pt = pd.DataFrame({"month": nm, "forecast": [sel.get("M1"), sel.get("M2"), sel.get("M3"), sel.get("M4")]})

        fig = go.Figure()
        if not hist.empty:
            fig.add_trace(go.Scatter(x=hist["month"], y=hist["qty"], name="Actual",
                                     line=dict(color=C_PRIMARY, width=2.5), mode="lines+markers",
                                     marker=dict(size=7)))
        fig.add_trace(go.Scatter(x=fc_pt["month"], y=fc_pt["forecast"], name="Forecast",
                                 line=dict(color=C_ACCENT, width=2, dash="dash"),
                                 mode="lines+markers", marker=dict(size=7, symbol="diamond")))
        fig.add_vline(x="2026-02", line_dash="dot", line_color="#CBD5E1",
                      annotation_text="Now", annotation_position="top right")
        fig.update_layout(
            title=f"{sel['id']}: {sel['desc']} · {sel['cat']} · {sel['division']}",
            xaxis_title="Month", yaxis_title="Qty",
            height=320, legend=dict(orientation="h", y=-0.2), margin=dict(t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"📋 Forecast Summary ({len(fc_df)} SKUs)")
        tbl = fc_df[["id","desc","cat","division","supplier","M1","M2","M3","M4"]].copy()
        tbl["4M Total"] = tbl[["M1","M2","M3","M4"]].sum(axis=1)
        tbl.columns = ["CJ Code","Description","Category","Division","Supplier","M1 มี.ค.","M2 เม.ย.","M3 พ.ค.","M4 มิ.ย.","4M Total"]
        st.dataframe(tbl, use_container_width=True, height=400, hide_index=True)

# ==================== PAGE: PROMO DEMAND FORECAST ====================
elif page == "fc_promo":
    st.markdown('<p class="page-title">🎯 Promo Demand Forecast รายSKU</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">พยากรณ์ยอดขายตามแผนโปรโมชั่น พร้อม Uplift Impact</p>', unsafe_allow_html=True)
    st.markdown("---")

    pfc_all = apply_filter(DATA.get("promo_forecast", []), GF)
    status_f = st.radio("Status", ["All","Active","Upcoming","Completed"], horizontal=True)
    if status_f != "All":
        pfc_all = [p for p in pfc_all if p.get("status") == status_f]
    pfc_df = to_df(pfc_all)

    total_fc   = sum(p.get("fc_qty", 0) for p in pfc_all)
    total_base = sum(p.get("base_qty", 0) for p in pfc_all)
    uplift_pct = (total_fc - total_base) / total_base * 100 if total_base else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎯 Promo SKUs",      len(pfc_all))
    c2.metric("📦 Forecast Qty",    fmt(total_fc))
    c3.metric("📊 Baseline Qty",    fmt(total_base))
    c4.metric("📈 Promo Uplift",    f"+{uplift_pct:.1f}%")

    if not pfc_df.empty:
        top15 = pfc_df.head(15)
        fig = go.Figure()
        fig.add_bar(x=top15["id"].str.slice(-6), y=top15["base_qty"], name="Baseline", marker_color=C_GRAY)
        fig.add_bar(x=top15["id"].str.slice(-6), y=top15["fc_qty"],   name="Promo Forecast", marker_color=C_ACCENT)
        fig.update_layout(barmode="group", title="Baseline vs Promo Forecast (Top 15)",
                          height=300, margin=dict(t=40, b=0), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"📋 Promo Demand List ({len(pfc_df)} items)")
        disp = pfc_df[["id","desc","division","cat","supplier","brand","buyer","type",
                        "normal_price","promo_price","disc_pct","period_days","start","end",
                        "base_qty","fc_qty","uplift","status"]].copy()
        disp.columns = ["CJ Code","Description","Division","Category","Supplier","Brand","Buyer","Type",
                         "ราคาปกติ","ราคาโปร","Discount%","วัน","เริ่ม","สิ้นสุด",
                         "Baseline","Forecast","Uplift×","Status"]
        st.dataframe(disp, use_container_width=True, height=420, hide_index=True)

# ==================== PAGE: PROMOTIONS ====================
elif page == "promotions":
    st.markdown('<p class="page-title">🏷️ Promotion Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">แผนโปรโมชั่นทั้งหมด</p>', unsafe_allow_html=True)
    st.markdown("---")

    pro_all = apply_filter(DATA.get("promotions", []), GF)
    status_f = st.radio("Status", ["All","Active","Upcoming","Completed"], horizontal=True)
    if status_f != "All":
        pro_all = [p for p in pro_all if p.get("status") == status_f]
    pro_df = to_df(pro_all)

    active   = sum(1 for p in pro_all if p.get("status") == "Active")
    upcoming = sum(1 for p in pro_all if p.get("status") == "Upcoming")
    compl    = sum(1 for p in pro_all if p.get("status") == "Completed")
    discs    = [p.get("disc_pct", 0) for p in pro_all if p.get("disc_pct", 0) > 0]
    avg_disc = sum(discs) / len(discs) if discs else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🟢 Active",    active)
    c2.metric("🔵 Upcoming", upcoming)
    c3.metric("⚪ Completed", compl)
    c4.metric("📊 Avg Disc",  f"{avg_disc:.1f}%")

    if not pro_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            by_type = pro_df.groupby("type").size().reset_index(name="count")
            fig = px.pie(by_type, values="count", names="type",
                         title="Promotion Type Mix", height=280,
                         color_discrete_sequence=PALETTE)
            fig.update_layout(margin=dict(t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            buckets = {"0-5%": 0, "5-10%": 0, "10-15%": 0, "15-20%": 0, ">20%": 0}
            for p in pro_all:
                d = p.get("disc_pct", 0) or 0
                if d <= 5:   buckets["0-5%"] += 1
                elif d <= 10: buckets["5-10%"] += 1
                elif d <= 15: buckets["10-15%"] += 1
                elif d <= 20: buckets["15-20%"] += 1
                else:         buckets[">20%"] += 1
            disc_df = pd.DataFrame({"range": list(buckets.keys()), "count": list(buckets.values())})
            fig2 = px.bar(disc_df, x="range", y="count", title="Discount Distribution",
                          color_discrete_sequence=[C_ACCENT], height=280)
            fig2.update_layout(margin=dict(t=40, b=0))
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader(f"📋 Promotion List ({len(pro_df)} items)")
        disp = pro_df[["id","desc","division","cat","supplier","brand","buyer","type",
                        "normal_price","promo_price","disc_pct","period_days","start","end","status"]].copy()
        disp.columns = ["CJ Code","Description","Division","Category","Supplier","Brand","Buyer","Type",
                         "ราคาปกติ","ราคาโปร","Discount%","วัน","เริ่ม","สิ้นสุด","Status"]
        st.dataframe(disp, use_container_width=True, height=420, hide_index=True)

# ==================== PAGE: SUPPLY PLANNING ====================
elif page == "supply":
    st.markdown('<p class="page-title">📋 Supply Planning & PO Management</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Purchase Order tracking & Fill Rate Analysis</p>', unsafe_allow_html=True)
    st.markdown("---")

    po_all  = apply_filter(DATA.get("po_detail", []), GF)
    po_sum  = DATA.get("po_summary", [])
    po_df   = to_df(po_all)

    year_f = st.radio("Year", ["All","2025","2026"], horizontal=True)
    if year_f != "All":
        po_all = [p for p in po_all if str(p.get("year","")) == year_f]
        po_df  = to_df(po_all)

    by_status = {}
    for r in po_sum:
        s = r.get("Delivery_Status", "Unknown")
        if s not in by_status:
            by_status[s] = {"orders": 0, "qty": 0, "actual": 0}
        by_status[s]["orders"] += r.get("orders", 0)
        by_status[s]["qty"]    += r.get("qty", 0) or 0
        by_status[s]["actual"] += r.get("actual", 0) or 0

    cols = st.columns(len(by_status) or 1)
    for i, (s, v) in enumerate(by_status.items()):
        fr = f"{v['actual']/v['qty']*100:.1f}%" if v["qty"] else "—"
        cols[i].metric(f"{'✅' if s=='Done' else '❌' if s=='Cancel' else '📦'} {s}",
                       f"{v['orders']} POs", f"Fill Rate: {fr}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly PO Count by Status")
        monthly_po = {}
        for r in po_sum:
            k = f"{r['Year']}-{str(r['Month']).zfill(2)}"
            if k not in monthly_po:
                monthly_po[k] = {"period": k, "Done": 0, "Cancel": 0, "MOQ": 0, "Hold": 0}
            monthly_po[k][r.get("Delivery_Status", "Done")] = monthly_po[k].get(r.get("Delivery_Status","Done"), 0) + r.get("orders", 0)
        po_chart = pd.DataFrame(sorted(monthly_po.values(), key=lambda x: x["period"]))
        if not po_chart.empty:
            po_chart["p"] = po_chart["period"].str.slice(5)
            fig = go.Figure()
            for st_name, clr in [("Done",C_SUCCESS),("Cancel",C_DANGER),("MOQ",C_WARNING),("Hold",C_GRAY)]:
                if st_name in po_chart.columns:
                    fig.add_bar(x=po_chart["p"], y=po_chart[st_name], name=st_name, marker_color=clr)
            fig.update_layout(barmode="stack", height=280, margin=dict(t=10, b=0),
                               legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly Fill Rate")
        fill = {}
        for r in po_sum:
            if r.get("Delivery_Status") == "Done":
                k = f"{r['Year']}-{str(r['Month']).zfill(2)}"
                if k not in fill:
                    fill[k] = {"period": k, "order": 0, "actual": 0}
                fill[k]["order"]  += r.get("qty", 0) or 0
                fill[k]["actual"] += r.get("actual", 0) or 0
        fill_df = pd.DataFrame(sorted(fill.values(), key=lambda x: x["period"]))
        if not fill_df.empty:
            fill_df["rate"] = (fill_df["actual"] / fill_df["order"].replace(0, np.nan) * 100).fillna(0)
            fill_df["p"] = fill_df["period"].str.slice(5)
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(go.Bar(x=fill_df["p"], y=fill_df["actual"]/1000, name="Actual Qty(K)",
                                  marker_color=C_TEAL, opacity=0.7), secondary_y=False)
            fig2.add_trace(go.Scatter(x=fill_df["p"], y=fill_df["rate"], name="Fill Rate%",
                                      line=dict(color=C_PRIMARY, width=2.5)), secondary_y=True)
            fig2.add_hline(y=95, line_dash="dash", line_color=C_SUCCESS,
                           annotation_text="95% target", secondary_y=True)
            fig2.update_layout(height=280, margin=dict(t=10, b=0), legend=dict(orientation="h", y=-0.2))
            fig2.update_yaxes(title_text="Qty (K)",    secondary_y=False)
            fig2.update_yaxes(title_text="Fill Rate%", secondary_y=True, range=[50, 110])
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader(f"📋 PO Detail ({len(po_df)} records)")
    if not po_df.empty:
        disp = po_df[["po","date","id","desc","division","cat","supplier","order_qty","actual_qty","status","year","month"]].copy()
        disp.columns = ["PO Number","PO Date","CJ Code","Description","Division","Category","Supplier",
                         "Order Qty","Actual Qty","Status","Year","Month"]
        st.dataframe(disp, use_container_width=True, height=420, hide_index=True)

# ==================== PAGE: REPORTS ====================
elif page == "reports":
    st.markdown('<p class="page-title">📊 Reports & Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">สรุปรายงานข้อมูลทั้งหมด</p>', unsafe_allow_html=True)
    st.markdown("---")

    report_type = st.selectbox("📄 เลือกประเภทรายงาน", [
        "📈 Sales Summary", "📦 Inventory Report", "🎯 Promotion Report", "📋 Supply Report"
    ])

    if report_type == "📈 Sales Summary":
        top  = to_df(apply_filter(DATA.get("top_skus", []), GF))
        ms   = to_df(DATA.get("monthly_sales", []))

        total_rev  = top["amt"].sum() if not top.empty else 0
        total_qty  = top["qty"].sum() if not top.empty else 0
        avg_monthly= ms["amt"].mean() if not ms.empty else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Revenue",      fmtB(total_rev))
        c2.metric("📦 Total Units Sold",   fmt(total_qty))
        c3.metric("📅 Avg Monthly Rev",    fmtB(avg_monthly))

        col1, col2 = st.columns(2)
        with col1:
            if not top.empty:
                cat_rev = top.groupby("cat")["amt"].sum().reset_index().sort_values("amt", ascending=False).head(12)
                fig = px.bar(cat_rev, x="amt", y="cat", orientation="h",
                             title="Revenue by Category", labels={"amt":"Revenue (฿)","cat":"Category"},
                             color_discrete_sequence=[C_PRIMARY], height=360)
                fig.update_layout(margin=dict(t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            if not ms.empty:
                ms["p"] = ms.get("period", ms.get("month","")).str.slice(5)
                fig2 = px.area(ms, x="p", y="amt", title="Monthly Revenue Trend",
                               labels={"amt":"Revenue (฿)","p":"Month"},
                               color_discrete_sequence=[C_PRIMARY], height=360)
                fig2.update_layout(margin=dict(t=40, b=0))
                st.plotly_chart(fig2, use_container_width=True)

        if not top.empty:
            st.subheader(f"Top SKUs ({len(top)} items)")
            disp = top[["id","desc","cat","division","supplier","qty","amt","promo_pct"]].copy()
            disp.columns = ["CJ Code","Description","Category","Division","Supplier","Total Qty","Total Revenue","Promo%"]
            disp["Total Revenue"] = disp["Total Revenue"].apply(fmtB)
            disp["Total Qty"]     = disp["Total Qty"].apply(fmt)
            st.dataframe(disp, use_container_width=True, height=400, hide_index=True)

            csv = top.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 Download Sales Report (CSV)", csv,
                               "sales_report.csv", "text/csv")

    elif report_type == "📦 Inventory Report":
        oos = to_df(apply_filter(DATA.get("oos_items", []), GF))
        cat = to_df(apply_filter(DATA.get("cat_inventory", []), GF))

        low7   = len(oos[oos["doh_store"] < 7])    if not oos.empty and "doh_store" in oos.columns else 0
        high30 = len(oos[oos["doh_store"] > 30])   if not oos.empty and "doh_store" in oos.columns else 0
        lost   = oos["lost"].sum()                  if not oos.empty else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("⚠️ Low Stock (<7d)",    low7,        "ต้องสั่งซื้อด่วน")
        c2.metric("📦 High Stock (>30d)", high30,       "พิจารณาลด")
        c3.metric("📉 Est. Lost/Day",     fmt(lost))

        if not oos.empty:
            disp = oos[["id","desc","cat","division","supplier","severity","doh_store","doh_dc","store_qty","dc_qty","lost"]].copy()
            disp.columns = ["CJ Code","Description","Category","Division","Supplier","Status","DOH Store","DOH DC","Store Qty","DC Qty","Lost/Day"]
            st.dataframe(disp, use_container_width=True, height=440, hide_index=True)
            csv = oos.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 Download Inventory Report (CSV)", csv, "inventory_report.csv", "text/csv")

    elif report_type == "🎯 Promotion Report":
        pros = to_df(apply_filter(DATA.get("promotions", []), GF))
        if not pros.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📋 Total",   len(pros))
            c2.metric("🟢 Active",  len(pros[pros["status"]=="Active"]))
            c3.metric("🔵 Upcoming",len(pros[pros["status"]=="Upcoming"]))
            disc = pros[pros["disc_pct"] > 0]["disc_pct"].mean()
            c4.metric("📊 Avg Disc", f"{disc:.1f}%")

            disp = pros[["id","desc","division","cat","supplier","buyer","type","disc_pct","start","end","status"]].copy()
            disp.columns = ["CJ Code","Description","Division","Category","Supplier","Buyer","Type","Discount%","Start","End","Status"]
            st.dataframe(disp, use_container_width=True, height=440, hide_index=True)
            csv = pros.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 Download Promotion Report (CSV)", csv, "promo_report.csv", "text/csv")

    elif report_type == "📋 Supply Report":
        po_sum = DATA.get("po_summary", [])
        by_s = {}
        for r in po_sum:
            s = r.get("Delivery_Status","Unknown")
            if s not in by_s: by_s[s] = {"orders":0,"qty":0,"actual":0}
            by_s[s]["orders"] += r.get("orders",0)
            by_s[s]["qty"]    += r.get("qty",0) or 0
            by_s[s]["actual"] += r.get("actual",0) or 0

        cols = st.columns(len(by_s) or 1)
        for i, (s, v) in enumerate(by_s.items()):
            fr = f"{v['actual']/v['qty']*100:.1f}%" if v["qty"] else "—"
            cols[i].metric(s, f"{v['orders']} POs", f"Fill Rate: {fr}")

        po_detail = to_df(apply_filter(DATA.get("po_detail", []), GF))
        if not po_detail.empty:
            disp = po_detail.rename(columns={"po":"PO","date":"Date","id":"CJ Code","desc":"Description",
                                              "division":"Division","cat":"Category","supplier":"Supplier",
                                              "order_qty":"Order Qty","actual_qty":"Actual Qty",
                                              "status":"Status","year":"Year","month":"Month"})
            st.dataframe(disp, use_container_width=True, height=400, hide_index=True)
            csv = po_detail.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 Download Supply Report (CSV)", csv, "supply_report.csv", "text/csv")

# ==================== PAGE: UPLOAD DATA ====================
elif page == "upload":
    st.markdown('<p class="page-title">📤 Upload Data</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">อัปโหลดข้อมูลเพื่ออัปเดตระบบ</p>', unsafe_allow_html=True)
    st.markdown("---")

    # ===== SECTION 1: Upload scm_v2.json (หลัก) =====
    st.subheader("🔄 อัปเดตข้อมูลหลัก (scm_v2.json)")
    st.info("📌 Upload ไฟล์ **scm_v2.json** เพื่อรีเฟรชข้อมูลทั้งหมดในระบบ")

    col_up, col_info = st.columns([2, 1])
    with col_up:
        json_file = st.file_uploader(
            "เลือกไฟล์ scm_v2.json",
            type=["json"],
            key="up_json",
            help="ไฟล์ที่ได้จากการ process ข้อมูลใหม่"
        )

    with col_info:
        if st.session_state.get("uploaded_data") is not None:
            udate = st.session_state.get("upload_time", "ไม่ทราบ")
            st.success(f"✅ ใช้ข้อมูลที่ Upload\nเวลา: {udate}")
            if st.button("🗑️ ล้างข้อมูลที่ Upload (ใช้ local file)"):
                st.session_state["uploaded_data"] = None
                st.session_state["upload_time"]   = None
                load_json_file.clear()
                st.success("✅ ล้างแล้ว กำลัง Reload...")
                st.rerun()
        else:
            json_path = os.path.join(os.path.dirname(__file__), "scm_v2.json")
            if os.path.exists(json_path):
                st.info("📂 ใช้ไฟล์ local\nscm_v2.json")
            else:
                st.warning("⚠️ ไม่พบ local file\nกรุณา Upload")

    if json_file is not None:
        try:
            raw_bytes = json_file.read()
            new_data  = json.loads(raw_bytes.decode("utf-8"))
            # Validate
            required_keys = ["monthly_sales", "oos_items", "promotions", "forecast"]
            missing = [k for k in required_keys if k not in new_data]
            if missing:
                st.error(f"❌ ไฟล์ไม่ครบถ้วน ขาด keys: {missing}")
            else:
                st.session_state["uploaded_data"] = new_data
                from datetime import datetime
                st.session_state["upload_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                load_json_file.clear()
                latest = new_data.get("latest_stock_date", "ไม่ทราบ")
                oos_cnt = len(new_data.get("oos_items", []))
                pro_cnt = len(new_data.get("promotions", []))
                st.success(f"""✅ โหลดสำเร็จ!
- 📅 ข้อมูล ณ: **{latest}**
- ⚠️ OOS Items: **{oos_cnt:,}**
- 🎯 Promotions: **{pro_cnt:,}**
                """)
                st.balloons()
                if st.button("🚀 ไปหน้า Dashboard"):
                    st.rerun()
        except json.JSONDecodeError:
            st.error("❌ ไฟล์ไม่ใช่ JSON ที่ถูกต้อง")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.markdown("---")

    # ===== SECTION 2: Refresh Button =====
    st.subheader("🔁 Refresh ข้อมูล")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("🔄 Refresh หน้าปัจจุบัน", use_container_width=True):
            st.rerun()
    with col_r2:
        if st.button("🗂️ Clear Cache & Reload", use_container_width=True):
            load_json_file.clear()
            st.session_state["uploaded_data"] = None
            st.success("✅ Cache cleared! กำลัง reload...")
            st.rerun()
    with col_r3:
        cur_date = DATA.get("latest_stock_date", "—")
        st.metric("📅 ข้อมูลปัจจุบัน ณ", cur_date)

    st.markdown("---")

    # ===== SECTION 3: Raw file upload tabs =====
    st.subheader("📋 ดูตัวอย่าง / Template ข้อมูลดิบ")
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Data","📦 Stock Data","🎯 Promotion","📋 Purchase Orders"])

    TEMPLATES = {
        "sales":  "date,product_id,product_name,sales_qty,unit_price,total_amount,category,channel\n2025-01-01,SKU001,นมUHT 1L,1200,45.00,54000,Dairy,CJ",
        "stock":  "date,product_id,beginning_stock,goods_received,sales_out,ending_stock,unit_cost,stock_value\n2025-01-01,SKU001,5000,0,1200,3800,35.00,133000",
        "promo":  "promotion_id,product_id,promotion_name,start_date,end_date,discount_type,discount_value,status\nPROMO001,SKU001,New Year Sale,2025-01-01,2025-01-07,Percentage,20,Completed",
        "po":     "po_id,po_date,product_id,supplier_id,order_qty,unit_cost,expected_delivery,status\nPO2025001,2025-01-05,SKU001,SUP001,2000,35.00,2025-01-19,Received",
    }
    REQUIRED = {
        "sales": "date, product_id, sales_qty",
        "stock": "date, product_id, ending_stock",
        "promo": "promotion_id, product_id, start_date, end_date",
        "po":    "po_id, product_id, order_qty",
    }

    for tab_obj, key, label in [
        (tab1, "sales", "Sales"),
        (tab2, "stock", "Stock"),
        (tab3, "promo", "Promotion"),
        (tab4, "po",    "Purchase Orders"),
    ]:
        with tab_obj:
            st.markdown(f"**Required columns:** `{REQUIRED[key]}`")
            file = st.file_uploader(f"เลือกไฟล์ {label} (CSV/Excel)", type=["csv","xlsx","xls"], key=f"up_{key}")
            if file:
                try:
                    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                    st.success(f"✅ โหลดสำเร็จ {len(df):,} records · {len(df.columns)} columns")
                    st.dataframe(df.head(10), use_container_width=True)
                    st.info("💡 ส่งไฟล์นี้ให้ Claude เพื่อ re-process เป็น scm_v2.json แล้ว Upload ใหม่ด้านบนครับ")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            st.markdown("---")
            st.markdown("**📥 Template:**")
            st.code(TEMPLATES[key], language="text")
            st.download_button(f"📥 Download {label} Template",
                               TEMPLATES[key], f"template_{key}.csv", "text/csv",
                               key=f"dl_{key}")

# ==================== FOOTER ====================
st.sidebar.markdown("---")
# Quick Refresh in sidebar
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    load_json_file.clear()
    st.rerun()
st.sidebar.caption(f"📅 ข้อมูล ณ {DATA.get('latest_stock_date','—')}")
st.sidebar.markdown(
    "<div style='text-align:center;color:#64748B;font-size:11px'>"
    "🏭 SCM Dashboard · CJ<br>Powered by Streamlit + Plotly"
    "</div>",
    unsafe_allow_html=True
)
