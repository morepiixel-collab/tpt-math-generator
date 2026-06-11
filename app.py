import streamlit as st
from fpdf import FPDF
import tempfile
import os
import random
import urllib.request
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# 0. Download Cute Google Fonts for Kids Worksheets
# ==========================================
def download_cute_fonts():
    fonts = {
        "ComicNeue-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Regular.ttf",
        "ComicNeue-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf"
    }
    for name, url in fonts.items():
        if not os.path.exists(name):
            try:
                urllib.request.urlretrieve(url, name)
            except Exception as e:
                st.error(f"Failed to download font {name}: {e}")

download_cute_fonts()

# ==========================================
# 1. Premium PDF Class for TpT (Double Border)
# ==========================================
class WorksheetPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists("ComicNeue-Regular.ttf"):
            self.add_font("ComicNeue", style="", fname="ComicNeue-Regular.ttf")
        if os.path.exists("ComicNeue-Bold.ttf"):
            self.add_font("ComicNeue", style="B", fname="ComicNeue-Bold.ttf")

    def header(self):
        self.set_line_width(0.8)
        self.rect(10, 10, 190, 277)
        self.set_line_width(0.2)
        self.rect(12, 12, 186, 273)
        self.set_line_width(0.2)
        
        self.set_font("ComicNeue", "B", 14)
        self.set_y(20)
        self.set_x(15)
        self.cell(85, 10, "Name: ______________________", border=0, align="L")
        self.cell(85, 10, "Date: ______________", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        
        self.set_y(28)
        self.set_x(15)
        self.cell(170, 10, "Score: _______ / _______", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("ComicNeue", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "(c) Your TpT Store Name - All Rights Reserved", align="C")
        self.set_text_color(0, 0, 0)

# ==========================================
# 2. Logic: สร้างข้อมูลโจทย์ (ป้องกันการซ้ำ)
# ==========================================
def generate_questions_data(topic, num_q):
    """ฟังก์ชันนี้ทำหน้าที่สร้างและจำโจทย์ เพื่อไม่ให้ซ้ำกัน และให้หน้าเฉลยมีเลขตรงกันเป๊ะ"""
    questions = []
    used_keys = set() # ตัวเก็บข้อมูลกันซ้ำ
    
    for _ in range(num_q):
        q_data = {}
        # พยายามสุ่มใหม่ถ้าซ้ำ (สูงสุด 30 รอบต่อข้อ ป้องกัน Infinite Loop)
        for _ in range(30):
            if topic == "Counting 1 to 10" or topic == "Number Tracing (1-10)":
                num = random.randint(1, 10)
                key = f"n_{num}"
                q_data = {'num': num}
            
            elif topic == "Teen Numbers (11-20)":
                num = random.randint(11, 20)
                key = f"n_{num}"
                q_data = {'num': num}
                
            elif topic == "What Comes Next?":
                start = random.randint(1, 15)
                key = f"seq_{start}"
                q_data = {'start': start}
                
            elif topic == "Addition to 10":
                a, b = random.randint(1, 5), random.randint(1, 5)
                key = f"add_{a}_{b}"
                q_data = {'a': a, 'b': b, 'op': '+', 'ans': a + b}
                
            elif topic == "Picture Subtraction":
                a = random.randint(5, 10)
                b = random.randint(1, a - 1)
                key = f"sub_{a}_{b}"
                q_data = {'a': a, 'b': b, 'op': '-', 'ans': a - b}
                
            elif topic == "Missing Addends (Up to 10)":
                total = random.randint(4, 10)
                a = random.randint(1, total - 1)
                key = f"miss_{a}_{total}"
                q_data = {'a': a, 'b': total - a, 'total': total}
                
            elif topic == "2D & 3D Shapes (Sides)":
                shapes = [("Triangle", "3"), ("Square", "4"), ("Rectangle", "4"), ("Pentagon", "5"), ("Hexagon", "6")]
                shape, sides = random.choice(shapes)
                key = f"shp_{shape}"
                q_data = {'shape': shape, 'sides': sides}
                
            elif topic == "Place Value (Tens and Ones)":
                tens, ones = random.choice([1, 2, 3]), random.randint(1, 9)
                key = f"pv_{tens}_{ones}"
                q_data = {'tens': tens, 'ones': ones, 'total': (tens * 10) + ones}
                
            elif topic == "Addition & Subtraction to 50":
                is_add = random.choice([True, False])
                a, b = (random.randint(10, 30), random.randint(1, 20)) if is_add else (random.randint(20, 50), random.randint(1, 19))
                op, ans = ("+", a + b) if is_add else ("-", a - b)
                key = f"math50_{a}_{op}_{b}"
                q_data = {'a': a, 'b': b, 'op': op, 'ans': ans}
                
            elif topic == "Skip Counting (by 2s, 5s, 10s)":
                step = random.choice([2, 5, 10])
                start = step * random.randint(1, 4)
                key = f"skip_{start}_{step}"
                q_data = {'start': start, 'step': step}
                
            elif topic == "True or False Equations":
                a, b = random.randint(5, 20), random.randint(5, 20)
                is_true = random.choice([True, False])
                disp_ans = (a + b) if is_true else (a + b + random.choice([-2, -1, 1, 2]))
                key = f"tf_{a}_{b}_{disp_ans}"
                q_data = {'a': a, 'b': b, 'disp_ans': disp_ans, 'is_true': is_true}
                
            elif topic == "Number Words (Names)":
                words_dict = {11: "eleven", 14: "fourteen", 15: "fifteen", 20: "twenty", 23: "twenty-three", 35: "thirty-five", 42: "forty-two", 50: "fifty"}
                val = random.choice(list(words_dict.keys()))
                key = f"word_{val}"
                q_data = {'val': val, 'word': words_dict[val]}

            # ตรวจสอบว่าซ้ำหรือไม่ ถ้าไม่ซ้ำให้บันทึกแล้วเบรคออกลูป
            if key not in used_keys:
                used_keys.add(key)
                break
                
        questions.append(q_data)
    return questions

# ==========================================
# 3. Render: นำโจทย์ที่สร้างไว้วาดลง PDF
# ==========================================
def render_pdf_worksheet(level, topic, theme, questions_data, is_answer_key=False):
    pdf = WorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False) 
    
    # Title
    pdf.set_font("ComicNeue", "B", 22)
    title_text = f"{topic}"
    if is_answer_key:
        pdf.set_text_color(220, 50, 50)
        title_text += " (ANSWER KEY)"
    
    pdf.set_y(38)
    pdf.cell(0, 10, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # Directions
    pdf.set_font("ComicNeue", "B", 13)
    pdf.set_x(15)
    directions_map = {
        "Counting 1 to 10": f"Directions: Count the {theme.lower()} and write the number in the box.",
        "Number Tracing (1-10)": "Directions: Trace the numbers. Then draw or color the items.",
        "Teen Numbers (11-20)": f"Directions: Count the {theme.lower()} and write the correct teen number.",
        "What Comes Next?": "Directions: Write the missing number that comes next in the pattern.",
        "Addition to 10": f"Directions: Add the {theme.lower()} together and write the sum.",
        "Picture Subtraction": f"Directions: Look at the pictures. Cross some out to solve the subtraction.",
        "Missing Addends (Up to 10)": "Directions: Find the missing addend to make the equation true.",
        "2D & 3D Shapes (Sides)": "Directions: Count and write how many sides each shape has.",
        "Place Value (Tens and Ones)": f"Directions: Count the tens and ones blocks, then write the total.",
        "Addition & Subtraction to 50": f"Directions: Solve the math problems carefully. Show your work!",
        "Skip Counting (by 2s, 5s, 10s)": "Directions: Fill in the missing numbers by skip counting.",
        "True or False Equations": "Directions: Check if the equation is right. Circle TRUE or FALSE.",
        "Number Words (Names)": "Directions: Read the number word carefully and write the digit."
    }
    pdf.multi_cell(180, 6, directions_map.get(topic, "Directions: Solve the math problems on this worksheet."))
    pdf.ln(5)

    q_heights = {
        "Counting 1 to 10": 45, "Number Tracing (1-10)": 35, "Teen Numbers (11-20)": 45,
        "What Comes Next?": 25, "Addition to 10": 45, "Picture Subtraction": 45,
        "Missing Addends (Up to 10)": 25, "2D & 3D Shapes (Sides)": 40,
        "Place Value (Tens and Ones)": 50, "Addition & Subtraction to 50": 30,
        "Skip Counting (by 2s, 5s, 10s)": 25, "True or False Equations": 25,
        "Number Words (Names)": 25
    }
    box_h = q_heights.get(topic, 30)

    # วาดกล่องทีละข้อ จากชุดข้อมูลที่สุ่มไว้
    for i, q in enumerate(questions_data, start=1):
        if pdf.get_y() + box_h > 265:
            pdf.add_page()
            pdf.set_y(40)
            
        y_start = pdf.get_y()
        
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.5)
        pdf.rect(14, y_start, 182, box_h, style="D")
        pdf.set_draw_color(0, 0, 0)
        
        pdf.set_font("ComicNeue", "B", 16)
        pdf.set_xy(16, y_start + 4)
        pdf.cell(10, 8, f"{i}.", align="L")
        pdf.set_font("ComicNeue", "", 16)
        
        # --- วาดข้อความตาม Topic ---
        if topic in ["Counting 1 to 10", "Teen Numbers (11-20)"]:
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(26, y_start + box_h - 12)
            ans_str = f"Answer:   {q['num']}" if is_answer_key else "Answer:   _______"
            if is_answer_key: pdf.set_text_color(220, 50, 50)
            pdf.cell(160, 8, ans_str, align="C")
            pdf.set_text_color(0, 0, 0)

        elif topic == "Number Tracing (1-10)":
            pdf.set_font("ComicNeue", "B", 22)
            pdf.set_xy(26, y_start + 12)
            pdf.cell(60, 10, f"Trace:    {q['num']}    {q['num']}    {q['num']}", align="L")

        elif topic == "What Comes Next?":
            start = q['start']
            seq = f"{start},   {start+1},   {start+2},   "
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(26, y_start + 8)
            if is_answer_key:
                pdf.cell(80, 10, seq, align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 10, f"{start+3}", align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"{seq}  ________", align="C")

        elif topic in ["Addition to 10", "Picture Subtraction"]:
            pdf.set_font("ComicNeue", "B", 22)
            pdf.set_xy(26, y_start + box_h - 15)
            if is_answer_key:
                pdf.cell(160, 10, f"{q['a']}   {q['op']}   {q['b']}   =   ", align="C")
                pdf.set_text_color(220, 50, 50)
                pdf.set_xy(115, y_start + box_h - 15) 
                pdf.cell(30, 10, f"{q['ans']}", align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"{q['a']}   {q['op']}   {q['b']}   =   ______", align="C")

        elif topic == "Missing Addends (Up to 10)":
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(26, y_start + 8)
            if is_answer_key:
                pdf.cell(60, 10, f"{q['a']}   +   ", align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(20, 10, f"{q['b']}", align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.cell(40, 10, f"   =   {q['total']}", align="L")
            else:
                pdf.cell(160, 10, f"{q['a']}   +   ________   =   {q['total']}", align="C")

        elif topic == "2D & 3D Shapes (Sides)":
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(26, y_start + 6)
            pdf.cell(60, 10, f"Shape: {q['shape']}", align="L")
            pdf.set_xy(26, y_start + box_h - 14)
            if is_answer_key:
                pdf.cell(150, 10, f"Sides: ", align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.set_xy(175, y_start + box_h - 14)
                pdf.cell(20, 10, f"{q['sides']}", align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"Sides: ______", align="R")

        elif topic == "Place Value (Tens and Ones)":
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(26, y_start + box_h - 15)
            if is_answer_key:
                pdf.set_text_color(220, 50, 50)
                pdf.cell(160, 10, f"{q['tens']} Tens and {q['ones']} Ones = {q['total']}", align="C")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, "______ Tens and ______ Ones = ______", align="C")

        elif topic == "Addition & Subtraction to 50":
            pdf.set_font("ComicNeue", "B", 22)
            pdf.set_xy(26, y_start + 10)
            if is_answer_key:
                pdf.cell(80, 10, f"{q['a']}   {q['op']}   {q['b']}   =   ", align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 10, f"{q['ans']}", align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"{q['a']}   {q['op']}   {q['b']}   =   ________", align="C")

        elif topic == "Skip Counting (by 2s, 5s, 10s)":
            start, step = q['start'], q['step']
            seq = f"{start},   {start+step},   {start+step*2},   "
            pdf.set_font("ComicNeue", "B", 20)
            pdf.set_xy(26, y_start + 8)
            if is_answer_key:
                pdf.cell(80, 10, seq, align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 10, f"{start+step*3}", align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"{seq}  ________", align="C")

        elif topic == "True or False Equations":
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(26, y_start + 8)
            pdf.cell(70, 10, f"{q['a']}   +   {q['b']}   =   {q['disp_ans']}", align="L")
            if is_answer_key:
                pdf.set_text_color(220, 50, 50)
                ans_tf = "[ TRUE ]       FALSE" if q['is_true'] else "TRUE       [ FALSE ]"
                pdf.cell(80, 10, ans_tf, align="R")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(80, 10, "TRUE    /    FALSE", align="R")

        elif topic == "Number Words (Names)":
            pdf.set_font("ComicNeue", "B", 18)
            pdf.set_xy(26, y_start + 8)
            pdf.cell(80, 10, f"{q['word']}  =", align="R")
            ans_val = f"  {q['val']}" if is_answer_key else "  _______"
            if is_answer_key: pdf.set_text_color(220, 50, 50)
            pdf.cell(40, 10, ans_val, align="L")
            pdf.set_text_color(0, 0, 0)

        pdf.set_y(y_start + box_h + 4)

    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    safe_topic = topic.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    file_path = os.path.join(temp_dir, f"{file_prefix}{level}_{safe_topic}.pdf")
    pdf.output(file_path)
    return file_path

# ==========================================
# 4. Secure PDF Preview (Image based)
# ==========================================
def display_pdf_preview_as_image(file_path):
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.image(img, use_container_width=True)
        doc.close()
    except Exception as e:
        st.error(f"Preview generation failed: {e}")

# ==========================================
# 5. Streamlit UI (Live Auto-Update System)
# ==========================================
st.set_page_config(page_title="TpT Math Worksheet Creator", page_icon="✏️", layout="wide")

st.title("✏️ TpT Math Worksheet Creator")
st.markdown("Create high-quality, professional math worksheets tailored for the US elementary market.")

st.sidebar.header("⚙️ Worksheet Settings")

level = st.sidebar.selectbox("1. Grade Level:", ["Pre-K", "Kindergarten", "1st Grade"])

if level == "Pre-K":
    topics = ["Counting 1 to 10", "Number Tracing (1-10)", "Teen Numbers (11-20)", "What Comes Next?"]
elif level == "Kindergarten":
    topics = ["Addition to 10", "Picture Subtraction", "Missing Addends (Up to 10)", "2D & 3D Shapes (Sides)", "Place Value (Tens and Ones)"]
else:
    topics = ["Addition & Subtraction to 50", "Skip Counting (by 2s, 5s, 10s)", "True or False Equations", "Number Words (Names)"]

topic = st.sidebar.selectbox("2. Math Skill / Topic:", topics)
theme = st.sidebar.selectbox("3. Clipart Theme:", ["Cute Animals", "Outer Space", "Dinosaurs", "Ocean Life", "Friendly Monsters"])
num_q = st.sidebar.slider("4. Questions per Page:", min_value=1, max_value=8, value=4)
include_answer_key = st.sidebar.checkbox("✅ Include Answer Key", value=True)

st.sidebar.markdown("---")

# ปุ่มสำหรับสุ่มโจทย์ใหม่โดยตรง (ถ้ารู้สึกว่าตัวเลขยังไม่ถูกใจ)
if st.sidebar.button("🎲 Reroll Numbers (สุ่มโจทย์ใหม่)", use_container_width=True):
    # เปลี่ยนค่าเพื่อบังคับให้ระบบสุ่มใหม่
    st.session_state.force_reroll = True

# ตรวจสอบว่ามีการเปลี่ยน Setting หรือไม่ เพื่อให้ระบบ Auto-Update
current_settings = f"{level}_{topic}_{theme}_{num_q}_{include_answer_key}"
if 'last_settings' not in st.session_state or st.session_state.last_settings != current_settings or st.session_state.get('force_reroll', False):
    # 1. สร้างชุดข้อมูลโจทย์ (และป้องกันการซ้ำ)
    st.session_state.q_data = generate_questions_data(topic, num_q)
    
    # 2. นำโจทย์ที่ได้ไปวาดลงใบงานและหน้าเฉลย (รับประกันว่าเลขตรงกัน)
    st.session_state.ws_path = render_pdf_worksheet(level, topic, theme, st.session_state.q_data, is_answer_key=False)
    if include_answer_key:
        st.session_state.ans_path = render_pdf_worksheet(level, topic, theme, st.session_state.q_data, is_answer_key=True)
    
    st.session_state.last_settings = current_settings
    st.session_state.force_reroll = False # รีเซ็ตปุ่มสุ่ม

# ==========================================
# ส่วนแสดงผลหน้าจอพรีวิว
# ==========================================
st.subheader("🔍 Live Worksheet Preview (อัปเดตอัตโนมัติ)")

tab_list = ["📄 Student Worksheet"]
if include_answer_key and 'ans_path' in st.session_state:
    tab_list.append("🔑 Answer Key")
    
tabs = st.tabs(tab_list)

with tabs[0]:
    with open(st.session_state.ws_path, "rb") as f:
        ws_bytes = f.read()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.download_button(
            label="📥 Download Student Worksheet (PDF)",
            data=ws_bytes,
            file_name=f"Worksheet_{level}_{topic.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        st.success("✅ Auto-Updated! จำนวนข้อเปลี่ยนแปลงตามที่คุณเลื่อนปรับเรียบร้อยแล้ว ลองทดสอบปรับจำนวนหรือเปลี่ยนหัวข้อดูได้เลยครับ!")
    with col2:
        display_pdf_preview_as_image(st.session_state.ws_path)

if include_answer_key and 'ans_path' in st.session_state:
    with tabs[1]:
        with open(st.session_state.ans_path, "rb") as f:
            ans_bytes = f.read()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label="📥 Download Answer Key (PDF)",
                data=ans_bytes,
                file_name=f"AnswerKey_{level}_{topic.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col2:
            display_pdf_preview_as_image(st.session_state.ans_path)
