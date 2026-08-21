import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Mô phỏng đầu tư định kỳ", page_icon="📈", layout="wide")

# ---------- Thông số mặc định cho từng kênh đầu tư ----------
KENH_MAC_DINH = {
    "Chứng chỉ quỹ": {"loi_suat": 12.0, "bien_dong": 15.0, "mau": "#2980b9"},
    "Cổ phiếu": {"loi_suat": 15.0, "bien_dong": 25.0, "mau": "#e74c3c"},
    "Trái phiếu": {"loi_suat": 7.0, "bien_dong": 5.0, "mau": "#27ae60"},
    "Tiết kiệm": {"loi_suat": 5.5, "bien_dong": 0.5, "mau": "#f39c12"},
}


def mo_phong_kenh(so_tien_thang, so_thang, loi_suat_nam, bien_dong_nam, so_lan_mo_phong, cac_cu_soc):
    """
    Mô phỏng Monte Carlo giá trị tài sản theo tháng cho 1 kênh đầu tư.
    Trả về mảng shape (so_lan_mo_phong, so_thang + 1)
    """
    loi_suat_thang = loi_suat_nam / 100 / 12
    bien_dong_thang = bien_dong_nam / 100 / np.sqrt(12)

    ket_qua = np.zeros((so_lan_mo_phong, so_thang + 1))

    if bien_dong_nam > 0:
        loi_suat_ngau_nhien = np.random.normal(
            loc=loi_suat_thang, scale=bien_dong_thang, size=(so_lan_mo_phong, so_thang)
        )
    else:
        loi_suat_ngau_nhien = np.full((so_lan_mo_phong, so_thang), loi_suat_thang)

    for thang in range(1, so_thang + 1):
        gia_tri_truoc = ket_qua[:, thang - 1]
        # Góp tiền đầu tháng rồi sinh lời trong tháng
        gia_tri_sau_gop = gia_tri_truoc + so_tien_thang
        gia_tri_moi = gia_tri_sau_gop * (1 + loi_suat_ngau_nhien[:, thang - 1])

        # Áp dụng cú sốc thị trường nếu tháng này trùng với cú sốc đã thiết lập
        for cu_soc in cac_cu_soc:
            if cu_soc["thang"] == thang:
                gia_tri_moi = gia_tri_moi * (1 + cu_soc["muc_giam"] / 100)

        gia_tri_moi = np.maximum(gia_tri_moi, 0)  # không cho âm
        ket_qua[:, thang] = gia_tri_moi

    return ket_qua


# ---------- Giao diện ----------
st.title("📈 Mô phỏng đầu tư định kỳ (DCA)")
st.markdown(
    "Mô phỏng kết quả khi đầu tư một khoản cố định mỗi tháng vào các kênh khác nhau, "
    "có tính đến biến động ngẫu nhiên và các cú sốc thị trường."
)

with st.sidebar:
    st.header("⚙️ Thiết lập đầu vào")

    so_tien_thang = st.number_input(
        "Số tiền đầu tư mỗi tháng (VNĐ)", min_value=100_000, step=500_000, value=5_000_000
    )
    so_nam = st.slider("Số năm đầu tư", min_value=1, max_value=30, value=10)
    so_thang = so_nam * 12

    st.markdown("---")
    kenh_chon = st.multiselect(
        "Chọn kênh đầu tư",
        options=list(KENH_MAC_DINH.keys()),
        default=["Chứng chỉ quỹ", "Cổ phiếu", "Trái phiếu"],
    )

    thong_so_kenh = {}
    if kenh_chon:
        st.markdown("**Điều chỉnh thông số từng kênh (%/năm)**")
        for kenh in kenh_chon:
            with st.expander(f"🔧 {kenh}", expanded=False):
                loi_suat = st.slider(
                    f"Lợi suất kỳ vọng - {kenh}",
                    min_value=-10.0, max_value=40.0,
                    value=KENH_MAC_DINH[kenh]["loi_suat"], step=0.5,
                    key=f"loi_suat_{kenh}",
                )
                bien_dong = st.slider(
                    f"Độ biến động (volatility) - {kenh}",
                    min_value=0.0, max_value=50.0,
                    value=KENH_MAC_DINH[kenh]["bien_dong"], step=0.5,
                    key=f"bien_dong_{kenh}",
                )
                thong_so_kenh[kenh] = {"loi_suat": loi_suat, "bien_dong": bien_dong}

    st.markdown("---")
    bat_mo_phong = st.checkbox("Bật mô phỏng biến động ngẫu nhiên (Monte Carlo)", value=True)
    so_lan_mo_phong = 1
    if bat_mo_phong:
        so_lan_mo_phong = st.slider(
            "Số lần mô phỏng (Monte Carlo)", min_value=100, max_value=2000, value=500, step=100
        )
    else:
        st.caption("Khi tắt, mỗi kênh chỉ chạy 1 kịch bản với lợi suất trung bình (không có biến động).")

    st.markdown("---")
    st.markdown("**⚡ Cú sốc thị trường (tùy chọn)**")
    so_cu_soc = st.number_input("Số lượng cú sốc muốn thêm", min_value=0, max_value=5, value=0, step=1)

    cac_cu_soc = []
    for i in range(int(so_cu_soc)):
        col1, col2 = st.columns(2)
        with col1:
            thang_soc = st.number_input(
                f"Tháng xảy ra cú sốc #{i+1}", min_value=1, max_value=so_thang, value=min(12, so_thang),
                key=f"thang_soc_{i}",
            )
        with col2:
            muc_giam = st.number_input(
                f"Mức giảm (%) #{i+1}", min_value=-90.0, max_value=0.0, value=-30.0, step=5.0,
                key=f"muc_giam_{i}",
            )
        cac_cu_soc.append({"thang": int(thang_soc), "muc_giam": muc_giam})

    nut_chay = st.button("🚀 Chạy mô phỏng", type="primary", use_container_width=True)


# ---------- Xử lý & hiển thị kết quả ----------
if not kenh_chon:
    st.warning("Vui lòng chọn ít nhất một kênh đầu tư ở thanh bên trái.")
elif nut_chay or "da_chay" in st.session_state:
    st.session_state["da_chay"] = True

    so_lan_thuc_te = so_lan_mo_phong if bat_mo_phong else 1
    tong_von_gop = so_tien_thang * so_thang

    ket_qua_theo_kenh = {}
    for kenh in kenh_chon:
        ts = thong_so_kenh[kenh]
        bien_dong_dung = ts["bien_dong"] if bat_mo_phong else 0.0
        mang_kq = mo_phong_kenh(
            so_tien_thang=so_tien_thang,
            so_thang=so_thang,
            loi_suat_nam=ts["loi_suat"],
            bien_dong_nam=bien_dong_dung,
            so_lan_mo_phong=so_lan_thuc_te,
            cac_cu_soc=cac_cu_soc,
        )
        ket_qua_theo_kenh[kenh] = mang_kq

    # ----- Biểu đồ đường: dải percentile theo thời gian -----
    st.subheader("📊 Diễn biến giá trị tài sản theo thời gian")

    truc_thang = np.arange(0, so_thang + 1)
    truc_nam = truc_thang / 12

    fig_duong = go.Figure()
    for kenh in kenh_chon:
        mang_kq = ket_qua_theo_kenh[kenh]
        p10 = np.percentile(mang_kq, 10, axis=0)
        p50 = np.percentile(mang_kq, 50, axis=0)
        p90 = np.percentile(mang_kq, 90, axis=0)
        mau = KENH_MAC_DINH[kenh]["mau"]

        # Dải P10-P90
        fig_duong.add_trace(go.Scatter(
            x=np.concatenate([truc_nam, truc_nam[::-1]]),
            y=np.concatenate([p90, p10[::-1]]),
            fill="toself",
            fillcolor=mau,
            opacity=0.15,
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="skip",
        ))
        # Đường trung vị
        fig_duong.add_trace(go.Scatter(
            x=truc_nam, y=p50,
            mode="lines",
            name=f"{kenh} (trung vị)",
            line=dict(color=mau, width=2.5),
        ))

    # Đánh dấu các cú sốc trên trục thời gian
    for cu_soc in cac_cu_soc:
        fig_duong.add_vline(
            x=cu_soc["thang"] / 12, line_dash="dash", line_color="gray",
            annotation_text=f"Sốc {cu_soc['muc_giam']}%", annotation_position="top",
        )

    fig_duong.update_layout(
        xaxis_title="Số năm",
        yaxis_title="Giá trị tài sản (VNĐ)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60),
    )
    st.plotly_chart(fig_duong, use_container_width=True)
    st.caption("Vùng tô màu thể hiện khoảng percentile 10–90 (dải kết quả có thể xảy ra); đường đậm là kịch bản trung vị.")

    # ----- Bảng tổng kết -----
    st.subheader("📋 Bảng tổng kết")

    hang = []
    for kenh in kenh_chon:
        mang_kq = ket_qua_theo_kenh[kenh]
        gia_tri_cuoi = mang_kq[:, -1]
        p10_cuoi = np.percentile(gia_tri_cuoi, 10)
        p50_cuoi = np.percentile(gia_tri_cuoi, 50)
        p90_cuoi = np.percentile(gia_tri_cuoi, 90)
        lai_lo_pct = (p50_cuoi - tong_von_gop) / tong_von_gop * 100

        hang.append({
            "Kênh đầu tư": kenh,
            "Tổng vốn đã góp (VNĐ)": tong_von_gop,
            "Giá trị trung vị cuối kỳ (VNĐ)": p50_cuoi,
            "Lãi/Lỗ (%)": lai_lo_pct,
            "Kịch bản xấu nhất - P10 (VNĐ)": p10_cuoi,
            "Kịch bản tốt nhất - P90 (VNĐ)": p90_cuoi,
        })

    df_tong_ket = pd.DataFrame(hang)
    st.dataframe(
        df_tong_ket.style.format({
            "Tổng vốn đã góp (VNĐ)": "{:,.0f}",
            "Giá trị trung vị cuối kỳ (VNĐ)": "{:,.0f}",
            "Lãi/Lỗ (%)": "{:+.1f}%",
            "Kịch bản xấu nhất - P10 (VNĐ)": "{:,.0f}",
            "Kịch bản tốt nhất - P90 (VNĐ)": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ----- Biểu đồ cột so sánh các kênh ở mốc kết thúc -----
    st.subheader("📊 So sánh các kênh ở thời điểm kết thúc")

    fig_cot = go.Figure()
    fig_cot.add_trace(go.Bar(
        x=df_tong_ket["Kênh đầu tư"],
        y=df_tong_ket["Giá trị trung vị cuối kỳ (VNĐ)"],
        name="Trung vị (P50)",
        marker_color=[KENH_MAC_DINH[k]["mau"] for k in df_tong_ket["Kênh đầu tư"]],
        error_y=dict(
            type="data",
            symmetric=False,
            array=df_tong_ket["Kịch bản tốt nhất - P90 (VNĐ)"] - df_tong_ket["Giá trị trung vị cuối kỳ (VNĐ)"],
            arrayminus=df_tong_ket["Giá trị trung vị cuối kỳ (VNĐ)"] - df_tong_ket["Kịch bản xấu nhất - P10 (VNĐ)"],
            color="gray",
        ),
        text=df_tong_ket["Giá trị trung vị cuối kỳ (VNĐ)"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
    ))
    fig_cot.add_hline(
        y=tong_von_gop, line_dash="dash", line_color="black",
        annotation_text="Tổng vốn đã góp", annotation_position="bottom right",
    )
    fig_cot.update_layout(
        yaxis_title="Giá trị tài sản cuối kỳ (VNĐ)",
        xaxis_title="Kênh đầu tư",
        margin=dict(t=40),
    )
    st.plotly_chart(fig_cot, use_container_width=True)
    st.caption("Thanh sai số thể hiện khoảng percentile 10–90. Đường nét đứt là tổng vốn đã góp (mốc hòa vốn).")

    st.markdown("---")
    st.markdown(
        "⚠️ **Lưu ý:** Đây là mô phỏng dựa trên các giả định lợi suất và biến động do người dùng nhập, "
        "không phải dự báo chính xác về hiệu suất đầu tư thực tế trong tương lai. "
        "Vui lòng tham khảo ý kiến chuyên gia tài chính trước khi ra quyết định đầu tư."
    )
else:
    st.info("Điều chỉnh thông số ở thanh bên trái rồi nhấn **🚀 Chạy mô phỏng** để xem kết quả.")
