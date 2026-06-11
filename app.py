import streamlit as st
from fpdf import FPDF
import tempfile
import os
import random
import urllib.request
import base64

# ==========================================
# 0. ฟังก์ชันดาวน์โหลดฟอนต์ภาษาไทยอัตโนมัติ (Google Fonts)
# ==========================================
def download_thai_fonts():
    """ฟังก์ชันตรวจสอบและดาวน์โหลดฟอนต์ภาษาไทย เพื่อใช้ป้องกัน Error เรื่อง Unicode"""
    fonts = {
        "Sarabun-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf",
        "Sarabun-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    }
    for name, url in fonts.items():
        if not os.path.exists(name):
            try:
                urllib.request.urlretrieve(url, name)
            except Exception as e:
                st.error(f"ไม่สามารถดาวน์โหลดฟอนต์ {name} ได้อัตโนมัติ: {e}")

download_thai_fonts()

# ==========================================
# 1. คลาสสำหรับการสร้าง PDF (FPDF) ที่รองรับภาษาไทย
# ==========================================
class WorksheetPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists("Sarabun-Regular.ttf"):
            self.add_font("Sarabun", style="", fname="Sarabun-Regular.ttf")
        if os.path.exists("Sarabun-Bold.ttf"):
            self.add_font("Sarabun", style="B", fname="Sarabun-Bold.ttf")

    def header(self):
        # สร้างกรอบรอบกระดาษคู่ (Double Border) ตามสไตล์ใบงาน TpT น่ารักๆ
        self.rect(10, 10, 190, 277)
        self.rect(12, 12, 186, 273)
        
        self.set_font("Sarabun", "B", 14)
        self.set_y(20)
        self.cell(90, 10, "Name: ________________________", border=0, align="L")
        self.cell(90, 10, "Date: _______________", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font("Sarabun", "", 10)
        self.cell(0, 10, "(c) Your TpT Store Name - Math Worksheet Generator", align="C")

# ==========================================
# 2. ฟังก์ชันสร้างเนื้อหาใบงาน (Logic)
# ==========================================
def generate_worksheet(level, topic, theme, num_questions, is_answer_key=False):
    pdf = WorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # หัวข้อใบงาน
    pdf.set_font("Sarabun", "B", 20)
    title_text = f"{level} - {topic}"
    if is_answer_key:
        title_text += " (ANSWER KEY)"
    
    pdf.cell(0, 15, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # สร้างคำถามตามระดับชั้น
    for i in range(1, num_questions + 1):
        pdf.set_font("Sarabun", "B", 14)
        pdf.cell(0, 10, f"Question {i}:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Sarabun", "", 14)
        
        # --- K1: อนุบาล 1 ---
        if level == "K1 (อนุบาล 1)":
            if topic == "นับจำนวน (Counting 1-10)":
                num = random.randint(1, 10)
                pdf.cell(0, 10, f"Count the {theme}s and write the number:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 20, f"[ Insert {num} images of {theme} here ]", align="C", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                if is_answer_key:
                    pdf.set_text_color(255, 0, 0)
                    pdf.cell(0, 10, f"Answer: {num}", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(0, 10, "Answer: ____", new_x="LMARGIN", new_y="NEXT")

        # --- K2: อนุบาล 2 ---
        elif level == "K2 (อนุบาล 2)":
            if topic == "บวกเลขพื้นฐาน (Basic Addition to 10)":
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                pdf.cell(0, 10, f"Add the {theme}s:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 20, f"[ {a} {theme} images ]   +   [ {b} {theme} images ]   =   ?", align="C", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                if is_answer_key:
                    pdf.set_text_color(255, 0, 0)
                    pdf.cell(0, 10, f"Answer: {a + b}", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(0, 10, f"{a} + {b} = ____", new_x="LMARGIN", new_y="NEXT")

        # --- K3: อนุบาล 3 ---
        elif level == "K3 (อนุบาล 3)":
            if topic == "บวก/ลบเลข (Addition/Subtraction to 50)":
                is_add = random.choice([True, False])
                if is_add:
                    a = random.randint(10, 30)
                    b = random.randint(1, 20)
                    op, ans = "+", a + b
                else:
                    a = random.randint(20, 50)
                    b = random.randint(1, 19)
                    op, ans = "-", a - b
                pdf.cell(0, 10, f"Solve the math problem. (Theme: {theme})", new_x="LMARGIN", new_y="NEXT")
                if is_answer_key:
                    pdf.set_text_color(255, 0, 0)
                    pdf.cell(0, 10, f"{a} {op} {b} = {ans}", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(0, 10, f"{a} {op} {b} = ____", new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)

    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    file_path = os.path.join(temp_dir, f"{file_prefix}{level[:2]}_{theme}.pdf")
    pdf.output(file_path)
    return file_path

# ==========================================
# 3. ฟังก์ชันสำหรับแสดงพรีวิว PDF บนเว็บ
# ==========================================
def display_pdf_preview(file_path):
    """แปลงไฟล์ PDF เป็น Base64 เพื่อฝังลงใน iframe สำหรับแสดงพรีวิว"""
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # สร้าง HTML iframe สำหรับแสดงผล PDF
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# ==========================================
# 4. Streamlit User Interface (UI)
# ==========================================
st.set_page_config(page_title="TpT Math Worksheet Generator", page_icon="🖍️", layout="wide")

st.title("🖍️ TpT Math Worksheet Generator (K1 - K3)")
st.markdown("ปรับแต่งการตั้งค่าทางซ้ายมือ และกดปุ่มเพื่อดูพรีวิวใบงานจริงได้ทันที")

# Sidebar สำหรับตั้งค่า
st.sidebar.header("⚙️ Worksheet Settings")
level = st.sidebar.selectbox("1. ระดับชั้น (Level):", ["K1 (อนุบาล 1)", "K2 (อนุบาล 2)", "K3 (อนุบาล 3)"])

if level == "K1 (อนุบาล 1)":
    topics = ["นับจำนวน (Counting 1-10)", "ฝึกเขียนตามรอยปะ (Tracing)"]
elif level == "K2 (อนุบาล 2)":
    topics = ["บวกเลขพื้นฐาน (Basic Addition to 10)", "เปรียบเทียบขนาด (Big/Small)"]
else:
    topics = ["บวก/ลบเลข (Addition/Subtraction to 50)", "อนุกรม (Patterns)"]

topic = st.sidebar.selectbox("2. ประเภทเนื้อหา (Topic):", topics)
theme = st.sidebar.selectbox("3. ธีม / รูปภาพประกอบ (Theme):", 
                             ["Animals (สัตว์น่ารัก)", "Space (อวกาศ)", "Dinosaur (ไดโนเสาร์)", "Underwater (ใต้ทะเล)"])
num_q = st.sidebar.slider("4. จำนวนข้อต่อหน้า (Questions):", min_value=1, max_value=10, value=4)
include_answer_key = st.sidebar.checkbox("✅ สร้างหน้าเฉลย (Answer Key)", value=True)

st.sidebar.markdown("---")

# ปุ่มกดสำหรับ Generate และอัปเดต Preview
generate_btn = st.sidebar.button("🚀 Generate & Preview", use_container_width=True)

# ส่วนการแสดงพรีวิวหลัก
st.subheader("🔍 Live Worksheet Preview")

# ตรวจสอบสถานะว่ามีการคลิกสร้างไฟล์หรือยัง
if generate_btn or 'worksheet_path' in st.session_state:
    # หากกดปุ่ม ให้สร้างไฟล์ใหม่และบันทึกลง session_state
    if generate_btn:
        with st.spinner("กำลังเรนเดอร์เอกสารและสร้างพรีวิว..."):
            st.session_state.worksheet_path = generate_worksheet(level, topic, theme, num_q, is_answer_key=False)
            if include_answer_key:
                st.session_state.answer_path = generate_worksheet(level, topic, theme, num_q, is_answer_key=True)
            else:
                st.session_state.answer_path = None

    # สร้างแท็บสำหรับพรีวิว
    tab_list = ["📄 ใบงานหลัก (Worksheet)"]
    if include_answer_key and st.session_state.get('answer_path'):
        tab_list.append("🔑 หน้าเฉลย (Answer Key)")
        
    tabs = st.tabs(tab_list)

    # แท็บที่ 1: พรีวิวใบงานหลัก + ปุ่มโหลด
    with tabs[0]:
        with open(st.session_state.worksheet_path, "rb") as f:
            ws_bytes = f.read()
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ใบงาน (PDF)",
            data=ws_bytes,
            file_name=f"Worksheet_{level[:2]}_{theme}.pdf",
            mime="application/pdf",
            type="primary"
        )
        # แสดงกล่อง PDF Preview
        display_pdf_preview(st.session_state.worksheet_path)

    # แท็บที่ 2: พรีวิวหน้าเฉลย + ปุ่มโหลด (ถ้ามี)
    if include_answer_key and st.session_state.get('answer_path'):
        with tabs[1]:
            with open(st.session_state.answer_path, "rb") as f:
                ans_bytes = f.read()
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์เฉลย (Answer Key PDF)",
                data=ans_bytes,
                file_name=f"Answer_Key_{level[:2]}_{theme}.pdf",
                mime="application/pdf"
            )
            # แสดงกล่อง PDF Preview ของหน้าเฉลย
            display_pdf_preview(st.session_state.answer_path)
else:
    # แสดงกล่องข้อความแนะนำเมื่อยังไม่ได้กด Generate
    st.info("💡 กรุณากดปุ่ม 🚀 Generate & Preview ที่แถบเมนูด้านซ้าย เพื่อแสดงหน้าพรีวิวใบงานและเปิดปุ่มดาวน์โหลดไฟล์ครับ")
