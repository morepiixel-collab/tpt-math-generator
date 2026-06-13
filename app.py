import streamlit as st
from fpdf import FPDF
import random
import fitz  
from PIL import Image

# ==========================================
# 1. ฐานข้อมูลหัวข้อ
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
    ]
}

THEME_COLORS = {
    "Cotton Candy (ฟ้า-ชมพู)": {"primary": (118, 165, 234), "secondary": (244, 164, 185), "box": (248, 250, 255)},
    "Minty Fresh (เขียวมิ้นต์)": {"primary": (104, 195, 163), "secondary": (243, 156, 18), "box": (245, 255, 250)},
    "Lavender Dream (ม่วงอ่อน)": {"primary": (155, 89, 182), "secondary": (26, 188, 156), "box": (252, 248, 255)},
    "Sunshine (เหลือง-ส้ม)": {"primary": (243, 156, 18), "secondary": (231, 76, 60), "box": (255, 253, 240)}
}

# ==========================================
# 2. คลาสหน้ากระดาษ (Premium Border & Footer)
# ==========================================
class PremiumTpTPDF(FPDF):
    def __init__(self, topic_name, color_theme, shop_name, is_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.topic_name = topic_name
        self.colors = color_theme
        self.shop_name = shop_name # รับชื่อร้านมา
        self.is_key = is_key
        # เผื่อขอบด้านล่างไว้สำหรับ Footer
        self.set_auto_page_break(auto=True, margin=15)

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
        
        self.set_font("helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, " P R E - K   M A T H", ln=True, align="C")
        
        self.set_font("helvetica", "B", 22)
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        title = clean_topic + (" (KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(6)
        
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

    # วาด Copyright ท้ายกระดาษทุกหน้า
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"© {self.shop_name} | All Rights Reserved.", align="C")

# ==========================================
# 3. Helpers สำหรับวาด
# ==========================================
def draw_placeholder(pdf, x, y, w, h, text=""):
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
        pdf.set_font("helvetica", "I", 10)
        pdf.set_text_color(150, 150, 150)
        text_w = pdf.get_string_width(text)
        pdf.text(x + (w/2) - (text_w/2), y + (h/2) + 2, text)

def draw_solid_box(pdf, x, y, w, h, text=""):
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*pdf.colors["primary"])
    pdf.set_line_width(0.8)
    pdf.rect(x, y, w, h, style='DF')
    if text:
        pdf.set_font("helvetica", "B", 18)
        pdf.set_text_color(*pdf.colors["primary"])
        text_w = pdf.get_string_width(text)
        pdf.text(x + (w/2) - (text_w/2), y + (h/2) + 6, text)

# ==========================================
# 4. BESPOKE LAYOUT ENGINE 
# ==========================================
def generate_worksheet(sub_topic, theme_colors, num_q, shop_name, is_key=False):
    pdf = PremiumTpTPDF(sub_topic, theme_colors, shop_name, is_key)
    pdf.add_page()
    
    clean_sub = sub_topic.lower()
    q_instruction = sub_topic.split(". ", 1)[-1] if ". " in sub_topic else sub_topic
    ans_color = (255, 75, 75) if is_key else (150, 150, 150)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(80, 80, 80)

    # 1. FIND THE NUMBER 
    if "find" in clean_sub:
        pdf.cell(0, 10, " Directions: Find and circle the target number in the picture below.", ln=True)
        pdf.ln(5)
        target = random.randint(1, 5)
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.cell(0, 10, f"Find the number:  {target}", ln=True, align="C")
        draw_placeholder(pdf, 15, 85, 185, 160, f"~ Canva: Add a large scene. Scatter number {target} inside ~")

    # 2. TRACE THE NUMBERS
    elif "trace" in clean_sub:
        pdf.cell(0, 10, " Directions: Trace the numbers.", ln=True)
        pdf.ln(5)
        for i in range(1, 6):
            y = pdf.get_y()
            draw_placeholder(pdf, 20, y, 30, 30, f"Pic x{i}")
            draw_placeholder(pdf, 60, y, 130, 30, f"~ Canva: Add dotted number {i} here ~")
            pdf.ln(40)

    # 3. COUNTING 1-5 
    elif "counting" in clean_sub:
        pdf.cell(0, 10, " Directions: Count the objects and circle the correct number.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_placeholder(pdf, 25, y, 80, 40, f"~ Add {random.randint(1,5)} items ~")
            draw_solid_box(pdf, 120, y+10, 20, 20, "1")
            draw_solid_box(pdf, 145, y+10, 20, 20, "3")
            draw_solid_box(pdf, 170, y+10, 20, 20, "5")
            pdf.ln(50)

    # 4. COUNT AND MATCH 
    elif "match" in clean_sub:
        pdf.cell(0, 10, " Directions: Count the objects and draw a line to the correct number.", ln=True)
        pdf.ln(10)
        for i in range(4):
            y = pdf.get_y()
            draw_placeholder(pdf, 30, y, 50, 35, f"~ Clipart Group {i+1} ~")
            draw_solid_box(pdf, 140, y, 35, 35, f"{random.randint(1,5)}")
            pdf.ln(45)

    # 5. MORE OR LESS 
    elif "more" in clean_sub:
        pdf.cell(0, 10, " Directions: Look at the two boxes. Circle the box that has MORE.", ln=True)
        pdf.ln(5)
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            y = pdf.get_y()
            draw_placeholder(pdf, 30, y, 60, 45, "~ Group A ~")
            pdf.set_font("helvetica", "B", 18)
            pdf.set_text_color(*theme_colors["secondary"])
            pdf.text(100, y + 25, "VS")
            draw_placeholder(pdf, 125, y, 60, 45, "~ Group B ~")
            pdf.ln(55)

    # 6. COLOR BY NUMBER
    elif "color" in clean_sub:
        pdf.cell(0, 10, " Directions: Color the picture using the color code.", ln=True)
        pdf.ln(5)
        y = pdf.get_y()
        pdf.set_fill_color(*theme_colors["box"])
        pdf.rect(15, y, 185, 30, style='F')
        colors = ["1 = Red", "2 = Blue", "3 = Green", "4 = Yellow"]
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(100, 100, 100)
        for i, c in enumerate(colors):
            pdf.text(30 + (i*40), y + 18, c)
        pdf.ln(40)
        draw_placeholder(pdf, 15, pdf.get_y(), 185, 140, "~ Canva: Add a large Coloring Image with numbers 1-4 inside ~")

    # 7. MISSING NUMBERS
    elif "missing" in clean_sub:
        pdf.cell(0, 10, " Directions: Fill in the missing numbers.", ln=True)
        pdf.ln(10)
        for i in range(num_q):
            if pdf.get_y() > 240: pdf.add_page()
            y = pdf.get_y()
            seq = [1, 2, 3, 4, 5]
            hidden = random.sample([0,1,2,3,4], 2)
            for j in range(5):
                x = 20 + (j * 35)
                if j in hidden:
                    draw_placeholder(pdf, x, y, 30, 30, "?")
                else:
                    draw_solid_box(pdf, x, y, 30, 30, str(seq[j]))
            pdf.ln(50)

    # 8. NUMBER MAZES
    elif "maze" in clean_sub:
        pdf.cell(0, 10, " Directions: Color the number 3 to find the way out of the maze!", ln=True)
        pdf.ln(5)
        start_x = 45
        start_y = pdf.get_y() + 10
        box_s = 25
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(*theme_colors["primary"])
        pdf.text(start_x, start_y - 5, "START")
        for row in range(5):
            for col in range(5):
                draw_solid_box(pdf, start_x + (col*box_s), start_y + (row*box_s), box_s, box_s, "3" if random.random() > 0.5 else "4")
        pdf.text(start_x + (4*box_s), start_y + (5*box_s) + 10, "FINISH")

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
st.set_page_config(page_title="Pre-K Premium Generator", layout="wide", page_icon="✨")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); padding: 2rem; border-radius: 15px; color: #2c3e50; text-align: center; margin-bottom: 2rem; }
    div.stButton > button { background-color: #ff9a9e; color: white; border: none; border-radius: 8px; font-weight: bold; }
</style>
<div class="main-header">
    <h1 style="margin:0; font-weight:800;">✨ Pre-K Bespoke Layout Generator</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem;">อัปเกรดเลย์เอาต์! แยกโครงสร้างการจัดหน้าตามประเภทกิจกรรมโดยเฉพาะ (ไม่ซ้ำซาก)</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 ตกแต่งใบงาน (Customize)")
    
    # เพิ่มช่องใส่ Shop Name สำหรับ Copyright
    shop_name = st.text_input("🏪 ชื่อร้าน (Copyright):", value="Kindergarten Learning Press")
    st.markdown("---")
    
    main_topic = "1. Number Sense (การรู้ค่าตัวเลข)" 
    sub_topic = st.selectbox("🎯 1. เลือกกิจกรรม (Activity):", PRE_K_CURRICULUM[main_topic])
    
    theme_choice = st.selectbox("🖌️ 2. โทนสี (Color Palette):", list(THEME_COLORS.keys()))
    selected_colors = THEME_COLORS[theme_choice]
    
    num_q = st.slider("🔢 3. จำนวนข้อต่อหน้า:", min_value=2, max_value=4, value=3)
    
    st.markdown("---")
    # เพิ่มปุ่มกด Generate
    generate_btn = st.button("🚀 สร้างโครงร่าง (Generate PDF)", use_container_width=True)

# ตรวจสอบการกดปุ่ม Generate
if generate_btn:
    with st.spinner("กำลังสร้างเลย์เอาต์เฉพาะกิจกรรม..."):
        ws_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, is_key=False)
        ans_bytes = generate_worksheet(sub_topic, selected_colors, num_q, shop_name, is_key=True)

        col1, col2 = st.columns([1.5, 1])
        with col1:
            display_pdf_preview(ws_bytes)
            
        with col2:
            st.subheader("📥 ดาวน์โหลดไฟล์ (Ready for Canva)")
            st.success("✅ สร้างใบงานสำเร็จ!")
            st.download_button(
                label="📄 ดาวน์โหลดโครงร่าง (Worksheet PDF)",
                data=ws_bytes,
                file_name=f"PreK_{sub_topic.split('. ')[1].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.download_button(
                label="🔑 ดาวน์โหลดเฉลย (Answer Key PDF)",
                data=ans_bytes,
                file_name=f"PreK_{sub_topic.split('. ')[1].replace(' ', '_')}_KEY.pdf",
                mime="application/pdf",
                use_container_width=True
            )
else:
    # หน้าจอเริ่มต้นก่อนกดปุ่ม
    st.info("👈 กรุณาตั้งค่าใบงานที่แถบด้านซ้าย (ใส่ชื่อร้าน, เลือกกิจกรรม, เลือกสี) แล้วกดปุ่ม **'🚀 สร้างโครงร่าง (Generate PDF)'**")
