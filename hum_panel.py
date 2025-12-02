# -*- coding: utf-8 -*-
import math
import sys
from io import BytesIO
from typing import List, Dict
import base64

import streamlit as st
import pandas as pd
from PIL import Image

# -------------------------------------------------
# Sayfa ayarları
# -------------------------------------------------
st.set_page_config(
    page_title="HUM İşlemler Paneli",
    layout="wide",
)

# -------------------------------------------------
# Arka plan (sadece ana bölge, HUM logo şeffaf)
# -------------------------------------------------
def set_main_background(image_path: str):
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            /* SIDEBAR sabit lacivert */
            section[data-testid="stSidebar"] > div:first-child {{
                background-color: #0D1B2A !important;
            }}

            /* ANA ÇALIŞMA ALANI */
            section.main {{
                background-image:
                    linear-gradient(rgba(255,255,255,0.90), rgba(255,255,255,0.90)),
                    url("data:image/png;base64,{data}");
                background-repeat: no-repeat;
                background-position: center;
                background-size: 55%;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.write("Arka plan yüklenemedi:", e)

# ⚠ KENDİ BİLGİSAYARINDAKİ LOGO YOLU
set_main_background(
    r"C:\Users\SUDE KÖKEN\OneDrive\Masaüstü\HUM_PANEL\hum_logo.png"
)

# -------------------------------------------------
# Üst navbar (sade, kurumsal)
# -------------------------------------------------
st.markdown(
    """
    <style>
    .hum-navbar {
        background-color: #0D1B2A;
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .block-container {
        padding-top: 0.6rem;
    }
    </style>
    <div class="hum-navbar">
        HUM Mühendislik Paneli
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Yardımcı fonksiyonlar
# -------------------------------------------------
def fmt(x: float, nd: int = 3) -> str:
    """Türkçe ondalık gösterim (virgül)."""
    if x is None:
        return "—"
    s = f"{x:.{nd}f}"
    return s.replace(".", ",")


def key(mod_id: str, field: str, row: int) -> str:
    """Her modül + satır için benzersiz key."""
    return f"{mod_id}_{field}_{row}"


# Hangi modülde hangi alanlar var? (reset için)
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
    """Verilen modüle ait tüm satır inputlarını temizle."""
    fields = RESET_FIELDS.get(mod_id, [])
    for i in range(1, 6):
        for f in fields:
            kname = key(mod_id, f, i)
            if kname in st.session_state:
                del st.session_state[kname]


def reset_all_modules():
    """Tüm modülleri sıfırla + kodlama alanlarını temizle."""
    for mod_id in RESET_FIELDS.keys():
        reset_module_state(mod_id)

    for kname in list(st.session_state.keys()):
        if kname.startswith("kodlama_"):
            del st.session_state[kname]


def download_excel(df: pd.DataFrame, filename: str, label: str = "Excel'e Aktar"):
    """Verilen DataFrame'i Excel olarak indirme butonu."""
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label=label,
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# -------------------------------------------------
# Katsayı tabloları (kg/m) — SON GÜNCEL HALLER
# -------------------------------------------------
# NPU AD-MM-KG için: Excel'deki yeni tablo
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

# HEB AD-MM-KG için: görsellerdeki katsayılar
HEB_KATSAYI = {
    100: 20.40,
    120: 26.70,
    160: 42.60,
    180: 51.20,
    200: 61.30,
    220: 71.50,
    240: 83.20,
    260: 93.00,
    280: 103.00,
    300: 117.00,
    320: 127.00,
}

# Profil Ağırlık Cetveli (1 m / 6 m)
PROFIL_AGIRLIK = {
    # HEA / HEB
    "HEA 100": {"1m": 16.70, "6m": 100.20},
    "HEB 100": {"1m": 20.40, "6m": 122.40},
    "HEA 120": {"1m": 19.90, "6m": 119.40},
    "HEB 120": {"1m": 26.70, "6m": 160.20},
    "HEA 140": {"1m": 24.70, "6m": 148.20},
    "HEB 140": {"1m": 33.70, "6m": 202.20},
    "HEA 160": {"1m": 30.40, "6m": 182.40},
    "HEB 160": {"1m": 42.60, "6m": 255.60},
    "HEA 180": {"1m": 35.50, "6m": 213.00},
    "HEB 180": {"1m": 51.20, "6m": 307.20},
    "HEA 200": {"1m": 42.30, "6m": 253.80},
    "HEB 200": {"1m": 61.30, "6m": 367.80},
    "HEA 220": {"1m": 50.50, "6m": 303.00},
    "HEB 220": {"1m": 71.50, "6m": 429.00},
    "HEA 240": {"1m": 60.30, "6m": 361.80},
    "HEB 240": {"1m": 83.20, "6m": 499.20},
    "HEA 260": {"1m": 68.20, "6m": 409.20},
    "HEB 260": {"1m": 93.00, "6m": 558.00},
    "HEA 280": {"1m": 76.40, "6m": 458.40},
    "HEB 280": {"1m": 103.00, "6m": 618.00},
    "HEA 300": {"1m": 88.30, "6m": 529.80},
    "HEB 300": {"1m": 117.00, "6m": 702.00},
    "HEA 320": {"1m": 97.60, "6m": 585.60},
    "HEB 320": {"1m": 127.00, "6m": 762.00},
    "HEA 340": {"1m": 105.00, "6m": 630.00},
    "HEB 340": {"1m": 134.00, "6m": 804.00},
    "HEA 360": {"1m": 112.00, "6m": 672.00},
    "HEB 360": {"1m": 142.00, "6m": 852.00},
    "HEA 400": {"1m": 125.00, "6m": 750.00},
    "HEB 400": {"1m": 155.00, "6m": 930.00},
    "HEA 450": {"1m": 140.00, "6m": 840.00},
    "HEB 450": {"1m": 171.00, "6m": 1026.00},
    "HEA 500": {"1m": 155.00, "6m": 930.00},
    "HEB 500": {"1m": 187.00, "6m": 1122.00},
    "HEA 550": {"1m": 166.00, "6m": 996.00},
    "HEB 550": {"1m": 199.00, "6m": 1194.00},
    "HEA 600": {"1m": 178.00, "6m": 1068.00},
    "HEB 600": {"1m": 212.00, "6m": 1272.00},

    # NPU (profil cetveli)
    "NPU 60": {"1m": 5.07, "6m": 30.42},
    "NPU 65": {"1m": 7.09, "6m": 42.54},
    "NPU 80": {"1m": 8.64, "6m": 51.84},
    "NPU 100": {"1m": 10.60, "6m": 63.60},
    "NPU 120": {"1m": 13.40, "6m": 80.40},
    "NPU 140": {"1m": 16.00, "6m": 96.00},
    "NPU 160": {"1m": 18.80, "6m": 112.80},
    "NPU 180": {"1m": 22.00, "6m": 132.00},
    "NPU 200": {"1m": 25.30, "6m": 151.80},
    "NPU 220": {"1m": 29.40, "6m": 176.40},
    "NPU 240": {"1m": 33.20, "6m": 199.20},
    "NPU 260": {"1m": 37.90, "6m": 227.40},
    "NPU 280": {"1m": 47.80, "6m": 286.80},
    "NPU 300": {"1m": 46.20, "6m": 277.20},
    "NPU 320": {"1m": 59.50, "6m": 357.00},
    "NPU 350": {"1m": 60.60, "6m": 363.60},
    "NPU 400": {"1m": 71.80, "6m": 430.80},

    # NPI (profil cetveli için)
    "NPI 80": {"1m": 5.94, "6m": 35.64},
    "NPI 100": {"1m": 8.34, "6m": 50.04},
    "NPI 120": {"1m": 11.10, "6m": 66.60},
    "NPI 140": {"1m": 14.30, "6m": 85.80},
    "NPI 160": {"1m": 17.90, "6m": 107.40},
    "NPI 180": {"1m": 21.90, "6m": 131.40},
    "NPI 200": {"1m": 26.20, "6m": 157.20},
    "NPI 220": {"1m": 31.10, "6m": 186.60},
    "NPI 240": {"1m": 36.20, "6m": 217.20},
    "NPI 260": {"1m": 41.90, "6m": 251.40},
    "NPI 280": {"1m": 47.90, "6m": 287.40},
    "NPI 300": {"1m": 54.20, "6m": 325.20},
    "NPI 320": {"1m": 61.00, "6m": 366.00},
    "NPI 340": {"1m": 68.00, "6m": 408.00},
    "NPI 360": {"1m": 76.10, "6m": 456.60},
    "NPI 380": {"1m": 84.00, "6m": 504.00},
    "NPI 400": {"1m": 92.40, "6m": 554.40},
    "NPI 425": {"1m": 104.00, "6m": 624.00},
    "NPI 450": {"1m": 115.00, "6m": 690.00},
    "NPI 475": {"1m": 128.00, "6m": 768.00},
    "NPI 500": {"1m": 141.00, "6m": 846.00},
    "NPI 550": {"1m": 166.00, "6m": 996.00},
    "NPI 600": {"1m": 199.00, "6m": 1194.00},
}

URETICI_MAP = {
    "HK": "HUM kaynaklı imalat",
    "HT": "HUM talaşlı imalat",
    "FL": "Lazerci & sac işleme fason",
    "FT": "Fason talaşlı imalat",
}

# -------------------------------------------------
# Modül tanımları
# -------------------------------------------------
MODULES = [
    {"id": "kestamit",      "label": "KESTAMİT LEVHALAR AD-KG"},
    {"id": "celik_levha",   "label": "ÇELİK LEVHALAR AD-KG"},
    {"id": "celik_mil",     "label": "ÇELİK MİL AD-MM-KG"},
    {"id": "altikose",      "label": "ALTIKÖŞE DOLU AD-MM-KG"},
    {"id": "kare",          "label": "KARE AD-MM-KG"},
    {"id": "lama",          "label": "LAMA AD-MM-KG"},
    {"id": "kosebent",      "label": "KÖŞEBENT AD-MM-KG"},
    {"id": "celik_cek_boru","label": "ÇEL.ÇEK.BORU AD-MM-KG"},
    {"id": "dik_boru_kutu", "label": "DİK.BORU&KUT.PROFİL h. AD-MM-MT"},
    {"id": "npu",           "label": "NPU AD-MM-KG"},
    {"id": "heb",           "label": "HEB AD-MM-KG"},
    {"id": "profil_cetveli","label": "Profil Ağırlık Cetveli"},
    {"id": "kodlama",       "label": "Kodlama Sistematiği"},
]

LABEL_TO_ID = {m["label"]: m["id"] for m in MODULES}

# -------------------------------------------------
# Sidebar (logo + menü + reset)
# -------------------------------------------------
with st.sidebar:
    st.title("İŞLEMLER")

    try:
        logo = Image.open(
            r"C:\Users\SUDE KÖKEN\OneDrive\Masaüstü\HUM_PANEL\hum_logo.png"
        )
        st.image(logo, use_container_width=True)
    except Exception:
        st.write("HUM Panel")

    st.markdown("---")

    if st.button("Tümünü Sıfırla"):
        reset_all_modules()
        st.rerun()

    st.markdown("---")
    selected_label = st.radio(
        "İşlem seç:",
        [m["label"] for m in MODULES],
        key="module_radio",
    )

selected_mod_id = LABEL_TO_ID[selected_label]

if "current_module" not in st.session_state:
    st.session_state["current_module"] = selected_mod_id

if selected_mod_id != st.session_state["current_module"]:
    reset_module_state(selected_mod_id)
    st.session_state["current_module"] = selected_mod_id

# -------------------------------------------------
# Ortak multi-satır render fonksiyonları
# -------------------------------------------------
def render_levha_multi(mod_id: str, title: str, alt_title: str, yogunluk: float):
    st.header(title)
    st.subheader(alt_title)
    st.markdown("Her satır bir üründür. Aynı anda 5 farklı ürün hesaplayabilirsiniz.")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.2, 1.2, 1.2, 1.4])
            cols[0].markdown(f"**{i}. Ürün**")

            label_vis = "visible" if i == 1 else "collapsed"
            kal = cols[1].number_input(
                "Sac kalınlığı (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "kal", i),
                label_visibility=label_vis,
            )
            en = cols[2].number_input(
                "Sac eni (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "en", i),
                label_visibility=label_vis,
            )
            boy = cols[3].number_input(
                "Sac boyu (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append((kal, en, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (kal, en, boy) in enumerate(rows, start=1):
            if kal > 0 and en > 0 and boy > 0:
                kg = yogunluk * kal * (en / 1000) * (boy / 1000)
                results.append(
                    {
                        "Ürün": idx,
                        "Kalınlık (mm)": kal,
                        "En (mm)": en,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_npu_heb(mod_id: str, title: str, katsayi_dict: Dict[int, float]):
    st.header(title)
    st.subheader("Profil kg/adet")
    st.markdown("Her satırda farklı ebat ve boy için hesaplama yapabilirsiniz.")
    st.markdown("---")

    ebatlar = sorted(katsayi_dict.keys())

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.2, 1.2, 1.6])
            cols[0].markdown(f"**{i}. Ürün**")

            label_vis = "visible" if i == 1 else "collapsed"
            ebat = cols[1].selectbox(
                "Ebat (mm)",
                ebatlar,
                key=key(mod_id, "ebat", i),
                label_visibility=label_vis,
            )
            boy = cols[2].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )

            rows.append((ebat, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (ebat, boy) in enumerate(rows, start=1):
            if boy > 0:
                katsayi = katsayi_dict[ebat]
                kg = katsayi * boy / 1000
                results.append(
                    {
                        "Ürün": idx,
                        "Ebat (mm)": ebat,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")
# -------------------------------------------------
# Tek tek modüller
# -------------------------------------------------
def render_kestamit():
    render_levha_multi(
        "kestamit",
        "KESTAMİT LEVHALAR AD-KG",
        "Kestamit Levha – kg/adet",
        yogunluk=1.365,
    )


def render_celik_levha():
    render_levha_multi(
        "celik_levha",
        "ÇELİK LEVHALAR AD-KG",
        "Çelik Levha – kg/adet",
        yogunluk=7.85,
    )


def render_celik_mil():
    mod_id = "celik_mil"
    st.header("ÇELİK MİL AD-MM-KG")
    st.subheader("Çelik Mil – kg/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.2, 1.2, 1.6])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            cap = cols[1].number_input(
                "Çap / Ebat (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "cap", i),
                label_visibility=label_vis,
            )
            boy = cols[2].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append((cap, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (cap, boy) in enumerate(rows, start=1):
            if cap > 0 and boy > 0:
                kg = (cap ** 2) * 0.0062832 * boy * 7.85 / 8000
                results.append(
                    {
                        "Ürün": idx,
                        "Çap (mm)": cap,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_altikose():
    mod_id = "altikose"
    st.header("ALTIKÖŞE DOLU AD-MM-KG")
    st.subheader("Altıköşe Dolu – kg/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.2, 1.2, 1.6])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            ebat = cols[1].number_input(
                "Ebat (AA) mm",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "ebat", i),
                label_visibility=label_vis,
            )
            boy = cols[2].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append((ebat, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (ebat, boy) in enumerate(rows, start=1):
            if ebat > 0 and boy > 0:
                kg = (ebat ** 2) * boy * 0.012 / (math.sqrt(3) * 1000)
                results.append(
                    {
                        "Ürün": idx,
                        "Ebat (mm)": ebat,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_kare():
    mod_id = "kare"
    st.header("KARE AD-MM-KG")
    st.subheader("Kare Dolu – kg/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.2, 1.2, 1.6])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            ebat = cols[1].number_input(
                "Ebat (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "ebat", i),
                label_visibility=label_vis,
            )
            boy = cols[2].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append((ebat, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (ebat, boy) in enumerate(rows, start=1):
            if ebat > 0 and boy > 0:
                kg = (ebat * ebat * boy * 0.00785) / 1000
                results.append(
                    {
                        "Ürün": idx,
                        "Ebat (mm)": ebat,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_lama():
    mod_id = "lama"
    st.header("LAMA AD-MM-KG")
    st.subheader("Lama – kg/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.1, 1.1, 1.1, 1.4])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            gen = cols[1].number_input(
                "Genişlik (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "gen", i),
                label_visibility=label_vis,
            )
            yuk = cols[2].number_input(
                "Yükseklik / Kalınlık (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "yuk", i),
                label_visibility=label_vis,
            )
            boy = cols[3].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append((gen, yuk, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (gen, yuk, boy) in enumerate(rows, start=1):
            if gen > 0 and yuk > 0 and boy > 0:
                kg = (gen * yuk * boy * 0.00785) / 1000
                results.append(
                    {
                        "Ürün": idx,
                        "Genişlik (mm)": gen,
                        "Yükseklik (mm)": yuk,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_kosebent():
    mod_id = "kosebent"
    st.header("KÖŞEBENT AD-MM-KG")
    st.subheader("Köşebent – kg/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.1, 1.1, 1.1, 1.4])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            ebat = cols[1].number_input(
                "Ebat (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "ebat", i),
                label_visibility=label_vis,
            )
            et = cols[2].number_input(
                "Et kalınlığı (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "et", i),
                label_visibility=label_vis,
            )
            boy = cols[3].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append((ebat, et, boy))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (ebat, et, boy) in enumerate(rows, start=1):
            if ebat > 0 and et > 0 and boy > 0:
                kg = (2 * ebat * et * boy * 0.00785) / 1000
                results.append(
                    {
                        "Ürün": idx,
                        "Ebat (mm)": ebat,
                        "Et kalınlığı (mm)": et,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_celik_cek_boru():
    mod_id = "celik_cek_boru"
    st.header("ÇELİK ÇEKME BORU AD-MM-KG")
    st.subheader("Çelik Çekme Boru – kg/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.4, 1.1, 1.1, 1.1, 1.3, 1.5])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            dis_cap = cols[1].number_input(
                "Dış çap (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "dis", i),
                label_visibility=label_vis,
            )
            et = cols[2].number_input(
                "Et kalınlığı (mm)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "et", i),
                label_visibility=label_vis,
            )
            boy = cols[3].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            ic_cap = cols[4].number_input(
                "İç çap (mm) (boşsa etten hesaplanır)",
                min_value=0.0,
                step=0.1,
                key=key(mod_id, "ic", i),
                label_visibility=label_vis,
            )
            rows.append((dis_cap, et, boy, ic_cap))

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, (dis_cap, et, boy, ic_cap) in enumerate(rows, start=1):
            if dis_cap > 0 and boy > 0 and (et > 0 or ic_cap > 0):
                if ic_cap <= 0 and et > 0:
                    ic_cap_eff = max(dis_cap - 2 * et, 0)
                else:
                    ic_cap_eff = ic_cap

                dis_hacim = (dis_cap ** 2) * 0.0062832 * boy * 7.85 / 8000
                ic_hacim = (ic_cap_eff ** 2) * 0.0062832 * boy * 7.85 / 8000
                kg = dis_hacim - ic_hacim

                results.append(
                    {
                        "Ürün": idx,
                        "Dış çap (mm)": dis_cap,
                        "Et kalınlığı (mm)": et,
                        "İç çap (mm)": ic_cap_eff,
                        "Boy (mm)": boy,
                        "Kg/Adet": kg,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["Kg/Adet"] = df["Kg/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_dik_boru_kutu():
    mod_id = "dik_boru_kutu"
    st.header("DİK.BORU&KUT.PROFİL h. AD-MM-MT")
    st.subheader("Dik Boru & Kutu Profil – mt/adet")
    st.markdown("---")

    with st.form(f"{mod_id}_form"):
        rows = []
        for i in range(1, 6):
            cols = st.columns([0.6, 2.0, 2.0])
            cols[0].markdown(f"**{i}. Ürün**")
            label_vis = "visible" if i == 1 else "collapsed"

            boy = cols[1].number_input(
                "Boy (mm)",
                min_value=0.0,
                step=1.0,
                key=key(mod_id, "boy", i),
                label_visibility=label_vis,
            )
            rows.append(boy)

        c1, c2 = st.columns(2)
        hesapla = c1.form_submit_button("HESAPLA")
        temizle = c2.form_submit_button("Bu sayfayı temizle")

    if temizle:
        reset_module_state(mod_id)
        st.rerun()

    if hesapla:
        results = []
        for idx, boy in enumerate(rows, start=1):
            if boy > 0:
                mt = boy / 1000
                results.append(
                    {
                        "Ürün": idx,
                        "Boy (mm)": boy,
                        "mt/Adet": mt,
                    }
                )

        if results:
            df = pd.DataFrame(results)
            df["mt/Adet"] = df["mt/Adet"].round(3)
            st.success("Hesaplama tamamlandı.")
            st.dataframe(df, use_container_width=True, hide_index=True)
            download_excel(df, f"{mod_id}_hesaplama.xlsx")
        else:
            st.info("Lütfen en az bir satıra değer girin.")


def render_npu():
    render_npu_heb("npu", "NPU AD-MM-KG", NPU_KATSAYI)


def render_heb():
    render_npu_heb("heb", "HEB AD-MM-KG", HEB_KATSAYI)


def render_profil_cetveli():
    mod_id = "profil_cetveli"
    st.header("Profil Ağırlık Cetveli")
    st.subheader("1 m ve 6 m ağırlıklar")

    profiller = sorted(PROFIL_AGIRLIK.keys())
    secim = st.selectbox("Malzeme seç", profiller, key="profil_secim")
    vals = PROFIL_AGIRLIK[secim]

    c1, c2 = st.columns(2)
    c1.metric("1 mt / kg", fmt(vals["1m"], 2))
    c2.metric("Boy = 6 mt / kg", fmt(vals["6m"], 2))

    df = pd.DataFrame(
        [
            {"MALZEME": k, "1 mt/Kg": v["1m"], "Boy=6 mt/Kg": v["6m"]}
            for k, v in PROFIL_AGIRLIK.items()
        ]
    ).sort_values("MALZEME")
    st.dataframe(df, use_container_width=True, hide_index=True)
    download_excel(df, f"{mod_id}.xlsx")


def build_mamul_code(prefix_m="M", siparis="", unite="", mamul_no=""):
    parts = [prefix_m, siparis, unite, mamul_no]
    parts = [p.strip() for p in parts if p and p.strip() != ""]
    return "-".join(parts)


def build_yari_mamul_code(prefix_y="Y", uretici="HK", siparis="", mamul_no="", resim_no="",
                          alt1="", alt2="", alt3=""):
    head = f"{prefix_y}{uretici}".strip()
    core = [head, siparis, mamul_no]
    if resim_no and resim_no.strip():
        core.append(resim_no.strip())
    for a in (alt1, alt2, alt3):
        if a and a.strip():
            core.append(a.strip())
    core = [c.strip() for c in core if c and c.strip() != ""]
    return "-".join(core)


def render_kodlama():
    st.header("Kodlama Sistematiği")
    st.subheader("Mamul ve Yarı Mamul Stok Kodları")
    st.markdown("---")

    stok_kodu = ""

    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        kod_tipi = st.radio(
            "Kod tipi seç:",
            ["MAMUL", "YARI MAMUL"],
            key="kodlama_tip",
        )
        st.markdown("---")

        if kod_tipi == "MAMUL":
            siparis = st.text_input(
                "Sipariş No (Proje Kodu)",
                placeholder="Örn: OR009-2020",
                key="kodlama_sip_m",
            )
            unite = st.text_input(
                "Ünite Kodu (Kapasite)",
                placeholder="Örn: HEXT50",
                key="kodlama_unite_m",
            )
            mamul_no = st.text_input(
                "Mamul No",
                placeholder="Örn: 40G651",
                key="kodlama_mno_m",
            )
            stok_kodu = build_mamul_code("M", siparis, unite, mamul_no)
        else:
            uretici = st.selectbox(
                "Üretici Kodu",
                list(URETICI_MAP.keys()),
                format_func=lambda k: f"{k} — {URETICI_MAP[k]}",
                key="kodlama_uret_y",
            )
            siparis = st.text_input(
                "Sipariş No (Proje Kodu)",
                placeholder="Örn: OR028-2019",
                key="kodlama_sip_y",
            )
            mamul_no = st.text_input(
                "Mamul No",
                placeholder="Örn: KS313 / 40G261",
                key="kodlama_mno_y",
            )
            resim_no = st.text_input(
                "Resim No (varsa)",
                placeholder="Örn: 10 / ZK3-07 / 00",
                key="kodlama_resim_y",
            )
            alt1 = st.text_input(
                "Alt Resim/Poz 1 (varsa)",
                placeholder="Örn: 04",
                key="kodlama_alt1_y",
            )
            alt2 = st.text_input(
                "Alt Resim/Poz 2 (varsa)",
                placeholder="Örn: 82",
                key="kodlama_alt2_y",
            )
            alt3 = st.text_input(
                "Alt Resim/Poz 3 (varsa)",
                placeholder="Örn: 1",
                key="kodlama_alt3_y",
            )
            stok_kodu = build_yari_mamul_code(
                "Y", uretici, siparis, mamul_no, resim_no, alt1, alt2, alt3
            )

    with col_right:
        st.markdown("### Üretilen Stok Kodu")
        st.code(stok_kodu if stok_kodu else "—", language="text")
        st.markdown("### Karakter Uzunluğu")
        st.write(len(stok_kodu))
        st.info("Kurallar değişirse rahatça güncellenebilir.")

    if st.button("Kodlama alanlarını temizle"):
        for kname in list(st.session_state.keys()):
            if kname.startswith("kodlama_"):
                del st.session_state[kname]
        st.rerun()
# -------------------------------------------------
# Router
# -------------------------------------------------
if selected_mod_id == "kestamit":
    render_kestamit()
elif selected_mod_id == "celik_levha":
    render_celik_levha()
elif selected_mod_id == "celik_mil":
    render_celik_mil()
elif selected_mod_id == "altikose":
    render_altikose()
elif selected_mod_id == "kare":
    render_kare()
elif selected_mod_id == "lama":
    render_lama()
elif selected_mod_id == "kosebent":
    render_kosebent()
elif selected_mod_id == "celik_cek_boru":
    render_celik_cek_boru()
elif selected_mod_id == "dik_boru_kutu":
    render_dik_boru_kutu()
elif selected_mod_id == "npu":
    render_npu()
elif selected_mod_id == "heb":
    render_heb()
elif selected_mod_id == "profil_cetveli":
    render_profil_cetveli()
elif selected_mod_id == "kodlama":
    render_kodlama()

st.markdown("---")
st.caption(f"HUM Paneli · Python {sys.version.split()[0]}")
