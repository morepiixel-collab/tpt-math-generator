import streamlit as st
from fpdf import FPDF
import random
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# 1. ฐานข้อมูลหัวข้อ Pre-K แท้ๆ (วัย 3-4 ขวบ)
# ==========================================
PRE_K_CURRICULUM = {
    "1. Number Sense (การรู้ค่าตัวเลข)": [
        "1. Find the Number",
        "2. Trace the Numbers 1-5",
        "3. Counting 1-5",
        "4. Count and Match",
        "5. More or Less?",
        "6. Color by Number",
        "7. Missing Numbers 1-5",
        "8. Number Mazes"
    ],
    "2. Geometry (เรขาคณิต)": [
        "1. Trace Basic Shapes",
        "2. Shape Recognition",
        "3. Match the Shapes",
        "4. Match Shapes to Real Objects",
        "5. Sort the Shapes",
        "6. Color by Shape",
        "7. Big and Small Shapes",
        "8. Draw the Shape"
    ],
    "3. Measurement (การวัด)": [
        "1. Big or Small?",
        "2. Tall or Short?",
        "3. Long or Short?",
        "4. Heavy or Light?",
        "5. Same Size",
        "6. Order by Size",
        "7. Measure with Blocks",
        "8. Which Holds More?"
    ],
    "4. Algebraic Thinking (พีชคณิตเบื้องต้น)": [
        "1. Complete the AB Pattern",
        "2. Complete the AAB Pattern",
        "3. Create Your Own Pattern",
        "4. Sort by Color",
        "5. Sort by Category",
        "6. Same or Different?",
        "7. Spot the Odd One Out",
        "8. Matching Pairs"
    ]
}

# โทนสีพาสเทลพรีเมียมสำหรับ Wireframe
THEME_COLORS = {
    "Cotton Candy (ฟ้า-ชมพู)": {"primary": (118, 165, 234), "secondary": (244, 164, 185), "box": (248, 250, 255)},
    "Minty Fresh (เขียวมิ้นต์)": {"primary": (104, 195, 163), "secondary": (243, 156, 18), "box": (245, 255, 250)},
    "Lavender Dream (ม่วงอ่อน)": {"primary": (155, 89, 182), "secondary": (26, 188, 156), "box": (252, 248, 255)},
    "Sunshine (เหลือง-ส้ม)": {"primary": (243, 156, 18), "secondary": (231, 76, 60), "box": (255, 253, 240)}
}

# ==========================================
# 2. คลาสสร้างหน้ากระดาษ (Premium Layout)
# ==========================================
class PremiumTpTPDF(FPDF):
    def __init__(self, topic_name, color_theme, is_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.topic_name = topic_name
        self.colors = color_theme
        self.is_key = is_key
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # 1. กรอบกระดาษขอบหนา
        self.set_line_width(2.0)
        self.set_draw_color(*self.colors["primary"])
        self.rect(8, 8, 200, 263)
        
        # 2. กรอบด้านใน (เช็คเพื่อกัน Error Streamlit)
        self.set_line_width(0.3)
        self.set_draw_color(*self.colors["secondary"])
        if hasattr(self, 'set_dash_pattern'):
            self.set_dash_pattern(dash=2, gap=2)
            self.rect(11, 11, 194, 257)
            self.set_dash_pattern()
        else:
            self.rect(11, 11, 194, 257) 

        # 3. แถบ Header สีสันสดใส
        self.set_fill_color(*self.colors["primary"])
        self.rect(11, 11, 194, 28, style='F')
        
        self.set_font("helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, " P R E - K   M A T H", ln=True, align="C")
        
        self.set_font("helvetica", "B", 22)
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        title = clean_topic + (" (KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(6)
        
        # 4. กล่องใส่ชื่อและวันที่
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(11, 41, 194, 12, style='DF')
        
        self.set_font("helvetica", "B", 12)
        self.set_text_color(100, 100, 100)
        self.set_y(44)
        self.cell(10, 5, "", ln=0)
        self.cell(90, 5, "Name: ___________________________", ln=0, align="L")
        self.cell(80, 5, "Date: _______________", ln=1, align="R")
        self.ln(8)

# ==========================================
# 3. ฟังก์ชันวาดกล่อง Placeholder แบบน่ารัก
# ==========================================
def draw_cute_placeholder(pdf, x, y, w, h, text="[ Drop Clipart Here ]"):
    pdf.set_fill_color(*pdf.colors["box"])
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.5)
    
    if hasattr(pdf, 'set_dash_pattern'):
        pdf.set_dash_pattern(dash=3, gap=3)
        pdf.rect(x, y, w, h, style='DF')
        pdf.set_dash_pattern()
    else:
        pdf.rect(x, y, w, h, style='DF')
    
    pdf.set_font("helvetica", "I", 11)
    pdf.set_text_color(150, 150, 150)
    text_w = pdf.get_string_width(text)
    pdf.text(x + (w/2) - (text_w/2), y + (h/2) + 2, text)

# ==========================================
# 4. เอนจินสร้างเลย์เอาต์สำหรับ Pre-K โดยเฉพาะ
# ==========================================
def generate_worksheet(sub_topic, theme_colors, num_q, is_key=False):
    pdf = PremiumTpTPDF(sub_topic, theme_colors, is_key)
    pdf.add_page()
    
    clean_sub = sub_topic.lower()
    q_instruction = sub_topic.split(". ", 1)[-1] if ". " in sub_topic else sub_topic
    ans_color = (255, 75, 75) if is_key else (150, 150, 150)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, " Directions: Follow the instructions to complete the activity.", ln=True)
    pdf.ln(2)
    
    # ---------------------------------------------------------
    # Layout 1: เปรียบเทียบ (Measurement / Comparisons)
    # ---------------------------------------------------------
    if any(k in clean_sub for k in ["big", "tall", "long", "heavy", "more", "different", "odd"]):
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            
            # เลขข้อ
            pdf.set_fill_color(*theme_colors["secondary"])
            pdf.rect(15, pdf.get_y(), 10, 10, style='F')
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(255, 255, 255)
            pdf.text(17, pdf.get_y() + 6, f"{i+1}")
            
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(80, 80, 80)
            pdf.text(30, pdf.get_y() + 6, f"Find the {q_instruction.split(' ')[0]} one!")
            
            # กล่องซ้าย
            draw_cute_placeholder(pdf, 30, pdf.get_y()+10, 60, 40, "~ Picture A ~")
            # คำว่า VS
            pdf.set_font("helvetica", "B", 16)
            pdf.set_text_color(*theme_colors["primary"])
            pdf.text(100, pdf.get_y() + 32, "VS")
            # กล่องขวา
            draw_cute_placeholder(pdf, 115, pdf.get_y()+10, 60, 40, "~ Picture B ~")
            
            if is_key:
                pdf.set_font("helvetica", "B", 24)
                pdf.set_text_color(*ans_color)
                pdf.text(185, pdf.get_y() + 32, "?")
            
            pdf.ln(55)

    # ---------------------------------------------------------
    # Layout 2: อนุกรมและลวดลาย (Patterns)
    # ---------------------------------------------------------
    elif "pattern" in clean_sub:
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            
            pdf.set_fill_color(*theme_colors["secondary"])
            pdf.rect(15, pdf.get_y(), 10, 10, style='F')
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(255, 255, 255)
            pdf.text(17, pdf.get_y() + 6, f"{i+1}")
            
            for col in range(4):
                draw_cute_placeholder(pdf, 30 + (col * 35), pdf.get_y(), 30, 30, "Pic")
                
            # กล่องคำตอบ 
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.set_line_width(1.0)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(170, pdf.get_y(), 30, 30, style='DF')
            
            if is_key:
                pdf.set_font("helvetica", "B", 20)
                pdf.set_text_color(*ans_color)
                pdf.text(180, pdf.get_y() + 18, "?")
            else:
                pdf.set_font("helvetica", "B", 10)
                pdf.set_text_color(150, 150, 150)
                pdf.text(173, pdf.get_y() + 16, "Next?")
            
            pdf.ln(40)

    # ---------------------------------------------------------
    # Layout 3: นับจำนวน (Counting 1-5)
    # ---------------------------------------------------------
    elif any(k in clean_sub for k in ["count", "match", "how many", "number"]):
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            
            pdf.set_fill_color(*theme_colors["secondary"])
            pdf.rect(15, pdf.get_y(), 10, 10, style='F')
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(255, 255, 255)
            pdf.text(17, pdf.get_y() + 6, f"{i+1}")
            
            draw_cute_placeholder(pdf, 30, pdf.get_y(), 120, 35, f"~ Add 1-5 Items for {q_instruction} ~")
            
            # กล่องคำตอบ
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.set_line_width(0.8)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(160, pdf.get_y(), 35, 35, style='DF')
            
            if is_key:
                pdf.set_font("helvetica", "B", 24)
                pdf.set_text_color(*ans_color)
                pdf.text(172, pdf.get_y() + 20, "?")
            else:
                pdf.set_font("helvetica", "B", 10)
                pdf.set_text_color(150, 150, 150)
                pdf.text(168, pdf.get_y() + 18, "Ans")
            
            pdf.ln(45)

    # ---------------------------------------------------------
    # Layout 4: รูปทรงและลากเส้น (Trace / Shapes)
    # ---------------------------------------------------------
    else:
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            
            pdf.set_fill_color(*theme_colors["secondary"])
            pdf.rect(15, pdf.get_y(), 10, 10, style='F')
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(255, 255, 255)
            pdf.text(17, pdf.get_y() + 6, f"{i+1}")
            
            draw_cute_placeholder(pdf, 30, pdf.get_y(), 165, 40, f"~ Add Traceable Lines / Shapes for {q_instruction} ~")
            
            pdf.ln(50)

    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. พรีวิวด้วย PyMuPDF 
# ==========================================
def display_pdf_preview(pdf_bytes):
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0) 
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        st.markdown(
            """
            <style>
            .premium-paper {
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                border-radius: 12px;
                background: white;
                padding: 10px;
                border: 1px solid #f0f0f0;
                transition: transform 0.3s ease;
            }
            .premium-paper:hover {
                transform: scale(1.02);
            }
            </style>
            """, unsafe_allow_html=True
        )
        st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        doc.close()
    except Exception as e:
        st.error(f"⚠️ พรีวิวขัดข้อง: {e}")

# ==========================================
# 6. Streamlit UI
# ==========================================
st.set_page_config(page_title="Pre-K Premium Generator", layout="wide", page_icon="✨")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    div.stButton > button {
        background-color: #ff9a9e;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #ff758c;
    }
</style>
<div class="main-header">
    <h1 style="margin:0; font-weight:800;">✨ Premium Pre-K Wireframe Generator</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem;">สร้างโครงกระดูกใบงานเตรียมอนุบาล (3-4 ขวบ) สไตล์พรีเมียม นำไปแต่งต่อใน Canva</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 ตกแต่งใบงาน (Customize)")
    
    main_topic = st.selectbox("📌 1. เลือกหมวดหลัก (Core Math):", list(PRE_K_CURRICULUM.keys()))
    sub_topic = st.selectbox("🎯 2. เลือกกิจกรรม (Activity):", PRE_K_CURRICULUM[main_topic])
    
    theme_choice = st.selectbox("🖌️ 3. โทนสี (Color Palette):", list(THEME_COLORS.keys()))
    selected_colors = THEME_COLORS[theme_choice]
    
    # Pre-K เน้นรูปใหญ่ จำนวนข้อเลยต้องน้อยๆ 2-4 ข้อต่อหน้าพอ
    num_q = st.slider("🔢 4. จำนวนข้อต่อหน้า:", min_value=2, max_value=4, value=3)

# Generate Live
ws_bytes = generate_worksheet(sub_topic, selected_colors, num_q, is_key=False)
ans_bytes = generate_worksheet(sub_topic, selected_colors, num_q, is_key=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    display_pdf_preview(ws_bytes)

with col2:
    st.subheader("📥 ดาวน์โหลดไฟล์ (Ready for Canva)")
    st.markdown("1. ดาวน์โหลดไฟล์ PDF ด้านล่าง\n2. เปิดในเว็บ **Canva**\n3. ลาก Clipart น่ารักๆ (จำนวน 1-5 ชิ้น) ไปวางทับในเส้นประได้เลย!")
    
    st.download_button(
        label="📄 ดาวน์โหลดใบงาน (Worksheet PDF)",
        data=ws_bytes,
        file_name=f"PreK_{sub_topic.split('. ')[1].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.download_button(
        label="🔑 ดาวน์โหลดเฉลย (Answer Key PDF)",
        data=ans_bytes,
        file_name=f"PreK_KEY_{sub_topic.split('. ')[1].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
