import streamlit as st
from fpdf import FPDF
import random
import tempfile
import os
import fitz  # ไลบรารีใหม่สำหรับแปลง PDF เป็นรูปภาพ (PyMuPDF)

# ==========================================
# 1. คลาสสำหรับสร้างเอกสาร PDF (มาตรฐาน TpT)
# ==========================================
class TpTWorksheet(FPDF):
    def __init__(self, level, topic, theme, is_answer_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.level = level
        self.topic = topic
        self.theme = theme
        self.is_answer_key = is_answer_key

    def header(self):
        self.set_line_width(0.5)
        self.rect(10, 10, 195.9, 259.4)
        self.rect(12, 12, 191.9, 255.4)
        
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Name: _______________________   Date: _______________", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        
        self.set_font("helvetica", "B", 18)
        title_text = f"{self.level} - {self.topic}"
        if self.is_answer_key:
            title_text += " [ANSWER KEY]"
            self.set_text_color(220, 53, 69)
        else:
            self.set_text_color(0, 0, 0)
            
        self.cell(0, 10, title_text, border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        footer_text = f"Page {self.page_no()} | Theme: {self.theme} | (c) Your TpT Store Name"
        self.cell(0, 10, footer_text, align="C")

# ==========================================
# 2. ฟังก์ชันจำลองโจทย์คณิตศาสตร์
# ==========================================
def generate_questions(level, topic, num_q):
    questions = []
    answers = []
    for _ in range(num_q):
        if level == "K1 (Kindergarten 1)":
            if topic == "Counting (1-10)":
                num = random.randint(1, 10)
                q_text = "O " * num
                questions.append(f"Count the objects:   {q_text}")
                answers.append(str(num))
            elif topic == "Number Tracing":
                num = random.randint(1, 10)
                questions.append(f"Trace the number:   {num}   ...   {num}   ...   {num}")
                answers.append("(Tracing)")
        elif level == "K2 (Kindergarten 2)":
            if topic == "Basic Math (Sum <= 10)":
                a = random.randint(1, 8)
                b = random.randint(1, 9 - a)
                questions.append(f"{a} + {b} =  ________")
                answers.append(str(a + b))
            elif topic == "Size Comparison":
                questions.append("Circle the BIGGER item:   [ O ]   or   [ o ]")
                answers.append("Left Item")
        elif level == "K3 (Kindergarten 3)":
            if topic == "Addition/Subtraction (No carry)":
                op = random.choice(['+', '-'])
                if op == '+':
                    a, b = random.randint(10, 30), random.randint(1, 19)
                    questions.append(f"{a} + {b} =  ________")
                    answers.append(str(a + b))
                else:
                    a, b = random.randint(20, 50), random.randint(1, 19)
                    questions.append(f"{a} - {b} =  ________")
                    answers.append(str(a - b))
            elif topic == "Patterns":
                patterns = [("O X O X O ___", "X"), ("O O X O O ___", "X"), ("[ ] ( ) [ ] ( ) ___", "[ ]")]
                p, ans = random.choice(patterns)
                questions.append(f"Complete the pattern:  {p}")
                answers.append(ans)
            elif topic == "Greater/Less Than":
                a, b = random.randint(1, 50), random.randint(1, 50)
                ans = ">" if a > b else "<" if a < b else "="
                questions.append(f"Write >, <, or =  :   {a}  ____  {b}")
                answers.append(ans)
    return questions, answers

# ==========================================
# 3. ฟังก์ชันสร้างไฟล์ PDF
# ==========================================
def create_pdf(level, topic, theme, num_q, include_ans):
    questions, answers = generate_questions(level, topic, num_q)
    output_files = {}

    pdf = TpTWorksheet(level, topic, theme, is_answer_key=False)
    pdf.add_page()
    pdf.set_font("helvetica", "", 16)
    for i, q in enumerate(questions):
        pdf.cell(0, 15, f"{i + 1}.  {q}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
    
    fd, path_student = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf.output(path_student)
    output_files["student"] = path_student

    if include_ans:
        pdf_ans = TpTWorksheet(level, topic, theme, is_answer_key=True)
        pdf_ans.add_page()
        pdf_ans.set_font("helvetica", "", 16)
        for i, q in enumerate(questions):
            pdf_ans.cell(0, 10, f"{i + 1}.  {q}", new_x="LMARGIN", new_y="NEXT")
            pdf_ans.set_font("helvetica", "B", 16)
            pdf_ans.set_text_color(220, 53, 69)
            pdf_ans.cell(0, 10, f"     Answer: {answers[i]}", new_x="LMARGIN", new_y="NEXT")
            pdf_ans.set_font("helvetica", "", 16)
            pdf_ans.set_text_color(0, 0, 0)
            pdf_ans.ln(5)
            
        fd, path_ans = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        pdf_ans.output(path_ans)
        output_files["answer"] = path_ans

    return output_files

# ระบบพรีวิวแบบใหม่ (แปลง PDF เป็นรูปภาพ ไม่โดนบล็อก 100%)
def display_pdf_as_image(file_path):
    doc = fitz.open(file_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=100)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, use_container_width=True)

# ==========================================
# 4. ส่วนแสดงผล UI
# ==========================================
st.set_page_config(page_title="TpT Math Generator", page_icon="📝", layout="wide")
st.title("📝 TpT Math Worksheet Generator")
st.markdown("ระบบสร้างใบงานคณิตศาสตร์ พร้อมพรีวิวแบบ Real-time")

with st.sidebar:
    st.header("⚙️ Worksheet Settings")
    level = st.selectbox("Select Grade Level:", ["K1 (Kindergarten 1)", "K2 (Kindergarten 2)", "K3 (Kindergarten 3)"])
    if level == "K1 (Kindergarten 1)":
        topics = ["Counting (1-10)", "Number Tracing"]
    elif level == "K2 (Kindergarten 2)":
        topics = ["Basic Math (Sum <= 10)", "Size Comparison"]
    else:
        topics = ["Addition/Subtraction (No carry)", "Patterns", "Greater/Less Than"]
        
    topic = st.selectbox("Select Topic:", topics)
    theme = st.selectbox("Select Theme:", ["Safari Animals", "Space Explorer", "Cute Dinosaurs", "Underwater World"])
    num_q = st.slider("Questions per page:", min_value=5, max_value=15, value=10)
    include_ans = st.checkbox("Generate Answer Key", value=True)
    st.markdown("---")
    generate_btn = st.button("✨ Generate & Preview", use_container_width=True, type="primary")

if generate_btn:
    with st.spinner("Generating High-Quality PDF and Previews..."):
        try:
            files = create_pdf(level, topic, theme, num_q, include_ans)
            st.success("✅ Worksheets generated successfully! Scroll down to preview.")
            
            col1, col2 = st.columns(2)
            with col1:
                with open(files["student"], "rb") as f:
                    st.download_button("📥 Download Student Worksheet", data=f, file_name=f"Student_{level[:2]}_{topic.replace('/', '-')}.pdf", mime="application/pdf", use_container_width=True)
            
            if include_ans and "answer" in files:
                with col2:
                    with open(files["answer"], "rb") as f:
                        st.download_button("📥 Download Answer Key", data=f, file_name=f"AnswerKey_{level[:2]}_{topic.replace('/', '-')}.pdf", mime="application/pdf", use_container_width=True)
            
            st.markdown("---")
            
            col_preview1, col_preview2 = st.columns(2)
            with col_preview1:
                st.subheader("👁️ Preview: Student Worksheet")
                display_pdf_as_image(files["student"])
            
            if include_ans and "answer" in files:
                with col_preview2:
                    st.subheader("👁️ Preview: Answer Key")
                    display_pdf_as_image(files["answer"])
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
