import streamlit as st
from fpdf import FPDF
import tempfile
import os
import random

# ==========================================
# 1. คลาสสำหรับการสร้าง PDF (FPDF)
# ==========================================
class WorksheetPDF(FPDF):
    def header(self):
        # สร้างกรอบรอบกระดาษ (Border) - ห่างจากขอบด้านละ 10mm
        self.rect(10, 10, 190, 277)
        # ขอบชั้นในให้ดูน่ารักขึ้น (Double Border)
        self.rect(12, 12, 186, 273)
        
        # ตั้งค่าฟอนต์ส่วนหัว (ชื่อ และ วันที่)
        self.set_font("helvetica", "B", 14)
        
        # พื้นที่เว้นด้านบน
        self.set_y(20)
        self.cell(90, 10, "Name: ________________________", border=0, align="L")
        self.cell(90, 10, "Date: _______________", border=0, align="R")
        self.ln(20) # ขึ้นบรรทัดใหม่

    def footer(self):
        # ลิขสิทธิ์ / ลายน้ำที่ด้านล่างกระดาษ (สำคัญสำหรับ TpT)
        self.set_y(-20)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, "(c) Your TpT Store Name - Math Worksheet Generator", align="C")

# ==========================================
# 2. ฟังก์ชันสร้างเนื้อหาใบงาน (Logic)
# ==========================================
def generate_worksheet(level, topic, theme, num_questions, is_answer_key=False):
    pdf = WorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # ส่วนหัวข้อใบงาน (Title)
    pdf.set_font("helvetica", "B", 20)
    title_text = f"{level} - {topic}"
    if is_answer_key:
        title_text += " (ANSWER KEY)"
    pdf.cell(0, 15, title_text, align="C", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 14)

    # สร้างคำถามตามระดับชั้น
    for i in range(1, num_questions + 1):
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"Question {i}:", ln=True)
        pdf.set_font("helvetica", "", 12)
        
        # --- K1: อนุบาล 1 ---
        if level == "K1 (อนุบาล 1)":
            if topic == "นับจำนวน (Counting 1-10)":
                num = random.randint(1, 10)
                pdf.cell(0, 10, f"Count the {theme}s and write the number:", ln=True)
                # พื้นที่เว้นไว้ให้ใส่รูปจาก Nano Banana
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 20, f"[ Insert {num} images of {theme} here ]", align="C", ln=True)
                pdf.set_text_color(0, 0, 0)
                
                if is_answer_key:
                    pdf.set_text_color(255, 0, 0)
                    pdf.cell(0, 10, f"Answer: {num}", ln=True)
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(0, 10, "Answer: ____", ln=True)

        # --- K2: อนุบาล 2 ---
        elif level == "K2 (อนุบาล 2)":
            if topic == "บวกเลขพื้นฐาน (Basic Addition to 10)":
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                pdf.cell(0, 10, f"Add the {theme}s:", ln=True)
                
                # Placeholder สำหรับรูปภาพ
                pdf.set_text_color(150, 150, 150)
                pdf.cell(0, 20, f"[ {a} {theme} images ]   +   [ {b} {theme} images ]   =   ?", align="C", ln=True)
                pdf.set_text_color(0, 0, 0)
                
                if is_answer_key:
                    pdf.set_text_color(255, 0, 0)
                    pdf.cell(0, 10, f"Answer: {a + b}", ln=True)
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(0, 10, f"{a} + {b} = ____", ln=True)

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
                
                pdf.cell(0, 10, f"Solve the math problem. (Theme: {theme} decoration)", ln=True)
                
                if is_answer_key:
                    pdf.set_text_color(255, 0, 0)
                    pdf.cell(0, 10, f"{a} {op} {b} = {ans}", ln=True)
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(0, 10, f"{a} {op} {b} = ____", ln=True)
        
        pdf.ln(10) # ระยะห่างระหว่างข้อ

    # บันทึกไฟล์ลง Temp Directory เพื่อให้ Streamlit โหลดได้
    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    file_path = os.path.join(temp_dir, f"{file_prefix}{level[:2]}_{theme}.pdf")
    pdf.output(file_path)
    
    return file_path

# ==========================================
# 3. Streamlit User Interface (UI)
# ==========================================
st.set_page_config(page_title="TpT Math Worksheet Generator", page_icon="🖍️", layout="wide")

st.title("🖍️ TpT Math Worksheet Generator (K1 - K3)")
st.markdown("สร้างใบงานคณิตศาสตร์คุณภาพสูง พร้อมนำไปขายบน Teachers Pay Teachers")

# Sidebar สำหรับตั้งค่า
st.sidebar.header("⚙️ Worksheet Settings")

level = st.sidebar.selectbox("1. ระดับชั้น (Level):", ["K1 (อนุบาล 1)", "K2 (อนุบาล 2)", "K3 (อนุบาล 3)"])

# ปรับเนื้อหาตามระดับชั้น
if level == "K1 (อนุบาล 1)":
    topics = ["นับจำนวน (Counting 1-10)", "ฝึกเขียนตามรอยปะ (Tracing)"]
elif level == "K2 (อนุบาล 2)":
    topics = ["บวกเลขพื้นฐาน (Basic Addition to 10)", "เปรียบเทียบขนาด (Big/Small)"]
else:
    topics = ["บวก/ลบเลข (Addition/Subtraction to 50)", "อนุกรม (Patterns)"]

topic = st.sidebar.selectbox("2. ประเภทเนื้อหา (Topic):", topics)

theme = st.sidebar.selectbox("3. ธีม / รูปภาพประกอบ (Theme):", 
                             ["Animals (สัตว์น่ารัก)", "Space (อวกาศ)", "Dinosaur (ไดโนเสาร์)", "Underwater (ใต้ทะเล)"])

num_q = st.sidebar.slider("4. จำนวนข้อต่อหน้า (Questions):", min_value=1, max_value=10, value=5)

include_answer_key = st.sidebar.checkbox("✅ สร้างหน้าเฉลย (Answer Key)", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **TpT Pro Tip:** ผู้ซื้อบน TpT ชื่นชอบใบงานที่มีหน้าเฉลย (Answer Key) เพราะช่วยลดเวลาตรวจการบ้านให้คุณครูได้มาก!")

# ส่วนหลัก (Main Content)
st.write("---")
st.subheader("พรีวิวการตั้งค่าของคุณ:")
col1, col2 = st.columns(2)
col1.write(f"**ระดับชั้น:** {level}")
col1.write(f"**เนื้อหา:** {topic}")
col2.write(f"**ธีม:** {theme}")
col2.write(f"**จำนวนข้อ:** {num_q} ข้อ")

if st.button("🚀 Generate PDF Worksheet", use_container_width=True):
    with st.spinner("กำลังสร้างใบงานและจัดหน้ากระดาษ..."):
        # สร้างใบงานปกติ
        pdf_path = generate_worksheet(level, topic, theme, num_q, is_answer_key=False)
        
        # ถ่ายโอนไฟล์ไบนารีเพื่อสร้างปุ่มดาวน์โหลด
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        st.success("✨ สร้างใบงานสำเร็จแล้ว!")
        
        st.download_button(
            label="📥 ดาวน์โหลดใบงาน (PDF)",
            data=pdf_bytes,
            file_name=f"Math_Worksheet_{level[:2]}_{theme}.pdf",
            mime="application/pdf",
        )
        
        # สร้างหน้าเฉลยถ้าเลือกไว้
        if include_answer_key:
            ans_path = generate_worksheet(level, topic, theme, num_q, is_answer_key=True)
            with open(ans_path, "rb") as ans_file:
                ans_bytes = ans_file.read()
                
            st.download_button(
                label="📥 ดาวน์โหลดหน้าเฉลย (Answer Key PDF)",
                data=ans_bytes,
                file_name=f"Answer_Key_{level[:2]}_{theme}.pdf",
                mime="application/pdf",
                type="secondary"
            )
            
    st.info("📌 หมายเหตุ: ในไฟล์ PDF จะมีการเว้นช่องว่าง [ Insert ... images here ] เอาไว้ เพื่อให้คุณนำไปประกอบร่างต่อกับรูปภาพที่สร้างจาก Nano Banana ครับ")
