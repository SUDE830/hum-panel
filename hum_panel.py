# -- coding: utf-8 --
import math
import sys
from io import BytesIO
from typing import Dict, List
import base64
import streamlit as st
import pandas as pd

# -------------------------------------------------
# SAYFA AYARLARI
# -------------------------------------------------
st.set_page_config(
    page_title="HUM İşlemler Paneli",
    layout="wide",
)

# -------------------------------------------------
# GLOBAL TASARIM (PROFESYONEL UI)
# -------------------------------------------------
st.markdown("""
<style>

    /* --- SAYFA ARKA PLANI --- */
    .stApp {
        background-color: #ffffff !important;
    }

    /* --- SIDEBAR TASARIMI --- */
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #0D1B2A !important;
        padding-top: 20px;
    }

    /* Sidebar yazıları beyaz */
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-size: 15px !important;
    }

    /* --- BAŞLIK TASARIMLARI --- */
    h1, h2, h3, h4 {
        color: #0D1B2A !important;
        font-weight: 700 !important;
        margin-top: 20px !important;
        margin-bottom: 10px !important;
    }

    /* --- RADIO BUTTON RENKLERİ --- */
    div[role="radiogroup"] > label > div:first-child span {
        background-color: #ffffff !important;
        border: 2px solid #4cc9f0 !important;
    }

    /* Seçili radio mavi */
    div[role="radiogroup"] > label[data-checked="true"] > div:first-child span {
        background-color: #4cc9f0 !important;
        border-color: #4cc9f0 !important;
    }

    /* --- NUMBER INPUT (sayı kutuları) --- */
    .stNumberInput input {
        background-color: #f7f7f7 !important;
        border-radius: 6px;
        border: 1px solid #c9c9c9 !important;
        color: #000 !important;
        font-size: 16px !important;
        height: 40px !important;
    }

    /* --- "+" ve "-" butonları --- */
    .stNumberInput button {
        background-color: #0D1B2A !important;
        color: white !important;
        border-radius: 5px !important;
        border: none !important;
    }

    /* --- KG sonuç yazıları --- */
    .kg-label {
        font-size: 18px;
        font-weight: 700;
        color: #0D1B2A !important;
        padding-left: 10px;
    }

    /* --- TOP NAVBAR --- */
    .hum-navbar {
        background-color: #0D1B2A;
        color: white;
        padding: 0.8rem 1.2rem;
        font-size: 20px;
        font-weight: 700;
        border-radius: 6px;
        text-align: center;
    }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# NAVBAR
# -------------------------------------------------
st.markdown(
    """
    <div class="hum-navbar">HUM Mühendislik Paneli</div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# LOGO – HER CİHAZDA DOĞRU GÖRÜNÜR
# -------------------------------------------------
st.image(
    "https://raw.githubusercontent.com/SUDE830/hum-panel/main/hum_logo.png",
    width=160,
)

# -------------------------------------------------
# YARDIMCI FONKSİYONLAR
# -------------------------------------------------
def fmt(x: float, nd: int = 3):
    if x is None:
        return "—"
    return str(round(x, nd)).replace(".", ",")

def key(mod_id: str, field: str, row: int):
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
    "hea": ["ebat", "boy"],
    "heb": ["ebat", "boy"],
    "npi": ["ebat", "boy"],
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
# KATSAYILAR
# -------------------------------------------------
NPU_KATSAYI = {60: 5.07, 65: 7.09, 80: 8.64, 100: 10.60, 120: 13.40,
               140: 16.00, 160: 18.80, 180: 22.00, 200: 25.30,
               220: 29.40, 240: 33.20, 260: 37.90, 280: 47.80,
               300: 46.20, 320: 59.50, 350: 60.60, 400: 71.80}

HEA_KATSAYI = {
    100: 16.70, 120: 19.90, 140: 24.70, 160: 30.40, 180: 35.50,
    200: 42.30, 220: 50.50, 240: 60.30, 260: 68.20, 280: 76.40,
    300: 88.30, 320: 97.60, 340: 105.00, 360: 112.00, 400: 125.00,
    450: 140.00, 500: 155.00, 550: 166.00, 600: 178.00
}

HEB_KATSAYI = {
    100: 20.40, 120: 26.70, 140: 33.70, 160: 42.60, 180: 51.20,
    200: 61.30, 220: 71.50, 240: 83.20, 260: 93.00, 280: 103.00,
    300: 117.00, 320: 127.00, 340: 134.00, 360: 142.00, 400: 155.00,
    450: 171.00, 500: 187.00, 550: 199.00, 600: 212.00
}

NPI_KATSAYI = {
    80: 5.94, 100: 8.34, 120: 11.10, 140: 14.30, 160: 17.90,
    180: 21.90, 200: 26.20, 220: 31.10, 240: 36.20, 260: 41.90,
    280: 47.90, 300: 54.20, 320: 61.00, 340: 68.00, 360: 76.10,
    380: 84.00, 400: 92.40, 425: 104.00, 450: 115.00, 475: 128.00,
    500: 141.00, 550: 166.00, 600: 199.00
}

# -------------------------------------------------
# SIDEBAR MENÜ
# -------------------------------------------------
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
    ("hea", "HEA AD-MM-KG"),
    ("heb", "HEB AD-MM-KG"),
    ("npi", "NPI AD-MM-KG"),
    ("profil_cetveli", "Profil Ağırlık Cetveli"),
    ("kodlama", "Kodlama Sistematiği"),
]

with st.sidebar:
    st.title("İŞLEMLER")

    if st.button("Tümünü Sıfırla"):
        reset_all()

    st.markdown("---")

    labels = [lbl for _, lbl in MODULES]
    selection = st.radio("İşlem seç:", labels)
    selected_mod = [mid for mid, lbl in MODULES if lbl == selection][0]

# -------------------------------------------------
# MODÜLLER
# -------------------------------------------------
def render_levha_multi(mod_id, title, yogunluk):
    st.header(title)
    br = "(Br-2)"  # özel istek

    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        kal = cols[1].number_input("Kalınlık (mm)", 0.0, step=0.1, key=key(mod_id, "kal", i),
                                   label_visibility="visible" if i == 1 else "collapsed")
        en = cols[2].number_input("En (mm)", 0.0, step=1.0, key=key(mod_id, "en", i),
                                  label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[3].number_input("Boy (mm)", 0.0, step=1.0, key=key(mod_id, "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        kg = yogunluk * kal * (en/1000) * (boy/1000) if kal and en and boy else None

        cols[4].markdown(f"<span class='kg-label'>Kg/Adet {br}: {fmt(kg)}</span>", unsafe_allow_html=True)


def render_celik_mil():
    st.header("ÇELİK MİL AD-MM-KG")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        cap = cols[1].number_input("Çap (mm)", 0.0, step=0.1, key=key("celik_mil", "cap", i),
                                   label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[2].number_input("Boy (mm)", 0.0, step=1.0, key=key("celik_mil", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        if cap and boy:
            kg = (cap**2) * 0.0062832 * boy * 7.85 / 8000
        else:
            kg = None

        cols[3].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_altikose():
    st.header("ALTIKÖŞE AD-MM-KG")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].number_input("Ebat (mm)", 0.0, step=0.1, key=key("altikose", "ebat", i),
                                    label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[2].number_input("Boy (mm)", 0.0, step=1.0, key=key("altikose", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        kg = (ebat**2 * boy * 0.012) / (math.sqrt(3)*1000) if ebat and boy else None
        cols[3].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_kare():
    st.header("KARE AD-MM-KG")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].number_input("Ebat (mm)", 0.0, step=0.1, key=key("kare", "ebat", i),
                                    label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[2].number_input("Boy (mm)", 0.0, step=1.0, key=key("kare", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        kg = (ebat*ebat*boy*0.00785)/1000 if ebat and boy else None
        cols[3].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_lama():
    st.header("LAMA AD-MM-KG")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        gen = cols[1].number_input("Genişlik (mm)", 0.0, step=0.1, key=key("lama", "gen", i),
                                   label_visibility="visible" if i == 1 else "collapsed")
        yuk = cols[2].number_input("Yükseklik (mm)", 0.0, step=0.1, key=key("lama", "yuk", i),
                                   label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[3].number_input("Boy (mm)", 0.0, step=1.0, key=key("lama", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        kg = (gen*yuk*boy*0.00785)/1000 if gen and yuk and boy else None
        cols[4].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_kosebent():
    st.header("KÖŞEBENT AD-MM-KG")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].number_input("Ebat (mm)", 0.0, step=0.1, key=key("kosebent", "ebat", i),
                                    label_visibility="visible" if i == 1 else "collapsed")
        et = cols[2].number_input("Et (mm)", 0.0, step=0.1, key=key("kosebent", "et", i),
                                  label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[3].number_input("Boy (mm)", 0.0, step=1.0, key=key("kosebent", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        kg = (2*ebat*et*boy*0.00785)/1000 if ebat and et and boy else None
        cols[4].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_celik_cek_boru():
    st.header("ÇELİK ÇEKME BORU AD-MM-KG")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        dis_cap = cols[1].number_input("Dış Çap (mm)", 0.0, step=0.1, key=key("celik_cek_boru", "dis", i),
                                       label_visibility="visible" if i == 1 else "collapsed")
        et = cols[2].number_input("Et (mm)", 0.0, step=0.1, key=key("celik_cek_boru", "et", i),
                                  label_visibility="visible" if i == 1 else "collapsed")
        boy = cols[3].number_input("Boy (mm)", 0.0, step=1.0, key=key("celik_cek_boru", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")
        ic_cap = cols[4].number_input("İç Çap (mm)", 0.0, step=0.1, key=key("celik_cek_boru", "ic", i),
                                      label_visibility="visible" if i == 1 else "collapsed")

        if dis_cap and boy and (et or ic_cap):
            ic_eff = ic_cap if ic_cap > 0 else max(dis_cap - 2 * et, 0)
            dis_hac = (dis_cap**2) * 0.0062832 * boy * 7.85 / 8000
            ic_hac = (ic_eff**2) * 0.0062832 * boy * 7.85 / 8000
            kg = dis_hac - ic_hac
        else:
            kg = None

        cols[5].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_dik_boru_kutu():
    st.header("DİK BORU & KUTU PROFİL AD-MM-MT")
    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        boy = cols[1].number_input("Boy (mm)", 0.0, step=1.0, key=key("dik_boru_kutu", "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        mt = boy/1000 if boy else None
        cols[2].markdown(f"<span class='kg-label'>mt/Adet: {fmt(mt)}</span>", unsafe_allow_html=True)


def render_profil(mod_id, title, kats):
    st.header(title)

    ebats = sorted(kats.keys())

    for i in range(1, 6):
        cols = st.columns([0.4, 1, 1, 1])
        cols[0].markdown(f"**{i}. Ürün**")

        ebat = cols[1].selectbox("Ebat (mm)", ebats, key=key(mod_id, "ebat", i),
                                 label_visibility="visible" if i == 1 else "collapsed")

        boy = cols[2].number_input("Boy (mm)", 0.0, step=1.0, key=key(mod_id, "boy", i),
                                   label_visibility="visible" if i == 1 else "collapsed")

        kg = kats[ebat] * boy / 1000 if boy else None

        cols[3].markdown(f"<span class='kg-label'>Kg/Adet (Br-3): {fmt(kg)}</span>", unsafe_allow_html=True)


def render_profil_cetveli():
    st.header("Profil Ağırlık Cetveli")
    st.write("Bu bölüm sadeleştirildi, tablo veya referans listesi ekleyebilirsin.")


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

def build_yari_mamul_code(prefix="Y", uretici="HK", sip="", mno="", res="", a1="", a2="", a3=""):
    parts = [prefix + uretici, sip, mno]
    if res.strip(): parts.append(res)
    for x in (a1, a2, a3):
        if x.strip(): parts.append(x)
    return "-".join(parts)

def render_kodlama():
    st.header("Kodlama Sistematiği")
    kod = ""

    sol, sag = st.columns([1, 2])

    with sol:
        tip = st.radio("Tip:", ["MAMUL", "YARI MAMUL"], key="kod_tip")

        if tip == "MAMUL":
            si = st.text_input("Sipariş No", key="kod_sip_m")
            un = st.text_input("Ünite", key="kod_un_m")
            mn = st.text_input("Mamul No", key="kod_no_m")
            kod = build_mamul_code("M", si, un, mn)

        else:
            ure = st.selectbox("Üretici", list(URETICI_MAP.keys()), key="kod_u")
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

elif selected_mod == "hea":
    render_profil("hea", "HEA AD-MM-KG", HEA_KATSAYI)

elif selected_mod == "heb":
    render_profil("heb", "HEB AD-MM-KG", HEB_KATSAYI)

elif selected_mod == "npi":
    render_profil("npi", "NPI AD-MM-KG", NPI_KATSAYI)

elif selected_mod == "profil_cetveli":
    render_profil_cetveli()

elif selected_mod == "kodlama":
    render_kodlama()

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(f"HUM Paneli • Python {sys.version.split()[0]}")
