# -*- coding: utf-8 -*-
import math
import sys
from typing import Dict, List

import streamlit as st
import pandas as pd

# -------------------------------------------------
# GENEL AYARLAR
# -------------------------------------------------
st.set_page_config(
    page_title="HUM İşlemler Paneli",
    layout="wide",
)

# HUM logosu (GitHub raw link)
LOGO_URL = "https://raw.githubusercontent.com/SUDE830/hum-panel/main/hum_logo.png"

# -------------------------------------------------
# GENEL TASARIM (CSS)
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* Genel arka plan ve yazı rengi */
    body {
        background-color: #050814 !important;
        color: #f5f5f5 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #050814 !important;
        border-right: 1px solid #1f2933;
    }

    /* Ana içerik alanı */
    div[data-testid="stAppViewContainer"] {
        background-color: #050814;
    }

    /* Kart benzeri beyaz paneller */
    .hum-card {
        background-color: #0f172a;
        padding: 1.5rem;
        border-radius: 0.6rem;
        box-shadow: 0 0 18px rgba(0, 0, 0, 0.45);
        margin-bottom: 1.2rem;
    }

    /* Üst navbar */
    .hum-navbar {
        background-color: #0B1F33;
        color: white;
        padding: 0.7rem 1.5rem;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 0.8rem;
        text-align: center;
        border-radius: 0.4rem;
    }

    /* Başlıklar */
    h1, h2, h3, h4 {
        color: #f9fafb !important;
    }

    /* Sidebar başlık */
    .sidebar-title {
        font-size: 20px;
        font-weight: 700;
        color: #e5e7eb;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Radio buton yazıları */
    label[data-baseweb="radio"] > div {
        color: #e5e7eb !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# YARDIMCI FONKSİYONLAR
# -------------------------------------------------
def fmt(x: float, nd: int = 3) -> str:
    """Türkçe virgüllü sayı formatı, boşsa '—'."""
    if x is None:
        return "—"
    try:
        return str(round(float(x), nd)).replace(".", ",")
    except Exception:
        return "—"


def key(mod_id: str, field: str, row: int) -> str:
    """Benzersiz Streamlit key üretimi."""
    return f"{mod_id}_{field}_{row}"


# -------------------------------------------------
# RESET FONKSİYONLARI
# -------------------------------------------------
RESET_FIELDS: Dict[str, List[str]] = {
    "kestamit": ["kal", "en", "boy"],
    "celik_levha": ["kal", "en", "boy"],
    "celik_mil": ["cap", "boy"],
    "altikose": ["ebat", "boy"],
    "kare": ["ebat", "boy"],
    "lama": ["gen", "yuk", "boy"],
    "kosebent": ["ebat", "et", "boy"],
    "celik_cek_boru": ["dis", "et", "boy", "ic"],
    "dik_boru_kutu": ["boy"],
    "npu": ["ebat", "boy"],
    "heb": ["ebat", "boy"],
}


def reset_module_state(mod_id: str):
    for i in range(1, 6):
        for f in RESET_FIELDS.get(mod_id, []):
            kname = key(mod_id, f, i)
            if kname in st.session_state:
                del st.session_state[kname]


def reset_all():
    for mod in RESET_FIELDS:
        reset_module_state(mod)
    st.rerun()


# -------------------------------------------------
# KATSAYILAR (Br-3 kg/mt)
# -------------------------------------------------
# NPU modülü: sadece 65, 80, 100, 120, 140, 160, 180, 200, 300, 320
NPU_KATSAYI = {
    65: 7.09,
    80: 8.64,
    100: 10.60,
    120: 13.40,
    140: 16.00,
    160: 18.80,
    180: 22.00,
    200: 25.30,
    300: 46.20,
    320: 59.50,
}

# HEB modülü: sadece 100, 120, 160, 180, 200, 220, 240, 320
HEB_KATSAYI = {
    100: 20.40,
    120: 26.70,
    160: 42.60,
    180: 51.20,
    200: 61.30,
    220: 71.50,
    240: 83.20,
    320: 127.00,
}

# -------------------------------------------------
# PROFİL AĞIRLIK CETVELİ VERİLERİ
# -------------------------------------------------
profil_rows = [
    # HEA / HEB
    ("HEA 100", 16.70, 100.20),
    ("HEB 100", 20.40, 122.40),
    ("HEA 120", 19.90, 119.40),
    ("HEB 120", 26.70, 160.20),
    ("HEA 140", 24.70, 148.20),
    ("HEB 140", 33.70, 202.20),
    ("HEA 160", 30.40, 182.40),
    ("HEB 160", 42.60, 255.60),
    ("HEA 180", 35.50, 213.00),
    ("HEB 180", 51.20, 307.20),
    ("HEA 200", 42.30, 253.80),
    ("HEB 200", 61.30, 367.80),
    ("HEA 220", 50.50, 303.00),
    ("HEB 220", 71.50, 429.00),
    ("HEA 240", 60.30, 361.80),
    ("HEB 240", 83.20, 499.20),
    ("HEA 260", 68.20, 409.20),
    ("HEB 260", 93.00, 558.00),
    ("HEA 280", 76.40, 458.40),
    ("HEB 280", 103.00, 618.00),
    ("HEA 300", 88.30, 529.80),
    ("HEB 300", 117.00, 702.00),
    ("HEA 320", 97.60, 585.60),
    ("HEB 320", 127.00, 762.00),
    ("HEA 340", 105.00, 630.00),
    ("HEB 340", 134.00, 804.00),
    ("HEA 360", 112.00, 672.00),
    ("HEB 360", 142.00, 852.00),
    ("HEA 400", 125.00, 750.00),
    ("HEB 400", 155.00, 930.00),
    ("HEA 450", 140.00, 840.00),
    ("HEB 450", 171.00, 1026.00),
    ("HEA 500", 155.00, 930.00),
    ("HEB 500", 187.00, 1122.00),
    ("HEA 550", 166.00, 996.00),
    ("HEB 550", 199.00, 1194.00),
    ("HEA 600", 178.00, 1068.00),
    ("HEB 600", 212.00, 1272.00),
    # NPU
    ("NPU 60", 5.07, 30.42),
    ("NPU 65", 7.09, 42.54),
    ("NPU 80", 8.64, 51.84),
    ("NPU 100", 10.60, 63.60),
    ("NPU 120", 13.40, 80.40),
    ("NPU 140", 16.00, 96.00),
    ("NPU 160", 18.80, 112.80),
    ("NPU 180", 22.00, 132.00),
    ("NPU 200", 25.30, 151.80),
    ("NPU 220", 29.40, 176.40),
    ("NPU 240", 33.20, 199.20),
    ("NPU 260", 37.90, 227.40),
    ("NPU 280", 47.80, 286.80),
    ("NPU 300", 46.20, 277.20),
    ("NPU 320", 59.50, 357.00),
    ("NPU 350", 60.60, 363.60),
    ("NPU 400", 71.80, 430.80),
    # NPI
    ("NPI 80", 5.94, 35.64),
    ("NPI 100", 8.34, 50.04),
    ("NPI 120", 11.10, 66.60),
    ("NPI 140", 14.30, 85.80),
    ("NPI 160", 17.90, 107.40),
    ("NPI 180", 21.90, 131.40),
    ("NPI 200", 26.20, 157.20),
    ("NPI 220", 31.10, 186.60),
    ("NPI 240", 36.20, 217.20),
    ("NPI 260", 41.90, 251.40),
    ("NPI 280", 47.90, 287.40),
    ("NPI 300", 54.20, 325.20),
    ("NPI 320", 61.00, 366.00),
    ("NPI 340", 68.00, 408.00),
    ("NPI 360", 76.10, 456.60),
    ("NPI 380", 84.00, 504.00),
    ("NPI 400", 92.40, 554.40),
    ("NPI 425", 104.00, 624.00),
    ("NPI 450", 115.00, 690.00),
    ("NPI 475", 128.00, 768.00),
    ("NPI 500", 141.00, 846.00),
    ("NPI 550", 166.00, 996.00),
    ("NPI 600", 199.00, 1194.00),
]

profil_df = pd.DataFrame(
    profil_rows,
    columns=["Malzeme", "1 mt/Kg", "Boy=6 mt/Kg"],
)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    if LOGO_URL:
        st.image(LOGO_URL, use_column_width=True)

    st.markdown('<div class="sidebar-title">İŞLEMLER</div>', unsafe_allow_html=True)

    if st.button("Tümünü Sıfırla"):
        reset_all()

    st.markdown("---")

    MODULES = [
        ("kestamit", "KESTAMİT LEVHALAR AD-KG"),
        ("celik_levha", "ÇELİK LEVHALAR AD-KG"),
        ("celik_mil", "ÇELİK MİL AD-MM-KG"),
        ("altikose", "ALTIKÖŞE AD-MM-KG"),
        ("kare", "KARE AD-MM-KG"),
        ("lama", "LAMA AD-MM-KG"),
        ("kosebent", "KÖŞEBENT AD-MM-KG"),
        ("celik_cek_boru", "ÇELİK ÇEKME BORU AD-MM-KG"),
        ("dik_boru_kutu", "DİK BORU & KUTU PROFİL AD-MM-MT"),
        ("npu", "NPU AD-MM-KG"),
        ("heb", "HEB AD-MM-KG"),
        ("profil_cetveli", "Profil Ağırlık Cetveli"),
        ("kodlama", "Kodlama Sistematiği"),
    ]

    labels = [lbl for _, lbl in MODULES]
    selection = st.radio("İşlem seç:", labels)
    selected_mod = [mid for mid, lbl in MODULES if lbl == selection][0]

# -------------------------------------------------
# NAVBAR
# -------------------------------------------------
st.markdown(
    '<div class="hum-navbar">HUM Mühendislik Paneli</div>',
    unsafe_allow_html=True,
)

# -------------------------------------------------
# MODÜLLER
# -------------------------------------------------
def render_levha_multi(mod_id: str, title: str, yogunluk: float):
    """Kestamit & Çelik Levha modülü (Br-2)."""
    st.header(title)
    st.subheader("Kg/Adet (Br-2) hesaplanır")

    br = "(Br-2)"

    with st.container():
        for i in range(1, 6):
            cols = st.columns([0.45, 1, 1, 1, 1])
            cols[0].markdown(f"**{i}. Ürün**")

            kal = cols[1].number_input(
                "Kalınlık (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "kal", i),
                label_visibility="visible" if i == 1 else "collapsed",
            )
            en = cols[2].number_input(
                "En (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "en", i),
                label_visibility="visible" if i == 1 else "collapsed",
            )
            boy = cols[3].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility="visible" if i == 1 else "collapsed",
            )

            kg = yogunluk * kal * (en / 1000) * (boy / 1000) if kal and en and boy else None
            cols[4].markdown(f"**Kg/Adet {br}:** {fmt(kg)}")


def render_celik_mil():
    st.header("ÇELİK MİL AD-MM-KG")
    st.subheader("Kg/Adet (Br-3)")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        cap = cols[1].number_input(
            "Çap (mm)",
            min_value=0.0,
            step=0.1,
            key=key("celik_mil", "cap", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        boy = cols[2].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("celik_mil", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        if cap and boy:
            kg = (cap ** 2) * 0.0062832 * boy * 7.85 / 8000
        else:
            kg = None

        cols[3].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_altikose():
    st.header("ALTIKÖŞE AD-MM-KG")
    st.subheader("Kg/Adet (Br-3)")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].number_input(
            "Ebat (mm)",
            min_value=0.0,
            step=0.1,
            key=key("altikose", "ebat", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        boy = cols[2].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("altikose", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        kg = (ebat ** 2 * boy * 0.012) / (math.sqrt(3) * 1000) if ebat and boy else None
        cols[3].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_kare():
    st.header("KARE AD-MM-KG")
    st.subheader("Kg/Adet (Br-3)")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].number_input(
            "Ebat (mm)",
            min_value=0.0,
            step=0.1,
            key=key("kare", "ebat", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        boy = cols[2].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("kare", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        kg = (ebat * ebat * boy * 0.00785) / 1000 if ebat and boy else None
        cols[3].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_lama():
    st.header("LAMA AD-MM-KG")
    st.subheader("Kg/Adet (Br-3)")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        gen = cols[1].number_input(
            "Genişlik (mm)",
            min_value=0.0,
            step=0.1,
            key=key("lama", "gen", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        yuk = cols[2].number_input(
            "Yükseklik (mm)",
            min_value=0.0,
            step=0.1,
            key=key("lama", "yuk", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        boy = cols[3].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("lama", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        kg = (gen * yuk * boy * 0.00785) / 1000 if gen and yuk and boy else None
        cols[4].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_kosebent():
    st.header("KÖŞEBENT AD-MM-KG")
    st.subheader("Kg/Adet (Br-3)")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].number_input(
            "Ebat (mm)",
            min_value=0.0,
            step=0.1,
            key=key("kosebent", "ebat", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        et = cols[2].number_input(
            "Et (mm)",
            min_value=0.0,
            step=0.1,
            key=key("kosebent", "et", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        boy = cols[3].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("kosebent", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        kg = (2 * ebat * et * boy * 0.00785) / 1000 if ebat and et and boy else None
        cols[4].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_celik_cek_boru():
    st.header("ÇELİK ÇEKME BORU AD-MM-KG")
    st.subheader("Kg/Adet (Br-3)")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        dis_cap = cols[1].number_input(
            "Dış Çap (mm)",
            min_value=0.0,
            step=0.1,
            key=key("celik_cek_boru", "dis", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        et = cols[2].number_input(
            "Et (mm)",
            min_value=0.0,
            step=0.1,
            key=key("celik_cek_boru", "et", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        boy = cols[3].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("celik_cek_boru", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )
        ic_cap = cols[4].number_input(
            "İç Çap (mm) (opsiyonel)",
            min_value=0.0,
            step=0.1,
            key=key("celik_cek_boru", "ic", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        if dis_cap and boy and (et or ic_cap):
            ic_eff = ic_cap if ic_cap > 0 else max(dis_cap - 2 * et, 0)
            dis_hac = (dis_cap ** 2) * 0.0062832 * boy * 7.85 / 8000
            ic_hac = (ic_eff ** 2) * 0.0062832 * boy * 7.85 / 8000
            kg = dis_hac - ic_hac
        else:
            kg = None

        cols[5].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_dik_boru_kutu():
    st.header("DİK BORU & KUTU PROFİL AD-MM-MT")
    st.subheader("mt/Adet hesaplanır")

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        boy = cols[1].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key("dik_boru_kutu", "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        mt = boy / 1000 if boy else None
        cols[2].markdown(f"**mt/Adet:** {fmt(mt)}")


def render_profil(mod_id: str, title: str, kats: Dict[int, float]):
    st.header(title)
    st.subheader("Kg/Adet (Br-3)")

    ebats = sorted(kats.keys())

    for i in range(1, 6):
        cols = st.columns([0.45, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].selectbox(
            "Ebat (mm)",
            ebats,
            key=key(mod_id, "ebat", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        boy = cols[2].number_input(
            "Boy (mm)",
            min_value=0.0,
            step=1.0,
            key=key(mod_id, "boy", i),
            label_visibility="visible" if i == 1 else "collapsed",
        )

        kg = kats[ebat] * boy / 1000 if boy else None
        cols[3].markdown(f"**Kg/Adet (Br-3):** {fmt(kg)}")


def render_profil_cetveli():
    st.header("Profil Ağırlık Cetveli")

    st.write(
        "Aşağıdaki tabloda HEA / HEB / NPU / NPI profiller için 1 mt/kg ve 6 mt (Boy=6 mt) ağırlıkları yer alır."
    )

    arama = st.text_input("Malzeme veya ebat ara (örn: HEB 200, NPU 100, 220)", "")

    df = profil_df.copy()
    if arama.strip():
        df = df[df["Malzeme"].str.contains(arama.strip(), case=False, na=False)]

    # Türkçe format için kopya oluştur
    df_disp = df.copy()
    for c in ["1 mt/Kg", "Boy=6 mt/Kg"]:
        df_disp[c] = df_disp[c].apply(lambda v: fmt(v, 2))

    st.dataframe(df_disp, use_container_width=True)


# -------------------------------------------------
# KODLAMA SİSTEMATİĞİ
# -------------------------------------------------
URETICI_MAP = {
    "HK": "HUM kaynaklı imalat",
    "HT": "HUM talaşlı imalat",
    "FL": "Lazerci & sac işleme fason",
    "FT": "Fason talaşlı imalat",
}


def build_mamul_code(prefix="M", siparis="", unite="", mamul_no=""):
    parts = [prefix, siparis, unite, mamul_no]
    return "-".join([p for p in parts if p.strip()])


def build_yari_mamul_code(
    prefix="Y", uretici="HK", sip="", mno="", res="", a1="", a2="", a3=""
):
    parts = [prefix + uretici, sip, mno]
    if res.strip():
        parts.append(res)
    for x in (a1, a2, a3):
        if x.strip():
            parts.append(x)
    return "-".join(parts)


def render_kodlama():
    st.header("Kodlama Sistematiği")

    sol, sag = st.columns([1, 2])
    kod = ""

    with sol:
        tip = st.radio("Tip:", ["MAMUL", "YARI MAMUL"], key="kod_tip")

        if tip == "MAMUL":
            si = st.text_input("Sipariş No", key="kod_sip_m")
            un = st.text_input("Ünite", key="kod_un_m")
            mn = st.text_input("Mamul No", key="kod_no_m")
            kod = build_mamul_code("M", si, un, mn)
        else:
            ure = st.selectbox(
                "Üretici",
                list(URETICI_MAP.keys()),
                key="kod_u",
            )
            si = st.text_input("Sipariş No", key="kod_sip_y")
            mn = st.text_input("Mamul No", key="kod_no_y")
            rs = st.text_input("Resim No", key="kod_res_y")
            a1 = st.text_input("Alt Poz 1", key="kod_a1")
            a2 = st.text_input("Alt Poz 2", key="kod_a2")
            a3 = st.text_input("Alt Poz 3", key="kod_a3")
            kod = build_yari_mamul_code("Y", ure, si, mn, rs, a1, a2, a3)

    with sag:
        st.subheader("Üretilen Kod")
        st.code(kod if kod else "—")
        st.write("Uzunluk:", len(kod))

        st.markdown("**Üretici Kodları Açıklaması**")
        for k, v in URETICI_MAP.items():
            st.write(f"- **{k}** : {v}")


# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if selected_mod == "kestamit":
    render_levha_multi("kestamit", "KESTAMİT LEVHALAR AD-KG – Kg/Adet (Br-2)", yogunluk=1.365)

elif selected_mod == "celik_levha":
    render_levha_multi("celik_levha", "ÇELİK LEVHALAR AD-KG – Kg/Adet (Br-2)", yogunluk=7.85)

elif selected_mod == "celik_mil":
    render_celik_mil()

elif selected_mod == "altikose":
    render_altikose()

elif selected_mod == "kare":
    render_kare()

elif selected_mod == "lama":
    render_lama()

elif selected_mod == "kosebent":
    render_kosebent()

elif selected_mod == "celik_cek_boru":
    render_celik_cek_boru()

elif selected_mod == "dik_boru_kutu":
    render_dik_boru_kutu()

elif selected_mod == "npu":
    render_profil("npu", "NPU AD-MM-KG", NPU_KATSAYI)

elif selected_mod == "heb":
    render_profil("heb", "HEB AD-MM-KG", HEB_KATSAYI)

elif selected_mod == "profil_cetveli":
    render_profil_cetveli()

elif selected_mod == "kodlama":
    render_kodlama()

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(f"HUM Paneli • Python {sys.version.split()[0]}")
