import streamlit as st
from fpdf import FPDF
import tempfile
import os
import random
import urllib.request
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# PART 1: Setup & PDF Template
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
                pass

download_cute_fonts()

class WorksheetPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists("ComicNeue-Regular.ttf"):
            self.add_font("ComicNeue", style="", fname="ComicNeue-Regular.ttf")
        if os.path.exists("ComicNeue-Bold.ttf"):
            self.add_font("ComicNeue", style="B", fname="ComicNeue-Bold.ttf")

    def header(self):
        # กรอบแบบ Double Border
        self.set_line_width(0.8)
        self.rect(10, 10, 190, 277)
        self.set_line_width(0.2)
        self.rect(12, 12, 186, 273)
        self.set_line_width(0.2)
        
        # หัวกระดาษ Name, Date, Score
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
# PART 2: Logic - Generate Data based on PDFs
# ==========================================
def generate_questions_data(topic, num_q):
    questions = []
    used_keys = set()
    
    for _ in range(num_q):
        q_data = {}
        for _ in range(30): # ป้องกันลูปค้างเวลาสุ่มเลข
            # 1. จาก PDF: "I Can Count Teen Numbers" / "TEEN Numbers"
            if topic == "1. Teen Numbers (11-20)":
                num = random.randint(11, 20)
                key = f"teen_{num}"
                q_data = {'num': num}
            
            # 2. จาก PDF: "What Comes Next?"
            elif topic == "2. What Comes Next?":
                start = random.randint(1, 15)
                key = f"next_{start}"
                q_data = {'start': start}
                
            # 3. จาก PDF: "I Can Order Numbers (Smallest to Largest)"
            elif topic == "3. Order Numbers (Smallest to Largest)":
                nums = random.sample(range(1, 25), 4)
                key = f"order_{'_'.join(map(str, nums))}"
                q_data = {'nums': nums, 'sorted': sorted(nums)}
                
            # 4. จาก PDF: "Write Your Number's Name"
            elif topic == "4. Write Number's Name":
                num_words = {11:"eleven", 12:"twelve", 13:"thirteen", 14:"fourteen", 15:"fifteen", 16:"sixteen", 17:"seventeen", 18:"eighteen", 19:"nineteen", 20:"twenty"}
                num = random.choice(list(num_words.keys()))
                key = f"name_{num}"
                q_data = {'num': num, 'word': num_words[num]}

            # 5. จาก PDF: "Missing Addends" (4 + _ = 6)
            elif topic == "5. Missing Addends":
                ans = random.randint(5, 12)
                a = random.randint(1, ans - 1)
                b = ans - a
                key = f"miss_{a}_{ans}"
                q_data = {'a': a, 'b': b, 'ans': ans}

            # 6. จาก PDF: "Cookie Picture Subtraction"
            elif topic == "6. Picture Subtraction":
                a = random.randint(5, 10)
                b = random.randint(1, a - 1)
                key = f"sub_{a}_{b}"
                q_data = {'a': a, 'b': b, 'ans': a - b}

            # 7. จาก PDF: "Color by Answer"
            elif topic == "7. Color by Answer":
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                colors = ["Red", "Blue", "Green", "Yellow", "Pink"]
                ans_color = random.choice(colors)
                key = f"cba_{a}_{b}"
                q_data = {'a': a, 'b': b, 'ans': a+b, 'color': ans_color}

            # 8. จาก PDF: "How Many Sides?" (2D/3D Shapes)
            elif topic == "8. How Many Sides?":
                shapes = [("Triangle", 3), ("Square", 4), ("Rectangle", 4), ("Pentagon", 5), ("Hexagon", 6)]
                shape, sides = random.choice(shapes)
                key = f"shape_{shape}"
                q_data = {'shape': shape, 'sides': sides}

            # 9. จาก PDF: "Tens and Ones Counting Blocks"
            elif topic == "9. Tens and Ones":
                t = random.randint(1, 3)
                o = random.randint(1, 9)
                key = f"tens_{t}_{o}"
                q_data = {'tens': t, 'ones': o, 'total': (t*10)+o}

            # 10. จาก PDF: "True or False"
            elif topic == "10. True or False":
                a, b = random.randint(1, 10), random.randint(1, 10)
                is_true = random.choice([True, False])
                eq_ans = (a + b) if is_true else (a + b + random.choice([-2, 2, 1]))
                key = f"tf_{a}_{b}_{eq_ans}"
                q_data = {'a': a, 'b': b, 'eq_ans': eq_ans, 'is_true': is_true}

            # 11. จาก PDF: "Which is More?" (Gumball Match)
            elif topic == "11. Which is More?":
                a, b = random.sample(range(5, 30), 2)
                key = f"more_{a}_{b}"
                q_data = {'a': a, 'b': b, 'more': max(a, b)}

            # 12. จาก PDF: "Count by 5's"
            elif topic == "12. Count by 5's":
                start = random.randint(1, 5) * 5
                key = f"by5_{start}"
                q_data = {'start': start, 'seq': [start, start+5, start+10, start+15]}

            # 13. จาก PDF: "Roll It On"
            elif topic == "13. Roll It On":
                dice1 = random.randint(1, 6)
                dice2 = random.randint(1, 6)
                key = f"roll_{dice1}_{dice2}"
                q_data = {'d1': dice1, 'd2': dice2, 'ans': dice1+dice2}

            # ป้องกันข้อซ้ำในหน้าเดียวกัน
            if key not in used_keys:
                used_keys.add(key)
                break
        questions.append(q_data)
    return questions

# ==========================================
# PART 3: Render Worksheet Layout
# ==========================================
def render_pdf_worksheet(topic, theme, questions_data, is_answer_key=False):
    pdf = WorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    
    # Title
    pdf.set_font("ComicNeue", "B", 20)
    title_text = topic.split(". ")[1] # ตัดตัวเลขลำดับหัวข้อข้างหน้าออก
    if is_answer_key:
        pdf.set_text_color(220, 50, 50)
        title_text += " (ANSWER KEY)"
    pdf.set_y(38)
    pdf.cell(0, 10, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # Directions (ปรับข้อความคำสั่งตามหน้าจริงใน PDF ของคุณ)
    pdf.set_font("ComicNeue", "B", 12)
    pdf.set_x(15)
    directions_map = {
        "1. Teen Numbers (11-20)": f"Directions: Count the {theme.lower()} items and write the correct teen number in the box.",
        "2. What Comes Next?": "Directions: Write the missing number that comes next in the number pattern.",
        "3. Order Numbers (Smallest to Largest)": "Directions: Write the given numbers in order from the smallest to the largest.",
        "4. Write Number's Name": "Directions: Read the number and write its name in words on the line.",
        "5. Missing Addends": "Directions: Find and write the missing number to make the addition equation true.",
        "6. Picture Subtraction": f"Directions: Look at the {theme.lower()} pictures. Cross out the items to solve the subtraction question.",
        "7. Color by Answer": "Directions: Solve the addition equation and use the answer key below to color the space.",
        "8. How Many Sides?": "Directions: Look at the 2D/3D shapes. Count and write how many sides each shape has.",
        "9. Tens and Ones": "Directions: Count the tens blocks and ones blocks, then write the total number.",
        "10. True or False": "Directions: Determine if the equation is true or false. Circle the correct answer.",
        "11. Which is More?": "Directions: Look at the two numbers and circle the number that is the largest.",
        "12. Count by 5's": "Directions: Fill in the missing numbers to count forward by 5s correctly.",
        "13. Roll It On": "Directions: Roll the dice, write down the numbers, and count on to find the total sum."
    }
    pdf.multi_cell(180, 6, directions_map.get(topic, "Directions: Solve the math problems on this worksheet carefully."))
    pdf.ln(5)

    # กำหนดความสูงของกล่องข้อตามความเหมาะสมของแต่ละหัวข้อกิจกรรม
    box_h = 35 
    if "Order Numbers" in topic or "Which is More" in topic or "What Comes Next" in topic: box_h = 25
    if "Count by 5's" in topic or "True or False" in topic or "Write Number's Name" in topic: box_h = 25
    if "Picture Subtraction" in topic or "Color by Answer" in topic or "Tens and Ones" in topic: box_h = 45

    # ลูปวาดกล่องทีละข้อจากชุดข้อมูลที่สุ่มไว้
    for i, q in enumerate(questions_data, start=1):
        if pdf.get_y() + box_h > 265:
            pdf.add_page()
            pdf.set_y(40)
            
        y_start = pdf.get_y()
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.5)
        pdf.rect(14, y_start, 182, box_h, style="D")
        pdf.set_draw_color(0, 0, 0)
        
        pdf.set_font("ComicNeue", "B", 16)
        pdf.set_xy(16, y_start + 4)
        pdf.cell(10, 8, f"{i}.", align="L")
        
        pdf.set_font("ComicNeue", "B", 18)
        ans_color = (220, 50, 50) if is_answer_key else (0, 0, 0)
        
        # 1. Teen Numbers Layout
        if "Teen Numbers" in topic:
            pdf.set_xy(26, y_start + box_h - 12)
            if is_answer_key: pdf.set_text_color(*ans_color)
            pdf.cell(160, 8, f"Answer: {q['num']}" if is_answer_key else "Answer: _______", align="C")
            pdf.set_text_color(0, 0, 0)
            
        # 2. What Comes Next Layout
        elif "What Comes Next" in topic:
            pdf.set_xy(26, y_start + 8)
            seq_text = f"{q['start']},  {q['start']+1},  {q['start']+2},  "
            if is_answer_key:
                pdf.cell(80, 10, seq_text, align="R")
                pdf.set_text_color(*ans_color)
                pdf.cell(40, 10, str(q['start']+3), align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, seq_text + "______", align="C")

        # 3. Order Numbers Layout
        elif "Order Numbers" in topic:
            pdf.set_xy(26, y_start + 8)
            num_str = "   ".join(map(str, q['nums']))
            pdf.cell(60, 10, f"Sort:  {num_str}", align="L")
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(100, 10, f"Answer:  {'  <  '.join(map(str, q['sorted']))}", align="R")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(100, 10, "____ < ____ < ____ < ____", align="R")

        # 4. Write Name Layout
        elif "Write Number's Name" in topic:
            pdf.set_xy(26, y_start + 8)
            pdf.cell(80, 10, f"{q['num']}  =  ", align="R")
            if is_answer_key: pdf.set_text_color(*ans_color)
            pdf.cell(80, 10, f"{q['word']}" if is_answer_key else "________________", align="L")
            pdf.set_text_color(0, 0, 0)

        # 5. Missing Addends Layout
        elif "Missing Addends" in topic:
            pdf.set_xy(26, y_start + 12)
            if is_answer_key:
                pdf.cell(60, 10, f"{q['a']}   +   ", align="R")
                pdf.set_text_color(*ans_color)
                pdf.cell(20, 10, str(q['b']), align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.cell(40, 10, f"   =   {q['ans']}", align="L")
            else:
                pdf.cell(160, 10, f"{q['a']}   +   ________   =   {q['ans']}", align="C")

        # 6. Picture Subtraction Layout
        elif "Picture Subtraction" in topic:
            pdf.set_xy(26, y_start + box_h - 15)
            if is_answer_key:
                pdf.cell(160, 10, f"{q['a']}   -   {q['b']}   =   ", align="C")
                pdf.set_text_color(*ans_color)
                pdf.set_xy(115, y_start + box_h - 15)
                pdf.cell(20, 10, str(q['ans']), align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"{q['a']}   -   {q['b']}   =   ______", align="C")

        # 7. Color by Answer Layout
        elif "Color by Answer" in topic:
            pdf.set_xy(26, y_start + 5)
            pdf.cell(160, 10, f"Solve: {q['a']} + {q['b']} = ?", align="C")
            pdf.set_xy(26, y_start + box_h - 15)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(160, 10, f"Color the picture: {q['color']} (Ans: {q['ans']})", align="C")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"If Answer is {q['ans']}, color it {q['color']}", align="C")

        # 8. How Many Sides Layout
        elif "How Many Sides" in topic:
            pdf.set_xy(26, y_start + 12)
            pdf.cell(80, 10, f"Shape: {q['shape']}", align="L")
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(80, 10, f"Sides: {q['sides']}", align="R")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(80, 10, "Sides: _____", align="R")

        # 9. Tens and Ones Layout
        elif "Tens and Ones" in topic:
            pdf.set_xy(26, y_start + box_h - 15)
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(160, 10, f"{q['tens']} Tens and {q['ones']} Ones = {q['total']}", align="C")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, "______ Tens and ______ Ones = ______", align="C")

        # 10. True or False Layout
        elif "True or False" in topic:
            pdf.set_xy(26, y_start + 8)
            pdf.cell(70, 10, f"{q['a']} + {q['b']} = {q['eq_ans']}", align="L")
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(90, 10, "[ TRUE ]     FALSE" if q['is_true'] else "TRUE     [ FALSE ]", align="R")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(90, 10, "TRUE   /   FALSE", align="R")

        # 11. Which is More Layout
        elif "Which is More" in topic:
            pdf.set_xy(26, y_start + 8)
            pdf.cell(80, 10, f"{q['a']}      or      {q['b']}", align="C")
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(80, 10, f"Larger: {q['more']}", align="R")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(80, 10, "Circle the larger number", align="R")

        # 12. Count by 5's Layout
        elif "Count by 5's" in topic:
            pdf.set_xy(26, y_start + 8)
            seq = q['seq']
            if is_answer_key:
                pdf.cell(80, 10, f"{seq[0]},  ", align="R")
                pdf.set_text_color(*ans_color)
                pdf.cell(80, 10, f"{seq[1]},  {seq[2]},  {seq[3]}", align="L")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(160, 10, f"{seq[0]},  ____,  ____,  ____", align="C")

        # 13. Roll It On Layout
        elif "Roll It On" in topic:
            pdf.set_xy(26, y_start + 12)
            pdf.cell(60, 10, f"Dice 1: [{q['d1']}]    Dice 2: [{q['d2']}]", align="L")
            if is_answer_key:
                pdf.set_text_color(*ans_color)
                pdf.cell(100, 10, f"Total: {q['ans']}", align="R")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(100, 10, "Total: ______", align="R")

        pdf.set_y(y_start + box_h + 4)

    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    safe_topic = topic.split(". ")[1].replace(" ", "_").replace("'", "")
    file_path = os.path.join(temp_dir, f"{file_prefix}{safe_topic}.pdf")
    pdf.output(file_path)
    return file_path

# ==========================================
# PART 4: Streamlit UI and Execution
# ==========================================
def display_pdf_preview(file_path):
    """ฟังก์ชันสำหรับแปลง PDF เป็นรูปภาพเพื่อแสดงพรีวิวบนหน้าเว็บ (ป้องกันเบราว์เซอร์บล็อก)"""
    try:
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # เพิ่มเงาให้รูปภาพดูเหมือนกระดาษจริง
        st.markdown(
            """
            <style>
            .paper-shadow {
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                transition: 0.3s;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
            }
            </style>
            """, unsafe_allow_html=True
        )
        st.image(img, use_container_width=True)
        doc.close()
    except Exception as e:
        st.error(f"Preview Error: {e}")

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="Ultimate TpT Worksheet Generator", page_icon="📝", layout="wide")
st.title("📝 Ultimate TpT Worksheet Generator")
st.markdown("ระบบสร้างใบงานตามเนื้อหาจริงจากไฟล์ PDF ทั้ง 13 รูปแบบ พร้อมตีเส้นตีกรอบ เตรียมพื้นที่ว่างให้คุณนำไปลากวางรูป Clipart ต่อใน Canva ได้ทันที")

# แถบเมนูด้านข้าง (Sidebar)
st.sidebar.header("⚙️ Worksheet Settings")

all_topics = [
    "1. Teen Numbers (11-20)",
    "2. What Comes Next?",
    "3. Order Numbers (Smallest to Largest)",
    "4. Write Number's Name",
    "5. Missing Addends",
    "6. Picture Subtraction",
    "7. Color by Answer",
    "8. How Many Sides?",
    "9. Tens and Ones",
    "10. True or False",
    "11. Which is More?",
    "12. Count by 5's",
    "13. Roll It On"
]

topic = st.sidebar.selectbox("🎯 Select Worksheet Activity:", all_topics)
theme = st.sidebar.selectbox("🎨 Clipart Theme:", ["Space", "Ocean", "Animals", "Monsters", "School", "Food", "Dinosaurs"])
num_q = st.sidebar.slider("📌 Questions per Page:", min_value=1, max_value=8, value=4)
include_ans = st.sidebar.checkbox("✅ Include Answer Key", value=True)

st.sidebar.markdown("---")
# ปุ่มสำหรับสุ่มตัวเลขใหม่
if st.sidebar.button("🎲 Generate & Shuffle Numbers", use_container_width=True):
    st.session_state.force_reroll = True

# ตรวจสอบการอัปเดตแบบเรียลไทม์
current_settings = f"{topic}_{theme}_{num_q}_{include_ans}"
if 'last_settings' not in st.session_state or st.session_state.last_settings != current_settings or st.session_state.get('force_reroll', False):
    with st.spinner("กำลังเรนเดอร์ใบงาน..."):
        # 1. สร้างชุดข้อมูลโจทย์
        st.session_state.q_data = generate_questions_data(topic, num_q)
        # 2. วาด PDF
        st.session_state.ws_path = render_pdf_worksheet(topic, theme, st.session_state.q_data, is_answer_key=False)
        if include_ans:
            st.session_state.ans_path = render_pdf_worksheet(topic, theme, st.session_state.q_data, is_answer_key=True)
        
        st.session_state.last_settings = current_settings
        st.session_state.force_reroll = False

# พื้นที่แสดงผลหลัก (Main Area)
st.subheader("🔍 Live Preview")

# ระบบ Tabs สำหรับแยกดูโจทย์และเฉลย
tabs = st.tabs(["📄 Worksheet", "🔑 Answer Key"]) if include_ans else st.tabs(["📄 Worksheet"])

# แท็บใบงาน
with tabs[0]:
    with open(st.session_state.ws_path, "rb") as f: 
        ws_bytes = f.read()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.download_button(
            label="📥 Download Worksheet (PDF)", 
            data=ws_bytes, 
            file_name=f"Worksheet_{topic.split('.')[1].strip().replace(' ', '_')}.pdf", 
            mime="application/pdf", 
            use_container_width=True,
            type="primary"
        )
        st.success(f"✨ รูปแบบที่เลือก: {topic.split('.')[1].strip()}\nระบบตีกล่องและจัดหน้าไว้ให้เรียบร้อยแล้ว!")
        st.info("💡 สามารถนำไฟล์ PDF ที่ดาวน์โหลดไปเปิดใน Canva เพื่อลาก Clipart น่ารักๆ ที่เตรียมไว้มาวางในพื้นที่ว่างได้เลยครับ")
    with col2: 
        display_pdf_preview(st.session_state.ws_path)

# แท็บเฉลย
if include_ans:
    with tabs[1]:
        with open(st.session_state.ans_path, "rb") as f: 
            ans_bytes = f.read()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label="📥 Download Answer Key (PDF)", 
                data=ans_bytes, 
                file_name=f"AnswerKey_{topic.split('.')[1].strip().replace(' ', '_')}.pdf", 
                mime="application/pdf", 
                use_container_width=True
            )
        with col2: 
            display_pdf_preview(st.session_state.ans_path)
