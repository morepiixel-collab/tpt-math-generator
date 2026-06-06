import streamlit as st
from fpdf import FPDF
import random
import tempfile
import os
import fitz

# ==========================================
# 1. คลาสสำหรับสร้างเอกสาร PDF (Super Fun Layout)
# ==========================================
class TpTWorksheet(FPDF):
    def __init__(self, level, topic, theme, is_answer_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.level = level
        self.topic = topic
        self.theme = theme
        self.is_answer_key = is_answer_key

    def header(self):
        # กรอบกระดาษขอบหนา สไตล์การ์ตูน
        self.set_line_width(1.0)
        self.set_draw_color(100, 100, 255) # กรอบสีฟ้า
        self.rect(10, 10, 195.9, 259.4)
        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        
        # พื้นหลังส่วนหัวกระดาษ (Header Banner)
        self.set_xy(15, 15)
        self.set_fill_color(255, 235, 153) # สีเหลืองพาสเทล
        self.set_draw_color(255, 200, 0)
        self.rect(15, 15, 140, 25, style="DF")
        
        # กล่องให้คะแนน (Score Box)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(255, 100, 100) # ขอบสีแดง
        self.rect(160, 15, 40, 25, style="DF")
        self.set_font("helvetica", "B", 10)
        self.set_text_color(255, 100, 100)
        self.set_xy(160, 17)
        self.cell(40, 5, "SCORE / STARS", align="C")
        self.set_text_color(0, 0, 0)
        
        # พิมพ์ชื่อและวันที่
        self.set_font("helvetica", "B", 12)
        self.set_xy(18, 18)
        self.cell(100, 8, "Name: __________________________")
        self.set_xy(18, 28)
        self.cell(100, 8, "Date: _________________")
        
        # ชื่อหัวข้อใบงาน
        self.set_xy(15, 45)
        self.set_font("helvetica", "B", 22)
        title_text = f"{self.topic}"
        if self.is_answer_key:
            title_text += " [ANSWER KEY]"
            self.set_text_color(220, 53, 69)
        else:
            self.set_text_color(40, 100, 200) # สีน้ำเงินเข้ม
            
        self.cell(185, 10, title_text, border=0, align="C")
        self.set_text_color(0, 0, 0)
        self.set_y(60)

    def footer(self):
        self.set_y(-16)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}  |  {self.theme}  |  Ready for TpT", align="C")

# ==========================================
# 2. ฟังก์ชันเตรียมข้อมูลโจทย์
# ==========================================
def generate_questions(level, topic, num_q):
    questions = []
    for _ in range(num_q):
        if topic == "Counting (1-10)":
            num = random.randint(1, 10)
            questions.append({"type": "counting", "text": "Count and write:", "count": num, "ans": str(num)})
        elif topic == "Number Tracing":
            num = random.randint(1, 10)
            questions.append({"type": "tracing", "text": "Trace:", "num": num, "ans": str(num)})
        else:
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            questions.append({"type": "math", "text": f"{a}  +  {b}  =", "ans": str(a + b)})
    return questions

# ==========================================
# 3. ฟังก์ชันสร้างไฟล์ PDF (ระบบวาดภาพกราฟิก)
# ==========================================
def render_pdf_content(pdf, questions):
    pdf.add_page()
    
    # ชุดสีพาสเทลสำหรับรูปทรง (ชมพู, ฟ้า, เขียว, เหลือง, ม่วง)
    color_palette = [
        (255, 153, 153), (102, 204, 255), 
        (102, 255, 153), (255, 220, 100), (204, 153, 255)
    ]
    shapes = ['circle', 'square', 'triangle']
    
    for i, q in enumerate(questions):
        y_start = pdf.get_y()
        if y_start > 240:
            pdf.add_page()
            y_start = pdf.get_y()

        # วาดกรอบการ์ดโจทย์ (มุมมนจำลองโดยการใช้สีอ่อน)
        if i % 2 == 0:
            pdf.set_fill_color(245, 250, 255) # สีฟ้าอ่อนมากสลับขาว
        else:
            pdf.set_fill_color(255, 250, 245) # สีส้มอ่อนมากสลับขาว
            
        pdf.set_draw_color(220, 220, 220)
        pdf.set_line_width(0.5)
        pdf.rect(15, y_start, 185, 22, style="DF")

        # เลขข้อ (สีสันสดใส)
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(255, 100, 100) # สีแดงแตงโม
        pdf.set_xy(18, y_start + 7)
        pdf.cell(12, 8, f"{i + 1}.")
        pdf.set_text_color(50, 50, 50)

        # เนื้อหาโจทย์
        pdf.set_xy(32, y_start + 7)
        
        if q["type"] == "counting":
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(45, 8, q["text"])
            cx = pdf.get_x()
            
            # สุ่มรูปทรงและสี
            shape_type = random.choice(shapes)
            r, g, b = random.choice(color_palette)
            pdf.set_fill_color(r, g, b)
            pdf.set_draw_color(100, 100, 100)
            pdf.set_line_width(0.4)
            
            # วาดรูปทรงเรขาคณิตสีสันสดใส
            for j in range(q["count"]):
                sx = cx + (j * 10)
                sy = y_start + 8
                if shape_type == 'circle':
                    pdf.ellipse(sx, sy, 7, 7, style="DF")
                elif shape_type == 'square':
                    pdf.rect(sx, sy, 7, 7, style="DF")
                elif shape_type == 'triangle':
                    pdf.polygon(((sx+3.5, sy), (sx+7, sy+7), (sx, sy+7)), style="DF")
                    
        elif q["type"] == "tracing":
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(30, 8, q["text"])
            pdf.set_font("helvetica", "B", 26)
            pdf.set_text_color(200, 200, 200) # สีเทาอ่อนสำหรับหัดเขียน
            pdf.cell(100, 7, f"{q['num']}      {q['num']}      {q['num']}      {q['num']}")
            pdf.set_text_color(50, 50, 50)
            
        elif q["type"] == "math":
            pdf.set_font("helvetica", "B", 20)
            pdf.cell(100, 8, q["text"], align="C")

        # วาด "ฟองสบู่คำตอบ" (Bubble Answer Box)
        pdf.set_draw_color(150, 200, 255) # ขอบสีฟ้า
        pdf.set_fill_color(255, 255, 255)
        pdf.set_line_width(0.8)
        pdf.ellipse(175, y_start + 3.5, 15, 15, style="DF")

        # ถ้าเป็นหน้าเฉลย ให้ใส่คำตอบในฟองสบู่
        if pdf.is_answer_key:
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(220, 53, 69)
            pdf.set_xy(175, y_start + 5)
            pdf.cell(15, 12, q["ans"], align="C")
            pdf.set_text_color(0, 0, 0)

        pdf.set_y(y_start + 26)

def create_pdf(level, topic, theme, num_q, include_ans):
    questions = generate_questions(level, topic, num_q)
    output_files = {}

    pdf_student = TpTWorksheet(level, topic, theme, is_answer_key=False)
    render_pdf_content(pdf_student, questions)
    fd, path_student = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf_student.output(path_student)
    output_files["student"] = path_student

    if include_ans:
        pdf_ans = TpTWorksheet(level, topic, theme, is_answer_key=True)
        render_pdf_content(pdf_ans, questions)
        fd, path_ans = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        pdf_ans.output(path_ans)
        output_files["answer"] = path_ans

    return output_files

def display_pdf_as_image(file_path):
    doc = fitz.open(file_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, use_container_width=True)

# ==========================================
# 4. หน้าต่างแสดงผล Streamlit
# ==========================================
st.set_page_config(page_title="Kids Math Generator", page_icon="🎨", layout="wide")
st.title("🎨 Super Fun Math Worksheet Generator")
st.markdown("ระบบสร้างใบงานคณิตศาสตร์สีสันสดใส สำหรับเด็ก K1-K3")

with st.sidebar:
    st.header("⚙️ Settings")
    level = st.selectbox("Grade Level:", ["K1 (Kindergarten 1)", "K2 (Kindergarten 2)"])
    topic = st.selectbox("Topic:", ["Counting (1-10)", "Number Tracing", "Basic Addition"])
    theme = st.selectbox("Theme:", ["Colorful Shapes", "Pastel Magic"])
    num_q = st.slider("Questions per page:", min_value=4, max_value=8, value=7)
    include_ans = st.checkbox("Generate Answer Key", value=True)
    st.markdown("---")
    generate_btn = st.button("✨ Generate Fun PDF", use_container_width=True, type="primary")

if generate_btn:
    with st.spinner("Drawing colorful shapes..."):
        try:
            files = create_pdf(level, topic, theme, num_q, include_ans)
            st.success("✅ Worksheets generated! Look at the colorful preview below.")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(files["student"], "rb") as f:
                    st.download_button("📥 Download Fun Worksheet", data=f, file_name="Fun_Worksheet.pdf", mime="application/pdf", use_container_width=True)
            if include_ans and "answer" in files:
                with col2:
                    with open(files["answer"], "rb") as f:
                        st.download_button("📥 Download Answer Key", data=f, file_name="Answer_Key.pdf", mime="application/pdf", use_container_width=True)
            
            st.markdown("---")
            col_preview1, col_preview2 = st.columns(2)
            with col_preview1:
                st.subheader("👁️ Preview: Student")
                display_pdf_as_image(files["student"])
            if include_ans and "answer" in files:
                with col_preview2:
                    st.subheader("👁️ Preview: Teacher")
                    display_pdf_as_image(files["answer"])
        except Exception as e:
            st.error(f"Error: {e}")
