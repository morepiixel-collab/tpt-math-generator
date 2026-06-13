import streamlit as st
from fpdf import FPDF
import random
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# 1. ฐานข้อมูลหัวข้อ
# ==========================================
KINDERGARTEN_TOPICS = [
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

# โทนสีพาสเทลระดับพรีเมียมสำหรับ Wireframe
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
        # 1. กรอบกระดาษขอบหนาสีพาสเทล (Outer Thick Border)
        self.set_line_width(2.0)
        self.set_draw_color(*self.colors["primary"])
        self.rect(8, 8, 200, 263)
        
        # 2. กรอบเส้นประด้านใน (Inner Dashed Border) เพื่อความน่ารัก
        self.set_line_width(0.3)
        self.set_draw_color(*self.colors["secondary"])
        self.set_dash_pattern(dash=2, gap=2)
        self.rect(11, 11, 194, 257)
        self.set_dash_pattern() # Reset

        # 3. แถบ Header สีสันสดใส
        self.set_fill_color(*self.colors["primary"])
        self.rect(11, 11, 194, 28, style='F')
        
        # ข้อความ KINDERGARTEN
        self.set_font("helvetica", "B", 10)
        self.set_text_color(255, 255, 255) # ตัวหนังสือสีขาว
        self.cell(0, 8, " K I N D E R G A R T E N   M A T H", ln=True, align="C")
        
        # ชื่อหัวข้อกิจกรรม
        self.set_font("helvetica", "B", 24)
        clean_topic = self.topic_name.split(". ", 1)[-1].upper()
        title = clean_topic + (" (KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        self.ln(6)
        
        # 4. กล่องใส่ชื่อและวันที่ (Name & Date Badge)
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(11, 41, 194, 12, style='DF')
        
        self.set_font("helvetica", "B", 12)
        self.set_text_color(100, 100, 100)
        self.set_y(44)
        self.cell(10, 5, "", ln=0) # Padding
        self.cell(90, 5, "Name: ___________________________", ln=0, align="L")
        self.cell(80, 5, "Date: _______________", ln=1, align="R")
        self.ln(8)

# ==========================================
# 3. ฟังก์ชันวาดกล่อง Placeholder สไตล์น่ารัก
# ==========================================
def draw_cute_placeholder(pdf, x, y, w, h, text="[ Drop Clipart Here ]"):
    # พื้นหลังสีอ่อนๆ ตามธีม
    pdf.set_fill_color(*pdf.colors["box"])
    # ขอบสีเทาอ่อนๆ เส้นประ
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.5)
    pdf.set_dash_pattern(dash=3, gap=3)
    pdf.rect(x, y, w, h, style='DF')
    pdf.set_dash_pattern() # Reset
    
    # ข้อความด้านใน (กึ่งกลาง)
    pdf.set_font("helvetica", "I", 11)
    pdf.set_text_color(150, 150, 150)
    text_w = pdf.get_string_width(text)
    pdf.text(x + (w/2) - (text_w/2), y + (h/2) + 2, text)

# ==========================================
# 4. เอนจินสร้างโจทย์และ Layout
# ==========================================
def generate_worksheet(topic, theme_colors, num_q, is_key=False):
    pdf = PremiumTpTPDF(topic, theme_colors, is_key)
    pdf.add_page()
    
    clean_topic = topic.split(". ", 1)[-1]
    ans_color = (255, 75, 75) if is_key else (0, 0, 0)
    
    # คำสั่ง (Directions) ที่ดูสะอาดตา
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, " Directions: Look at the pictures and solve the problems below.", ln=True)
    pdf.ln(2)
    
    # ------------------------------------------------
    # รูปแบบ 1: แบบ 2 คอลัมน์ (โจทย์สมการ/ตัวเลข)
    # ------------------------------------------------
    if clean_topic in ["What Comes Next?", "Missing Addends", "True or False", "Which is More?", "Write Number's Name"]:
        col_w = 85
        box_h = 35
        for i in range(num_q):
            col = i % 2
            x = 18 if col == 0 else 18 + col_w + 15
            if col == 0 and i > 0:
                pdf.set_y(pdf.get_y() + box_h + 8)
            if pdf.get_y() > 220:
                pdf.add_page()
                pdf.set_y(60)
            
            # วาดกล่องโจทย์แบบมุมมน (จำลองด้วยการซ้อนสี)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.set_line_width(0.8)
            pdf.rect(x, pdf.get_y(), col_w, box_h, style='DF')
            
            # เลขข้อ (น่ารักๆ)
            pdf.set_fill_color(*theme_colors["secondary"])
            pdf.rect(x, pdf.get_y(), 12, 10, style='F')
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(255, 255, 255)
            pdf.text(x + 2, pdf.get_y() + 6, f"{i+1}")
            
            # เนื้อหาโจทย์
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("helvetica", "B", 18)
            
            if clean_topic == "What Comes Next?":
                start = random.randint(1, 15)
                pdf.text(x + 15, pdf.get_y() + 22, f"{start},  {start+1},  {start+2},  ___")
                if is_key:
                    pdf.set_text_color(*ans_color)
                    pdf.text(x + 65, pdf.get_y() + 21, str(start+3))

            elif clean_topic == "True or False":
                a, b = random.randint(1, 10), random.randint(1, 10)
                is_true = random.choice([True, False])
                ans = a + b if is_true else a + b + random.choice([1, -1])
                pdf.text(x + 20, pdf.get_y() + 15, f"{a} + {b} = {ans}")
                pdf.set_font("helvetica", "", 12)
                if is_key:
                    pdf.set_text_color(*ans_color)
                    pdf.text(x + 20, pdf.get_y() + 28, "[ TRUE ]" if is_true else "[ FALSE ]")
                else:
                    pdf.text(x + 20, pdf.get_y() + 28, "TRUE       FALSE")
                    
            elif clean_topic == "Write Number's Name":
                num = random.randint(11, 20)
                words = {11:"Eleven", 12:"Twelve", 13:"Thirteen", 14:"Fourteen", 15:"Fifteen", 16:"Sixteen", 17:"Seventeen", 18:"Eighteen", 19:"Nineteen", 20:"Twenty"}
                pdf.text(x + 15, pdf.get_y() + 22, f"{num} = __________")
                if is_key:
                    pdf.set_text_color(*ans_color)
                    pdf.text(x + 40, pdf.get_y() + 21, words[num])

    # ------------------------------------------------
    # รูปแบบ 2: แบบมีช่องเว้นวางภาพ (Placeholder)
    # ------------------------------------------------
    else:
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            
            # เลขข้อ (น่ารักๆ)
            pdf.set_fill_color(*theme_colors["secondary"])
            pdf.rect(15, pdf.get_y(), 10, 10, style='F')
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(255, 255, 255)
            pdf.text(17, pdf.get_y() + 6, f"{i+1}")
            
            # วาดเส้นประกล่องเว้นภาพ
            if clean_topic == "Tens and Ones":
                draw_cute_placeholder(pdf, 30, pdf.get_y(), 100, 35, "~ Add Tens & Ones Blocks ~")
            elif clean_topic == "Roll It On":
                draw_cute_placeholder(pdf, 30, pdf.get_y(), 60, 35, "~ Add 2 Dice Images ~")
            elif clean_topic == "Picture Subtraction":
                draw_cute_placeholder(pdf, 30, pdf.get_y(), 110, 35, "~ Add objects with 'X' ~")
            else:
                draw_cute_placeholder(pdf, 30, pdf.get_y(), 100, 35, "~ Insert Clipart Here ~")
                
            # กล่องคำตอบด้านขวา (Premium Box)
            pdf.set_draw_color(*theme_colors["primary"])
            pdf.set_line_width(0.8)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(150, pdf.get_y() + 5, 35, 25, style='DF')
            
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.text(152, pdf.get_y() + 10, "Answer:")
            
            if is_key:
                pdf.set_font("helvetica", "B", 24)
                pdf.set_text_color(*ans_color)
                pdf.text(162, pdf.get_y() + 24, "?") # เฉลยขึ้นกับรูป
            
            pdf.ln(45)

    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. พรีวิวด้วย PyMuPDF (กันเบราว์เซอร์บล็อก)
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
# 6. Streamlit UI (สวยงามน่าใช้)
# ==========================================
st.set_page_config(page_title="TpT Premium Generator", layout="wide", page_icon="✨")

# Custom CSS สำหรับ Streamlit
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
        box-shadow: 0 4px 10px rgba(255, 117, 140, 0.4);
    }
</style>
<div class="main-header">
    <h1 style="margin:0; font-weight:800;">✨ Premium TpT Wireframe Generator</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem;">สร้างโครงกระดูกใบงานคณิตศาสตร์สไตล์พรีเมียม พร้อมนำไปแต่งต่อใน Canva</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("🎨 ตกแต่งใบงาน (Customize)")
    topic = st.selectbox("📌 1. เลือกหัวข้อ (Activity):", KINDERGARTEN_TOPICS)
    
    theme_choice = st.selectbox("🖌️ 2. โทนสี (Color Palette):", list(THEME_COLORS.keys()))
    selected_colors = THEME_COLORS[theme_choice]
    
    is_two_col = topic.split(". ", 1)[-1] in ["What Comes Next?", "Missing Addends", "True or False", "Which is More?", "Write Number's Name"]
    num_q = st.slider("🔢 3. จำนวนข้อต่อหน้า:", min_value=2, max_value=8, value=6 if is_two_col else 3)
    
    st.markdown("---")
    st.success("💡 **Tip:** โทนสีพาสเทลจะช่วยให้ใบงานของคุณดูแพง และโดดเด่นกว่าใบงานขาวดำทั่วไปบน TpT")

# Generate Live
ws_bytes = generate_worksheet(topic, selected_colors, num_q, is_key=False)
ans_bytes = generate_worksheet(topic, selected_colors, num_q, is_key=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    display_pdf_preview(ws_bytes)

with col2:
    st.subheader("📥 ดาวน์โหลดไฟล์ (Ready for Canva)")
    st.markdown("ไฟล์ที่ได้จะถูกจัดรูปแบบไว้อย่างสมบูรณ์แบบ คุณเพียงแค่นำไปเปิดใน **Canva** และลาก Clipart น่ารักๆ ไปวางทับบริเวณเส้นประ")
    
    st.download_button(
        label="📄 ดาวน์โหลดใบงาน (Worksheet PDF)",
        data=ws_bytes,
        file_name=f"Premium_WS_{topic.split('. ')[1].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.download_button(
        label="🔑 ดาวน์โหลดเฉลย (Answer Key PDF)",
        data=ans_bytes,
        file_name=f"Premium_KEY_{topic.split('. ')[1].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
