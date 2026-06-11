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
        # Premium Thick & Thin Double Border
        self.set_line_width(0.8)
        self.rect(10, 10, 190, 277)
        self.set_line_width(0.2)
        self.rect(12, 12, 186, 273)
        
        self.set_line_width(0.2)
        
        # Student Information Header
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
# 2. Worksheet Logic & Generation (Updated from PDFs)
# ==========================================
def generate_worksheet(level, topic, theme, num_questions, is_answer_key=False):
    pdf = WorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # Title
    pdf.set_font("ComicNeue", "B", 22)
    title_text = f"{topic}"
    if is_answer_key:
        pdf.set_text_color(220, 50, 50)
        title_text += " (ANSWER KEY)"
    
    pdf.cell(0, 15, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # Dynamic Directions based on authentic US Worksheets
    pdf.set_font("ComicNeue", "B", 13)
    pdf.set_x(15)
    
    directions_map = {
        "Counting 1 to 10": f"Directions: Count the cute {theme.lower()} items and write the total number in the box.",
        "Number Tracing (1-10)": "Directions: Trace the numbers carefully. Then color the correct number of items.",
        "Teen Numbers (11-20)": f"Directions: Count the {theme.lower()} objects. Practice recognizing your teen numbers!",
        "What Comes Next?": "Directions: Look at the number sequences below. Fill in the missing number that comes next.",
        "Addition to 10": f"Directions: Solve the addition equations below. Use the {theme.lower()} clipart to help you count.",
        "Picture Subtraction": f"Directions: Look at the groups of {theme.lower()}. Cross out the items to solve the subtraction facts.",
        "Missing Addends (Up to 10)": "Directions: Find the missing addend to make the equation true. Write the missing number in the blank.",
        "2D & 3D Shapes (Sides)": "Directions: Look at each geometric shape. Count and write down how many sides it has.",
        "Place Value (Tens and Ones)": f"Directions: Count the base-ten blocks ({theme.lower()} themed) and write how many tens and ones there are.",
        "Addition & Subtraction to 50": f"Directions: Solve the math problems carefully. Use the space provided for your scratch work.",
        "Skip Counting (by 2s, 5s, 10s)": "Directions: Fill in the missing numbers by skip counting. Look closely at the pattern!",
        "True or False Equations": "Directions: Check if the math equation is correct. Circle TRUE if it is right, or FALSE if it is wrong.",
        "Number Words (Names)": "Directions: Read the number word carefully. Write the correct digit next to its name."
    }
    
    directions = directions_map.get(topic, "Directions: Solve the math problems on this worksheet.")
    pdf.multi_cell(180, 7, directions)
    pdf.ln(8)

    # Question Generation Loop
    for i in range(1, num_questions + 1):
        pdf.set_x(15)
        pdf.set_font("ComicNeue", "B", 15)
        pdf.cell(0, 8, f"{i}.", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("ComicNeue", "", 14)
        
        # --- PRE-K SKILLS ---
        if topic == "Counting 1 to 10":
            num = random.randint(1, 10)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 22, f"[ Clipart Box: Insert {num} {theme.lower()} here ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 15)
            ans_str = f"Answer: {num}" if is_answer_key else "Answer: [   ]"
            pdf.cell(0, 10, ans_str, align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "Number Tracing (1-10)":
            num = random.randint(1, 10)
            pdf.set_font("ComicNeue", "B", 18)
            pdf.cell(50, 12, f"Trace:  {num}  {num}  {num}", align="L")
            pdf.set_font("ComicNeue", "", 12)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 12, f"[ Draw {num} {theme.lower()} outline for coloring ]", align="R", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        elif topic == "Teen Numbers (11-20)":
            num = random.randint(11, 20)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 22, f"[ Teen Count: {num} items of {theme.lower()} ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 15)
            ans_str = f"Number:  {num}" if is_answer_key else "Number:  _____"
            pdf.cell(0, 10, ans_str, align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "What Comes Next?":
            start = random.randint(1, 15)
            seq = f"{start},  {start+1},  {start+2},  "
            pdf.set_font("ComicNeue", "B", 18)
            if is_answer_key:
                pdf.cell(80, 12, seq, align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 12, f"{start+3}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 12, f"{seq}  ____", align="C", new_x="LMARGIN", new_y="NEXT")

        # --- KINDERGARTEN SKILLS ---
        elif topic == "Addition to 10":
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 12, f"[ Clipart: {a} {theme.lower()} ]   +   [ {b} {theme.lower()} ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 18)
            ans_val = f"{a + b}" if is_answer_key else "____"
            pdf.cell(0, 12, f"{a}  +  {b}  =  {ans_val}", align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "Picture Subtraction":
            a = random.randint(5, 10)
            b = random.randint(1, a - 1)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 12, f"[ Clipart: {a} {theme.lower()} with {b} crossed out ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 18)
            ans_val = f"{a - b}" if is_answer_key else "____"
            pdf.cell(0, 12, f"{a}  -  {b}  =  {ans_val}", align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "Missing Addends (Up to 10)":
            total = random.randint(4, 10)
            a = random.randint(1, total - 1)
            b = total - a
            pdf.set_font("ComicNeue", "B", 18)
            if is_answer_key:
                pdf.cell(70, 12, f"{a}  +  ", align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(15, 12, f"{b}", align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.cell(40, 12, f"  =  {total}", align="L", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 12, f"{a}  +  _____  =  {total}", align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "2D & 3D Shapes (Sides)":
            shape, sides = random.choice([("Triangle", "3"), ("Square", "4"), ("Pentagon", "5"), ("Hexagon", "6")])
            pdf.set_font("ComicNeue", "B", 16)
            pdf.cell(60, 12, f"Shape: {shape}", align="L")
            pdf.set_font("ComicNeue", "", 12)
            pdf.set_text_color(160, 160, 160)
            pdf.cell(60, 12, f"[ Insert {shape} Outline ]", align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 14)
            ans_str = f"Sides: {sides}" if is_answer_key else "Sides: ____"
            pdf.cell(40, 12, ans_str, align="R", new_x="LMARGIN", new_y="NEXT")

        elif topic == "Place Value (Tens and Ones)":
            tens = random.choice([1, 2])
            ones = random.randint(1, 9)
            total = (tens * 10) + ones
            pdf.set_text_color(160, 160, 160)
            pdf.cell(0, 12, f"[ Insert base-ten block clipart for {total} ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("ComicNeue", "B", 15)
            if is_answer_key:
                pdf.cell(0, 10, f"Answer: {tens} Tens and {ones} Ones = {total}", align="C", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 10, "______ Tens and ______ Ones = ______", align="C", new_x="LMARGIN", new_y="NEXT")

        # --- 1ST GRADE SKILLS ---
        elif topic == "Addition & Subtraction to 50":
            is_add = random.choice([True, False])
            a, b = (random.randint(10, 30), random.randint(1, 20)) if is_add else (random.randint(20, 50), random.randint(1, 19))
            op, ans = ("+", a + b) if is_add else ("-", a - b)
            pdf.set_font("ComicNeue", "B", 20)
            if is_answer_key:
                pdf.cell(80, 14, f"{a}  {op}  {b}  =  ", align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 14, f"{ans}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 14, f"{a}  {op}  {b}  =  ______", align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "Skip Counting (by 2s, 5s, 10s)":
            step = random.choice([2, 5, 10])
            start = step * random.randint(1, 4)
            seq = f"{start},  {start+step},  {start+step*2},  "
            pdf.set_font("ComicNeue", "B", 18)
            if is_answer_key:
                pdf.cell(80, 12, seq, align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 12, f"{start+step*3}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 12, f"{seq}  ____", align="C", new_x="LMARGIN", new_y="NEXT")

        elif topic == "True or False Equations":
            a, b = random.randint(5, 20), random.randint(5, 20)
            is_true = random.choice([True, False])
            disp_ans = (a + b) if is_true else (a + b + random.choice([-2, -1, 1, 2]))
            pdf.set_font("ComicNeue", "B", 16)
            pdf.cell(90, 12, f"{a}  +  {b}  =  {disp_ans}", align="L")
            
            if is_answer_key:
                pdf.set_text_color(220, 50, 50)
                ans_tf = "[ TRUE ]  FALSE" if is_true else "TRUE  [ FALSE ]"
                pdf.cell(0, 12, ans_tf, align="R", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 12, "TRUE   /   FALSE", align="R", new_x="LMARGIN", new_y="NEXT")

        elif topic == "Number Words (Names)":
            words_dict = {11: "eleven", 14: "fourteen", 15: "fifteen", 20: "twenty", 23: "twenty-three", 35: "thirty-five", 42: "forty-two", 50: "fifty"}
            val = random.choice(list(words_dict.keys()))
            word = words_dict[val]
            pdf.set_font("ComicNeue", "B", 16)
            pdf.cell(90, 12, f"Write the number for:   {word}", align="L")
            ans_val = f"{val}" if is_answer_key else "_______"
            if is_answer_key:
                pdf.set_text_color(220, 50, 50)
            pdf.cell(0, 12, ans_val, align="R", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        pdf.ln(8)

    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    safe_topic = topic.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    file_path = os.path.join(temp_dir, f"{file_prefix}{level}_{safe_topic}.pdf")
    pdf.output(file_path)
    return file_path

# ==========================================
# 3. Secure PDF Preview (Image based)
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
# 4. Streamlit UI (English Only)
# ==========================================
st.set_page_config(page_title="TpT Math Worksheet Creator", page_icon="✏️", layout="wide")

st.title("✏️ TpT Math Worksheet Creator")
st.markdown("Create high-quality, professional math worksheets tailored for the US elementary market.")

st.sidebar.header("⚙️ Worksheet Settings")

level = st.sidebar.selectbox("1. Grade Level:", ["Pre-K", "Kindergarten", "1st Grade"])

# Dynamic skills loaded from your provided PDF reference samples
if level == "Pre-K":
    topics = ["Counting 1 to 10", "Number Tracing (1-10)", "Teen Numbers (11-20)", "What Comes Next?"]
elif level == "Kindergarten":
    topics = ["Addition to 10", "Picture Subtraction", "Missing Addends (Up to 10)", "2D & 3D Shapes (Sides)", "Place Value (Tens and Ones)"]
else:
    topics = ["Addition & Subtraction to 50", "Skip Counting (by 2s, 5s, 10s)", "True or False Equations", "Number Words (Names)"]

topic = st.sidebar.selectbox("2. Math Skill / Topic:", topics)
theme = st.sidebar.selectbox("3. Clipart Theme:", ["Cute Animals", "Outer Space", "Dinosaurs", "Ocean Life", "Friendly Monsters"])
num_q = st.sidebar.slider("4. Questions per Page:", min_value=1, max_value=6, value=4)
include_answer_key = st.sidebar.checkbox("✅ Include Answer Key", value=True)

st.sidebar.markdown("---")
generate_btn = st.sidebar.button("🚀 Generate & Preview", use_container_width=True)

st.subheader("🔍 Live Worksheet Preview")

if generate_btn or 'worksheet_path' in st.session_state:
    if generate_btn:
        with st.spinner("Rendering professional worksheet..."):
            st.session_state.worksheet_path = generate_worksheet(level, topic, theme, num_q, is_answer_key=False)
            if include_answer_key:
                st.session_state.answer_path = generate_worksheet(level, topic, theme, num_q, is_answer_key=True)
            else:
                st.session_state.answer_path = None

    tab_list = ["📄 Student Worksheet"]
    if include_answer_key and st.session_state.get('answer_path'):
        tab_list.append("🔑 Answer Key")
        
    tabs = st.tabs(tab_list)

    with tabs[0]:
        with open(st.session_state.worksheet_path, "rb") as f:
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
            st.info("💡 Ready for TpT! Open this PDF in Adobe Acrobat, Canva, or Photoshop to insert your cute clipart where the placeholders are.")
        with col2:
            display_pdf_preview_as_image(st.session_state.worksheet_path)

    if include_answer_key and st.session_state.get('answer_path'):
        with tabs[1]:
            with open(st.session_state.answer_path, "rb") as f:
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
                display_pdf_preview_as_image(st.session_state.answer_path)
else:
    st.info("💡 Click the '🚀 Generate & Preview' button on the sidebar to create your first TpT-ready worksheet!")
