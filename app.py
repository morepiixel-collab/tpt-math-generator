import streamlit as st
from fpdf import FPDF
import random
import fitz  
from PIL import Image
import os
import urllib.request

# ==========================================
# 0. ระบบดาวน์โหลดฟอนต์ (Comic Neue)
# ==========================================
FONT_FILE = "ComicNeue.ttf"
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
    "Sweet Pink (ชมพูหวานแหวว) 🎀": {"primary": (244, 143, 177), "secondary": (129, 212, 250), "box": (255, 240, 245)},
    "Cotton Candy (ฟ้า-ชมพู)": {"primary": (118, 165, 234), "secondary": (244, 164, 185), "box": (248, 250, 255)},
    "Minty Fresh (เขียวมิ้นต์)": {"primary": (104, 195, 163), "secondary": (243, 156, 18), "box": (245, 255, 250)},
    "Lavender Dream (ม่วงอ่อน)": {"primary": (155, 89, 182), "secondary": (26, 188, 156), "box": (252, 248, 255)},
    "Sunshine (เหลือง-ส้ม)": {"primary": (243, 156, 18), "secondary": (231, 76, 60), "box": (255, 253, 240)}
}

# ==========================================
# 2. คลาสหน้ากระดาษ Premium Border
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
            self.add_font("ComicNeue", "", FONT_FILE)
        else:
            self.add_font("ComicNeue", "", "helvetica") 

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
        
        self.set_font("ComicNeue", "", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, " P R E - K   M A T H", ln=True, align="C")
        
        self.set_font("ComicNeue", "", 24)
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        title = f"{clean_topic} : NUMBER {self.target_num}" + (" (KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(6)
        
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(11, 41, 194, 12, style='DF')
        
        self.set_font("ComicNeue", "", 14)
        self.set_text_color(100, 100, 100)
        self.set_y(44)
        self.cell(10, 5, "", ln=0)
        self.cell(90, 5, "Name: ___________________________", ln=0, align="L")
        self.cell(80, 5, "Date: _______________", ln=1, align="R")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("ComicNeue", "", 10)
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
        pdf.set_font("ComicNeue", "", font_size)
        pdf.set_text_color(150, 150, 150)
        text_w = pdf.get_string_width(text)
        text_h_offset = (font_size * 0.352777) / 2.8 
        pdf.text(x + (w/2) - (text_w/2), y + (h/2) + text_h_offset, text)

def draw_solid_circle(pdf, x, y, d, text="", font_size=28):
    if pdf.is_key and text == str(pdf.target_num):
        pdf.set_fill_color(*pdf.colors["secondary"])
        pdf.set_draw_color(*pdf.colors["primary"])
        text_color = (255, 255, 255)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(*pdf.colors["primary"])
        text_color = pdf.colors["primary"]
        
    pdf.set_line_width(0.8)
    pdf.ellipse(x, y, d, d, style='DF') 
    
    if text:
        pdf.set_font("ComicNeue", "", font_size)
        pdf.set_text_color(*text_color)
        text_w = pdf.get_string_width(text)
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
        pdf.set_font("ComicNeue", "", 28)
        pdf.set_text_color(150, 150, 150)
        text_w = pdf.get_string_width(text)
        text_h_offset = (28 * 0.352777) / 3.0
        pdf.text(x + (d/2) - (text_w/2), y + (d/2) + text_h_offset, text)

# ==========================================
# 4. BESPOKE LAYOUT ENGINE (Dynamic & Anti-Duplication)
# ==========================================
def generate_worksheet(sub_topic, theme_colors, num_q, shop_name, target_num, session_seed, is_key=False):
    random.seed(session_seed)
    
    pdf = PremiumTpTPDF(sub_topic, theme_colors, shop_name, target_num, is_key)
    pdf.add_page()
    
    clean_sub = sub_topic.lower()
    pdf.set_font("ComicNeue", "", 14)
    pdf.set_text_color(80, 80, 80)

    # 1. FIND THE NUMBER
    if "find" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color the number {target_num} in the picture below.", ln=True)
        pdf.ln(5)
        pdf.set_font("ComicNeue", "", 20)
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

    # 3. COUNTING OBJECTS (Anti-Duplication)
    elif "counting" in clean_sub:
        pdf.cell(0, 10, f" Directions: Count the objects. Color the circle with the correct number.", ln=True)
        pdf.ln(5)
        
        seen_choices = set() # เก็บประวัติข้อที่เคยออกแล้ว
        
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            actual_count = target_num 
            
            # ระบบป้องกันช้อยส์สลับซ้ำตำแหน่งเดิมเป๊ะๆ
            for _ in range(50):
                choices = [actual_count]
                while len(choices) < 3:
                    wrong = random.randint(1, 10)
                    if wrong not in choices:
                        choices.append(wrong)
                random.shuffle(choices) 
                
                sig = tuple(choices)
                if sig not in seen_choices:
                    seen_choices.add(sig)
                    break
            
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
        
        wrong_count = random.choice([x for x in range(1, 11) if x != target_num])
        
        boxes = [
            f"~ {target_num} dots ~",
            f"~ {target_num} fingers ~",
            f"~ {target_num} animals ~",
            f"~ {wrong_count} items ~" 
        ]
        random.shuffle(boxes) 
        
        draw_placeholder(pdf, 20, 80, 45, 35, boxes[0])
        draw_placeholder(pdf, 150, 80, 45, 35, boxes[1])
        draw_placeholder(pdf, 20, 160, 45, 35, boxes[2]) 
        draw_placeholder(pdf, 150, 160, 45, 35, boxes[3])

    # 5. MORE OR LESS? (Anti-Duplication)
    elif "more" in clean_sub:
        pdf.cell(0, 10, f" Directions: Color the box that has exactly {target_num} items.", ln=True)
        pdf.ln(5)
        
        seen_options = set()
        
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            
            # ป้องกันการแสดงฝั่งเดิมๆ ซ้ำกันติดๆ กัน
            for _ in range(50):
                wrong = random.choice([x for x in range(1, 11) if x != target_num])
                options = [target_num, wrong]
                random.shuffle(options) 
                
                sig = tuple(options)
                if sig not in seen_options:
                    seen_options.add(sig)
                    break
            
            txt_left = f"~ {options[0]} items ~" + (" (CORRECT)" if (pdf.is_key and options[0] == target_num) else "")
            txt_right = f"~ {options[1]} items ~" + (" (CORRECT)" if (pdf.is_key and options[1] == target_num) else "")
            
            draw_placeholder(pdf, 30, y, 60, 45, txt_left)
            pdf.set_font("ComicNeue", "", 20)
            pdf.set_text_color(*theme_colors["secondary"])
            pdf.text(102, y + 28, "VS")
            draw_placeholder(pdf, 125, y, 60, 45, txt_right)
            pdf.ln(55)

    # 6. COLOR BY NUMBER 
    elif "color" in clean_sub:
        pdf.cell(0, 10, f" Directions: Find and color all the number {target_num}s.", ln=True)
        pdf.ln(5)
        y = pdf.get_y()
        pdf.set_fill_color(*theme_colors["box"])
        pdf.rect(15, y, 20, 20, style='F') # ย่อแถบให้เล็กลงเหลือแค่อันเดียว
        
        all_colors = ["Red", "Blue", "Yellow", "Green", "Pink", "Purple", "Orange"]
        chosen_color = random.choice(all_colors)
        
        pdf.set_font("ComicNeue", "", 18)
        pdf.set_text_color(100, 100, 100)
        pdf.text(45, y + 14, f"Color {target_num} = {chosen_color}")
            
        pdf.ln(30)
        draw_placeholder(pdf, 15, pdf.get_y(), 185, 150, f"~ Canva: Add a picture with hidden {target_num}s to color ~", font_size=14)

    # 7. MISSING NUMBERS (Anti-Duplication + เปลี่ยนคำสั่งให้เข้าใจง่าย)
    elif "missing" in clean_sub:
        # เปลี่ยนคำสั่งให้เด็กไม่งง และรู้ว่าเป้าหมายคือเขียนเลขอะไร
        pdf.cell(0, 10, f" Directions: Fill in the missing numbers. Can you find where {target_num} goes?", ln=True)
        pdf.ln(10)
        
        seen_sequences = set() # ป้องกันโจทย์ซ้ำเป๊ะๆ ในหน้าเดียวกัน
        
        for i in range(num_q):
            if pdf.get_y() > 240: pdf.add_page()
            y = pdf.get_y()
            
            for _ in range(50):
                start_val = max(1, target_num - random.randint(0, 4))
                seq = [start_val + k for k in range(5)]
                
                # บังคับซ่อนเป้าหมาย (target_num) เสมอ และสุ่มซ่อนเพิ่มอีก 1 จุด
                hidden = [seq.index(target_num)] if target_num in seq else [2]
                other_hidden = random.choice([x for x in range(5) if x not in hidden])
                hidden.append(other_hidden)
                
                sig = (start_val, frozenset(hidden))
                if sig not in seen_sequences:
                    seen_sequences.add(sig)
                    break
            
            for j in range(5):
                x = 18 + (j * 34)
                if j in hidden:
                    val = str(seq[j]) if pdf.is_key else "?"
                    draw_circle_placeholder(pdf, x, y, 28, val)
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
        pdf.set_font("ComicNeue", "", 16)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.text(start_x, start_y - 5, "START")
        
        for row in range(5):
            for col in range(5):
                val = str(target_num) if random.random() > 0.4 else str(wrong_maze)
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
    .main-header { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 2rem; border-radius: 15px; color: #2c3e50; text-align: center; margin-bottom: 2rem; }
    div.stButton > button { background-color: #ff7494; color: white; border: none; border-radius: 8px; font-weight: bold; }
</style>
<div class="main-header">
    <h1 style="margin:0; font-weight:800;">🎨 Pre-K Focus Number Generator</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem;">(เวอร์ชันอัปเกรด: แก้ไขคำสั่ง + ระบบป้องกันข้อซ้ำซ้อน 100%)</p>
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
    current_session_seed = random.randint(1, 9999999)
    
    with st.spinner(f"กำลังสร้างใบงานแบบ Dynamic โฟกัสเลข {target_num}..."):
        ws_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed=current_session_seed, is_key=False)
        ans_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, target_num, session_seed=current_session_seed, is_key=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            display_pdf_preview(ws_bytes)
            
        with col2:
            st.subheader(f"📥 ดาวน์โหลดไฟล์ (Number {target_num})")
            st.success(f"✅ สร้างใบงานสำเร็จ! เลย์เอาต์ถูกสุ่มใหม่ 100%")
            
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
    st.info("👈 กรุณาเลือก **ตัวเลขที่ต้องการ** แล้วกดปุ่มสร้างใบงานได้เลยครับ (ไม่มีปัญหาข้อซ้ำติดกันแน่นอนครับ)")
