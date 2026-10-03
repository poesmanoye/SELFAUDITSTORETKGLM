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

# URL Web App dari Google Apps Script yang sudah di-deploy
GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwfa1C-Defh98DPxXqHivE8g4Ok67RBlXrJHWKeyQfdbJLElfdImHlJPrEM9yBORMD7fQ/exec"


# --- Helper Fungsi Nama Bulan Bahasa Indonesia ---
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
  hari = dt.day
  bulan = BULAN_INDONESIA[dt.month]
  tahun = dt.year
  return f"{hari} {bulan} {tahun}"


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
      st.success("Login berhasil, Selamat mengerjakan Audit wkwkwkw!")
      st.rerun()
    else:
      st.error("Anda terpantau belum minum kopi hari ini!")
  st.stop()
# === END LOGIN SYSTEM ===

# --- CSS Styling & Header ---
st.markdown(
    """
    <style>
        h1 a, h2 a, h3 a { display: none !important; }
        .header-container h1 { color: #FF0000 !important; font-weight: 900 !important; margin-bottom: 6px !important; }
        .header-container p { font-size: 16px !important; color: #666 !important; margin-top: 0px !important; }
        
        div[data-baseweb="select"] div {
            white-space: pre-wrap !important;
        }
        
        .priority-box {
            background-color: rgba(59, 130, 246, 0.12);
            border-left: 5px solid #3b82f6;
            padding: 12px 14px;
            border-radius: 6px;
            margin-bottom: 15px;
        }
        
        .regular-box {
            padding: 12px 14px;
            border-radius: 6px;
            margin-bottom: 15px;
        }
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

checklist_points = [
    # Halaman 1 (Index 0)
    {
        "code": "1.a",
        "desc": "Room Layout: Does actual room layout conform to approved plan?",
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
        "code": "1.b",
        "desc": "Code Location: What is location codes used in store area?",
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
        "code": "1.c",
        "desc": "Temperature & Humidity: Ventilation good & control devices valid?",
        "page": 0,
        "y": 470,
        "y_remark": 495,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": [
            "-- Pilih Remark --",
            "Input Suhu & Kelembapan Saja",
            "NILL",
            "Good",
            "Lainnya",
        ],
    },
    {
        "code": "1.d_1",
        "desc": "Segregation (1): Is there proper segregation applied?",
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
        "code": "1.d_2",
        "desc": "Segregation (2): Between aircraft parts and non-aircraft parts",
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
        "code": "1.d_3",
        "desc": "Segregation (3): Between serviceable and unserviceable parts",
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
        "code": "1.d_4",
        "desc": "Segregation (4): Are bin segregation clearly marked?",
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
        "code": "1.e",
        "desc": "Cleanliness: Are store areas clean and bin segregation marked?",
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
        "code": "1.f_1",
        "desc": (
            "Security (1): The door is equipped with a fingerprint lock and remains"
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
    # Halaman 2 (Index 1)
    {
        "code": "1.g_1",
        "desc": "Security (1): is the entire store area covered by CCTV ?",
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
        "code": "1.g_2",
        "desc": (
            "Security (2): CCTV pointed entrance area, Shelf and part in the front"
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
        "code": "1.g_3",
        "desc": (
            "Security (3): CCTV pointed at the shelves and stored items, covering"
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
        "code": "1.g_4",
        "desc": (
            "Security (4): CCTV pointed the counter, preparation area and item"
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
        "code": "1.h",
        "desc": "Safety: Fire extinguishers & sprinklers up to date & good?",
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
        "code": "1.i",
        "desc": "Safety: Emergency exits clear & exit signs good?",
        "page": 1,
        "y": 330,
        "y_remark": 330,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEAR AND GOOD", "NILL", "Lainnya"],
    },
    {
        "code": "2.a_1",
        "desc": (
            "TO Receiving (1): Are asset and spare part received by Store"
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
        "code": "2.a_2",
        "desc": (
            "TO Receiving (2): eMRO system updated real time as per actual"
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
    # Halaman 3 (Index 2)
    {
        "code": "2.a_3",
        "desc": (
            "TO Receiving (3): Shipper location and contact person are clearly"
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
        "code": "2.a_4",
        "desc": (
            "TO Receiving (4): Received items are completed with Tag/label?"
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
        "code": "2.b_1",
        "desc": (
            "RTS Part (1): Are all Spare Part received ex Aircraft, registered"
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
        "code": "2.b_2",
        "desc": (
            "RTS Part (2): Return date are real time updated or within time"
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
        "code": "2.b_3",
        "desc": (
            "RTS Part (3): Giver and receiver name and ID are clearly noted?"
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
        "code": "2.c_1",
        "desc": (
            "Tool In (1): Are all tools returned to Store updated into eMRO"
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
        "code": "2.c_2",
        "desc": "Tool In (2): Loan return date are real time updated?",
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
        "code": "2.c_3",
        "desc": (
            "Tool In (3): The name and ID of person who returns the tool are"
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
        "code": "2.c_4",
        "desc": (
            "Tool In (4): Are all tools returned to Store in a clean condition?"
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
        "code": "2.d_1",
        "desc": "ESDS Placement (1): Are ESDS system implemented?",
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
        "code": "2.d_2",
        "desc": "ESDS Placement (2): Personnel understand and has the awareness?",
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
        "code": "2.d_3",
        "desc": "ESDS Placement (3): Bins are clearly marked?",
        "page": 2,
        "y": 105,
        "y_remark": 105,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEARLY MARKED", "NILL", "Lainnya"],
    },
    # Halaman 4 (Index 3)
    {
        "code": "2.d_4",
        "desc": "ESDS Placement (3): Safety equipment are available?",
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
        "code": "2.e_1",
        "desc": (
            "TO Creation (1): Are asset and spare part sent by Store completed"
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
        "code": "2.e_2",
        "desc": (
            "TO Creation (2): eMRO system updated real time as per actual"
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
        "code": "2.e_3",
        "desc": (
            "TO Creation (3): Destinated location and contact person are"
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
        "code": "2.f_1",
        "desc": (
            "Part Issuance (1): Are all asset and spare part given to be"
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
        "code": "2.f_2",
        "desc": (
            "Part Issuance (2): Issued date are real time updated or within time"
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
        "code": "2.f_3",
        "desc": (
            "Part Issuance (3): Giver and receiver name and ID are clearly"
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
        "code": "2.g_1",
        "desc": (
            "Tool Out (1): Are all tools lend by Store recorded into eMRO"
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
        "code": "2.g_2",
        "desc": "Tool Out (2): Loan date are real time updated?",
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
        "code": "2.g_3",
        "desc": "Tool Out (3): Loaner name and ID are clearly noted?",
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
        "code": "2.g_4",
        "desc": "Tool Out (4): Are tools lend by Store in a clean condition?",
        "page": 3,
        "y": 131,
        "y_remark": 131,
        "x_yes": 380,
        "x_no": 410,
        "x_na": 441,
        "x_remark": 470,
        "options": ["-- Pilih Remark --", "CLEAN", "NILL", "Lainnya"],
    },
    # Halaman 5 (Index 4)
    {
        "code": "3.a",
        "desc": "eMRO User: Check conformity of User ID and access module?",
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
        "code": "3.b",
        "desc": (
            "Binning Check: Check the Conformity of total actual bin with total"
            " bin and bin names registered on the system?"
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
        "code": "3.c",
        "desc": "Transaction Check: Check transaction records at store for last year?",
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

# --- FORM INPUT UTAMA (Interaktif Real-Time) ---
st.subheader("📝 1. TANGGAL AUDIT")
audit_date = st.date_input("Audit Date")

st.markdown("---")
st.subheader("✅ 2. FORM CHECKLIST & REMARK")
st.info(
    "Pilih status Compliant (Yes / No / N/A) dan pilih/ketik remark pada setiap"
    " poin."
)

audit_data = {}
for item in checklist_points:
  code = item["code"]

  is_priority = (
      code == "1.c"
      or code == "1.h"
      or code.startswith("2.a")
      or code.startswith("2.b")
      or code.startswith("2.c")
      or code.startswith("2.e")
      or code.startswith("2.f")
      or code.startswith("2.g")
  )

  box_class = "priority-box" if is_priority else "regular-box"

  with st.container():
    st.markdown(
        f"""
            <div class="{box_class}">
                <b>[{code}]</b> {item['desc']}
            </div>
            """,
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
            f"""<div style="padding: 6px 12px; background: #e0f2fe; border: 1px solid #bae6fd; border-radius: 4px; font-weight: 500; font-size: 14px; color: #0369a1; white-space: pre-wrap;">Remark: {default_yes_val} (Otomatis karena YES)</div>""",
            unsafe_allow_html=True,
        )
        remark = default_yes_val

      elif status == "N/A":
        st.markdown(
            "<div"
            ' style="padding: 6px 12px; background: #e2e8f0; border-radius:'
            ' 4px; font-weight: 500; font-size: 14px; color:'
            ' #475569;">Remark: NILL (Otomatis karena N/A)</div>',
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

        if code == "1.c" and remark_choice == "Input Suhu & Kelembapan Saja":
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
              placeholder=(
                  "Ketik catatan manual di sini (bisa tekan Enter untuk baris"
                  " baru)..."
              ),
              key=f"remark_custom_{code}",
              label_visibility="collapsed",
          )
        elif (
            remark_choice
            and remark_choice
            not in ["-- Pilih Remark --", "-- Pilih Status --"]
        ):
          remark = remark_choice

    audit_data[code] = {"status": status, "remark": remark}
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

      # Pengaturan Font per Halaman (Tanggal di Halaman 5 / Index 4 di-set Bold, 10 pt)
      for i, page in enumerate(template.pages):
        if i == 4:
          canvases[i].setFont("Helvetica-Bold", 10)
          canvases[i].drawString(96, 290, str(date_str))
          canvases[i].setFont("Helvetica", 9)  # Kembalikan ke normal
        else:
          canvases[i].setFont("Helvetica", 9)

      # Tanggal utama di halaman pertama
      canvases[0].drawString(310, 704, str(date_str))

      for item in checklist_points:
        code = item["code"]
        page_idx = item["page"]
        y = item["y"]
        y_remark = item["y_remark"]
        x_yes = item["x_yes"]
        x_no = item["x_no"]
        x_na = item["x_na"]
        x_remark = item["x_remark"]

        status = audit_data[code]["status"]
        remark = audit_data[code]["remark"]

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
      st.error(
          f"⚠️ File template '{template_filename}' tidak ditemukan di folder"
          " yang sama."
      )

# --- TAMPILKAN PREVIEW PDF ---
if st.session_state.get("pdf_generated", False):
  st.markdown("---")
  st.success(
      "✅ **AUDIT RESULT SUDAH KELUAR!** SILAKAN CEK HASIL AUDIT"
      " PREVIEW ADA DIBAWAH."
  )

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
            st.success("✅ HASIL AUDIT BERHASIL TERKIRIM KE GOOGLE DRIVE!")
            drive_link = res_json.get("file_url")
            if drive_link:
              st.markdown(
                  f"🔗 **[SILAKAN CEK HASIL AUDIT DI GDRIVE TKG"
                  f" LM]({drive_link})**"
              )
          else:
            st.error(
                f"⚠️ Upload gagal: {res_json.get('message', 'Kesalahan server.')}"
            )
        except Exception as exc:
          st.error(f"⚠️ Gagal menghubungkan ke Google Drive API: {exc}")

  with col_b:
    if st.button("🔄 EDIT DATA / INPUT BARU DATA", use_container_width=True):
      st.session_state.pdf_generated = False
      st.rerun()

# Footer Aplikasi
st.markdown(
    "<hr><p style='text-align:center;color:#94a3b8;'>Dibuat oleh nomnom_</p>",
    unsafe_allow_html=True,
)