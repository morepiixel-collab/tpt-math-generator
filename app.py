import streamlit as st
from fpdf import FPDF
import random
import fitz  
from PIL import Image
import os
import urllib.request

# ==========================================
# 0. ระบบดาวน์โหลดฟอนต์น่ารักๆ อัตโนมัติ (Cute Font)
# ==========================================
FONT_FILE = "CuteFont.ttf"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/comicneue/ComicNeue-Bold.ttf"

if not os.path.exists(FONT_FILE):
    try:
        urllib.request.urlretrieve(FONT_URL, FONT_FILE)
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถดาวน์โหลดฟอนต์ได้: {e}")

# ==========================================
# 1. ฐานข้อมูลหัวข้อ
# ==========================================
PRE_K_CURRICULUM = {
    "1. Number Sense (การรู้ค่าตัวเลข)": [
        "1. Find the Number",
        "2. Trace the Numbers",
        "3. Counting Objects",
        "4. Count and Match",
        "5. More or Less?",
        "6. Color by Number",
        "7. Missing Numbers",
        "8. Number Mazes"
    ]
}

THEME_COLORS = {
    "Cotton Candy (ฟ้า-ชมพู)": {"primary": (118, 165, 234), "secondary": (244, 164, 185), "box": (248, 250, 255)},
    "Minty Fresh (เขียวมิ้นต์)": {"primary": (104, 195, 163), "secondary": (243, 156, 18), "box": (245, 255, 250)},
    "Lavender Dream (ม่วงอ่อน)": {"primary": (155, 89, 182), "secondary": (26, 188, 156), "box": (252, 248, 255)},
    "Sunshine (เหลือง-ส้ม)": {"primary": (243, 156, 18), "secondary": (231, 76, 60), "box": (255, 253, 240)}
}

# ==========================================
# 2. คลาสหน้ากระดาษ 
# ==========================================
class PremiumTpTPDF(FPDF):
    def __init__(self, topic_name, color_theme, shop_name, target_num, is_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.topic_name = topic_name
        self.colors = color_theme
        self.shop_name = shop_name 
        self.target_num = target_num 
        self.is_key = is_key
        self.set_auto_page_break(auto=True, margin=15)
        
        if os.path.exists(FONT_FILE):
            self.add_font("CuteFont", "", FONT_FILE)
        else:
            self.add_font("CuteFont", "", "helvetica") 

    def header(self):
        self.set_line_width(2.0)
        self.set_draw_color(*self.colors["primary"])
        self.rect(8, 8, 200, 263)
        
        self.set_line_width(0.3)
        self.set_draw_color(*self.colors["secondary"])
        if hasattr(self, 'set_dash_pattern'):
            self.set_dash_pattern(dash=2, gap=2)
            self.rect(11, 11, 194, 257)
            self.set_dash_pattern()
        else:
            self.rect(11, 11, 194, 257) 

        self.set_fill_color(*self.colors["primary"])
        self.rect(11, 11, 194, 28, style='F')
        
        self.set_font("CuteFont", "", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, " P R E - K   M A T H", ln=True, align="C")
        
        self.set_font("CuteFont", "", 24)
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        title = f"{clean_topic} : NUMBER {self.target_num}" + (" (KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(6)
        
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(11, 41, 194, 12, style='DF')
        
        self.set_font("CuteFont", "", 14)
        self.set_text_color(100, 100, 100)
        self.set_y(44)
        self.cell(10, 5, "", ln=0)
        self.cell(90, 5, "Name: ___________________________", ln=0, align="L")
        self.cell(80, 5, "Date: _______________", ln=1, align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("CuteFont", "", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"© {self.shop_name} | All Rights Reserved.", align="C")

# ==========================================
# 3. Helpers สำหรับวาด 
# ==========================================
def draw_placeholder(pdf, x, y, w, h, text="", font_size=12):
    pdf.set_fill_color(*pdf.colors["box"])
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.5)
    if hasattr(pdf, 'set_dash_pattern'):
        pdf.set_dash_pattern(dash=3, gap=3)
        pdf.rect(x, y, w, h, style='DF')
        pdf.set_dash_pattern()
    else:
        pdf.rect(x, y, w, h, style='DF')
    
    if text:
        pdf.set_font("CuteFont", "", font_size)
        pdf.set_text_color(150, 150, 150)
        text_w = pdf.get_string_width(text)
        text_h_offset = (font_size * 0.352777) / 2.8 
        pdf.text(x + (w/2) - (text_w/2), y + (h/2) + text_h_offset, text)

# ลดขนาดวงกลม ปรับตัวเลขให้ใหญ่และกึ่งกลางเป๊ะ
def draw_solid_circle(pdf, x, y, d, text="", font_size=28):
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*pdf.colors["primary"])
    pdf.set_line_width(0.8)
    pdf.ellipse(x, y, d, d, style='DF') 
    if text:
        pdf.set_font("CuteFont", "", font_size)
        pdf.set_text_color(*pdf.colors["primary"])
        text_w = pdf.get_string_width(text)
        # ปรับการชดเชยเพื่อให้ตัวเลขอยู่กึ่งกลางวงกลมอย่างสมบูรณ์
        text_h_offset = (font_size * 0.352777) / 3.0 
        pdf.text(x + (d/2) - (text_w/2), y + (d/2) + text_h_offset, text)

def draw_circle_placeholder(pdf, x, y, d, text="?"):
    pdf.set_fill_color(*pdf.colors["box"])
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.5)
    if hasattr(pdf, 'set_dash_pattern'):
        pdf.set_dash_pattern(dash=3, gap=3)
        pdf.ellipse(x, y, d, d, style='DF')
        pdf.set_dash_pattern()
    else:
        pdf.ellipse(x, y, d, d, style='DF')
        
    if text:
        pdf.set_font("CuteFont", "", 28)
        pdf.set_text_color(150, 150, 150)
        text_w = pdf.get_string_width(text)
        text_h_offset = (28 * 0.352777) / 3.0
        pdf.text(x + (d/2) - (text_w/2), y + (d/2) + text_h_offset, text)

# ==========================================
# 4. BESPOKE LAYOUT ENGINE 
# ==========================================
def generate_worksheet(sub_topic, theme_colors, num_q, shop_name, target_num, is_key=False):
    pdf = PremiumTpTPDF(sub_topic, theme_colors, shop_name, target_num, is_key)
    pdf.add_page()
    
    clean_sub = sub_topic.lower()
    
    pdf.set_font("CuteFont", "", 14)
    pdf.set_text_color(80, 80, 80)

    # 1. FIND THE NUMBER (เน้นระบายสี)
    if "find" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color the number {target_num} in the picture below.", ln=True)
        pdf.ln(5)
        pdf.set_font("CuteFont", "", 20)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.cell(0, 10, f"Target: {target_num}", ln=True, align="C")
        draw_placeholder(pdf, 15, 85, 185, 160, f"~ Canva: Add a large scene. Scatter number {target_num} everywhere! ~", font_size=14)

    # 2. TRACE THE NUMBERS
    elif "trace" in clean_sub:
        pdf.cell(0, 10, f" Directions: Trace and write the number {target_num}.", ln=True)
        pdf.ln(5)
        for i in range(num_q + 1): 
            if pdf.get_y() > 240: pdf.add_page()
            y = pdf.get_y()
            draw_placeholder(pdf, 20, y, 30, 30, f"~ {target_num} Items ~")
            draw_placeholder(pdf, 60, y, 130, 30, f"~ Canva: Dotted number {target_num} ~")
            pdf.ln(40)

    # 3. COUNTING (เปลี่ยนวงกลมให้เล็กลง และให้ระบายสี)
    elif "counting" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count the objects. Color the correct number.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            actual_count = target_num if i == 0 else random.choice([target_num, random.randint(1, 10)])
            choices = [actual_count]
            while len(choices) < 3:
                wrong = random.randint(1, 10)
                if wrong not in choices:
                    choices.append(wrong)
            random.shuffle(choices) 
            
            # ลดขนาดวงกลม (d=22) ขยับตำแหน่ง x เข้ามาเพื่อให้ห่างขอบขวา
            draw_placeholder(pdf, 20, y, 80, 35, f"~ Add {actual_count} items ~")
            draw_solid_circle(pdf, 115, y+6, 22, str(choices[0]), font_size=28)
            draw_solid_circle(pdf, 145, y+6, 22, str(choices[1]), font_size=28)
            draw_solid_circle(pdf, 175, y+6, 22, str(choices[2]), font_size=28)
            pdf.ln(50)

    # 4. COUNT AND MATCH 
    elif "match" in clean_sub:
        pdf.cell(0, 10, f" Directions: Draw a line to match the groups of {target_num}.", ln=True)
        pdf.ln(5)
        draw_solid_circle(pdf, 85, 120, 45, str(target_num), font_size=50)
        
        draw_placeholder(pdf, 20, 80, 45, 35, f"~ {target_num} dots ~")
        draw_placeholder(pdf, 150, 80, 45, 35, f"~ {target_num} fingers ~")
        draw_placeholder(pdf, 20, 160, 45, 35, f"~ {random.randint(1, 10)} items ~") 
        draw_placeholder(pdf, 150, 160, 45, 35, f"~ {target_num} animals ~")

    # 5. MORE OR LESS (ให้ระบายสีกล่อง)
    elif "more" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the box that has {target_num} items.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            wrong = random.choice([x for x in range(1, 11) if x != target_num])
            options = [target_num, wrong]
            random.shuffle(options)
            
            draw_placeholder(pdf, 30, y, 60, 45, f"~ {options[0]} items ~")
            pdf.set_font("CuteFont", "", 20)
            pdf.set_text_color(*theme_colors["secondary"])
            pdf.text(102, y + 28, "VS")
            draw_placeholder(pdf, 125, y, 60, 45, f"~ {options[1]} items ~")
            pdf.ln(55)

    # 6. COLOR BY NUMBER
    elif "color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the picture using the code.", ln=True)
        pdf.ln(5)
        y = pdf.get_y()
        pdf.set_fill_color(*theme_colors["box"])
        pdf.rect(15, y, 185, 20, style='F')
        
        pdf.set_font("CuteFont", "", 16)
        pdf.set_text_color(100, 100, 100)
        pdf.text(35, y + 14, f"{target_num} = Red")
        pdf.text(90, y + 14, f"{target_num+1 if target_num<10 else target_num-1} = Blue")
        pdf.text(145, y + 14, f"{target_num+2 if target_num<9 else target_num-2} = Yellow")
            
        pdf.ln(30)
        draw_placeholder(pdf, 15, pdf.get_y(), 185, 150, f"~ Canva: Coloring Image focusing on {target_num} ~", font_size=14)

    # 7. MISSING NUMBERS 
    elif "missing" in clean_sub:
        pdf.cell(0, 10, f" Directions: Fill in the missing numbers to reach {target_num}.", ln=True)
        pdf.ln(10)
        for i in range(num_q):
            if pdf.get_y() > 240: pdf.add_page()
            y = pdf.get_y()
            
            start_val = max(1, target_num - random.randint(0, 4))
            seq = [start_val + k for k in range(5)]
            
            hidden = [seq.index(target_num)] if target_num in seq else [2]
            other_hidden = random.choice([x for x in range(5) if x not in hidden])
            hidden.append(other_hidden)
            
            for j in range(5):
                # ขยับช่องไฟให้พอดี ปรับขนาดวงกลมเป็น 28 และตัวเลข 28
                x = 18 + (j * 34)
                if j in hidden:
                    draw_circle_placeholder(pdf, x, y, 28, "?")
                else:
                    draw_solid_circle(pdf, x, y, 28, str(seq[j]), font_size=28)
            pdf.ln(50)

    # 8. NUMBER MAZES
    elif "maze" in clean_sub:
        wrong_maze = random.choice([x for x in range(1, 11) if x != target_num])
        
        pdf.cell(0, 10, f" Directions: Color the number {target_num} to find the way out of the maze!", ln=True)
        pdf.ln(5)
        start_x = 45
        start_y = pdf.get_y() + 10
        box_s = 25
        pdf.set_font("CuteFont", "", 16)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.text(start_x, start_y - 5, "START")
        
        for row in range(5):
            for col in range(5):
                val = str(target_num) if random.random() > 0.5 else str(wrong_maze)
                # ปรับวงกลมให้เล็กลง (d=20) และตัวเลขกึ่งกลาง
                draw_solid_circle(pdf, start_x + (col*box_s) + 2, start_y + (row*box_s) + 2, 20, val, font_size=22)
                
        pdf.text(start_x + (4*box_s), start_y + (5*box_s) + 5, "FINISH")

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
            .premium-paper { box-shadow: 0 15px 35px rgba(0,0,0,0.1); border-radius: 12px; background: white; padding: 10px; border: 1px solid #f0f0f0; }
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
st.set_page_config(page_title="Pre-K Focus Number Gen", layout="wide", page_icon="🎨")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); padding: 2rem; border-radius: 15px; color: #2c3e50; text-align: center; margin-bottom: 2rem; }
    div.stButton > button { background-color: #ff9a9e; color: white; border: none; border-radius: 8px; font-weight: bold; }
</style>
<div class="main-header">
    <h1 style="margin:0; font-weight:800;">🎨 Pre-K Focus Number Generator</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem;">(อัปเดต: เน้นกิจกรรมระบายสี, ขนาดวงกลมพอดีขอบ, ตัวเลขใหญ่กึ่งกลางเป๊ะ)</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 ตกแต่งใบงาน (Customize)")
    
    shop_name = st.text_input("🏪 ชื่อร้าน (Copyright):", value="Kindergarten Learning Press")
    st.markdown("---")
    
    main_topic = "1. Number Sense (การรู้ค่าตัวเลข)" 
    sub_topic = st.selectbox("🎯 1. เลือกกิจกรรม (Activity):", PRE_K_CURRICULUM[main_topic])
    
    theme_choice = st.selectbox("🖌️ 2. โทนสี (Color Palette):", list(THEME_COLORS.keys()))
    selected_colors = THEME_COLORS[theme_choice]
    
    st.markdown("---")
    target_num = st.selectbox("🎯 3. เลือกตัวเลขเป้าหมาย (Focus Number):", list(range(1, 11)))
    
    num_q = st.slider("📝 4. จำนวนข้อต่อหน้า:", min_value=2, max_value=5, value=3)
    
    st.markdown("---")
    generate_btn = st.button("🚀 สร้างโครงร่าง (Generate PDF)", use_container_width=True)

if generate_btn:
    with st.spinner(f"กำลังสร้างใบงานและดาวน์โหลดฟอนต์น่ารัก โฟกัสเลข {target_num}..."):
        ws_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, is_key=False)
        ans_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, is_key=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            display_pdf_preview(ws_bytes)
            
        with col2:
            st.subheader(f"📥 ดาวน์โหลดไฟล์ (Number {target_num})")
            st.success(f"✅ สร้างใบงานโฟกัสเลข {target_num} สำเร็จ!")
            
            file_title = sub_topic.split('. ')[1].replace(' ', '_')
            
            st.download_button(
                label=f"📄 โหลดโครงร่าง (Worksheet - Num {target_num})",
                data=ws_bytes,
                file_name=f"PreK_{file_title}_Number_{target_num}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.download_button(
                label=f"🔑 โหลดเฉลย (Answer Key - Num {target_num})",
                data=ans_bytes,
                file_name=f"PreK_{file_title}_Number_{target_num}_KEY.pdf",
                mime="application/pdf",
                use_container_width=True
            )
else:
    st.info("👈 กรุณาเลือก **ตัวเลขที่ต้องการ (Focus Number)** แล้วกดปุ่มสร้างใบงานได้เลยครับ")
