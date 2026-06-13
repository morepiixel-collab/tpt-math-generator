import streamlit as st
from fpdf import FPDF
import random
import base64
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# 1. ฐานข้อมูลหัวข้อ (จากไฟล์อ้างอิงของคุณ)
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

# ==========================================
# 2. คลาสสร้างหน้ากระดาษ (US Letter)
# ==========================================
class TpTKindergartenPDF(FPDF):
    def __init__(self, topic_name, is_key=False):
        super().__init__(orientation='P', unit='mm', format='Letter')
        self.topic_name = topic_name
        self.is_key = is_key
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # กรอบขอบกระดาษ (Border)
        self.set_line_width(0.5)
        self.rect(10, 10, 196, 259)
        self.set_line_width(0.2)
        self.rect(12, 12, 192, 255)

        # แถบ Header สีเทาด้านบน (สไตล์ TpT)
        self.set_fill_color(230, 230, 230)
        self.rect(10, 10, 196, 25, style='F')
        
        self.set_font("helvetica", "B", 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "KINDERGARTEN MATH", ln=True, align="L")
        
        # ชื่อหัวข้อ
        self.set_font("helvetica", "B", 20)
        self.set_text_color(0, 0, 0)
        clean_topic = self.topic_name.split(". ", 1)[-1]
        title = clean_topic + (" (ANSWER KEY)" if self.is_key else "")
        self.cell(0, 10, title, ln=True, align="C")
        
        # ช่องกรอกชื่อ
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Name: _______________________   Date: _________", ln=True, align="R")
        self.ln(5)

# ==========================================
# 3. ฟังก์ชันวาดกรอบเว้นว่างสำหรับรูปภาพ (Placeholder)
# ==========================================
def draw_image_placeholder(pdf, x, y, w, h, text="[ Insert Image Here ]"):
    pdf.set_fill_color(250, 250, 250)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_dash_pattern(dash=2, gap=2) # ทำเส้นประ
    pdf.rect(x, y, w, h, style='DF')
    pdf.set_dash_pattern() # คืนค่าเส้นทึบ
    
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(150, 150, 150)
    pdf.text(x + (w/2) - (pdf.get_string_width(text)/2), y + (h/2) + 2, text)
    pdf.set_text_color(0, 0, 0)

# ==========================================
# 4. ฟังก์ชันสร้างโจทย์และ Layout
# ==========================================
def generate_worksheet(topic, num_q, is_key=False):
    pdf = TpTKindergartenPDF(topic, is_key)
    pdf.add_page()
    pdf.set_font("helvetica", "", 14)
    
    clean_topic = topic.split(". ", 1)[-1]
    ans_color = (220, 20, 20) if is_key else (0, 0, 0)
    
    # ------------------------------------------------
    # รูปแบบ 1: แบบ 2 คอลัมน์ (โจทย์สั้นๆ / สมการ)
    # ------------------------------------------------
    if clean_topic in ["What Comes Next?", "Missing Addends", "True or False", "Which is More?", "Write Number's Name"]:
        pdf.cell(0, 10, "Directions: Solve the math problems below.", ln=True)
        pdf.ln(5)
        
        col_w = 90
        box_h = 40
        for i in range(num_q):
            col = i % 2
            x = 15 if col == 0 else 15 + col_w + 10
            if col == 0 and i > 0:
                pdf.set_y(pdf.get_y() + box_h + 5)
            if pdf.get_y() > 220:
                pdf.add_page()
                pdf.set_y(45)
            
            # วาดกล่องโจทย์
            pdf.set_draw_color(0, 0, 0)
            pdf.rect(x, pdf.get_y(), col_w, box_h)
            pdf.set_font("helvetica", "B", 12)
            pdf.text(x + 5, pdf.get_y() + 8, f"Q{i+1}")
            
            # เนื้อหาโจทย์
            pdf.set_font("helvetica", "B", 18)
            if clean_topic == "What Comes Next?":
                start = random.randint(1, 15)
                pdf.text(x + 15, pdf.get_y() + 25, f"{start},  {start+1},  {start+2},  _____")
                if is_key:
                    pdf.set_text_color(*ans_color)
                    pdf.text(x + 65, pdf.get_y() + 24, str(start+3))
                    pdf.set_text_color(0, 0, 0)

            elif clean_topic == "True or False":
                a, b = random.randint(1, 10), random.randint(1, 10)
                is_true = random.choice([True, False])
                ans = a + b if is_true else a + b + random.choice([1, -1])
                pdf.text(x + 20, pdf.get_y() + 18, f"{a} + {b} = {ans}")
                pdf.set_font("helvetica", "", 14)
                if is_key:
                    pdf.set_text_color(*ans_color)
                    pdf.text(x + 20, pdf.get_y() + 32, "[ TRUE ]" if is_true else "[ FALSE ]")
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.text(x + 20, pdf.get_y() + 32, "TRUE      FALSE")
                    
            elif clean_topic == "Write Number's Name":
                num = random.randint(11, 20)
                words = {11:"Eleven", 12:"Twelve", 13:"Thirteen", 14:"Fourteen", 15:"Fifteen", 16:"Sixteen", 17:"Seventeen", 18:"Eighteen", 19:"Nineteen", 20:"Twenty"}
                pdf.text(x + 15, pdf.get_y() + 25, f"{num}  =  ______________")
                if is_key:
                    pdf.set_text_color(*ans_color)
                    pdf.text(x + 45, pdf.get_y() + 24, words[num])
                    pdf.set_text_color(0, 0, 0)

    # ------------------------------------------------
    # รูปแบบ 2: แบบมีช่องเว้นวางภาพ (Wireframe Placeholder)
    # ------------------------------------------------
    else:
        pdf.cell(0, 10, "Directions: Look at the pictures and solve the problems.", ln=True)
        pdf.ln(5)
        
        for i in range(num_q):
            if pdf.get_y() > 220: pdf.add_page()
            
            # วาดเส้นประกล่องเว้นภาพ!
            if clean_topic == "Tens and Ones":
                draw_image_placeholder(pdf, 20, pdf.get_y(), 100, 35, "[ Add Tens & Ones Blocks ]")
            elif clean_topic == "Roll It On":
                draw_image_placeholder(pdf, 20, pdf.get_y(), 60, 35, "[ Add 2 Dice ]")
            elif clean_topic == "Picture Subtraction":
                draw_image_placeholder(pdf, 20, pdf.get_y(), 120, 35, "[ Add objects with 'X' crossed out ]")
            elif clean_topic == "Teen Numbers (11-20)":
                draw_image_placeholder(pdf, 20, pdf.get_y(), 120, 35, "[ Add 11-20 Clipart items ]")
            else:
                draw_image_placeholder(pdf, 20, pdf.get_y(), 100, 35, "[ Insert Clipart Here ]")
                
            # กล่องคำตอบด้านขวา
            pdf.set_draw_color(0, 0, 0)
            pdf.rect(150, pdf.get_y() + 5, 30, 25)
            pdf.set_font("helvetica", "B", 12)
            pdf.text(152, pdf.get_y() + 3, "Answer:")
            
            if is_key:
                pdf.set_font("helvetica", "B", 24)
                pdf.set_text_color(*ans_color)
                pdf.text(160, pdf.get_y() + 24, "?") # เป็น ? เพราะเฉลยขึ้นอยู่กับภาพที่คุณใส่
                pdf.set_text_color(0, 0, 0)
            
            pdf.ln(45)

    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. ฟังก์ชันพรีวิวด้วย PyMuPDF 
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
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border-radius: 8px;
                background: white;
                padding: 4px;
                border: 1px solid #e0e0e0;
                display: inline-block;
            }
            </style>
            """, unsafe_allow_html=True
        )
        st.markdown("<div class='premium-paper'>", unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        doc.close()
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถแสดงพรีวิวได้: {e}")

# ==========================================
# 6. Streamlit UI
# ==========================================
st.set_page_config(page_title="TpT Layout Generator", layout="wide")

st.title("🧩 TpT Worksheet Wireframe Generator")
st.markdown("ระบบสร้างโครงกระดูกใบงาน (Wireframe) ที่ตีเส้นประเว้นช่องว่างให้คุณนำไฟล์ไปใส่รูปจาก Canva ต่อได้ทันที!")

with st.sidebar:
    st.header("⚙️ การตั้งค่าใบงาน")
    topic = st.selectbox("📌 เลือกหัวข้อกิจกรรม (Activity):", KINDERGARTEN_TOPICS)
    
    is_two_col = topic.split(". ", 1)[-1] in ["What Comes Next?", "Missing Addends", "True or False", "Which is More?", "Write Number's Name"]
    num_q = st.slider("🔢 จำนวนข้อต่อหน้า:", min_value=2, max_value=8, value=6 if is_two_col else 3)

# Generate Live
ws_bytes = generate_worksheet(topic, num_q, is_key=False)
ans_bytes = generate_worksheet(topic, num_q, is_key=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"🔍 พรีวิวโครงสร้าง: {topic.split('. ')[-1]}")
    display_pdf_preview(ws_bytes)

with col2:
    st.subheader("📥 ดาวน์โหลดไฟล์ไปเปิดใน Canva")
    st.download_button(
        label="📄 ดาวน์โหลดใบงาน (Worksheet PDF)",
        data=ws_bytes,
        file_name=f"Wireframe_{topic.split('. ')[1].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.download_button(
        label="🔑 ดาวน์โหลดเฉลย (Answer Key PDF)",
        data=ans_bytes,
        file_name=f"Wireframe_Key_{topic.split('. ')[1].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
