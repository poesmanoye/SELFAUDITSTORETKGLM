import base64
from io import BytesIO
import requests
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="SELF AUDIT CHECKLIST STORE & SO TKG LM", layout="centered"
)

GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwfa1C-Defh98DPxXqHivE8g4Ok67RBlXrJHWKeyQfdbJLElfdImHlJPrEM9yBORMD7fQ/exec"

BULAN_INDONESIA = {
    1: "JANUARI",
    2: "FEBRUARI",
    3: "MARET",
    4: "APRIL",
    5: "MEI",
    6: "JUNI",
    7: "JULI",
    8: "AGUSTUS",
    9: "SEPTEMBER",
    10: "OKTOBER",
    11: "NOVEMBER",
    12: "DESEMBER",
}


def format_tanggal_indo(dt):
  return f"{dt.day} {BULAN_INDONESIA[dt.month]} {dt.year}"


# === SISTEM LOGIN ===
PASSWORD = "LION321"

if "auth" not in st.session_state:
  st.session_state.auth = False

if not st.session_state.auth:
  st.markdown(
      "<h1 style='text-align: center;'>🔐 STORE AUDIT TKG</h1>",
      unsafe_allow_html=True,
  )
  pwd = st.text_input("Masukkan Password", type="password")

  if st.button("LOGIN", use_container_width=True):
    if pwd == PASSWORD:
      st.session_state.auth = True
      st.success("Login berhasil!")
      st.rerun()
    else:
      st.error("Password salah!")
  st.stop()
# === END LOGIN SYSTEM ===

# --- CSS Styling ---
st.markdown(
    """
    <style>
        h1 a, h2 a, h3 a { display: none !important; }
        .header-container h1 { color: #FF0000 !important; font-weight: 900 !important; margin-bottom: 6px !important; }
        .header-container p { font-size: 16px !important; color: #666 !important; margin-top: 0px !important; }
        div[data-baseweb="select"] div { white-space: pre-wrap !important; }
        .question-text { font-weight: 600; margin-bottom: 8px; margin-top: 15px; }

        /* Ukuran font tebal & besar untuk tab utama */
        div[data-baseweb="tab-list"] button div p {
            font-size: 18px !important;
            font-weight: 800 !important;
        }

        /* Warna Pasti per Tab Utama (Step 1: Merah, Step 2: Biru, Step 3: Kuning) */
        div[data-baseweb="tab-list"] > div:nth-child(1) button p { color: #ef4444 !important; }
        div[data-baseweb="tab-list"] > div:nth-child(2) button p { color: #3b82f6 !important; }
        div[data-baseweb="tab-list"] > div:nth-child(3) button p { color: #eab308 !important; }
    </style>
    <div class="header-container" style="text-align:center; margin-top:-25px;">
        <h1>SELF AUDIT CHECKLIST STORE & SO</h1>
        <p>LION GROUP - QUALITY ACCOUNTING</p>
    </div>
""",
    unsafe_allow_html=True,
)

if "pdf_generated" not in st.session_state:
  st.session_state.pdf_generated = False

if "audit_data" not in st.session_state:
  st.session_state.audit_data = {}

checklist_points = [
    # === BAB 1: FACILITY ===
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Room Layout",
        "code": "1.a",
        "desc": "Does actual room layout conform to approved plan?",
        "page": 0,
        "y": 600,
        "y_remark": 600,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "APPROVED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Code Location",
        "code": "1.b",
        "desc": "What is location codes used in store area?",
        "page": 0,
        "y": 545,
        "y_remark": 553,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "TKG Store\nT2 : Serviceable\nT9 : Unserviceable",
            "NILL",
            "Standard",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Temperature & Humidity",
        "code": "1.c",
        "desc": "Ventilation good & control devices valid?",
        "page": 0,
        "y": 470,
        "y_remark": 495,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "Input Suhu & Kelembapan",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Segregation",
        "code": "1.d_1",
        "desc": "Is there proper segregation applied?",
        "page": 0,
        "y": 410,
        "y_remark": 407,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "PROPER", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Segregation",
        "code": "1.d_2",
        "desc": "Between aircraft parts and non-aircraft parts",
        "page": 0,
        "y": 367,
        "y_remark": 367,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "PROPER", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Segregation",
        "code": "1.d_3",
        "desc": "Between serviceable and unserviceable parts",
        "page": 0,
        "y": 318,
        "y_remark": 318,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "PROPER", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Segregation",
        "code": "1.d_4",
        "desc": "Are bin segregation clearly marked?",
        "page": 0,
        "y": 250,
        "y_remark": 248,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEAR", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Cleanliness",
        "code": "1.e",
        "desc": "Are store areas clean and bin segregation marked?",
        "page": 0,
        "y": 186,
        "y_remark": 184,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEAN", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Security",
        "code": "1.f_1",
        "desc": (
            "The door is equipped with a fingerprint lock and remains"
            " locked at all times?"
        ),
        "page": 0,
        "y": 130,
        "y_remark": 128,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Security",
        "code": "1.g_1",
        "desc": "is the entire store area covered by CCTV ?",
        "page": 1,
        "y": 660,
        "y_remark": 660,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "COVERED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Security",
        "code": "1.g_2",
        "desc": (
            "CCTV pointed entrance area, Shelf and part in the front"
            " area?"
        ),
        "page": 1,
        "y": 600,
        "y_remark": 600,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "POINTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Security",
        "code": "1.g_3",
        "desc": (
            "CCTV pointed at the shelves and stored items, covering"
            " all Parts?"
        ),
        "page": 1,
        "y": 540,
        "y_remark": 540,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "POINTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Security",
        "code": "1.g_4",
        "desc": (
            "CCTV pointed the counter, preparation area and item"
            " handover area?"
        ),
        "page": 1,
        "y": 470,
        "y_remark": 470,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "POINTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Safety",
        "code": "1.h",
        "desc": "Fire extinguishers & sprinklers up to date & good?",
        "page": 1,
        "y": 400,
        "y_remark": 400,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "GOOD CONDITION\nVUT : 22 SEP 2027",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 1: FACILITY",
        "sub_step": "Safety",
        "code": "1.i",
        "desc": "Emergency exits clear & exit signs good?",
        "page": 1,
        "y": 330,
        "y_remark": 330,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEAR AND GOOD", "NILL", "Lainnya"],
    },
    # === BAB 2: FLOW PROSES ===
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Receiving",
        "code": "2.a_1",
        "desc": (
            "Are asset and spare part received by Store"
            " completed with a eMRO order number?"
        ),
        "page": 1,
        "y": 185,
        "y_remark": 185,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "COMPLETE",
            "NOT COMPLETE",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Receiving",
        "code": "2.a_2",
        "desc": (
            "eMRO system updated real time as per actual"
            " receiving?"
        ),
        "page": 1,
        "y": 120,
        "y_remark": 120,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "UPDATED REAL TIME",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Receiving",
        "code": "2.a_3",
        "desc": (
            "Shipper location and contact person are clearly"
            " noted on the delivery?"
        ),
        "page": 2,
        "y": 648,
        "y_remark": 648,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARY NOTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Receiving",
        "code": "2.a_4",
        "desc": (
            "Received items are completed with Tag/label?"
        ),
        "page": 2,
        "y": 595,
        "y_remark": 593,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "COMPLETED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "RTS Part",
        "code": "2.b_1",
        "desc": (
            "Are all Spare Part received ex Aircraft, registered"
            " in eMRO system by Store?"
        ),
        "page": 2,
        "y": 535,
        "y_remark": 535,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "COMPLETED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "RTS Part",
        "code": "2.b_2",
        "desc": (
            "Return date are real time updated or within time"
            " limit allowed?"
        ),
        "page": 2,
        "y": 470,
        "y_remark": 470,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "ON TIME",
            "OVERDUE",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "RTS Part",
        "code": "2.b_3",
        "desc": (
            "Giver and receiver name and ID are clearly noted?"
        ),
        "page": 2,
        "y": 415,
        "y_remark": 415,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY NOTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool In",
        "code": "2.c_1",
        "desc": (
            "Are all tools returned to Store updated into eMRO"
            " system?"
        ),
        "page": 2,
        "y": 365,
        "y_remark": 365,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "UPDATED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool In",
        "code": "2.c_2",
        "desc": "Loan return date are real time updated?",
        "page": 2,
        "y": 328,
        "y_remark": 328,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "UPDATED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool In",
        "code": "2.c_3",
        "desc": (
            "The name and ID of person who returns the tool are"
            " clearly noted?"
        ),
        "page": 2,
        "y": 278,
        "y_remark": 278,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY NOTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool In",
        "code": "2.c_4",
        "desc": (
            "Are all tools returned to Store in a clean condition?"
        ),
        "page": 2,
        "y": 223,
        "y_remark": 223,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "CLEAN",
            "DIRTY",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "ESDS Placement",
        "code": "2.d_1",
        "desc": "Are ESDS system implemented?",
        "page": 2,
        "y": 185,
        "y_remark": 185,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "IMPLEMENTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "ESDS Placement",
        "code": "2.d_2",
        "desc": "Personnel understand and has the awareness?",
        "page": 2,
        "y": 143,
        "y_remark": 143,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "UNDERSTAND", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "ESDS Placement",
        "code": "2.d_3",
        "desc": "Bins are clearly marked?",
        "page": 2,
        "y": 105,
        "y_remark": 105,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY MARKED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "ESDS Placement",
        "code": "2.d_4",
        "desc": "Safety equipment are available?",
        "page": 3,
        "y": 665,
        "y_remark": 665,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "AVAILABLE", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Creation",
        "code": "2.e_1",
        "desc": (
            "Are asset and spare part sent by Store completed"
            " with eMRO order number?"
        ),
        "page": 3,
        "y": 613,
        "y_remark": 613,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "UPDATED",
            "PENDING",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Creation",
        "code": "2.e_2",
        "desc": (
            " eMRO system updated real time as per actual"
            " delivery?"
        ),
        "page": 3,
        "y": 545,
        "y_remark": 545,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "UPDATED REAL TIME",
            "PENDING",
            "NILL",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "TO Creation",
        "code": "2.e_3",
        "desc": (
            "Destinated location and contact person are"
            " clearly noted on the delivery?"
        ),
        "page": 3,
        "y": 490,
        "y_remark": 490,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY NOTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Part Issuance",
        "code": "2.f_1",
        "desc": (
            "Are all asset and spare part given to be"
            " installed on Aircraft updated into eMRO system?"
        ),
        "page": 3,
        "y": 416,
        "y_remark": 416,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "UPDATED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Part Issuance",
        "code": "2.f_2",
        "desc": (
            "Issued date are real time updated or within time"
            " limit allowed?"
        ),
        "page": 3,
        "y": 347,
        "y_remark": 347,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "UPDATED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Part Issuance",
        "code": "2.f_3",
        "desc": (
            "Giver and receiver name and ID are clearly"
            " noted?"
        ),
        "page": 3,
        "y": 290,
        "y_remark": 290,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY NOTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool Out",
        "code": "2.g_1",
        "desc": (
            "Are all tools lend by Store recorded into eMRO"
            " system?"
        ),
        "page": 3,
        "y": 243,
        "y_remark": 243,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "RECORDED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool Out",
        "code": "2.g_2",
        "desc": "Loan date are real time updated?",
        "page": 3,
        "y": 203,
        "y_remark": 203,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "UPDATED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool Out",
        "code": "2.g_3",
        "desc": "Loaner name and ID are clearly noted?",
        "page": 3,
        "y": 170,
        "y_remark": 170,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY NOTED", "NILL", "Lainnya"],
    },
    {
        "main_step": "STEP 2: FLOW PROSES",
        "sub_step": "Tool Out",
        "code": "2.g_4",
        "desc": "Are tools lend by Store in a clean condition?",
        "page": 3,
        "y": 131,
        "y_remark": 131,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "CLEAN",
            "DIRTY",
            "NILL",
            "Lainnya",
        ],
    },
    # === BAB 3: SYSTEM & INVENTORY ===
    {
        "main_step": "STEP 3: SYSTEM & INVENTORY",
        "sub_step": "eMRO User",
        "code": "3.a",
        "desc": "Check conformity of User ID and access module?",
        "page": 4,
        "y": 610,
        "y_remark": 610,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Status --", "CONFORM", "MISMATCH", "Lainnya"],
    },
    {
        "main_step": "STEP 3: SYSTEM & INVENTORY",
        "sub_step": "Binning Check",
        "code": "3.b",
        "desc": (
            "Check the Conformity of total actual bin with total"
            "bin and bin names registered on the system?"
        ),
        "page": 4,
        "y": 543,
        "y_remark": 543,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Status --",
            "CONFORM",
            "DISCREPANCY FOUND",
            "Lainnya",
        ],
    },
    {
        "main_step": "STEP 3: SYSTEM & INVENTORY",
        "sub_step": "Transaction Check",
        "code": "3.c",
        "desc": "Check transaction records at store for last year?",
        "page": 4,
        "y": 466,
        "y_remark": 466,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Status --", "VERIFIED", "ERROR FOUND", "Lainnya"],
    },
]

# --- TANGGAL AUDIT ---
st.markdown("TANGGAL AUDIT")
audit_date = st.date_input("Audit Date", label_visibility="collapsed")
st.markdown("---")

# --- TAB UTAMA (STEP 1, STEP 2, STEP 3) ---
main_tab1, main_tab2, main_tab3 = st.tabs(
    ["STEP 1: FACILITY", "STEP 2: FLOW PROSES", "STEP 3: SYSTEM & INVENTORY"]
)

main_tabs_mapping = {
    "STEP 1: FACILITY": main_tab1,
    "STEP 2: FLOW PROSES": main_tab2,
    "STEP 3: SYSTEM & INVENTORY": main_tab3,
}

for main_step_name, m_tab in main_tabs_mapping.items():
  with m_tab:
    items_in_main = [
        it for it in checklist_points if it["main_step"] == main_step_name
    ]
    sub_step_names = list(dict.fromkeys([it["sub_step"] for it in items_in_main]))

    if len(sub_step_names) > 1:
      sub_tabs = st.tabs(sub_step_names)
      sub_tabs_mapping = dict(zip(sub_step_names, sub_tabs))

      for item in items_in_main:
        s_tab = sub_tabs_mapping[item["sub_step"]]
        with s_tab:
          code = item["code"]
          st.markdown(
              f'<div class="question-text">{item["desc"]}</div>',
              unsafe_allow_html=True,
          )

          c1, c2 = st.columns([1, 2])
          with c1:
            status = st.selectbox(
                "Compliant",
                ["Yes", "No", "N/A"],
                index=None,
                key=f"status_{code}",
                placeholder="Pilih...",
                label_visibility="collapsed",
            )
          with c2:
            remark = ""
            if status == "Yes" and code != "1.c":
              default_yes_val = (
                  item["options"][1] if len(item["options"]) > 1 else ""
              )
              st.markdown(
                  f"""<div style="padding: 6px 12px; background: rgba(14, 165, 233, 0.15); border: 1px solid rgba(14, 165, 233, 0.4); border-radius: 4px; font-weight: 500; font-size: 14px; color: #38bdf8; white-space: pre-wrap;">Remark: {default_yes_val} </div>""",
                  unsafe_allow_html=True,
              )
              remark = default_yes_val
            elif status == "N/A":
              st.markdown(
                  "<div"
                  ' style="padding: 6px 12px; background: rgba(100, 116, 139,'
                  ' 0.2); border-radius: 4px; font-weight: 500; font-size: 14px;'
                  ' color: #cbd5e1;">Remark: NILL </div>',
                  unsafe_allow_html=True,
              )
              remark = "NILL"
            else:
              remark_choice = st.selectbox(
                  "Pilih Remark",
                  item["options"],
                  index=None,
                  key=f"remark_choice_{code}",
                  placeholder="Pilih Remark...",
                  label_visibility="collapsed",
              )
              if code == "1.c" and remark_choice == "Input Suhu & Kelembapan":
                sub_c1, sub_c2 = st.columns(2)
                with sub_c1:
                  temp_val = st.text_input(
                      "Suhu (°C)",
                      value="23.1",
                      key=f"temp_val_{code}",
                      placeholder="Suhu e.g. 23.1",
                  )
                with sub_c2:
                  hum_val = st.text_input(
                      "Kelembapan (%)",
                      value="64",
                      key=f"hum_val_{code}",
                      placeholder="Hum e.g. 64",
                  )
                remark = f"Temp :{temp_val} C\nHumidity : {hum_val} %\n\nPN : HTC-2\nSN : LSN08260028\nVUT : 3 Sep 2027"
              elif remark_choice == "Lainnya":
                remark = st.text_area(
                    "Ketik Remark Multi-baris",
                    placeholder="Ketik catatan manual di sini...",
                    key=f"remark_custom_{code}",
                    label_visibility="collapsed",
                )
              elif (
                  remark_choice
                  and remark_choice
                  not in ["-- Pilih Remark --", "-- Pilih Status --"]
              ):
                remark = remark_choice

          st.session_state.audit_data[code] = {
              "status": status,
              "remark": remark,
          }
          st.write("")
    else:
      for item in items_in_main:
        code = item["code"]
        st.markdown(
            f'<div class="question-text">{item["desc"]}</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([1, 2])
        with c1:
          status = st.selectbox(
              "Compliant",
              ["Yes", "No", "N/A"],
              index=None,
              key=f"status_{code}",
              placeholder="Pilih...",
              label_visibility="collapsed",
          )
        with c2:
          remark = ""
          if status == "Yes":
            default_yes_val = (
                item["options"][1] if len(item["options"]) > 1 else ""
            )
            st.markdown(
                f"""<div style="padding: 6px 12px; background: rgba(14, 165, 233, 0.15); border: 1px solid rgba(14, 165, 233, 0.4); border-radius: 4px; font-weight: 500; font-size: 14px; color: #38bdf8; white-space: pre-wrap;">Remark: {default_yes_val}</div>""",
                unsafe_allow_html=True,
            )
            remark = default_yes_val
          elif status == "N/A":
            st.markdown(
                "<div"
                ' style="padding: 6px 12px; background: rgba(100, 116, 139,'
                ' 0.2); border-radius: 4px; font-weight: 500; font-size: 14px;'
                ' color: #cbd5e1;">Remark: NILL </div>',
                unsafe_allow_html=True,
            )
            remark = "NILL"
          else:
            remark_choice = st.selectbox(
                "Pilih Remark",
                item["options"],
                index=None,
                key=f"remark_choice_{code}",
                placeholder="Pilih Remark...",
                label_visibility="collapsed",
            )
            if remark_choice == "Lainnya":
              remark = st.text_area(
                  "Ketik Remark Multi-baris",
                  placeholder="Ketik catatan manual di sini...",
                  key=f"remark_custom_{code}",
                  label_visibility="collapsed",
              )
            elif (
                remark_choice
                and remark_choice not in ["-- Pilih Remark --", "-- Pilih Status --"]
            ):
              remark = remark_choice

        st.session_state.audit_data[code] = {"status": status, "remark": remark}
        st.write("")

st.markdown("---")
submitted_preview = st.button("REVIEW RESULT AUDIT", use_container_width=True)

if submitted_preview:
  if not audit_date:
    st.warning("⚠️ Harap isi tanggal audit dengan lengkap!")
  else:
    template_filename = "Self Audit Checklist Store & SO.pdf"

    try:
      template = PdfReader(template_filename)
      output = PdfWriter()
      date_str = format_tanggal_indo(audit_date)

      page_packets = [BytesIO() for _ in range(len(template.pages))]
      canvases = [canvas.Canvas(pkt, pagesize=A4) for pkt in page_packets]

      for i, page in enumerate(template.pages):
        canvases[i].setFont("Times-Roman", 9)
        canvases[i].drawString(310, 704, str(date_str))
        if i == 4:
          canvases[i].drawString(96, 290, f"TKG, {date_str}")

      for item in checklist_points:
        code = item["code"]
        page_idx = item["page"]
        y = item["y"]
        y_remark = item["y_remark"]
        x_yes = item["x_yes"]
        x_no = item["x_no"]
        x_na = item["x_na"]
        x_remark = item["x_remark"]

        data_item = st.session_state.audit_data.get(
            code, {"status": None, "remark": ""}
        )
        status = data_item["status"]
        remark = data_item["remark"]

        if status == "Yes":
          canvases[page_idx].drawString(x_yes, y, "✓")
        elif status == "No":
          canvases[page_idx].drawString(x_no, y, "✓")
        elif status == "N/A":
          canvases[page_idx].drawString(x_na, y, "✓")

        if remark:
          if "\n" in remark:
            text_obj = canvases[page_idx].beginText(x_remark, y_remark)
            text_obj.setFont("Helvetica", 8)
            text_obj.setLeading(9)
            for line in remark.split("\n"):
              text_obj.textLine(line)
            canvases[page_idx].drawText(text_obj)
          else:
            canvases[page_idx].drawString(x_remark, y_remark, str(remark))

      for i, page in enumerate(template.pages):
        canvases[i].save()
        page_packets[i].seek(0)
        overlay_pdf = PdfReader(page_packets[i])
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)

      result = BytesIO()
      output.write(result)
      result.seek(0)
      st.session_state.pdf_data = result.getvalue()

      filename_date_str = audit_date.strftime("%Y%m%d")
      st.session_state.filename = (
          f"{filename_date_str} Self Audit Checklist Store & SO TKG.pdf"
      )
      st.session_state.pdf_generated = True

    except FileNotFoundError:
      st.error(f"⚠️ File template '{template_filename}' tidak ditemukan.")

# --- TAMPILKAN PREVIEW PDF ---
if st.session_state.get("pdf_generated", False):
  st.markdown("---")
  st.success("✅ **AUDIT RESULT SUDAH KELUAR!** SILAKAN CEK PREVIEW DIBAWAH.")

  b64 = base64.b64encode(st.session_state.pdf_data).decode("utf-8")
  filename = st.session_state.filename

  st.markdown(
      f"""
        <div style="text-align:center; margin-bottom:15px;">
            <a href="data:application/pdf;base64,{b64}" 
               download="{filename}"
               style="background:#2563eb; color:white; padding:10px 20px; border-radius:8px;
                      font-weight:600; text-decoration:none;">⬇ DOWNLOAD LOKAL PDF</a>
        </div>
        <iframe src="data:application/pdf;base64,{b64}" width="100%" height="700px" 
                style="border:1px solid #ccc; border-radius:10px; margin-bottom:20px;"></iframe>
        """,
      unsafe_allow_html=True,
  )

  col_a, col_b = st.columns(2)
  with col_a:
    if st.button(
        "🚀 INPUT HASIL AUDIT KE GOOGLE DRIVE (OTOMATIS)",
        use_container_width=True,
    ):
      with st.spinner("Sedang mengunggah file ke Google Drive..."):
        payload = {"file_data": b64, "filename": filename}
        try:
          response = requests.post(
              GOOGLE_APPS_SCRIPT_URL, json=payload, timeout=30
          )
          response.raise_for_status()
          res_json = response.json()
          if res_json.get("status") == "success":
            st.success("✅ BERHASIL TERKIRIM KE GOOGLE DRIVE!")
            if drive_link := res_json.get("file_url"):
              st.markdown(f"🔗 **[CEK FILE DI G DRIVE]({drive_link})**")
          else:
            st.error(f"⚠️ Upload gagal: {res_json.get('message')}")
        except Exception as exc:
          st.error(f"⚠️ Gagal menghubungkan ke Google Drive: {exc}")

  with col_b:
    if st.button("🔄 EDIT / INPUT BARU", use_container_width=True):
      st.session_state.pdf_generated = False
      st.rerun()

st.markdown(
    "<hr><p style='text-align:center;color:#94a3b8;'>Dibuat oleh nomnom_</p>",
    unsafe_allow_html=True,
)