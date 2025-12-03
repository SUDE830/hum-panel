# -- coding: utf-8 --
import math
import sys
from typing import Dict, List
import streamlit as st

# -------------------------------------------------
# SAYFA AYARLARI
# -------------------------------------------------
st.set_page_config(
    page_title="HUM İşlemler Paneli",
    layout="wide",
)

# -------------------------------------------------
# GLOBAL TASARIM - HUM TEMA
# -------------------------------------------------
st.markdown("""
<style>

    /* ANA ARKA PLAN */
    .stApp {
        background-color: black !important;
    }

    /* SIDEBAR TEMA */
    section[data-testid="stSidebar"] {
        background-color: #0D1B2A !important;
        padding-top: 20px;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* LOGO ORTALAMA */
    .sidebar-logo {
        display: flex;
        justify-content: center;
        margin-bottom: 25px;
        margin-top: 10px;
    }

    /* NAVBAR */
    .hum-navbar {
        background-color: #0D1B2A;
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 19px;
        font-weight: 600;
        margin-bottom: 1rem;
        border-radius: 4px;
    }

    /* INPUT TASARIMI */
    .stNumberInput input {
        background-color: #FFFFFF !important;
        color: black !important;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600;
    }

    /* LABEL RENKLERİ */
    label {
        font-weight: 600 !important;
        color: #1E293B !important;
    }

    /* KG/Adet sonuçları */
    .result-text {
        font-weight: 700;
        font-size: 16px;
        color: #0F172A;
        padding-top: 14px;
    }

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# NAVBAR
# -------------------------------------------------
st.markdown(
    """<div class="hum-navbar">HUM Mühendislik Paneli</div>""",
    unsafe_allow_html=True
)

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def fmt(x, nd=3):
    if x is None:
        return "—"
    return str(round(x, nd)).replace(".", ",")

def key(mod, field, row):
    return f"{mod}_{field}_{row}"

# -------------------------------------------------
# RESET ALANLARI
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

def reset_module(mod):
    for i in range(1, 6):
        for f in RESET_FIELDS.get(mod, []):
            st.session_state.pop(key(mod, f, i), None)

def reset_all():
    for m in RESET_FIELDS:
        reset_module(m)
    st.rerun()

# -------------------------------------------------
# KATSAYILAR
# -------------------------------------------------
NPU = {60:5.07,65:7.09,80:8.64,100:10.6,120:13.4,140:16,160:18.8,180:22,
       200:25.3,220:29.4,240:33.2,260:37.9,280:47.8,300:46.2,320:59.5,350:60.6,400:71.8}

HEA = {
    100:16.7,120:19.9,140:24.7,160:30.4,180:35.5,200:42.3,220:50.5,
    240:60.3,260:68.2,280:76.4,300:88.3,320:97.6,340:105,360:112,400:125,
    450:140,500:155,550:166,600:178
}

HEB = {
    100:20.4,120:26.7,140:33.7,160:42.6,180:51.2,200:61.3,220:71.5,
    240:83.2,260:93,280:103,300:117,320:127,340:134,360:142,400:155,
    450:171,500:187,550:199,600:212
}

NPI = {
    80:5.94,100:8.34,120:11.1,140:14.3,160:17.9,180:21.9,200:26.2,
    220:31.1,240:36.2,260:41.9,280:47.9,300:54.2,320:61,340:68,
    360:76.1,380:84,400:92.4,425:104,450:115,475:128,500:141,
    550:166,600:199
}

# -------------------------------------------------
# SIDEBAR MENU
# -------------------------------------------------
MODULES = [
    ("kestamit","KESTAMİT LEVHALAR AD-KG"),
    ("celik_levha","ÇELİK LEVHALAR AD-KG"),
    ("celik_mil","ÇELİK MİL AD-MM-KG"),
    ("altikose","ALTIKÖŞE AD-MM-KG"),
    ("kare","KARE AD-MM-KG"),
    ("lama","LAMA AD-MM-KG"),
    ("kosebent","KÖŞEBENT AD-MM-KG"),
    ("celik_cek_boru","ÇELİK ÇEKME BORU AD-MM-KG"),
    ("dik_boru_kutu","DİK BORU & KUTU PROFİL AD-MM-MT"),
    ("npu","NPU AD-MM-KG"),
    ("hea","HEA AD-MM-KG"),
    ("heb","HEB AD-MM-KG"),
    ("npi","NPI AD-MM-KG"),
    ("profil","Profil Ağırlık Cetveli"),
    ("kodlama","Kodlama Sistematiği")
]
LOGO_URL = "https://raw.githubusercontent.com/SUDE830/hum-panel/main/hum_logo.png"

st.markdown(
    f"""
    <div class="sidebar-logo">
        <img src="{LOGO_URL}" width="150" style="border-radius:8px; margin-bottom:20px;">
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><img src="https://i.imgur.com/Sz5Z7GU.png" width="140"></div>', unsafe_allow_html=True)

    if st.button("Tümünü Sıfırla"):
        reset_all()

    st.markdown("---")

    selected_label = st.radio("İşlem seç:", [lbl for _, lbl in MODULES])
    selected_mod = [mid for mid, lbl in MODULES if lbl == selected_label][0]


# -------------------------------------------------
# MODÜLLER
# -------------------------------------------------

def render_levha(mod, title, density):
    st.header(title + " – Kg/Adet (Br-2)")

    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")

        kal = c[1].number_input("Kalınlık (mm)", 0.0, step=0.1, key=key(mod,"kal",i),
                                label_visibility="collapsed" if i>1 else "visible")
        en  = c[2].number_input("En (mm)", 0.0, step=1.0, key=key(mod,"en",i),
                                label_visibility="collapsed" if i>1 else "visible")
        boy = c[3].number_input("Boy (mm)", 0.0, step=1.0, key=key(mod,"boy",i),
                                label_visibility="collapsed" if i>1 else "visible")

        kg = density * kal * (en/1000) * (boy/1000) if kal and en and boy else None
        c[4].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_celik_mil():
    st.header("ÇELİK MİL AD-MM-KG – Kg/Adet (Br-3)")
    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")
        cap = c[1].number_input("Çap (mm)", 0.0, step=0.1, key=key("celik_mil","cap",i),
                                label_visibility="collapsed" if i>1 else "visible")
        boy = c[2].number_input("Boy (mm)", 0.0, step=1.0, key=key("celik_mil","boy",i),
                                label_visibility="collapsed" if i>1 else "visible")
        kg = (cap**2)*0.0062832*boy*7.85/8000 if cap and boy else None
        c[3].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_altikose():
    st.header("ALTIKÖŞE AD-MM-KG – Kg/Adet (Br-3)")
    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")
        e = c[1].number_input("Ebat (mm)", 0.0, step=0.1, key=key("altikose","ebat",i),
                              label_visibility="collapsed" if i>1 else "visible")
        b = c[2].number_input("Boy (mm)", 0.0, step=1.0, key=key("altikose","boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        kg = (e**2 * b * 0.012) / (math.sqrt(3)*1000) if e and b else None
        c[3].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_kare():
    st.header("KARE AD-MM-KG – Kg/Adet (Br-3)")
    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")
        e = c[1].number_input("Ebat (mm)", 0.0, step=0.1, key=key("kare","ebat",i),
                              label_visibility="collapsed" if i>1 else "visible")
        b = c[2].number_input("Boy (mm)", 0.0, step=1.0, key=key("kare","boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        kg = (e*e*b*0.00785)/1000 if e and b else None
        c[3].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_lama():
    st.header("LAMA AD-MM-KG – Kg/Adet (Br-3)")
    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")
        g = c[1].number_input("Genişlik", 0.0, step=0.1, key=key("lama","gen",i),
                              label_visibility="collapsed" if i>1 else "visible")
        y = c[2].number_input("Yükseklik", 0.0, step=0.1, key=key("lama","yuk",i),
                              label_visibility="collapsed" if i>1 else "visible")
        b = c[3].number_input("Boy", 0.0, step=1.0, key=key("lama","boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        kg = (g*y*b*0.00785)/1000 if g and y and b else None
        c[4].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_kosebent():
    st.header("KÖŞEBENT AD-MM-KG – Kg/Adet (Br-3)")
    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")
        e = c[1].number_input("Ebat (mm)", 0.0, step=0.1, key=key("kosebent","ebat",i),
                              label_visibility="collapsed" if i>1 else "visible")
        et = c[2].number_input("Et (mm)", 0.0, step=0.1, key=key("kosebent","et",i),
                               label_visibility="collapsed" if i>1 else "visible")
        b = c[3].number_input("Boy (mm)", 0.0, step=1.0, key=key("kosebent","boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        kg = (2*e*et*b*0.00785)/1000 if e and et and b else None
        c[4].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_celik_cek_boru():
    st.header("ÇELİK ÇEKME BORU AD-MM-KG – Kg/Adet (Br-3)")
    for i in range(1, 6):
        c = st.columns([0.3, 1, 1, 1, 1, 1])
        c[0].write(f"**{i}. Ürün**")
        d = c[1].number_input("Dış Çap",0.0,step=0.1,key=key("celik_cek_boru","dis",i),
                              label_visibility="collapsed" if i>1 else "visible")
        et = c[2].number_input("Et",0.0,step=0.1,key=key("celik_cek_boru","et",i),
                               label_visibility="collapsed" if i>1 else "visible")
        b = c[3].number_input("Boy",0.0,step=1.0,key=key("celik_cek_boru","boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        ic = c[4].number_input("İç Çap",0.0,step=0.1,key=key("celik_cek_boru","ic",i),
                               label_visibility="collapsed" if i>1 else "visible")

        if d and b and (et or ic):
            real_ic = ic if ic>0 else max(d - 2*et, 0)
            d_h = (d**2)*0.0062832*b*7.85/8000
            i_h = (real_ic**2)*0.0062832*b*7.85/8000
            kg = d_h - i_h
        else:
            kg = None

        c[5].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_dik_boru_kutu():
    st.header("DİK BORU & KUTU PROFİL AD-MM-MT")
    for i in range(1,6):
        c = st.columns([0.3,1,1])
        c[0].write(f"**{i}. Ürün**")
        b = c[1].number_input("Boy (mm)",0.0,step=1.0,key=key("dik_boru_kutu","boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        mt = b/1000 if b else None
        c[2].markdown(f"<div class='result-text'>{fmt(mt)}</div>", unsafe_allow_html=True)


def render_profil(mod,title,kats):
    st.header(title + " – Kg/Adet (Br-3)")
    ebats = sorted(kats.keys())
    for i in range(1,6):
        c = st.columns([0.3,1,1,1])
        c[0].write(f"**{i}. Ürün**")
        e = c[1].selectbox("Ebat", ebats, key=key(mod,"ebat",i),
                           label_visibility="collapsed" if i>1 else "visible")
        b = c[2].number_input("Boy",0.0,step=1.0,key=key(mod,"boy",i),
                              label_visibility="collapsed" if i>1 else "visible")
        kg = kats[e]*b/1000 if b else None
        c[3].markdown(f"<div class='result-text'>{fmt(kg)}</div>", unsafe_allow_html=True)


def render_profil_cetveli():
    st.header("Profil Ağırlık Cetveli")
    st.info("Bu bölüm sadeleştirildi. Talep edilirse tablo eklenir.")


# -------------------------------------------------
# KODLAMA SİSTEMATİĞİ
# -------------------------------------------------
URETICI = {"HK":"HUM kaynaklı", "HT":"HUM talaşlı", "FL":"Lazerci", "FT":"Fason Talaşlı"}

def build_m(prefix, sip, un, mn):
    return "-".join([x for x in [prefix,sip,un,mn] if x.strip()])

def build_y(prefix, ur, sip, mn, rs, a1, a2, a3):
    parts = [prefix+ur, sip, mn]
    if rs.strip(): parts.append(rs)
    for x in (a1,a2,a3):
        if x.strip(): parts.append(x)
    return "-".join(parts)

def render_kodlama():
    st.header("Kodlama Sistematiği")
    sol,sag = st.columns([1,2])
    kod = ""

    with sol:
        tip = st.radio("Tip:",["MAMUL","YARI MAMUL"])
        if tip=="MAMUL":
            si = st.text_input("Sipariş No")
            un = st.text_input("Ünite")
            mn = st.text_input("Mamul No")
            kod = build_m("M",si,un,mn)
        else:
            ur = st.selectbox("Üretici", list(URETICI.keys()))
            si = st.text_input("Sipariş No")
            mn = st.text_input("Mamul No")
            rs = st.text_input("Resim No")
            a1 = st.text_input("Alt Poz 1")
            a2 = st.text_input("Alt Poz 2")
            a3 = st.text_input("Alt Poz 3")
            kod = build_y("Y",ur,si,mn,rs,a1,a2,a3)

    with sag:
        st.subheader("Üretilen Kod")
        st.code(kod if kod else "—")
        st.write("Uzunluk:", len(kod))


# -------------------------------------------------
# ROUTER
# -------------------------------------------------
if selected_mod == "kestamit":
    render_levha("kestamit", "KESTAMİT LEVHALAR AD-KG", 1.365)

elif selected_mod == "celik_levha":
    render_levha("celik_levha", "ÇELİK LEVHALAR AD-KG", 7.85)

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
    render_profil("npu","NPU AD-MM-KG",NPU)

elif selected_mod == "hea":
    render_profil("hea","HEA AD-MM-KG",HEA)

elif selected_mod == "heb":
    render_profil("heb","HEB AD-MM-KG",HEB)

elif selected_mod == "npi":
    render_profil("npi","NPI AD-MM-KG",NPI)

elif selected_mod == "profil":
    render_profil_cetveli()

elif selected_mod == "kodlama":
    render_kodlama()

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(f"HUM Paneli • Python {sys.version.split()[0]}")

