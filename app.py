import streamlit as st
from fpdf import FPDF
import random
import tempfile
import os

# ==========================================
# ส่วนที่ 1: คลาสสำหรับสร้าง PDF (มาตรฐาน TpT)
# ==========================================
class TpTWorksheet(FPDF):
    def __init__(self, level, topic, theme, is_answer_key=False):
        # ใช้ขนาดกระดาษ Letter (8.5 x 11 นิ้ว) มาตรฐานอเมริกาสำหรับ TpT
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.level = level
        self.topic = topic
        self.theme = theme
        self.is_answer_key = is_answer_key

    def header(self):
        # 1. สร้างกรอบกระดาษ (Border) เพื่อความสวยงาม
        self.set_line_width(0.5)
        self.rect(10, 10, 195.9, 259.4)
        self.rect(12, 12, 191.9, 255.4) # กรอบด้านใน
        
        # 2. หัวกระดาษ (Name & Date)
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Name: _______________________   Date: _______________", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        
        # 3. ชื่อเรื่อง (Title)
        self.set_font("helvetica", "B", 18)
        title_text = f"{self.level} - {self.topic}"
        if self.is_answer_key:
            title_text += " [ANSWER KEY]"
            self.set_text_color(220, 53, 69) # สีแดงสำหรับใบเฉลย
        else:
            self.set_text_color(0, 0, 0)
            
        self.cell(0, 10, title_text, border=0, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def footer(self):
        # 4. ท้ายกระดาษ (ลิขสิทธิ์ และ เลขหน้า)
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        footer_text = f"Page {self.page_no()} | Theme: {self.theme} | (c) Your TpT Store Name"
        self.cell(0, 10, footer_text, align="C")

# ==========================================
# ส่วนที่ 2: ฟังก์ชันสร้างโจทย์ (Logic & Content)
# ==========================================
def generate_questions(level, topic, num_q):
    questions = []
    answers = []
    
    for _ in range(num_q):
        if level == "K1 (Kindergarten 1)":
            if topic == "Counting (1-10)":
                num = random.randint(1, 10)
                # จำลองการใช้รูปภาพด้วยสัญลักษณ์ (ในของจริงใช้ pdf.image() แทรก Clipart ได้)
                q_text = "★ " * num
                questions.append(f"Count the stars:   {q_text}")
                answers.append(str(num))
            elif topic == "Number Tracing":
                num = random.randint(1, 10)
                questions.append(f"Trace the number:   {num}   ...   {num}   ...   {num}")
                answers.append("(Tracing)")
                
        elif level == "K2 (Kindergarten 2)":
            if topic == "Basic Addition (Sum <= 10)":
                a = random.randint(1, 8)
                b = random.randint(1, 9 - a)
                questions.append(f"{a} + {b} =  ________")
                answers.append(str(a + b))
            elif topic == "Size Comparison":
                questions.append(f"Circle the BIGGER one:   [Image A]   or   [Image B]")
                answers.append("(Teacher Check)")
                
        elif level == "K3 (Kindergarten 3)":
            if topic == "Addition/Subtraction (No carrying)":
                op = random.choice(['+', '-'])
                if op == '+':
                    a = random.randint(10, 30)
                    b = random.randint(1, 19)
                    questions.append(f"{a} + {b} =  ________")
                    answers.append(str(a + b))
                else:
                    a = random.randint(20, 50)
                    b = random.randint(1, 19)
                    questions.append(f"{a} - {b} =  ________")
                    answers.append(str(a - b))
            elif topic == "Patterns":
                patterns = [
                    ("A B A B A ___", "B"),
                    ("A A B A A ___", "B"),
                    ("Circle Square Circle Square ___", "Circle")
                ]
                p, ans = random.choice(patterns)
                questions.append(f"Complete the pattern:  {p}")
                answers.append(ans)
            elif topic == "Greater/Less Than (>, <, =)":
                a = random.randint(1, 50)
                b = random.randint(1, 50)
                ans = ">" if a > b else "<" if a < b else "="
                questions.append(f"Write >, <, or =  :   {a}  ____  {b}")
                answers.append(ans)
                
    return questions, answers

# ==========================================
# ส่วนที่ 3: ฟังก์ชันประกอบ PDF (Generator)
# ==========================================
def create_pdf_file(level, topic, theme, num_q, include_ans):
    questions, answers = generate_questions(level, topic, num_q)
    output_files = {}

    # สร้างใบงานของนักเรียน (Student Worksheet)
    pdf_student = TpTWorksheet(level, topic, theme, is_answer_key=False)
    pdf_student.add_page()
    pdf_student.set_font("helvetica", "", 16)
    
    for i, q in enumerate(questions):
        pdf_student.cell(0, 15, f"{i + 1}.  {q}", new_x="LMARGIN", new_y="NEXT")
        pdf_student.ln(5)
    
    # บันทึกไฟล์ลง Temp Directory เพื่อให้ Streamlit โหลดได้
    fd, path_student = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf_student.output(path_student)
    output_files["student"] = path_student

    # สร้างใบเฉลย (Answer Key) หากผู้ใช้เลือก
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

# ==========================================
# ส่วนที่ 4: Streamlit User Interface (UI)
# ==========================================
st.set_page_config(page_title="TpT Math Generator", page_icon="📝", layout="wide")

st.title("📝 TpT Math Worksheet Generator")
st.markdown("เครื่องมือสร้างใบงานคณิตศาสตร์ระดับอนุบาล (K1-K3) สำหรับผู้ขาย Teachers Pay Teachers")

# สร้าง Sidebar สำหรับตั้งค่า
with st.sidebar:
    st.header("⚙️ Worksheet Settings")
    
    level = st.selectbox("Select Grade Level:", [
        "K1 (Kindergarten 1)", 
        "K2 (Kindergarten 2)", 
        "K3 (Kindergarten 3)"
    ])
    
    # เปลี่ยนหัวข้อตามระดับชั้นแบบ Dynamic
    if level == "K1 (Kindergarten 1)":
        topics = ["Counting (1-10)", "Number Tracing"]
    elif level == "K2 (Kindergarten 2)":
        topics = ["Basic Addition (Sum <= 10)", "Size Comparison"]
    else:
        topics = ["Addition/Subtraction (No carrying)", "Patterns", "Greater/Less Than (>, <, =)"]
        
    topic = st.selectbox("Select Topic:", topics)
    
    theme = st.selectbox("Select Theme:", [
        "Safari Animals", "Space Explorer", "Cute Dinosaurs", "Underwater World"
    ])
    
    num_q = st.slider("Questions per page:", min_value=5, max_value=15, value=10)
    
    include_ans = st.checkbox("Generate Answer Key (Highly Recommended)", value=True)
    
    st.markdown("---")
    generate_btn = st.button("✨ Generate PDF", use_container_width=True, type="primary")

# พื้นที่แสดงผลการทำงาน
st.subheader("Preview Selection")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Level:** {level}")
    st.write(f"**Topic:** {topic}")
with col2:
    st.write(f"**Theme:** {theme}")
    st.write(f"**Questions:** {num_q}")

if generate_btn:
    with st.spinner("Generating High-Quality PDFs..."):
        try:
            files = create_pdf_file(level, topic, theme, num_q, include_ans)
            st.success("✅ Worksheets generated successfully!")
            
            # ปุ่มดาวน์โหลด
            col3, col4 = st.columns(2)
            with col3:
                with open(files["student"], "rb") as f:
                    st.download_button(
                        label="📥 Download Student Worksheet",
                        data=f,
                        file_name=f"Student_{level[:2]}_{topic.replace('/', '-')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            if include_ans and "answer" in files:
                with col4:
                    with open(files["answer"], "rb") as f:
                        st.download_button(
                            label="📥 Download Answer Key",
                            data=f,
                            file_name=f"AnswerKey_{level[:2]}_{topic.replace('/', '-')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
        except Exception as e:
            st.error(f"An error occurred: {e}")
