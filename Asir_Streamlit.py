<<<<<<< HEAD
import streamlit as st
import pandas as pd
import pickle
from datetime import timedelta, date
import plotly.graph_objects as go

# =========================
# إعداد الصفحة والهوية البصرية
# =========================
st.set_page_config(
    page_title="منصة التنبؤ بعدد البلاغات - أمانة منطقة عسير",
    layout="wide"
)

# تنسيق عام (يمين لليسار + ألوان وهوية مختلفة)
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; font-family: 'Arial', sans-serif; }
    /* شريط علوي */
    .header-bar {
        background: linear-gradient(90deg, #0b6e4f 0%, #118a7e 100%);
        color: white; padding: 18px 22px; border-radius: 12px; margin-bottom: 18px;
    }
    .header-title { font-size: 28px; font-weight: 700; margin: 0; }
    .header-sub { font-size: 16px; opacity: 0.95; margin-top: 6px; }

    /* بطاقات مؤشرات */
    .kpi-box {
        border: 1px solid #e6e6e6; border-radius: 14px; padding: 18px;
        background: #fafafa;
    }
    .kpi-title { font-size: 16px; color: #666; margin-bottom: 8px; }
    .kpi-value { font-size: 30px; font-weight: 700; color: #0b6e4f; }

    /* زر التنفيذ */
    div.stButton > button {
        width: 100%;
        background: #0b6e4f;
        color: #fff;
        border-radius: 12px;
        height: 50px;
        font-weight: 700;
        border: 0;
        font-size: 18px;
    }
    div.stButton > button:hover { background: #118a7e; }

    /* عناوين فرعية */
    .section-title { font-size: 20px; font-weight: 700; margin: 12px 0 6px 0; color: #0b6e4f; }

    /* تكبير حجم النص في selectbox و radio */
    .stSelectbox label, .stRadio label, .stDateInput label {
        font-size: 18px !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# شريط علوي بهوية عسير
with st.container():
    cols = st.columns([1, 5, 1])
    with cols[0]:
        st.image("Asir_Lugo.jpg", width=160)  # شعار أكبر
    with cols[1]:
        st.markdown("""
            <div class="header-bar">
                <div class="header-title">منصة التنبؤ بعدد البلاغات - أمانة منطقة عسير</div>
                <div class="header-sub">أداة داخلية لدعم التخطيط التشغيلي وتوزيع الموارد بناءً على التوقعات اليومية، مع تجميع شهري وسنوي.</div>
            </div>
        """, unsafe_allow_html=True)

# وصف موجز
with st.expander("حول المنصة"):
    st.write("""
    تم تطوير هذه المنصة لصالح **أمانة منطقة عسير** بهدف الاستفادة من البيانات التاريخية للبلاغات
    لتوقع حجم العمل المستقبلي على مستوى البلدية. تعتمد المنصة نموذجًا مدرّبًا على بيانات **يومية**،
    وتقوم باشتقاق التوقعات **الشهرية** و**السنوية** بجمع القيم اليومية للفترة المختارة.
    """)

# =========================
# تحميل النموذج وخريطة البلديات
# =========================
with open('model_daily.pkl', 'rb') as f:
    model, بلدية_الخريطة = pickle.load(f)

بلديات_قائمة = sorted(بلدية_الخريطة.keys())

# =========================
# واجهة الإدخال
# =========================
st.markdown('<div class="section-title">إعدادات التنبؤ</div>', unsafe_allow_html=True)
c1, c2, c3, _ = st.columns([3, 2, 2, 3])

with c1:
    البلدية = st.selectbox("البلدية", بلديات_قائمة, index=0)

with c2:
    التاريخ = st.date_input("تاريخ البداية", min_value=date.today())

with c3:
    الفترة_عربي = st.radio("النطاق الزمني", ["يومي", "شهري", "سنوي"], horizontal=True)
    الفترة_map = {"يومي": "day", "شهري": "month", "سنوي": "year"}
    الفترة = الفترة_map[الفترة_عربي]

st.write("")  # فراغ بسيط
run = st.button("تنفيذ التنبؤ")

# =========================
# دوال مساعدة
# =========================
def staffing_recommendation(total):
    if total < 50:
        return "فريق صغير (2 - 3 أفراد)"
    elif total < 200:
        return "فريق متوسط (4 - 6 أفراد)"
    else:
        return "فريق كبير (7 أفراد أو أكثر)"

def make_dates(start_d, period):
    if period == "day":
        return [start_d]
    elif period == "month":
        return [start_d + timedelta(days=i) for i in range(30)]
    else:
        return [start_d + timedelta(days=i) for i in range(365)]

# =========================
# تنفيذ التنبؤ + عرض النتائج
# =========================
if run:
    try:
        البلدية_كود = بلدية_الخريطة[البلدية]
        dates = make_dates(التاريخ, الفترة)

        daily_predictions = []
        for d in dates:
            X_new = pd.DataFrame([[البلدية_كود, d.year, d.month, d.day]],
                                 columns=['البلدية_كود', 'السنة', 'الشهر', 'اليوم'])
            pred = float(model.predict(X_new)[0])
            daily_predictions.append((d, pred))

        total_prediction = int(round(sum(p for _, p in daily_predictions)))
        rec = staffing_recommendation(total_prediction)

        # مؤشرات
        k1, k2, k3 = st.columns([2, 2, 2])
        with k1:
            st.markdown('<div class="kpi-box"><div class="kpi-title">إجمالي التوقع للفترة</div>'
                        f'<div class="kpi-value">{total_prediction}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="kpi-box"><div class="kpi-title">نوع الفترة</div>'
                        f'<div class="kpi-value">{الفترة_عربي}</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown('<div class="kpi-box"><div class="kpi-title">توصية الكادر</div>'
                        f'<div class="kpi-value">{rec}</div></div>', unsafe_allow_html=True)

        # تبويبات
        tabs = st.tabs(["المخطط الزمني", "تفاصيل يومية"])

        with tabs[0]:
            if الفترة in ["month", "year"]:
                df_plot = pd.DataFrame(daily_predictions, columns=["التاريخ", "التوقع"])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_plot["التاريخ"], y=df_plot["التوقع"],
                    mode="lines",
                    fill="tozeroy",
                    name="التوقع اليومي"
                ))
                fig.update_layout(
                    title="منحنى التوقع اليومي خلال الفترة",
                    xaxis_title="التاريخ",
                    yaxis_title="عدد البلاغات",
                    font=dict(family="Arial", size=16),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=50, b=20),
                    plot_bgcolor="#ffffff",
                    paper_bgcolor="#ffffff"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("النطاق اليومي لا يعرض مخططًا زمنياً. استخدم تبويب التفاصيل للاطلاع على القيمة اليومية.")

        with tabs[1]:
            df_details = pd.DataFrame(daily_predictions, columns=["التاريخ", "التوقع"])
            df_details["التوقع"] = df_details["التوقع"].round(2)
            st.dataframe(df_details, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"حدث خطأ غير متوقع: {e}")
=======
import streamlit as st
import pandas as pd
import pickle
from datetime import timedelta, date
import plotly.graph_objects as go

# =========================
# إعداد الصفحة والهوية البصرية
# =========================
st.set_page_config(
    page_title="منصة التنبؤ بعدد البلاغات - أمانة منطقة عسير",
    layout="wide"
)

# تنسيق عام (يمين لليسار + ألوان وهوية مختلفة)
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; font-family: 'Arial', sans-serif; }
    /* شريط علوي */
    .header-bar {
        background: linear-gradient(90deg, #0b6e4f 0%, #118a7e 100%);
        color: white; padding: 18px 22px; border-radius: 12px; margin-bottom: 18px;
    }
    .header-title { font-size: 28px; font-weight: 700; margin: 0; }
    .header-sub { font-size: 16px; opacity: 0.95; margin-top: 6px; }

    /* بطاقات مؤشرات */
    .kpi-box {
        border: 1px solid #e6e6e6; border-radius: 14px; padding: 18px;
        background: #fafafa;
    }
    .kpi-title { font-size: 16px; color: #666; margin-bottom: 8px; }
    .kpi-value { font-size: 30px; font-weight: 700; color: #0b6e4f; }

    /* زر التنفيذ */
    div.stButton > button {
        width: 100%;
        background: #0b6e4f;
        color: #fff;
        border-radius: 12px;
        height: 50px;
        font-weight: 700;
        border: 0;
        font-size: 18px;
    }
    div.stButton > button:hover { background: #118a7e; }

    /* عناوين فرعية */
    .section-title { font-size: 20px; font-weight: 700; margin: 12px 0 6px 0; color: #0b6e4f; }

    /* تكبير حجم النص في selectbox و radio */
    .stSelectbox label, .stRadio label, .stDateInput label {
        font-size: 18px !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# شريط علوي بهوية عسير
with st.container():
    cols = st.columns([1, 5, 1])
    with cols[0]:
        st.image("Asir_Lugo.jpg", width=160)  # شعار أكبر
    with cols[1]:
        st.markdown("""
            <div class="header-bar">
                <div class="header-title">منصة التنبؤ بعدد البلاغات - أمانة منطقة عسير</div>
                <div class="header-sub">أداة داخلية لدعم التخطيط التشغيلي وتوزيع الموارد بناءً على التوقعات اليومية، مع تجميع شهري وسنوي.</div>
            </div>
        """, unsafe_allow_html=True)

# وصف موجز
with st.expander("حول المنصة"):
    st.write("""
    تم تطوير هذه المنصة لصالح **أمانة منطقة عسير** بهدف الاستفادة من البيانات التاريخية للبلاغات
    لتوقع حجم العمل المستقبلي على مستوى البلدية. تعتمد المنصة نموذجًا مدرّبًا على بيانات **يومية**،
    وتقوم باشتقاق التوقعات **الشهرية** و**السنوية** بجمع القيم اليومية للفترة المختارة.
    """)

# =========================
# تحميل النموذج وخريطة البلديات
# =========================
with open('model_daily.pkl', 'rb') as f:
    model, بلدية_الخريطة = pickle.load(f)

بلديات_قائمة = sorted(بلدية_الخريطة.keys())

# =========================
# واجهة الإدخال
# =========================
st.markdown('<div class="section-title">إعدادات التنبؤ</div>', unsafe_allow_html=True)
c1, c2, c3, _ = st.columns([3, 2, 2, 3])

with c1:
    البلدية = st.selectbox("البلدية", بلديات_قائمة, index=0)

with c2:
    التاريخ = st.date_input("تاريخ البداية", min_value=date.today())

with c3:
    الفترة_عربي = st.radio("النطاق الزمني", ["يومي", "شهري", "سنوي"], horizontal=True)
    الفترة_map = {"يومي": "day", "شهري": "month", "سنوي": "year"}
    الفترة = الفترة_map[الفترة_عربي]

st.write("")  # فراغ بسيط
run = st.button("تنفيذ التنبؤ")

# =========================
# دوال مساعدة
# =========================
def staffing_recommendation(total):
    if total < 50:
        return "فريق صغير (2 - 3 أفراد)"
    elif total < 200:
        return "فريق متوسط (4 - 6 أفراد)"
    else:
        return "فريق كبير (7 أفراد أو أكثر)"

def make_dates(start_d, period):
    if period == "day":
        return [start_d]
    elif period == "month":
        return [start_d + timedelta(days=i) for i in range(30)]
    else:
        return [start_d + timedelta(days=i) for i in range(365)]

# =========================
# تنفيذ التنبؤ + عرض النتائج
# =========================
if run:
    try:
        البلدية_كود = بلدية_الخريطة[البلدية]
        dates = make_dates(التاريخ, الفترة)

        daily_predictions = []
        for d in dates:
            X_new = pd.DataFrame([[البلدية_كود, d.year, d.month, d.day]],
                                 columns=['البلدية_كود', 'السنة', 'الشهر', 'اليوم'])
            pred = float(model.predict(X_new)[0])
            daily_predictions.append((d, pred))

        total_prediction = int(round(sum(p for _, p in daily_predictions)))
        rec = staffing_recommendation(total_prediction)

        # مؤشرات
        k1, k2, k3 = st.columns([2, 2, 2])
        with k1:
            st.markdown('<div class="kpi-box"><div class="kpi-title">إجمالي التوقع للفترة</div>'
                        f'<div class="kpi-value">{total_prediction}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="kpi-box"><div class="kpi-title">نوع الفترة</div>'
                        f'<div class="kpi-value">{الفترة_عربي}</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown('<div class="kpi-box"><div class="kpi-title">توصية الكادر</div>'
                        f'<div class="kpi-value">{rec}</div></div>', unsafe_allow_html=True)

        # تبويبات
        tabs = st.tabs(["المخطط الزمني", "تفاصيل يومية"])

        with tabs[0]:
            if الفترة in ["month", "year"]:
                df_plot = pd.DataFrame(daily_predictions, columns=["التاريخ", "التوقع"])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_plot["التاريخ"], y=df_plot["التوقع"],
                    mode="lines",
                    fill="tozeroy",
                    name="التوقع اليومي"
                ))
                fig.update_layout(
                    title="منحنى التوقع اليومي خلال الفترة",
                    xaxis_title="التاريخ",
                    yaxis_title="عدد البلاغات",
                    font=dict(family="Arial", size=16),
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=50, b=20),
                    plot_bgcolor="#ffffff",
                    paper_bgcolor="#ffffff"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("النطاق اليومي لا يعرض مخططًا زمنياً. استخدم تبويب التفاصيل للاطلاع على القيمة اليومية.")

        with tabs[1]:
            df_details = pd.DataFrame(daily_predictions, columns=["التاريخ", "التوقع"])
            df_details["التوقع"] = df_details["التوقع"].round(2)
            st.dataframe(df_details, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"حدث خطأ غير متوقع: {e}")
>>>>>>> 910d6f03abe0833ce2eca0acd7293c8a973ff287
