import streamlit as st
from fpdf import FPDF
import random
import tempfile
import os
import fitz

# ==========================================
# 1. คลาสสำหรับสร้างเอกสาร PDF 
# ==========================================
class TpTWorksheet(FPDF):
    def __init__(self, level, topic, theme, is_answer_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.level = level
        self.topic = topic
        self.theme = theme
        self.is_answer_key = is_answer_key

    def header(self):
        self.set_line_width(1.0)
        self.set_draw_color(100, 100, 255) 
        self.rect(10, 10, 195.9, 259.4)
        self.set_line_width(0.3)
        self.set_draw_color(0, 0, 0)
        
        self.set_xy(15, 15)
        self.set_fill_color(255, 235, 153)
        self.set_draw_color(255, 200, 0)
        self.rect(15, 15, 140, 25, style="DF")
        
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(255, 100, 100) 
        self.rect(160, 15, 40, 25, style="DF")
        self.set_font("helvetica", "B", 10)
        self.set_text_color(255, 100, 100)
        self.set_xy(160, 17)
        self.cell(40, 5, "SCORE / STARS", align="C")
        self.set_text_color(0, 0, 0)
        
        self.set_font("helvetica", "B", 12)
        self.set_xy(18, 18)
        self.cell(100, 8, "Name: __________________________")
        self.set_xy(18, 28)
        self.cell(100, 8, "Date: _________________")
        
        self.set_xy(15, 45)
        self.set_font("helvetica", "B", 22)
        title_text = f"{self.topic}"
        if self.is_answer_key:
            title_text += " [ANSWER KEY]"
            self.set_text_color(220, 53, 69)
        else:
            self.set_text_color(40, 100, 200) 
            
        self.cell(185, 10, title_text, border=0, align="C")
        self.set_text_color(0, 0, 0)
        self.set_y(60)

    def footer(self):
        self.set_y(-16)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}  |  {self.theme}  |  Ready for TpT", align="C")

# ==========================================
# 2. ฟังก์ชันเตรียมข้อมูลโจทย์ (ระบบกันโจทย์ซ้ำ)
# ==========================================
def generate_questions(level, topic, num_q):
    questions = []
    
    # สุ่มชุดตัวเลข 1-10 แบบไม่ให้ซ้ำกันเลย สำหรับข้อที่ต้องนับหรือเขียน
    if topic in ["Counting (1-10)", "Number Tracing"]:
        unique_numbers = random.sample(range(1, 11), num_q)
    else:
        unique_numbers = []
        
    used_math_pairs = set() # เก็บโจทย์บวกเลขที่ออกไปแล้ว

    for i in range(num_q):
        if topic == "Counting (1-10)":
            num = unique_numbers[i] # ดึงตัวเลขที่ไม่ซ้ำมาใช้
            
            # สร้างตัวเลือกลวง 2 ตัวที่ไม่ซ้ำกับคำตอบจริง
            choices = [num]
            while len(choices) < 3:
                fake_ans = random.randint(1, 10)
                if fake_ans not in choices:
                    choices.append(fake_ans)
            random.shuffle(choices) # สลับตำแหน่งตัวเลือก
            
            questions.append({
                "type": "counting_choice", 
                "text": "Point, Count & Circle:", 
                "count": num, 
                "choices": choices,
                "ans": str(num)
            })
            
        elif topic == "Number Tracing":
            num = unique_numbers[i]
            questions.append({"type": "tracing", "text": "Trace:", "num": num, "ans": str(num)})
            
        else: # Basic Addition
            # ลูปสุ่มไปเรื่อยๆ จนกว่าจะได้โจทย์ที่ไม่เคยออกในหน้านี้
            while True:
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                pair = (a, b)
                if pair not in used_math_pairs:
                    used_math_pairs.add(pair)
                    questions.append({"type": "math", "text": f"{a}  +  {b}  =", "ans": str(a + b)})
                    break
                    
    return questions

# ==========================================
# 3. ฟังก์ชันสร้างไฟล์ PDF
# ==========================================
def render_pdf_content(pdf, questions):
    pdf.add_page()
    
    color_palette = [
        (255, 153, 153), (102, 204, 255), 
        (102, 255, 153), (255, 220, 100), (204, 153, 255)
    ]
    shapes = ['circle', 'square', 'triangle']
    
    for i, q in enumerate(questions):
        y_start = pdf.get_y()
        card_height = 28 
        if y_start > 230:
            pdf.add_page()
            y_start = pdf.get_y()

        if i % 2 == 0:
            pdf.set_fill_color(245, 250, 255) 
        else:
            pdf.set_fill_color(255, 250, 245) 
            
        pdf.set_draw_color(220, 220, 220)
        pdf.set_line_width(0.5)
        pdf.rect(15, y_start, 185, card_height, style="DF")

        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(255, 100, 100) 
        pdf.set_xy(18, y_start + 10)
        pdf.cell(12, 8, f"{i + 1}.")
        pdf.set_text_color(50, 50, 50)

        pdf.set_xy(30, y_start + 10)
        
        if q["type"] == "counting_choice":
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(50, 8, q["text"])
            
            cx = 85
            shape_type = random.choice(shapes)
            r, g, b = random.choice(color_palette)
            pdf.set_fill_color(r, g, b)
            pdf.set_draw_color(100, 100, 100)
            pdf.set_line_width(0.4)
            
            for j in range(q["count"]):
                row = j // 5  
                col = j % 5
                sx = cx + (col * 11)
                sy = y_start + 6 + (row * 10)
                
                if shape_type == 'circle':
                    pdf.ellipse(sx, sy, 8, 8, style="DF")
                elif shape_type == 'square':
                    pdf.rect(sx, sy, 8, 8, style="DF")
                elif shape_type == 'triangle':
                    pdf.polygon(((sx+4, sy), (sx+8, sy+8), (sx, sy+8)), style="DF")

            pdf.set_font("helvetica", "B", 16)
            for idx, choice in enumerate(q["choices"]):
                bx = 145 + (idx * 16)
                by = y_start + 8
                
                if pdf.is_answer_key and str(choice) == q["ans"]:
                    pdf.set_fill_color(255, 180, 180)
                else:
                    pdf.set_fill_color(255, 255, 255)
                    
                pdf.set_draw_color(150, 150, 200)
                pdf.set_line_width(0.6)
                pdf.ellipse(bx, by, 12, 12, style="DF")
                
                pdf.set_text_color(50, 50, 50)
                pdf.set_xy(bx, by + 2)
                pdf.cell(12, 8, str(choice), align="C")
                    
        elif q["type"] == "tracing":
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(30, 8, q["text"])
            pdf.set_font("helvetica", "B", 26)
            pdf.set_text_color(200, 200, 200) 
            pdf.cell(100, 7, f"{q['num']}      {q['num']}      {q['num']}      {q['num']}")
            pdf.set_text_color(50, 50, 50)
            
        elif q["type"] == "math":
            pdf.set_font("helvetica", "B", 20)
            pdf.cell(100, 8, q["text"], align="C")
            pdf.set_draw_color(150, 200, 255)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_line_width(0.8)
            pdf.ellipse(175, y_start + 6.5, 15, 15, style="DF")
            if pdf.is_answer_key:
                pdf.set_font("helvetica", "B", 16)
                pdf.set_text_color(220, 53, 69)
                pdf.set_xy(175, y_start + 8)
                pdf.cell(15, 12, q["ans"], align="C")
                pdf.set_text_color(0, 0, 0)

        pdf.set_y(y_start + card_height + 4)

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
st.title("🎨 K1-Friendly Math Worksheet Generator")
st.markdown("ระบบสร้างใบงานคณิตศาสตร์ (อัปเกรด: ป้องกันข้อซ้ำ 100%)")

with st.sidebar:
    st.header("⚙️ Settings")
    level = st.selectbox("Grade Level:", ["K1 (Kindergarten 1)", "K2 (Kindergarten 2)"])
    topic = st.selectbox("Topic:", ["Counting (1-10)", "Number Tracing", "Basic Addition"])
    theme = st.selectbox("Theme:", ["Colorful Shapes", "Pastel Magic"])
    num_q = st.slider("Questions per page:", min_value=3, max_value=6, value=5) 
    include_ans = st.checkbox("Generate Answer Key", value=True)
    st.markdown("---")
    generate_btn = st.button("✨ Generate Unique PDF", use_container_width=True, type="primary")

if generate_btn:
    with st.spinner("Preparing unique questions..."):
        try:
            files = create_pdf(level, topic, theme, num_q, include_ans)
            st.success("✅ Worksheets generated! No duplicate questions.")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(files["student"], "rb") as f:
                    st.download_button("📥 Download Fun Worksheet", data=f, file_name="K1_Worksheet_Unique.pdf", mime="application/pdf", use_container_width=True)
            if include_ans and "answer" in files:
                with col2:
                    with open(files["answer"], "rb") as f:
                        st.download_button("📥 Download Answer Key", data=f, file_name="Answer_Key_Unique.pdf", mime="application/pdf", use_container_width=True)
            
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
