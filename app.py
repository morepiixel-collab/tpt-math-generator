import streamlit as st
from fpdf import FPDF
import random
import tempfile
import os
import fitz  # PyMuPDF สำหรับทำพรีวิว

# ==========================================
# 1. คลาสสำหรับสร้างเอกสาร PDF (รูปแบบ Premium Layout)
# ==========================================
class TpTWorksheet(FPDF):
    def __init__(self, level, topic, theme, is_answer_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.level = level
        self.topic = topic
        self.theme = theme
        self.is_answer_key = is_answer_key

    def header(self):
        # กรอบกระดาษแบบเส้นคู่ (Double Border)
        self.set_line_width(0.6)
        self.rect(10, 10, 195.9, 259.4)
        self.set_line_width(0.2)
        self.rect(12, 12, 191.9, 255.4)
        
        # กล่องชื่อและวันที่ (Header Box)
        self.set_xy(15, 18)
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(150, 150, 150)
        self.rect(15, 18, 185, 15, style="DF")
        
        self.set_font("helvetica", "B", 12)
        self.set_xy(18, 21.5)
        self.cell(100, 8, "Name: ___________________________________")
        self.set_xy(130, 21.5)
        self.cell(60, 8, "Date: __________________")
        
        # ชื่อหัวข้อใบงาน
        self.set_xy(15, 38)
        self.set_font("helvetica", "B", 20)
        title_text = f"{self.topic}"
        if self.is_answer_key:
            title_text += " [ANSWER KEY]"
            self.set_text_color(220, 53, 69) # สีแดงสำหรับหน้าเฉลย
        else:
            self.set_text_color(0, 0, 0)
            
        self.cell(185, 10, title_text, border=0, align="C")
        self.set_text_color(0, 0, 0)
        self.set_y(55) # ตั้งค่า Y เริ่มต้นสำหรับข้อแรก

    def footer(self):
        # ท้ายกระดาษ
        self.set_y(-16)
        self.set_font("helvetica", "I", 9)
        self.set_text_color(150, 150, 150)
        footer_text = f"Page {self.page_no()}  |  Theme: {self.theme}  |  (c) Your TpT Store"
        self.cell(0, 10, footer_text, align="C")

# ==========================================
# 2. ฟังก์ชันเตรียมข้อมูลโจทย์ (Data Structure)
# ==========================================
def generate_questions(level, topic, num_q):
    questions = []
    for _ in range(num_q):
        if topic == "Counting (1-10)":
            num = random.randint(1, 10)
            questions.append({"type": "counting", "text": "Count the shapes:", "count": num, "ans": str(num)})
        elif topic == "Number Tracing":
            num = random.randint(1, 10)
            questions.append({"type": "tracing", "text": "Trace the number:", "num": num, "ans": str(num)})
        elif topic == "Basic Math (Sum <= 10)":
            a = random.randint(1, 8)
            b = random.randint(1, 9 - a)
            questions.append({"type": "math", "text": f"{a}   +   {b}   =", "ans": str(a + b)})
        elif topic == "Addition/Subtraction (No carry)":
            op = random.choice(['+', '-'])
            if op == '+':
                a, b = random.randint(10, 30), random.randint(1, 19)
                ans = a + b
            else:
                a, b = random.randint(20, 50), random.randint(1, 19)
                ans = a - b
            questions.append({"type": "math", "text": f"{a}   {op}   {b}   =", "ans": str(ans)})
        elif topic == "Size Comparison":
            questions.append({"type": "text", "text": "Which one is BIGGER? (Circle it):   O   or   o", "ans": "Left"})
        elif topic == "Patterns":
            patterns = [("O  [ ]  O  [ ]  __", "O"), ("X  X  O  X  X  __", "O")]
            p, ans = random.choice(patterns)
            questions.append({"type": "text", "text": f"What comes next?    {p}", "ans": ans})
        elif topic == "Greater/Less Than":
            a, b = random.randint(1, 50), random.randint(1, 50)
            ans = ">" if a > b else "<" if a < b else "="
            questions.append({"type": "math", "text": f"{a}    ______    {b}", "ans": ans})
        else:
            questions.append({"type": "text", "text": "Answer the question.", "ans": "-"})
    return questions

# ==========================================
# 3. ฟังก์ชันสร้างไฟล์ PDF (Rendering)
# ==========================================
def render_pdf_content(pdf, questions):
    pdf.add_page()
    
    for i, q in enumerate(questions):
        y_start = pdf.get_y()
        
        # เช็คว่าล้นหน้ากระดาษไหม ถ้าล้นให้ขึ้นหน้าใหม่
        if y_start > 230:
            pdf.add_page()
            y_start = pdf.get_y()

        # วาดกรอบการ์ดของแต่ละข้อ (Card Box)
        pdf.set_fill_color(252, 253, 255) # สีฟ้าอมเทาอ่อนๆ
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(15, y_start, 185, 20, style="DF")

        # พิมพ์เลขข้อ
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(50, 50, 50)
        pdf.set_xy(18, y_start + 6.5)
        pdf.cell(10, 8, f"{i + 1}.")

        # พิมพ์เนื้อหาตามประเภทโจทย์
        pdf.set_xy(30, y_start + 6.5)
        
        if q["type"] == "counting":
            pdf.set_font("helvetica", "", 13)
            pdf.cell(40, 8, q["text"])
            cx = pdf.get_x() + 2
            # วาดรูปวงกลมจริงๆ แทนการพิมพ์ตัวอักษร
            for j in range(q["count"]):
                pdf.set_fill_color(100, 149, 237) # Cornflower Blue
                pdf.set_draw_color(80, 120, 200)
                pdf.ellipse(cx + (j * 7), y_start + 7, 5, 5, style="DF")
                
        elif q["type"] == "tracing":
            pdf.set_font("helvetica", "", 13)
            pdf.cell(45, 8, q["text"])
            pdf.set_font("helvetica", "B", 24)
            pdf.set_text_color(210, 210, 210) # สีเทาอ่อนสำหรับให้เด็กหัดเขียน
            pdf.cell(80, 7, f"{q['num']}       {q['num']}       {q['num']}")
            pdf.set_text_color(50, 50, 50)
            
        elif q["type"] == "math":
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(100, 8, q["text"], align="C")
            
        else:
            pdf.set_font("helvetica", "", 13)
            pdf.cell(120, 8, q["text"])

        # วาดกล่องสำหรับใส่คำตอบ (Answer Box)
        pdf.set_draw_color(150, 150, 150)
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(175, y_start + 4, 15, 12, style="DF")

        # ถ้าเป็นหน้าเฉลย ให้พิมพ์คำตอบลงในกล่อง
        if pdf.is_answer_key:
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(220, 53, 69) # สีแดง
            pdf.set_xy(175, y_start + 4)
            pdf.cell(15, 12, q["ans"], align="C")
            pdf.set_text_color(0, 0, 0)

        # ขยับแกน Y ลงไปเพื่อวาดข้อถัดไป
        pdf.set_y(y_start + 24)

def create_pdf(level, topic, theme, num_q, include_ans):
    questions = generate_questions(level, topic, num_q)
    output_files = {}

    # 1. ไฟล์ใบงานนักเรียน
    pdf_student = TpTWorksheet(level, topic, theme, is_answer_key=False)
    render_pdf_content(pdf_student, questions)
    
    fd, path_student = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf_student.output(path_student)
    output_files["student"] = path_student

    # 2. ไฟล์เฉลย (ถ้าเลือก)
    if include_ans:
        pdf_ans = TpTWorksheet(level, topic, theme, is_answer_key=True)
        render_pdf_content(pdf_ans, questions)
        
        fd, path_ans = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        pdf_ans.output(path_ans)
        output_files["answer"] = path_ans

    return output_files

# ==========================================
# 4. ระบบพรีวิวรูปภาพ
# ==========================================
def display_pdf_as_image(file_path):
    doc = fitz.open(file_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150) # เพิ่มความคมชัด
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, use_container_width=True)

# ==========================================
# 5. หน้าต่างแสดงผล Streamlit
# ==========================================
st.set_page_config(page_title="TpT Math Generator", page_icon="📝", layout="wide")
st.title("📝 Premium TpT Math Worksheet Generator")
st.markdown("ระบบสร้างใบงานคณิตศาสตร์ (อัปเกรด Layout แบบมืออาชีพ)")

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
    num_q = st.slider("Questions per page:", min_value=5, max_value=12, value=8) # ปรับลดจำนวนข้อสูงสุดลงเพื่อให้พอดีกับ Layout ใหม่
    include_ans = st.checkbox("Generate Answer Key", value=True)
    st.markdown("---")
    generate_btn = st.button("✨ Generate Premium PDF", use_container_width=True, type="primary")

if generate_btn:
    with st.spinner("Generating Premium Layout..."):
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
