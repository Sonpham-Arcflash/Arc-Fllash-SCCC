import streamlit as st
import math
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

# --- 1. GIAO DIỆN SIÊU TO (HIGH-VISIBILITY) ---
st.set_page_config(page_title="Arc Flash Pro - Engineer Son", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] { font-size: 20px !important; }
    label { font-size: 23px !important; font-weight: bold !important; color: #1f4e78 !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 52px !important; font-weight: bold !important; color: #1f4e78; }
    .stAlert p { font-size: 21px !important; line-height: 1.6 !important; }
    .stButton button { height: 3.5em !important; font-size: 23px !important; font-weight: bold !important; }
    .afb-note { font-size: 21px !important; color: #1f4e78; font-weight: bold; background-color: #eaf2f8; padding: 15px; border-radius: 10px; border-left: 10px solid #1f4e78; }
    .instruction-box { background-color: #fff4e6; padding: 15px; border-left: 8px solid #ff922b; border-radius: 5px; font-weight: bold; font-size: 19px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ ARC FLASH CALCULATOR - ENGINEER SON")
st.caption("Professional Site Edition v16.0 | Site SCCC Approved")

if 'history_list' not in st.session_state:
    st.session_state.history_list = []

# --- 2. VỊ TRÍ & THIẾT BỊ ---
with st.expander("📍 VỊ TRÍ & THIẾT BỊ (Bấm để nhập)", expanded=True):
    c_inf1, c_inf2 = st.columns(2)
    tram = c_inf1.text_input("SUBSTATION (TRẠM)", value="Sub-01")
    thiet_bi = c_inf2.text_input("EQUIPMENT (THIẾT BỊ)", value="VCB Panel T1")

# --- 3. NHẬP LIỆU ---
st.header("📋 THÔNG SỐ ĐẦU VÀO")
col1, col2, col3 = st.columns([1, 1, 1.8])

with col1:
    i_sc = st.number_input("I_sc (kA)", value=20.0, step=1.0)
    t_ms = st.number_input("Time (ms)", value=100.0, step=10.0)
with col2:
    d = st.number_input("Distance (mm)", value=455.0, step=5.0)
    config_dict = {"VCB": "Tủ kín đứng", "VCBB": "Tủ có vách ngăn", "HCB": "Thanh cái ngang", "VOA": "Ngoài trời đứng", "HOA": "Ngoài trời ngang"}
    config_code = st.selectbox("Cấu hình (Config):", options=list(config_dict.keys()), format_func=lambda x: config_dict[x])
    cf = 1.5 if config_code in ["VCB", "VCBB", "HCB"] else 1.0

with col3:
    notes = {
        "VCB": "**[VCB] Vertical in Box**: Thanh cái đứng trong tủ kín.",
        "VCBB": "**[VCBB] Vertical Barrier**: Thanh cái đứng trong tủ kín, có thêm vách ngăn.",
        "HCB": "**[HCB] Horizontal in Box**: Thanh cái ngang hướng về phía người thao tác.",
        "VOA": "**[VOA] Vertical Open Air**: Thiết bị hở ngoài trời, dây dẫn dọc.",
        "HOA": "**[HOA] Horizontal Open Air**: Thiết bị hở ngoài trời, dây dẫn ngang."
    }
    st.info(f"🔍 **CHI TIẾT KỸ THUẬT:**\n\n{notes[config_code]}")

# --- 4. TÍNH TOÁN ---
t_s = t_ms / 1000
energy = cf * 0.0135 * i_sc * (t_s / 0.1) * (610 / d)**2
boundary = 610 * math.sqrt(cf * 0.0135 * i_sc * (t_s / 0.1) / 1.2)

# --- 5. BIỂU ĐỒ THANH NHIỆT ---
fig = go.Figure(go.Indicator(
    mode = "gauge+number", value = energy,
    number = {'suffix': " cal/cm²", 'font': {'size': 65}},
    gauge = {
        'axis': {'range': [0, 50], 'tickfont': {'size': 22}},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 1.2], 'color': "#2ecc71"}, {'range': [1.2, 8], 'color': "#f1c40f"},
            {'range': [8, 25], 'color': "#e67e22"}, {'range': [25, 40], 'color': "#e74c3c"},
            {'range': [40, 50], 'color': "#000000"}
        ]
    }
))
fig.update_layout(height=450, margin=dict(l=30, r=30, t=30, b=0))
st.plotly_chart(fig, width="stretch")

res1, res2 = st.columns(2)
res1.metric("NĂNG LƯỢNG (E)", f"{energy:.2f} cal/cm²")
res2.metric("RANH GIỚI AFB (mm)", f"{boundary:.0f} mm")

# --- 6. PPE CHI TIẾT ---
def get_ppe_detailed(e):
    if e < 1.2:
        return "SAFE / AN TOÀN", "• Đồng phục BHLĐ Cotton.\n• Kính bảo hộ.\n• Găng tay da.\n• Nút tai chống ồn."
    if e < 8:
        return "CAT 2 (Mức 2)", "• Quần áo chống hồ quang 8 cal/cm².\n• Tấm che mặt + Mũ trùm Balaclava.\n• Kính bảo hộ + Nút tai.\n• Găng tay da chịu nhiệt."
    if e < 25:
        return "CAT 3 (Mức 3)", "• Moon suit chống hồ quang 25 cal/cm².\n• Mũ trùm đầu kín chuyên dụng.\n• Găng tay cao su cách điện + Găng da.\n• Kính bảo hộ + Nút tai."
    if e <= 40:
        return "CAT 4 (Mức 4)", "• Quần áo toàn thân 40 cal/cm².\n• Mũ trùm kín 40 cal/cm².\n• Găng tay cao su cách điện Lớp 2.\n• Giày cách điện + Nút tai."
    return "🔥 NGUY HIỂM", "CẤM THAO TÁC - Năng lượng vượt mức 40 cal/cm²."

cat, ppe_list = get_ppe_detailed(energy)
st.error(f"🛡️ **MỨC BẢO HỘ PPE: {cat}**\n\n{ppe_list}")

# --- 7. LƯU KẾT QUẢ ---
current_data = {"Time": datetime.now().strftime("%H:%M"), "Station": tram, "Equipment": thiet_bi, "Energy": round(energy, 2), "AFB": round(boundary, 0), "Category": cat, "PPE_Items": ppe_list}
current_fp = f"{i_sc}-{t_ms}-{d}-{config_code}-{thiet_bi}"

st.divider()
if st.button("💾 LƯU KẾT QUẢ (SAVE TO HISTORY)", disabled=(st.session_state.get('last_fp') == current_fp), width="stretch"):
    st.session_state.history_list.append(current_data)
    st.session_state.last_fp = current_fp
    st.rerun()

# --- 8. NHẬT KÝ (LUÔN HIỆN TIÊU ĐỀ) ---
st.subheader("📝 NHẬT KÝ TÍNH TOÁN")
if not st.session_state.history_list:
    st.info("Chưa có dữ liệu nhật ký. Hãy nhấn 'Save' để lưu kết quả đầu tiên.")
else:
    st.markdown("<div class='instruction-box'>🗑️ XÓA DÒNG: Tích chọn đầu hàng -> Nhấn biểu tượng Thùng rác -> Nhấn Update History.</div>", unsafe_allow_html=True)
    df_history = pd.DataFrame(st.session_state.history_list)
    edited_df = st.data_editor(df_history, num_rows="dynamic", width="stretch", key="editor_v16")
    
    if st.button("🔄 CẬP NHẬT NHẬT KÝ", width="stretch"):
        st.session_state.history_list = edited_df.to_dict('records')
        st.rerun()

    def to_excel(df):
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Report', startrow=2)
            workbook, worksheet = writer.book, writer.sheets['Report']
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1f4e78', 'font_color': 'white', 'border': 1})
            worksheet.write('A1', f'ARC FLASH REPORT - ENGINEER SON - {tram}', workbook.add_format({'bold': True, 'font_size': 14}))
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(2, col_num, value, header_fmt)
            worksheet.set_column('G:G', 90)
        return out.getvalue()

    st.download_button("📥 TẢI BÁO CÁO EXCEL", data=to_excel(pd.DataFrame(st.session_state.history_list)), file_name=f"ArcFlash_{tram}.xlsx", width="stretch")

# --- 9. PHỤ LỤC (LUÔN HIỆN Ở CUỐI) ---
st.divider()
st.subheader("📚 BẢNG TRA CỨU NHANH PPE")
st.markdown("""<table style="width:100%; font-size:22px; text-align:center; border-collapse: collapse;">
<tr style="background-color:#1f4e78; color:white;"><th>Điện áp</th><th>Cấp PPE</th><th>Năng lượng (cal/cm²)</th></tr>
<tr style="background-color:#2ecc71;"><td>&lt; 240V</td><td>CAT 1</td><td>&lt; 1.2</td></tr>
<tr style="background-color:#f1c40f;"><td>240-600V</td><td>CAT 2</td><td>1.2 - 8</td></tr>
<tr style="background-color:#e67e22;"><td>480-600V</td><td>CAT 3</td><td>8 - 25</td></tr>
<tr style="background-color:#e74c3c; color:white;"><td>600V-15kV</td><td>CAT 4</td><td>25 - 40</td></tr></table>""", unsafe_allow_html=True)