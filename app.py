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
    # Using "Comic Neue" - A very popular, clean, and cute font for US elementary worksheets
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
# 1. Premium PDF Class for TpT
# ==========================================
class WorksheetPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register the cute fonts
        if os.path.exists("ComicNeue-Regular.ttf"):
            self.add_font("ComicNeue", style="", fname="ComicNeue-Regular.ttf")
        if os.path.exists("ComicNeue-Bold.ttf"):
            self.add_font("ComicNeue", style="B", fname="ComicNeue-Bold.ttf")

    def header(self):
        # Premium TpT Border Style (Thick outer line, thin inner line)
        self.set_line_width(0.8) # Thick line
        self.rect(10, 10, 190, 277)
        self.set_line_width(0.2) # Thin line
        self.rect(12, 12, 186, 273)
        
        # Reset line width for other elements
        self.set_line_width(0.2)
        
        # Header text: Name, Date, Score
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
        # Professional Copyright watermark
        self.set_y(-20)
        self.set_font("ComicNeue", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, "(c) Your TpT Store Name - All Rights Reserved", align="C")
        self.set_text_color(0, 0, 0) # Reset color

# ==========================================
# 2. Worksheet Logic & Generation
# ==========================================
def generate_worksheet(level, topic, theme, num_questions, is_answer_key=False):
    pdf = WorksheetPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    
    # Title
    pdf.set_font("ComicNeue", "B", 24)
    title_text = f"{topic}"
    if is_answer_key:
        pdf.set_text_color(220, 50, 50)
        title_text += " (ANSWER KEY)"
    
    pdf.cell(0, 15, title_text, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Directions (Very important for USA worksheets)
    pdf.set_font("ComicNeue", "B", 14)
    pdf.set_x(15)
    
    if level == "Pre-K":
        directions = f"Directions: Count the {theme.lower()} and write the correct number in the box."
    elif level == "Kindergarten":
        directions = f"Directions: Add the {theme.lower()} together. Write the sum on the line."
    else:
        directions = f"Directions: Solve the math problems carefully. Show your work!"

    pdf.multi_cell(180, 8, directions)
    pdf.ln(8)

    # Generate Questions
    for i in range(1, num_questions + 1):
        pdf.set_x(15)
        pdf.set_font("ComicNeue", "B", 16)
        pdf.cell(0, 10, f"{i}.", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("ComicNeue", "", 14)
        
        # --- Pre-K ---
        if level == "Pre-K":
            num = random.randint(1, 10)
            pdf.set_text_color(180, 180, 180)
            # Image Placeholder
            pdf.cell(0, 25, f"[ Insert {num} cute {theme.lower()} clipart here ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            
            if is_answer_key:
                pdf.set_text_color(220, 50, 50)
                pdf.set_font("ComicNeue", "B", 16)
                pdf.cell(0, 10, f"Answer:  {num}", align="C", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_font("ComicNeue", "B", 16)
                pdf.cell(0, 10, "Answer:  ____", align="C", new_x="LMARGIN", new_y="NEXT")

        # --- Kindergarten ---
        elif level == "Kindergarten":
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            
            pdf.set_text_color(180, 180, 180)
            pdf.cell(0, 25, f"[ {a} {theme.lower()} ]    +    [ {b} {theme.lower()} ]    =", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            
            if is_answer_key:
                pdf.set_text_color(220, 50, 50)
                pdf.set_font("ComicNeue", "B", 18)
                pdf.cell(0, 10, f"Answer: {a + b}", align="C", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_font("ComicNeue", "B", 18)
                pdf.cell(0, 10, f"Answer: ____", align="C", new_x="LMARGIN", new_y="NEXT")

        # --- 1st Grade ---
        elif level == "1st Grade":
            is_add = random.choice([True, False])
            if is_add:
                a, b = random.randint(10, 30), random.randint(1, 20)
                op, ans = "+", a + b
            else:
                a, b = random.randint(20, 50), random.randint(1, 19)
                op, ans = "-", a - b
            
            # Equation Placeholder
            pdf.set_font("ComicNeue", "B", 20)
            if is_answer_key:
                pdf.cell(80, 15, f"{a}  {op}  {b}  =  ", align="R")
                pdf.set_text_color(220, 50, 50)
                pdf.cell(40, 15, f"{ans}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.cell(0, 15, f"{a}  {op}  {b}  =  ______", align="C", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_text_color(180, 180, 180)
            pdf.set_font("ComicNeue", "", 12)
            pdf.cell(0, 10, f"[ Optional: Add small {theme.lower()} decor here ]", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        
        pdf.ln(10) # Space between questions

    temp_dir = tempfile.gettempdir()
    file_prefix = "Answer_Key_" if is_answer_key else "Worksheet_"
    safe_topic = topic.replace(" ", "_").replace("/", "_")
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
        st.error(f"Preview generation failed: {e}")

# ==========================================
# 4. Streamlit UI (English Only for USA Market)
# ==========================================
st.set_page_config(page_title="TpT Math Worksheet Creator", page_icon="✏️", layout="wide")

st.title("✏️ TpT Math Worksheet Creator")
st.markdown("Create high-quality, professional math worksheets tailored for the US elementary market.")

st.sidebar.header("⚙️ Worksheet Settings")

# Using USA Grade Levels
level = st.sidebar.selectbox("1. Grade Level:", ["Pre-K", "Kindergarten", "1st Grade"])

if level == "Pre-K":
    topics = ["Counting 1 to 10", "Number Tracing"]
elif level == "Kindergarten":
    topics = ["Addition to 10", "Comparing Sizes"]
else:
    topics = ["Addition & Subtraction to 50", "Math Patterns"]

topic = st.sidebar.selectbox("2. Math Skill / Topic:", topics)
theme = st.sidebar.selectbox("3. Clipart Theme:", 
                             ["Cute Animals", "Outer Space", "Dinosaurs", "Ocean Life", "Friendly Monsters"])

num_q = st.sidebar.slider("4. Questions per Page:", min_value=1, max_value=8, value=4)
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
                file_name=f"Worksheet_{level.replace(' ', '_')}_{topic.replace(' ', '_')}.pdf",
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
                    file_name=f"AnswerKey_{level.replace(' ', '_')}_{topic.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with col2:
                display_pdf_preview_as_image(st.session_state.answer_path)
else:
    st.info("💡 Click the '🚀 Generate & Preview' button on the sidebar to create your first TpT-ready worksheet!")
