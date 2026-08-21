import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Máy tính chỉ số BMI", page_icon="⚖️", layout="centered")


def phan_loai_bmi(bmi):
    if bmi < 18.5:
        return "Thiếu cân", "#e67e22"   # cam
    elif bmi < 25:
        return "Bình thường", "#27ae60"  # xanh lá
    elif bmi < 30:
        return "Thừa cân", "#e67e22"    # cam
    else:
        return "Béo phì", "#e74c3c"     # đỏ


def ve_thang_bmi(bmi):
    fig, ax = plt.subplots(figsize=(7, 1.6))

    vung = [
        (15, 18.5, "#f1c40f", "Thiếu cân"),
        (18.5, 25, "#27ae60", "Bình thường"),
        (25, 30, "#e67e22", "Thừa cân"),
        (30, 40, "#e74c3c", "Béo phì"),
    ]

    for start, end, mau, ten in vung:
        ax.axvspan(start, end, color=mau, alpha=0.8)
        ax.text((start + end) / 2, 1.35, ten, ha="center", va="center",
                fontsize=9, fontweight="bold")

    bmi_ve = min(max(bmi, 15), 40)
    ax.axvline(bmi_ve, color="black", linewidth=3)
    ax.plot(bmi_ve, 0.5, marker="v", markersize=14, color="black")
    ax.text(bmi_ve, -0.55, f"{bmi}", ha="center", va="center",
            fontsize=10, fontweight="bold")

    ax.set_xlim(15, 40)
    ax.set_ylim(-1, 2)
    ax.set_yticks([])
    ax.set_xticks([15, 18.5, 25, 30, 40])
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_xlabel("Chỉ số BMI")
    plt.tight_layout()
    return fig


# ---------- Giao diện ----------
st.title("⚖️ Máy tính chỉ số BMI")
st.markdown("### 🧮 Nhập thông tin và nhận kết quả BMI cùng gợi ý cân nặng lý tưởng.")

col1, col2 = st.columns(2)
with col1:
    can_nang = st.slider("Cân nặng (kg)", min_value=30, max_value=200, value=60)
with col2:
    chieu_cao = st.slider("Chiều cao (cm)", min_value=100, max_value=220, value=165)

# ---------- Xử lý ----------
chieu_cao_m = chieu_cao / 100
bmi = round(can_nang / (chieu_cao_m ** 2), 1)
ten_phan_loai, mau = phan_loai_bmi(bmi)

can_nang_min = round(18.5 * (chieu_cao_m ** 2), 1)
can_nang_max = round(24.9 * (chieu_cao_m ** 2), 1)

# ---------- Kết quả ----------
col1, col2 = st.columns(2)
with col1:
    st.metric("Chỉ số BMI", bmi)
with col2:
    st.markdown(
        f"""
        <div style="text-align:center; padding:14px; border-radius:12px;
                    background-color:{mau}20; border:2px solid {mau}; margin-top:6px;">
            <span style="font-size:22px; font-weight:bold; color:{mau};">
                {ten_phan_loai}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"Với chiều cao **{chieu_cao:.0f} cm**, cân nặng lý tưởng khoảng "
    f"**{can_nang_min} kg – {can_nang_max} kg**."
)

st.subheader("Vị trí BMI trên thang phân loại")
fig = ve_thang_bmi(bmi)
st.pyplot(fig)

st.markdown("---")
st.markdown(
    "⚠️ **Lưu ý:** Kết quả trên chỉ mang tính chất tham khảo, không thay thế cho tư vấn y tế "
    "hoặc dinh dưỡng chuyên môn. Vui lòng tham khảo ý kiến bác sĩ hoặc chuyên gia dinh dưỡng "
    "để có đánh giá chính xác về tình trạng sức khỏe của bạn."
)
